from django.urls import path
from .views import (
    SpotifySyncView,
    UserListCreate, 
    NearbyMatchesView, 
    UniversalMusicMatchView,
    UserVenueMatchingView,
    VenueMenuUpdateView,
    
    RegisterView, 
    spotify_login,
    spotify_callback,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Authentication (keeping your JWT setup)
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User endpoints
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('users/<int:user_id>/matches/', NearbyMatchesView.as_view(), name='nearby-matches'),
    path('users/<int:user_id>/music-matches/', UniversalMusicMatchView.as_view(), name='music-matches'),
    path('users/<int:user_id>/venue-matches/', UserVenueMatchingView.as_view(), name='venue-matches'),  # Add this
    
    # Spotify OAuth endpoints
    path('spotify/login/', spotify_login, name='spotify-login'),
    path('spotify/callback/', spotify_callback, name='spotify-callback'),
    path('spotify-sync/', SpotifySyncView.as_view(), name='spotify-sync'),
    
    # Venue endpoints
    path('venues/<int:pk>/update-menu/', VenueMenuUpdateView.as_view(), name='venue-update-menu'),  # Add this
]