# def build_absolute_uri(path):
#     """Turn a relative URL into an absolute URL."""
#     if not path:
#         return ''
#
#     from django.contrib.sites.models import Site
#
#     site = Site.objects.get_current()
#     return '{protocol}://{domain}{path}'.format(
#         protocol=getattr(settings, 'ABSOLUTEURI_PROTOCOL', 'https'),
#         domain=site.domain,
#         path=path
#     )