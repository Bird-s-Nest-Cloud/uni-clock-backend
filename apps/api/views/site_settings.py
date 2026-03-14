"""
API Views for Site Settings
"""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import SiteSettings


class SiteSettingsView(APIView):
    """
    GET /api/site-settings/ - Retrieve public site settings for frontend.
    Does NOT expose meta_access_token.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        settings_obj = SiteSettings.load()
        data = {
            'tracking_code': settings_obj.site_tracking_code,
            'meta_pixel_id': settings_obj.meta_pixel_id,
        }
        return Response(data)
