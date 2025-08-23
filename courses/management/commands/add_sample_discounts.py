from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from courses.models import Course


class Command(BaseCommand):
    help = 'Add sample discount data to courses for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days for discount to last (default: 7)'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Get the first few published courses
        courses = Course.objects.filter(is_published=True)[:3]
        
        if not courses.exists():
            self.stdout.write(
                self.style.ERROR('No published courses found. Please create some courses first.')
            )
            return
        
        now = timezone.now()
        end_date = now + timedelta(days=days)
        
        for i, course in enumerate(courses):
            if course.price > 0:  # Only add discounts to paid courses
                # Calculate discount price (20% off)
                discount_price = course.price * Decimal('0.8')
                
                course.discount_price = discount_price
                course.discount_start_date = now
                course.discount_end_date = end_date
                course.is_discount_active = True
                course.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Added {20}% discount to "{course.title}" '
                        f'(PKR {course.price} → PKR {discount_price}) '
                        f'until {end_date.strftime("%Y-%m-%d %H:%M")}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added sample discounts to {courses.count()} course(s)'
            )
        )
