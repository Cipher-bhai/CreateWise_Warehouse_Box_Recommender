from django.core.management.base import BaseCommand

from accounts.models import User
from core.models import Box, Product


class Command(BaseCommand):
    help = 'Seed the database with demo users, products, and boxes.'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(username='admin', email='admin@example.com',
                                           password='ChangeMe123!', role=User.Role.ADMIN)
            self.stdout.write(self.style.SUCCESS('Created superuser "admin" / "ChangeMe123!"'))

        demo_users = [
            ('manager1', User.Role.MANAGER),
            ('staff1', User.Role.STAFF),
        ]
        for username, role in demo_users:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password='ChangeMe123!', role=role)
                self.stdout.write(self.style.SUCCESS(f'Created demo user "{username}" / "ChangeMe123!" ({role})'))

        products = [
            ('Wireless Mouse', 12, 7, 4, 0.3),
            ('Bluetooth Speaker', 18, 18, 15, 1.2),
            ('Paperback Novel', 20, 13, 3, 0.4),
            ('Coffee Mug', 11, 11, 12, 0.5),
            ('Laptop Stand', 30, 22, 6, 1.8),
            ('Desk Lamp', 25, 15, 40, 2.1),
        ]
        for name, length, width, height, weight in products:
            Product.objects.get_or_create(
                name=name,
                defaults={'length': length, 'width': width, 'height': height, 'weight': weight},
            )

        boxes = [
            ('XS Mailer', 15, 10, 5, 2, 6),
            ('Small Box', 25, 20, 15, 5, 12),
            ('Medium Box', 35, 30, 20, 10, 20),
            ('Large Box', 50, 40, 35, 15, 32),
            ('XL Crate', 70, 60, 50, 25, 55),
        ]
        for name, length, width, height, max_weight, cost in boxes:
            Box.objects.get_or_create(
                name=name,
                defaults={'length': length, 'width': width, 'height': height,
                          'max_weight': max_weight, 'cost': cost},
            )

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {Product.objects.count()} products, {Box.objects.count()} boxes.'
        ))
