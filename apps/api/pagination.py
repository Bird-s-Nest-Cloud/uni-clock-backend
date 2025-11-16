"""
Custom pagination classes for API responses
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class LaravelStylePagination(PageNumberPagination):
    """
    Laravel-style pagination format matching the API documentation
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return standardized paginated response format with status, status_code, message
        """
        # Build links array
        links = []
        
        # Previous link
        if self.page.has_previous():
            links.append({
                'url': self.get_previous_link(),
                'label': '&laquo; Previous',
                'page': self.page.previous_page_number(),
                'active': False
            })
        else:
            links.append({
                'url': None,
                'label': '&laquo; Previous',
                'page': None,
                'active': False
            })
        
        # Page number links
        for page_num in self.page.paginator.page_range:
            links.append({
                'url': self.get_page_link(page_num) if page_num != self.page.number else self.request.build_absolute_uri(),
                'label': str(page_num),
                'page': page_num,
                'active': page_num == self.page.number
            })
        
        # Next link
        if self.page.has_next():
            links.append({
                'url': self.get_next_link(),
                'label': 'Next &raquo;',
                'page': self.page.next_page_number(),
                'active': False
            })
        else:
            links.append({
                'url': None,
                'label': 'Next &raquo;',
                'page': None,
                'active': False
            })
        
        # Calculate from and to
        from_item = (self.page.number - 1) * self.page_size + 1 if self.page.object_list else 0
        to_item = from_item + len(self.page.object_list) - 1 if self.page.object_list else 0
        
        return Response(OrderedDict([
            ('status', True),
            ('status_code', 200),
            ('message', 'Data retrieved successfully'),
            ('data', OrderedDict([
                ('items', data),
                ('pagination', OrderedDict([
                    ('current_page', self.page.number),
                    ('from', from_item),
                    ('last_page', self.page.paginator.num_pages),
                    ('links', links),
                    ('path', self.request.build_absolute_uri().split('?')[0]),
                    ('per_page', self.page_size),
                    ('to', to_item),
                    ('total', self.page.paginator.count),
                ]))
            ]))
        ]))
    
    def get_page_link(self, page_number):
        """Get full URL for a specific page number"""
        url = self.request.build_absolute_uri()
        if '?' in url:
            # Replace or add page parameter
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            params['page'] = [str(page_number)]
            new_query = urlencode(params, doseq=True)
            return urlunparse(parsed._replace(query=new_query))
        else:
            return f"{url}?page={page_number}"
