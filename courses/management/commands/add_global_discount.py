from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from courses.models import GlobalDiscount


class Command(BaseCommand):
    help = 'Add a sample global discount for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days for discount to last (default: 7)'
        )
        parser.add_argument(
            '--percentage',
            type=int,
            default=50,
            help='Discount percentage (default: 50)'
        )

    def handle(self, *args, **options):
        days = options['days']
        percentage = options['percentage']
        
        # Check if there's already an active global discount
        existing_discount = GlobalDiscount.objects.filter(is_active=True).first()
        if existing_discount:
            self.stdout.write(
                self.style.WARNING(
                    f'There is already an active global discount: "{existing_discount.title}" '
                    f'({existing_discount.discount_percentage}% off)'
                )
            )
            return
        
        now = timezone.now()
        end_date = now + timedelta(days=days)
        
        # Create the global discount
        global_discount = GlobalDiscount.objects.create(
            title="Limited Time Offer!",
            description=f"Get {percentage}% off all AI courses",
            discount_percentage=percentage,
            start_date=now,
            end_date=end_date,
            is_active=True,
            show_banner=True,
            banner_color='orange'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created global discount: "{global_discount.title}" '
                f'({percentage}% off) until {end_date.strftime("%Y-%m-%d %H:%M")}'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Global discount is now active and will be displayed on all pages!'
            )
        )
