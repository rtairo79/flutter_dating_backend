# serializers.py - Complete improved version:

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from .models import (
    Profile, Interest, Artist, MusicGenre, 
    Venue, Dish, Drink, DishCategory, DrinkCategory
)

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name']

class MusicGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicGenre
        fields = ['id', 'name']

class DishCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DishCategory
        fields = ['id', 'name']

class DrinkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DrinkCategory
        fields = ['id', 'name']

class DishSerializer(serializers.ModelSerializer):
    category = DishCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=DishCategory.objects.all(),
        source='category',
        write_only=True
    )
    
    class Meta:
        model = Dish
        fields = ['id', 'name', 'category', 'category_id']

class DrinkSerializer(serializers.ModelSerializer):
    category = DrinkCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=DrinkCategory.objects.all(),
        source='category',
        write_only=True
    )
    
    class Meta:
        model = Drink
        fields = ['id', 'name', 'category', 'category_id']

class ProfileSerializer(serializers.ModelSerializer):
    # Read-only fields for detailed information
    interests_detail = InterestSerializer(source='interests', many=True, read_only=True)
    artists_detail = ArtistSerializer(source='artists', many=True, read_only=True)
    genres_detail = MusicGenreSerializer(source='genres', many=True, read_only=True)
    favorite_dishes_detail = DishSerializer(source='favorite_dishes', many=True, read_only=True)
    favorite_drinks_detail = DrinkSerializer(source='favorite_drinks', many=True, read_only=True)
    
    # Write-only fields for updating relationships
    interest_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Interest.objects.all(),
        source='interests',
        write_only=True,
        required=False
    )
    artist_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Artist.objects.all(),
        source='artists',
        write_only=True,
        required=False
    )
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=MusicGenre.objects.all(),
        source='genres',
        write_only=True,
        required=False
    )
    
    # Location handling
    location = serializers.SerializerMethodField()
    location_input = serializers.ListField(
        child=serializers.FloatField(),
        write_only=True,
        required=False,
        help_text="Format: [longitude, latitude]"
    )
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'location', 'location_input', 'gender', 'age', 
            'bio', 'visibility', 'streaming_service',
            # Read fields
            'interests_detail', 'artists_detail', 'genres_detail',
            'favorite_dishes_detail', 'favorite_drinks_detail',
            # Write fields
            'interest_ids', 'artist_ids', 'genre_ids'
        ]
        read_only_fields = ['user']
    
    def get_location(self, obj):
        if obj.location:
            return {
                'longitude': obj.location.x,
                'latitude': obj.location.y
            }
        return None
    
    def create(self, validated_data):
        location_data = validated_data.pop('location_input', None)
        if location_data and len(location_data) == 2:
            validated_data['location'] = Point(location_data[0], location_data[1])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        location_data = validated_data.pop('location_input', None)
        if location_data and len(location_data) == 2:
            validated_data['location'] = Point(location_data[0], location_data[1])
        return super().update(instance, validated_data)

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'first_name', 'last_name']
        read_only_fields = ['id']

class VenueSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)
    drinks = DrinkSerializer(many=True, read_only=True)
    music_genres = MusicGenreSerializer(many=True, read_only=True)
    location = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'location', 'distance',
            'dishes', 'drinks', 'music_genres'
        ]
    
    def get_location(self, obj):
        if obj.location:
            return {
                'longitude': obj.location.x,
                'latitude': obj.location.y
            }
        return None
    
    def get_distance(self, obj):
        # This will be populated if you use .distance() in your queryset
        if hasattr(obj, 'distance'):
            return obj.distance.km if obj.distance else None
        return None
class RegisterSerializer(ModelSerializer):
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Automatically create profile for new user
        Profile.objects.create(user=user)
        return user    