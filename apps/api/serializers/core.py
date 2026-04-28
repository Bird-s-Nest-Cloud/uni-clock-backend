from rest_framework import serializers
from core.models import Page

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'content', 'meta_title', 'meta_description', 'updated_at']
