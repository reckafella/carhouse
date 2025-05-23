import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create a superuser"

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "ethan")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "@100/Chem")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "ethan@gmail.com")
        first_name = os.getenv("DJANGO_SUPERUSER_FIRST_NAME", "Ethan")
        last_name = os.getenv("DJANGO_SUPERUSER_LAST_NAME", "Wanyoike")

        if not username or not email or not password:
            part_1 = "Please provide a username, password, and email."
            part_2 = "Required for account creation."
            raise ValueError(f"{part_1} {part_2}")

        # Create the superuser if it doesn't already exist
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser `{username}` created successfully."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Superuser `{username}` already exists.")
            )
            self.stdout.write(
                self.style.WARNING(f"Updating details for `{username}`.")
            )

            # Update the superuser's details
            User.objects.filter(username=username).update(
                email=email, first_name=first_name, last_name=last_name
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser `{username}` details: updated successfully."
                )
            )
