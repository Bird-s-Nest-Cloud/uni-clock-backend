"""
API Views for homepage content
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from core.models import Banner, FeaturedSection
from catalog.models import Category, Brand
from api.serializers import (
    BannerSerializer, 
    FeaturedSectionSerializer,
    HomepageCategorySerializer,
    HomepageBrandSerializer
)
from api.utils import success_response


class HomepageView(APIView):
    """
    GET /api/homepage/
    Get homepage data (banners, featured sections, categories, and brands)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get active banners, featured sections, categories, and brands"""
        # Get active banners that are currently active (considering date ranges)
        banners = Banner.objects.filter(is_active=True).select_related('link_product')
        active_banners = [banner for banner in banners if banner.is_currently_active()]
        
        # Get active featured sections
        featured_sections = FeaturedSection.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('products')
        
        # Get active categories (limit to top 10 or all if needed)
        categories = Category.objects.filter(
            is_active=True
        ).prefetch_related('products')[:20]
        
        # Get active brands (limit to featured brands or all)
        brands = Brand.objects.filter(
            is_active=True
        ).prefetch_related('products')[:20]
        
        data = {
            'banners': BannerSerializer(
                active_banners,
                many=True,
                context={'request': request}
            ).data,
            'featured_sections': FeaturedSectionSerializer(
                featured_sections,
                many=True,
                context={'request': request}
            ).data,
            'categories': HomepageCategorySerializer(
                categories,
                many=True,
                context={'request': request}
            ).data,
            'brands': HomepageBrandSerializer(
                brands,
                many=True,
                context={'request': request}
            ).data
        }
        
        return success_response(
            data=data,
            message="Homepage data retrieved successfully"
        )
