from .models import GlobalDiscount, SiteSettings, Banner
from django.db.models import Q
from django.utils import timezone

def global_discount(request):
    """Add global discount information to all templates"""
    try:
        global_discount = GlobalDiscount.objects.filter(
            is_active=True,
            show_banner=True
        ).first()
        
        if global_discount and global_discount.is_currently_active():
            return {
                'global_discount': global_discount,
                'global_discount_active': True,
            }
    except:
        pass
    
    return {
        'global_discount': None,
        'global_discount_active': False,
    }

def site_settings(request):
    """Add site settings to all templates"""
    try:
        settings = SiteSettings.get_settings()
        return {
            'site_settings': settings,
        }
    except:
        # Fallback to default values if settings don't exist
        return {
            'site_settings': {
                'site_name': 'AI Course Platform',
                'site_tagline': 'Learn AI & Machine Learning',
                'footer_text': '© 2024 AI Course Platform. All rights reserved.',
                'contact_email': 'contact@aicourseplatform.com',
                'contact_phone': '+1 (555) 123-4567',
            }
        }


