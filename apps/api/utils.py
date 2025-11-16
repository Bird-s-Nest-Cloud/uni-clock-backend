"""
Utility functions for API responses
"""
from rest_framework.response import Response
from rest_framework import status as http_status


def api_response(data=None, message="Success", status=True, status_code=200):
    """
    Generate a standardized API response
    
    Args:
        data: The response data (dict, list, or any serializable data)
        message: A descriptive message about the response
        status: Boolean indicating success (True) or failure (False)
        status_code: HTTP status code
    
    Returns:
        Response object with standardized format
    """
    response_data = {
        "status": status,
        "status_code": status_code,
        "message": message,
        "data": data if data is not None else {}
    }
    return Response(response_data, status=status_code)


def success_response(data=None, message="Success", status_code=200):
    """Generate a success response"""
    return api_response(
        data=data,
        message=message,
        status=True,
        status_code=status_code
    )


def error_response(message="Error", errors=None, status_code=400):
    """
    Generate an error response with proper error formatting
    
    Args:
        message: A descriptive error message
        errors: Can be a dict (serializer.errors), list, or string
        status_code: HTTP status code
    """
    # Format errors properly
    if errors:
        if isinstance(errors, dict):
            # Format serializer errors nicely
            formatted_errors = {}
            for field, field_errors in errors.items():
                if isinstance(field_errors, list):
                    formatted_errors[field] = [str(e) for e in field_errors]
                else:
                    formatted_errors[field] = str(field_errors)
            data = {"errors": formatted_errors}
        elif isinstance(errors, list):
            data = {"errors": [str(e) for e in errors]}
        else:
            data = {"errors": str(errors)}
    else:
        data = {}
    
    return api_response(
        data=data,
        message=message,
        status=False,
        status_code=status_code
    )


def created_response(data=None, message="Created successfully"):
    """Generate a created (201) response"""
    return success_response(
        data=data,
        message=message,
        status_code=http_status.HTTP_201_CREATED
    )


def not_found_response(message="Not found"):
    """Generate a not found (404) response"""
    return error_response(
        message=message,
        status_code=http_status.HTTP_404_NOT_FOUND
    )


def bad_request_response(message="Bad request", errors=None):
    """Generate a bad request (400) response"""
    return error_response(
        message=message,
        errors=errors,
        status_code=http_status.HTTP_400_BAD_REQUEST
    )


class StandardResponseMixin:
    """
    Mixin to wrap DRF generic views responses in standardized format
    """
    
    def list(self, request, *args, **kwargs):
        """Override list to return standardized response"""
        response = super().list(request, *args, **kwargs)
        return Response({
            "status": True,
            "status_code": response.status_code,
            "message": f"{self.get_serializer_class().Meta.model.__name__}s retrieved successfully",
            "data": response.data
        }, status=response.status_code)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return standardized response"""
        try:
            response = super().retrieve(request, *args, **kwargs)
            return Response({
                "status": True,
                "status_code": response.status_code,
                "message": f"{self.get_serializer_class().Meta.model.__name__} retrieved successfully",
                "data": response.data
            }, status=response.status_code)
        except Exception as e:
            return not_found_response(message=str(e))

