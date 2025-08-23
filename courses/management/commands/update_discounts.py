from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import Course


class Command(BaseCommand):
    help = 'Update discount status for courses based on current time'

    def handle(self, *args, **options):
        now = timezone.now()
        updated_count = 0
        
        # Get all courses with discount settings
        courses_with_discounts = Course.objects.filter(
            discount_price__isnull=False,
            discount_end_date__isnull=False
        )
        
        for course in courses_with_discounts:
            old_status = course.is_discount_active
            new_status = course.has_active_discount()
            
            if old_status != new_status:
                course.is_discount_active = new_status
                course.save()
                updated_count += 1
                
                if new_status:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Activated discount for "{course.title}" (ends: {course.discount_end_date})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Deactivated discount for "{course.title}" (expired: {course.discount_end_date})'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} course discount(s)'
            )
        )
