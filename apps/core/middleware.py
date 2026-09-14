from django.middleware.csrf import get_token

class SecurityAndPermissionsMiddleware:
    """
    Middleware that ensures:
    1. CSRF Cookie is guaranteed to be set on every HTTP response.
    2. HTML5 Permissions-Policy header enables camera, geolocation, microphone,
       photos/media storage, and clipboard permissions across frames and top windows.
    3. Security headers (X-Content-Type-Options, Referrer-Policy) are applied.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force evaluation of the CSRF token for the request.
        # This causes CsrfViewMiddleware to send the 'csrftoken' cookie in the response.
        get_token(request)

        response = self.get_response(request)

        # Standard modern Permissions-Policy header
        # Enables camera, geolocation, microphone, and clipboard for both direct origin and iframes
        response['Permissions-Policy'] = (
            'camera=*, '
            'geolocation=*, '
            'microphone=*, '
            'display-capture=*, '
            'clipboard-read=*, '
            'clipboard-write=*'
        )

        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response
