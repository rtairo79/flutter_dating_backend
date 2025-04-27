from django.urls import path
from .views import UserListCreate, NearbyMatchesView, UniversalMusicMatchView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('users/<int:user_id>/matches/', NearbyMatchesView.as_view(), name='nearby-matches'),
    path('users/<int:user_id>/music-matches/', UniversalMusicMatchView.as_view(), name='music-matches'),
]