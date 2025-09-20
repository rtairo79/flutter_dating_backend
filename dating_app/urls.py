from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request):
    return JsonResponse({
        "users": request.build_absolute_uri('users/'),
        "spotify_login": request.build_absolute_uri('spotify/login/'),
        "spotify_callback": request.build_absolute_uri('spotify/callback/'),
        "spotify_sync": request.build_absolute_uri('spotify-sync/'),
    })

urlpatterns = [
    path('', lambda request: JsonResponse({"message": "Welcome to Soulmate Dating App!"})),
    path('admin/', admin.site.urls),

    # ✅ Route to API root
    path('api/', api_root, name='api-root'),

    # ✅ Include all user-related endpoints under /api/
    path('api/', include('users.urls')),

    # Optional: for browsable API login
    path('api-auth/', include('rest_framework.urls')),
]