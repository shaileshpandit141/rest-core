import json
from typing import Any

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.db.models import ForeignKey, OneToOneField


class Command(BaseCommand):
    help = "Create or update model records from a JSON file with FK/M2M support."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--model",
            required=True,
            type=str,
            help="Model in 'app_label.ModelName' format",
        )
        parser.add_argument(
            "--records",
            required=True,
            type=str,
            help="Path to JSON file with a list of records",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Update existing records instead of skipping",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate actions without saving to DB",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print each processed record",
        )
        parser.add_argument(
            "--lookup",
            type=str,
            default="id,pk",
            help="Comma-separated list of lookup fields to be used for FK and M2M relations (default: id,pk)",
        )

    def handle(self, *args, **options) -> Any:
        model_path = options["model"]
        json_file_path = options["records"]
        force_update = options["force"]
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        # Get lookup fields from the command argument
        lookup_fields = options["lookup"].split(",")

        # Load model
        try:
            app_label, model_name = model_path.split(".")
            model = apps.get_model(app_label, model_name)
        except Exception:
            raise CommandError("Invalid model format. Use 'app_label.ModelName'.")

        # Load records
        try:
            with open(json_file_path, "r") as f:
                records = json.load(f)
            if not isinstance(records, list):
                raise CommandError("JSON must be a list of objects.")
        except Exception as e:
            raise CommandError(f"Failed to load JSON: {e}")

        self.stdout.write(self.style.NOTICE("\n=============================="))
        self.stdout.write(self.style.NOTICE(f"Model: {model_name}"))
        self.stdout.write(self.style.NOTICE(f"Records: {json_file_path}"))
        self.stdout.write(self.style.NOTICE("==============================\n"))

        # Field analysis
        model_fields = {f.name for f in model._meta.get_fields()}
        fk_fields = {
            f.name: f.remote_field.model
            for f in model._meta.fields
            if isinstance(f, (ForeignKey, OneToOneField))
        }
        m2m_fields = {f.name: f.remote_field.model for f in model._meta.many_to_many}

        inserted = updated = skipped = errors = 0

        for idx, record in enumerate(records, 1):
            original_record = record.copy()
            skip = False

            # Resolve ForeignKeys
            for field_name, related_model in fk_fields.items():
                if field_name in record:
                    fk_value = record[field_name]
                    resolved = False
                    for lookup in lookup_fields:
                        try:
                            record[field_name] = related_model.objects.get(
                                **{lookup: fk_value}
                            )
                            resolved = True
                            break
                        except related_model.DoesNotExist:
                            continue
                        except Exception:
                            continue
                    if not resolved:
                        self.stderr.write(
                            self.style.ERROR(
                                f"Record {idx}: FK '{field_name}' not found for '{fk_value}'"
                            )
                        )
                        skip = True
                        errors += 1
                        break
            if skip:
                continue

            # Resolve ManyToMany
            m2m_data = {}
            for field_name, related_model in m2m_fields.items():
                if field_name in record:
                    values = record.pop(field_name)
                    if not isinstance(values, list):
                        self.stderr.write(
                            self.style.ERROR(
                                f"Record {idx}: M2M '{field_name}' must be a list"
                            )
                        )
                        skip = True
                        errors += 1
                        break
                    related_objs = []
                    for val in values:
                        found = False
                        for lookup in lookup_fields:
                            try:
                                obj = related_model.objects.get(**{lookup: val})
                                related_objs.append(obj)
                                found = True
                                break
                            except related_model.DoesNotExist:
                                continue
                        if not found:
                            self.stderr.write(
                                self.style.WARNING(
                                    f"Record {idx}: M2M '{field_name}' value '{val}' not found"
                                )
                            )
                    m2m_data[field_name] = related_objs
            if skip:
                continue

            # Filter valid fields
            record = {k: v for k, v in record.items() if k in model_fields}
            invalid_fields = set(original_record) - model_fields
            if verbose and invalid_fields:
                self.stdout.write(
                    self.style.WARNING(
                        f"Record {idx}: Ignored fields - {invalid_fields}"
                    )
                )

            # Find existing record by unique fields
            unique_fields = [
                f.name for f in model._meta.fields if f.unique and f.name in record
            ]
            filter_kwargs = {f: record[f] for f in unique_fields}
            try:
                with transaction.atomic():
                    instance = None
                    if filter_kwargs:
                        instance = model.objects.filter(**filter_kwargs).first()

                    # Update
                    if instance:
                        if force_update:
                            for k, v in record.items():
                                setattr(instance, k, v)
                            instance.full_clean()
                            if not dry_run:
                                instance.save()
                            updated += 1
                            msg = f"Updated record {idx}"
                        else:
                            skipped += 1
                            msg = f"Skipped record {idx} (already exists)"
                    # Insert
                    else:
                        instance = model(**record)
                        instance.full_clean()
                        if not dry_run:
                            instance.save()
                        inserted += 1
                        msg = f"Inserted record {idx}"

                    # Handle ManyToMany
                    for field, objs in m2m_data.items():
                        getattr(instance, field).set(objs)

                    self.stdout.write(self.style.SUCCESS(msg))
                    if verbose:
                        self.stdout.write(f"Record {idx}:")
                        self.stdout.write(json.dumps(original_record, indent=2))

            except (IntegrityError, ValidationError) as error:
                self.stderr.write(
                    self.style.ERROR(f"Record {idx}: {type(error).__name__} - {error}")
                )
                errors += 1
            except Exception as error:
                self.stderr.write(
                    self.style.ERROR(f"Record {idx}: {type(error).__name__} - {error}")
                )
                errors += 1

        # Summary
        self.stdout.write(self.style.SUCCESS("\n=============================="))
        self.stdout.write(self.style.SUCCESS(f"Inserted: {inserted}"))
        self.stdout.write(self.style.SUCCESS(f"Updated : {updated}"))
        self.stdout.write(self.style.WARNING(f"Skipped : {skipped}"))
        self.stdout.write(self.style.ERROR(f"Errors  : {errors}"))
        self.stdout.write(self.style.SUCCESS("==============================\n"))
