from django.core.management.base import BaseCommand
from courses.models import SiteSettings

class Command(BaseCommand):
    help = 'Initialize default site settings'

    def handle(self, *args, **options):
        # Check if settings already exist
        if SiteSettings.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    'Site settings already exist. Use the admin panel to modify them.'
                )
            )
            return

        # Create default site settings
        settings = SiteSettings.objects.create(
            site_name="AI Course Platform",
            site_tagline="Learn AI & Machine Learning",
            footer_text="© 2024 AI Course Platform. All rights reserved.",
            contact_email="contact@aicourseplatform.com",
            contact_phone="+1 (555) 123-4567",
            meta_description="Learn AI and Machine Learning with our comprehensive online courses. Expert-led tutorials, hands-on projects, and flexible learning paths.",
            meta_keywords="AI, Machine Learning, Python, Data Science, Online Courses",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created default site settings: "{settings.site_name}"'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                'You can now customize these settings from the Django admin panel.'
            )
        )
