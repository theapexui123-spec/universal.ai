from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import GlobalDiscount


class Command(BaseCommand):
    help = 'Update global discount status based on current time'

    def handle(self, *args, **options):
        now = timezone.now()
        updated_count = 0
        
        # Get all global discounts
        global_discounts = GlobalDiscount.objects.all()
        
        for discount in global_discounts:
            old_status = discount.is_active
            new_status = discount.is_currently_active()
            
            if old_status != new_status:
                discount.is_active = new_status
                discount.save()
                updated_count += 1
                
                if new_status:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Activated global discount: "{discount.title}" ({discount.discount_percentage}% off)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Deactivated global discount: "{discount.title}" (expired: {discount.end_date})'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} global discount(s)'
            )
        )
