from django.core.cache import cache
from django.db.models import Prefetch
from apps.core.models import SiteSettings, NavItem, FooterColumn, FooterLink, SocialLink, FooterService

CACHE_KEY = 'public_site_context'


def site_settings_context(request):
    """
    Context processor that provides cached, pre-fetched site settings,
    primary navigation items, footer columns & links, social media links,
    and footer services across all public and admin templates.
    """
    data = cache.get(CACHE_KEY)
    if data is None:
        try:
            site = SiteSettings.get_settings()

            # Pre-fetch root NavItems with pre-fetched visible children
            nav_items = list(
                NavItem.objects.filter(parent__isnull=True, is_visible=True)
                .prefetch_related(
                    Prefetch(
                        'children',
                        queryset=NavItem.objects.filter(is_visible=True).order_by('order', 'id')
                    )
                )
                .order_by('order', 'id')
            )

            # Pre-fetch Footer Columns with visible links
            footer_columns = list(
                FooterColumn.objects.filter(is_visible=True)
                .prefetch_related(
                    Prefetch(
                        'links',
                        queryset=FooterLink.objects.filter(is_visible=True).order_by('order', 'id')
                    )
                )
                .order_by('order', 'id')
            )

            # Enabled Social Links
            social_links = list(
                SocialLink.objects.filter(is_enabled=True).order_by('order', 'id')
            )

            # Visible Footer Services
            footer_services = list(
                FooterService.objects.filter(is_visible=True).order_by('order', 'id')
            )

            data = {
                'site': site,
                'nav_items': nav_items,
                'footer_columns': footer_columns,
                'social_links': social_links,
                'footer_services': footer_services,
            }
            # Cache for 5 minutes (invalidated immediately via post_save/post_delete signals)
            cache.set(CACHE_KEY, data, timeout=300)
        except Exception:
            data = {
                'site': None,
                'nav_items': [],
                'footer_columns': [],
                'social_links': [],
                'footer_services': [],
            }

    return data
