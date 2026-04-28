import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from finance.models import *
from django.db import connection


class Command(BaseCommand):
    help = 'Seed sample data from Jan 2025 to Dec 2026 for Revenue/Expense trends'

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed data...')

        # Get existing users
        users = list(Users.objects.all()[:10])
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        # Get existing departments
        depts = list(Departments.objects.all()[:5])
        if not depts:
            depts = [None]

        # Statuses
        statuses = ['pending', 'approved', 'rejected', 'po_created', 'approved_ceo']

        # Generate data from Jan 2025 to Dec 2026
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2026, 12, 31)

        current_date = start_date
        pr_count = PurchaseRequests.objects.count()
        po_count = PurchaseOrders.objects.count()

        self.stdout.write('Generating Purchase Requests and Orders...')

        while current_date <= end_date:
            # Generate 5-20 PRs per month
            for _ in range(random.randint(5, 20)):
                try:
                    user = random.choice(users)
                    dept = random.choice(depts)

                    pr = PurchaseRequests.objects.create(
                        user=user,
                        item_name=f'Item {pr_count + 1}',
                        description=f'Description for item {pr_count + 1}',
                        qty=random.randint(1, 100),
                        estimated_price=random.uniform(100000, 5000000),
                        status=random.choice(statuses),
                        created_at=current_date.replace(day=random.randint(1, 28)),
                        updated_at=current_date.replace(day=random.randint(1, 28)),
                        department=dept
                    )
                    pr_count += 1

                    # Create PO for some PRs
                    if random.choice([True, False]) and pr.status in ['approved', 'approved_ceo']:
                        try:
                            PurchaseOrders.objects.create(
                                request=pr,
                                po_number=f'PO-{po_count + 1:05d}',
                                total_price=pr.estimated_price * random.uniform(0.9, 1.1),
                                status='issued',
                                created_at=pr.created_at + timedelta(days=random.randint(1, 7)),
                                created_by=user
                            )
                            po_count += 1
                        except:
                            pass

                except Exception as e:
                    pass

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        self.stdout.write(self.style.SUCCESS('Successfully seeded data from Jan 2025 to Dec 2026!'))
        self.stdout.write(f'Total PRs: {PurchaseRequests.objects.count()}')
        self.stdout.write(f'Total POs: {PurchaseOrders.objects.count()}')
