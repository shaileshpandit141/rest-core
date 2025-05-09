import json

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.db.models import ForeignKey


class Command(BaseCommand):
    help = "Create or update model records from a JSON file, supporting ForeignKey lookups and safe error handling."

    def add_arguments(self, parser):
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

    def handle(self, *args, **options):
        model_path = options["model"]
        json_file_path = options["records"]
        force_update = options["force"]

        # Resolve model
        try:
            app_label, model_name = model_path.split(".")
            model = apps.get_model(app_label, model_name)
        except Exception:
            raise CommandError("Invalid model format. Use 'app_label.ModelName'")

        # Load JSON
        try:
            with open(json_file_path, "r") as file:
                records = json.load(file)
            if not isinstance(records, list):
                raise CommandError("JSON must be a list of objects.")
        except IsADirectoryError:
            raise CommandError(f"Expected file path, got directory: {json_file_path}")
        except FileNotFoundError:
            raise CommandError(f"File not found: {json_file_path}")
        except json.JSONDecodeError as error:
            raise CommandError(f"Invalid JSON: {error}")

        model_fields = {field.name for field in model._meta.get_fields()}
        fk_fields = {
            field.name: field.remote_field.model
            for field in model._meta.fields
            if isinstance(field, ForeignKey)
        }

        inserted_count = updated_count = skipped_count = error_count = 0

        print()
        for idx, record in enumerate(records, start=1):
            record = record.copy()
            skip_record = False

            # Handle ForeignKeys dynamically
            for field_name, related_model in fk_fields.items():
                if field_name in record:
                    fk_value = record[field_name]
                    resolved = False

                    for lookup_field in [
                        "username",
                        "email",
                        "slug",
                        "name",
                        "pk",
                        "id",
                    ]:
                        try:
                            instance = related_model.objects.get(
                                **{lookup_field: fk_value}
                            )
                            record[field_name] = instance
                            resolved = True
                            break
                        except related_model.DoesNotExist:
                            continue
                        except Exception:
                            continue

                    if not resolved:
                        self.stderr.write(
                            self.style.ERROR(
                                f" Skipped record {idx} (raise error):\n   ForeignKey '{field_name}' with value '{fk_value}' not found."
                            )
                        )
                        skip_record = True
                        break

            if skip_record:
                error_count += 1
                continue

            # Filter valid fields
            valid_data = {k: v for k, v in record.items() if k in model_fields}

            # Find unique fields for duplicate check
            unique_fields = [
                f.name for f in model._meta.fields if f.unique and f.name in valid_data
            ]
            if not unique_fields:
                self.stderr.write(
                    self.style.WARNING(
                        f" Skipped record {idx} (no unique field):\n   No unique field to check for duplicates."
                    )
                )
                skipped_count += 1
                continue

            filter_kwargs = {f: valid_data[f] for f in unique_fields}

            try:
                existing = model.objects.filter(**filter_kwargs).first()
                if existing:
                    if force_update:
                        for k, v in valid_data.items():
                            setattr(existing, k, v)
                        existing.save()
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f" Updated record {idx}"))
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.NOTICE(f" Skipped record {idx} (already exists)")
                        )
                else:
                    model.objects.create(**valid_data)
                    inserted_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Inserted record {idx}"))
            except IntegrityError:
                error_count += 1
                self.stderr.write(
                    self.style.ERROR(
                        f" Skipped record {idx} (failed to save):\n   raise IntegrityError"
                    )
                )
            except Exception:
                error_count += 1
                self.stderr.write(
                    self.style.ERROR(f" Skipped record {idx} (failed to save)")
                )

        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nInserted: {inserted_count}\n Updated: {updated_count}\n Skipped: {skipped_count}\n  Errors: {error_count}\n"
            )
        )
