from .models import GlobalDiscount, SiteSettings, Banner
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache

def global_discount(request):
    """Add global discount information to all templates"""
    cache_key = 'global_discount_context'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return cached_data
    
    try:
        global_discount = GlobalDiscount.objects.filter(
            is_active=True,
            show_banner=True
        ).first()
        
        if global_discount and global_discount.is_currently_active():
            result = {
                'global_discount': global_discount,
                'global_discount_active': True,
            }
        else:
            result = {
                'global_discount': None,
                'global_discount_active': False,
            }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        return result
    except:
        result = {
            'global_discount': None,
            'global_discount_active': False,
        }
        cache.set(cache_key, result, 300)
        return result

def site_settings(request):
    """Add site settings to all templates"""
    cache_key = 'site_settings_context'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return cached_data
    
    try:
        settings = SiteSettings.get_settings()
        result = {
            'site_settings': settings,
        }
    except:
        # Fallback to default values if settings don't exist
        result = {
            'site_settings': {
                'site_name': 'AI Course Platform',
                'site_tagline': 'Learn AI & Machine Learning',
                'footer_text': '© 2024 AI Course Platform. All rights reserved.',
                'contact_email': 'contact@aicourseplatform.com',
                'contact_phone': '+1 (555) 123-4567',
            }
        }
    
    # Cache for 10 minutes
    cache.set(cache_key, result, 600)
    return result


