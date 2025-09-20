from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.db.models import Count, Q

import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Profile, Venue
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    VenueSerializer
)
from .utils import sync_user_music

# API получения и создания пользователей
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# API для поиска ближайших матчей по интересам
class NearbyMatchesView(generics.ListAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        
        # Security check - users can only see their own matches
        if self.request.user.id != user_id:
            return User.objects.none()
            
        try:
            user_profile = Profile.objects.select_related('user').prefetch_related('interests').get(user__id=user_id)
        except Profile.DoesNotExist:
            return User.objects.none()
        
        if user_profile.location is None:
            return User.objects.none()

        interests = user_profile.interests.all()
        user_point = user_profile.location

        nearby_profiles = Profile.objects.filter(
            location__distance_lte=(user_point, D(km=5)),
            interests__in=interests,
            visibility__in=['public', 'interests']
        ).exclude(user=user_profile.user).distinct().select_related(
            'user'
        ).prefetch_related('interests', 'artists', 'genres')

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
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        spotify_token = request.data.get('spotify_token')
        
        if not spotify_token:
            return Response(
                {"error": "Missing Spotify token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = Profile.objects.get(user=user)
            
            # Get Spotify data
            sp = spotipy.Spotify(auth=spotify_token)
            top_artists = sp.current_user_top_artists(limit=10)
            
            # Sync with database
            sync_user_music(profile, 'spotify', top_artists)
            
            return Response({
                'status': 'success',
                'synced_artists': len(top_artists['items'])
            }, status=status.HTTP_200_OK)
            
        except Profile.DoesNotExist:
            return Response(
                {"error": "User profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class UniversalMusicMatchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        
        # Security check
        if self.request.user.id != user_id:
            return User.objects.none()
            
        try:
            user_profile = Profile.objects.get(user__id=user_id)
        except Profile.DoesNotExist:
            return User.objects.none()
            
        if not user_profile.location:
            return User.objects.none()

        user_point = user_profile.location

        matches = Profile.objects.filter(
            location__distance_lte=(user_point, D(km=5))
        ).exclude(user=user_profile.user).annotate(
            shared_artists=Count('artists', filter=Q(artists__in=user_profile.artists.all())),
            shared_genres=Count('genres', filter=Q(genres__in=user_profile.genres.all()))
        ).filter(
            Q(shared_artists__gt=0) | Q(shared_genres__gt=0)
        ).order_by('-shared_artists', '-shared_genres').select_related(
            'user'
        ).prefetch_related('artists', 'genres')

        return User.objects.filter(profile__in=matches)


class UserVenueMatchingView(generics.ListAPIView):
    serializer_class = VenueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        
        # Security check
        if self.request.user.id != user_id:
            return Venue.objects.none()
            
        try:
            user_profile = Profile.objects.get(user__id=user_id)
        except Profile.DoesNotExist:
            return Venue.objects.none()
            
        if not user_profile.location:
            return Venue.objects.none()

        user_point = user_profile.location

        venues = Venue.objects.filter(
            location__distance_lte=(user_point, D(km=10))
        ).prefetch_related(
            'dishes', 'drinks', 'dishes__category', 'drinks__category'
        ).annotate(
            matched_dishes=Count('dishes', filter=Q(dishes__in=user_profile.favorite_dishes.all())),
            matched_drinks=Count('drinks', filter=Q(drinks__in=user_profile.favorite_drinks.all())),
            matched_dish_cats=Count('dishes__category', filter=Q(dishes__category__in=user_profile.preferred_dish_categories.all())),
            matched_drink_cats=Count('drinks__category', filter=Q(drinks__category__in=user_profile.preferred_drink_categories.all()))
        ).filter(
            Q(matched_dishes__gt=0) | Q(matched_drinks__gt=0) | 
            Q(matched_dish_cats__gt=0) | Q(matched_drink_cats__gt=0)
        ).order_by('-matched_dishes', '-matched_drinks', '-matched_dish_cats', '-matched_drink_cats')

        return venues
    
class VenueMenuUpdateView(generics.UpdateAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

# Add Login View for token authentication
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                serializer = UserSerializer(user)
                return Response({
                    'token': token.key,
                    'user': serializer.data
                })
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )