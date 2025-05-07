import json
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import IntegrityError
from django.db.models import ForeignKey


class Command(BaseCommand):
    help = "Create or update model records from a JSON file, supporting FK lookups."

    def add_arguments(self, parser):
        parser.add_argument('--model', required=True, type=str, help="Model in 'app_label.ModelName' format")
        parser.add_argument('--records', required=True, type=str, help="Path to JSON file with a list of records")
        parser.add_argument('--force', action='store_true', help="Update existing records instead of skipping")

    def handle(self, *args, **options):
        model_path = options['model']
        json_file_path = options['records']
        force_update = options['force']

        # Resolve model
        try:
            app_label, model_name = model_path.split('.')
            model = apps.get_model(app_label, model_name)
        except Exception:
            raise CommandError("Invalid model format. Use 'app_label.ModelName'")

        # Load JSON
        try:
            with open(json_file_path, 'r') as file:
                records = json.load(file)
            if not isinstance(records, list):
                raise CommandError("JSON must be a list of objects.")
        except IsADirectoryError:
            raise CommandError(f"Except File path not Directory: {json_file_path}")
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

        inserted_count = updated_count = skipped_count = 0

        for idx, record in enumerate(records, start=1):
            record = record.copy()

            # Handle ForeignKeys dynamically
            for field_name, related_model in fk_fields.items():
                if field_name in record:
                    fk_value = record[field_name]

                    # Try common unique field names
                    for lookup_field in ["username", "email", "slug", "name", "pk", "id"]:
                        try:
                            related_instance = related_model.objects.get(**{lookup_field: fk_value})
                            record[field_name] = related_instance
                            break
                        except related_model.DoesNotExist:
                            continue
                    else:
                        self.stderr.write(self.style.ERROR(
                            f"Record {idx}: ForeignKey lookup failed for '{field_name}'='{fk_value}'"
                        ))
                        continue

            # Filter valid fields
            valid_data = {k: v for k, v in record.items() if k in model_fields}

            # Find unique fields
            unique_fields = [
                f.name for f in model._meta.fields if f.unique and f.name in valid_data
            ]
            if not unique_fields:
                self.stderr.write(self.style.WARNING(
                    f"Record {idx} skipped: No unique field found to check for duplicates."
                ))
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
                        self.stdout.write(self.style.SUCCESS(
                            f"Updated record {idx}: {filter_kwargs}"
                        ))
                    else:
                        skipped_count += 1
                        self.stdout.write(self.style.NOTICE(
                            f"Skipped record {idx} (exists): {filter_kwargs}"
                        ))
                else:
                    instance = model(**valid_data)
                    instance.save()
                    inserted_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Inserted record {idx}"
                    ))

            except IntegrityError as e:
                self.stderr.write(self.style.ERROR(
                    f"Record {idx} failed to save: {e}"
                ))

        # Final summary
        self.stdout.write(self.style.SUCCESS(
            f"\nInserted: {inserted_count} \n Updated: {updated_count} \n Skipped: {skipped_count}\n"
        ))
