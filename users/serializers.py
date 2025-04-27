from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Interest, Artist, MusicGenre, Venue
from rest_framework.serializers import ModelSerializer

# --- Interest ---
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'

# --- Artist ---
class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

# --- Music Genre ---
class MusicGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicGenre
        fields = '__all__'

# --- Profile ---
class ProfileSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    artists = ArtistSerializer(many=True, read_only=True)
    genres = MusicGenreSerializer(many=True, read_only=True)
    favorite_dishes = serializers.StringRelatedField(many=True, read_only=True)
    favorite_drinks = serializers.StringRelatedField(many=True, read_only=True)
    preferred_dish_categories = serializers.StringRelatedField(many=True, read_only=True)
    preferred_drink_categories = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = (
            'user', 'location', 'gender', 'age', 'bio', 'visibility',
            'interests', 'artists', 'genres', 'streaming_service',
            'favorite_dishes', 'favorite_drinks',
            'preferred_dish_categories', 'preferred_drink_categories',
        )

# --- User ---
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance

# --- Registration ---
class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# --- Venue Menu ---
class VenueMenuSerializer(serializers.ModelSerializer):
    dishes = serializers.StringRelatedField(many=True)
    drinks = serializers.StringRelatedField(many=True)

    class Meta:
        model = Venue
        fields = ('id', 'name', 'dishes', 'drinks')