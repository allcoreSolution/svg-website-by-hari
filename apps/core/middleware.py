from django.http import HttpResponse
from django.conf import settings


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin") or request.META.get("HTTP_ORIGIN")
        allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        is_allowed = bool(origin and origin in allowed_origins)

        if request.method == "OPTIONS":
            response = HttpResponse()
            if is_allowed:
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
                response["Access-Control-Allow-Credentials"] = "true"
                response["Vary"] = "Origin"
            elif origin:
                response["Vary"] = "Origin"
            return response

        response = self.get_response(request)
        if is_allowed:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
            response["Access-Control-Allow-Credentials"] = "true"
            response["Vary"] = "Origin"
        elif origin:
            response["Vary"] = "Origin"

        return response
