from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from rest_framework import generics
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from .serializers import UserSerializer
from .serializers import RegisterSerializer
from .models import Profile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from .utils import sync_user_music
import spotipy
from django.db.models import Count, Q
from django.contrib.gis.measure import D
from .serializers import VenueMenuSerializer
from .models import Venue

# API получения и создания пользователей
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# API для поиска ближайших матчей по интересам
class NearbyMatchesView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = Profile.objects.get(user__id=user_id)

        if user.location is None:
            return User.objects.none()

        interests = user.interests.all()
        user_point = user.location

        nearby_profiles = Profile.objects.filter(
            location__distance_lte=(user_point, D(km=5)),
            interests__in=interests,
            visibility__in=['public', 'interests']
        ).exclude(user=user.user).distinct()

        return User.objects.filter(profile__in=nearby_profiles)



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

def spotify_login(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-top-read"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
# views.py
def spotify_callback(request):
    code = request.GET.get('code')
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-top-read"
    )
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    sp = spotipy.Spotify(auth=access_token)
    top_artists = sp.current_user_top_artists(limit=10)

    
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        sync_user_music(profile, 'spotify', top_artists)

    artist_names = [artist['name'] for artist in top_artists['items']]
    # store or sync artist_names with your Profile    

    return JsonResponse({'top_artists': artist_names})

class SpotifySyncView(APIView):
    def post(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        
        # Получение токена из запроса
        token = request.data.get('spotify_token')

        sp = spotipy.Spotify(auth=token)
        top_artists = sp.current_user_top_artists(limit=10)

        # Используем функцию из utils.py
        sync_user_music(profile, 'spotify', top_artists)

        return Response({'status': 'success'})
    
class UniversalMusicMatchView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_profile = Profile.objects.get(user__id=self.kwargs['user_id'])
        user_point = user_profile.location

        # Найти пользователей с пересечением исполнителей или жанров
        matches = Profile.objects.filter(
            location__distance_lte=(user_point, D(km=5))
        ).exclude(user=user_profile.user).annotate(
            shared_artists=Count('artists', filter=Q(artists__in=user_profile.artists.all())),
            shared_genres=Count('genres', filter=Q(genres__in=user_profile.genres.all()))
        ).filter(
            Q(shared_artists__gt=0) | Q(shared_genres__gt=0)
        ).order_by('-shared_artists', '-shared_genres')

        return User.objects.filter(profile__in=matches)

class UserVenueMatchingView(generics.ListAPIView):
    serializer_class = VenueMenuSerializer

    def get_queryset(self):
        user_profile = Profile.objects.get(user__id=self.kwargs['user_id'])
        user_point = user_profile.location

        venues = Venue.objects.filter(
            location__distance_lte=(user_point, D(km=10))
        ).annotate(
            matched_dishes=Count('dishes', filter=Q(dishes__in=user_profile.favorite_dishes.all())),
            matched_drinks=Count('drinks', filter=Q(drinks__in=user_profile.favorite_drinks.all())),
            matched_dish_cats=Count('dishes__category', filter=Q(dishes__category__in=user_profile.preferred_dish_categories.all())),
            matched_drink_cats=Count('drinks__category', filter=Q(drinks__category__in=user_profile.preferred_drink_categories.all()))
        ).filter(
            Q(matched_dishes__gt=0) | Q(matched_drinks__gt=0) | Q(matched_dish_cats__gt=0) | Q(matched_drink_cats__gt=0)
        ).order_by('-matched_dishes', '-matched_drinks', '-matched_dish_cats', '-matched_drink_cats')

        return venues    
    
class VenueMenuUpdateView(generics.UpdateAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueMenuSerializer