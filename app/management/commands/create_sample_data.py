#ignore flake8 errors
# flake8: noqa
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models.car import (
    VehicleIndexPage, Vehicle, VehicleCategory, VehicleFeature,
    VehicleGalleryImage
)
from wagtail.models import Site, Page
from wagtail.rich_text import RichText
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample vehicle data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample vehicle data...')

        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # Create VehicleIndexPage if it doesn't exist
        root_page = Page.objects.get(slug='root')
        vehicle_index, created = VehicleIndexPage.objects.get_or_create(
            slug='vehicles',
            defaults={
                'title': 'Vehicle Listings',
                'intro_text': RichText('<p>Browse our extensive collection of quality vehicles.</p>'),
                'items_per_page': 12,
            }
        )
        if created:
            root_page.add_child(instance=vehicle_index)
            vehicle_index.save_revision().publish()

        # Create categories
        categories_data = [
            {'name': 'SUV', 'description': 'Sport Utility Vehicles'},
            {'name': 'Sedan', 'description': '4-door passenger cars'},
            {'name': 'Truck', 'description': 'Pickup trucks'},
            {'name': 'Coupe', 'description': '2-door sports cars'},
            {'name': 'Hatchback', 'description': 'Compact cars with rear hatch'},
            {'name': 'Convertible', 'description': 'Cars with retractable roof'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = VehicleCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)

        # Create features
        features_data = [
            {'name': 'Air Conditioning', 'icon': 'fa fa-snowflake-o'},
            {'name': 'Leather Seats', 'icon': 'fa fa-star'},
            {'name': 'Navigation System', 'icon': 'fa fa-map'},
            {'name': 'Backup Camera', 'icon': 'fa fa-video-camera'},
            {'name': 'Bluetooth', 'icon': 'fa fa-bluetooth'},
            {'name': 'Heated Seats', 'icon': 'fa fa-fire'},
            {'name': 'Sunroof', 'icon': 'fa fa-sun-o'},
            {'name': 'All-Wheel Drive', 'icon': 'fa fa-cog'},
            {'name': 'Keyless Entry', 'icon': 'fa fa-key'},
            {'name': 'Premium Sound', 'icon': 'fa fa-music'},
        ]

        features = []
        for feat_data in features_data:
            feature, created = VehicleFeature.objects.get_or_create(
                name=feat_data['name'],
                defaults={'icon': feat_data['icon']}
            )
            features.append(feature)

        # Sample vehicle data
        vehicles_data = [
            {
                'title': '2022 Toyota Camry LE',
                'year': 2022,
                'make': 'Toyota',
                'model': 'Camry',
                'trim': 'LE',
                'price': Decimal('24500.00'),
                'mileage': 15000,
                'condition': 'used',
                'engine': '2.5L 4-Cylinder',
                'color': 'white',
                'fuel_type': 'petrol',
                'transmission': 'automatic',
                'description': RichText('<p>Well-maintained Toyota Camry with excellent fuel economy and reliability.</p>'),
            },
            {
                'title': '2021 Honda CR-V EX',
                'year': 2021,
                'make': 'Honda',
                'model': 'CR-V',
                'trim': 'EX',
                'price': Decimal('28900.00'),
                'sale_price': Decimal('27500.00'),
                'mileage': 22000,
                'condition': 'used',
                'engine': '1.5L Turbo',
                'color': 'black',
                'fuel_type': 'petrol',
                'transmission': 'automatic',
                'description': RichText('<p>Popular SUV with all-wheel drive and advanced safety features.</p>'),
            },
            {
                'title': '2023 Tesla Model 3',
                'year': 2023,
                'make': 'Tesla',
                'model': 'Model 3',
                'trim': 'Standard Range',
                'price': Decimal('42000.00'),
                'mileage': 5000,
                'condition': 'used',
                'engine': 'Electric Motor',
                'color': 'blue',
                'fuel_type': 'electric',
                'transmission': 'automatic',
                'description': RichText('<p>Electric vehicle with autopilot capabilities and supercharger access.</p>'),
            },
            {
                'title': '2020 Ford F-150 XLT',
                'year': 2020,
                'make': 'Ford',
                'model': 'F-150',
                'trim': 'XLT',
                'price': Decimal('35000.00'),
                'mileage': 35000,
                'condition': 'used',
                'engine': '3.5L V6',
                'color': 'red',
                'fuel_type': 'petrol',
                'transmission': 'automatic',
                'description': RichText('<p>Reliable pickup truck perfect for work and recreation.</p>'),
            },
            {
                'title': '2019 BMW 3 Series 330i',
                'year': 2019,
                'make': 'BMW',
                'model': '3 Series',
                'trim': '330i',
                'price': Decimal('31500.00'),
                'mileage': 28000,
                'condition': 'used',
                'engine': '2.0L Turbo',
                'color': 'black',
                'fuel_type': 'petrol',
                'transmission': 'automatic',
                'description': RichText('<p>Luxury sedan with sport package and premium features.</p>'),
            },
        ]

        # Create vehicles
        for vehicle_data in vehicles_data:
            # Check if vehicle already exists
            if Vehicle.objects.filter(title=vehicle_data['title']).exists():
                continue

            vehicle_data['listed_by'] = admin_user
            vehicle_data['published'] = True
            vehicle_data['featured'] = random.choice([True, False])

            vehicle = Vehicle(**vehicle_data)
            vehicle_index.add_child(instance=vehicle)
            vehicle.save_revision().publish()

            # Add random categories and features
            vehicle.categories.set(random.sample(categories, random.randint(1, 3)))
            vehicle.features.set(random.sample(features, random.randint(3, 7)))

            self.stdout.write(f'Created vehicle: {vehicle.title}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('Admin login: admin / admin123')
