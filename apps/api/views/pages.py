from rest_framework import generics
from core.models import Page
from ..serializers.core import PageSerializer

class PageDetailView(generics.RetrieveAPIView):
    queryset = Page.objects.filter(is_active=True)
    serializer_class = PageSerializer
    lookup_field = 'slug'

class PageListView(generics.ListAPIView):
    queryset = Page.objects.filter(is_active=True)
    serializer_class = PageSerializer
