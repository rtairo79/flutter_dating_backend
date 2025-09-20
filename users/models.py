# models.py - Complete improved version:

from django.contrib.auth.models import User
from django.contrib.gis.db import models as geomodels
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TimestampedModel(models.Model):
    """Abstract base class with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class MusicGenre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class ProfileManager(models.Manager):
    def public_profiles(self):
        return self.filter(visibility='public')
    
    def nearby(self, point, distance_km=10):
        from django.contrib.gis.measure import Distance
        return self.filter(location__distance_lte=(point, Distance(km=distance_km)))

class Profile(TimestampedModel):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    STREAMING_CHOICES = (
        ('spotify', 'Spotify'),
        ('apple_music', 'Apple Music'),
        ('youtube_music', 'YouTube Music'),
        ('other', 'Other'),
    )
    
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('friends', 'Friends'),
        ('interests', 'Interests'),
        ('closed', 'Closed'),
    )
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    location = geomodels.PointField(null=True, blank=True, spatial_index=True)
    gender = models.CharField(
        max_length=10, 
        choices=GENDER_CHOICES, 
        default='other'
    )
    age = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(13), MaxValueValidator(120)]
    )
    bio = models.TextField(null=True, blank=True, max_length=500)
    interests = models.ManyToManyField(Interest, blank=True, related_name='profiles')
    artists = models.ManyToManyField(Artist, blank=True, related_name='profiles')
    genres = models.ManyToManyField(MusicGenre, blank=True, related_name='profiles')
    streaming_service = models.CharField(
        max_length=30, 
        choices=STREAMING_CHOICES, 
        blank=True
    )
    visibility = models.CharField(
        max_length=20, 
        choices=VISIBILITY_CHOICES, 
        default='public',
        db_index=True
    )
    favorite_dishes = models.ManyToManyField(
        'Dish', 
        blank=True, 
        related_name='favorited_by_profiles'
    )
    favorite_drinks = models.ManyToManyField(
        'Drink', 
        blank=True, 
        related_name='favorited_by_profiles'
    )
    preferred_dish_categories = models.ManyToManyField(
        'DishCategory', 
        blank=True,
        related_name='preferred_by_profiles'
    )
    preferred_drink_categories = models.ManyToManyField(
        'DrinkCategory', 
        blank=True,
        related_name='preferred_by_profiles'
    )
    
    objects = ProfileManager()
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    class Meta:
        indexes = [
            models.Index(fields=['visibility']),
            models.Index(fields=['age']),
            models.Index(fields=['streaming_service']),
        ]

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class DishCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Dish categories"
        ordering = ['name']

class DrinkCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Drink categories"
        ordering = ['name']

class Dish(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.ManyToManyField(Ingredient, related_name='dishes')
    category = models.ForeignKey(
        DishCategory, 
        on_delete=models.CASCADE,
        related_name='dishes'
    )
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    class Meta:
        verbose_name_plural = "Dishes"
        unique_together = ['name', 'category']
        ordering = ['name']

class Drink(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        DrinkCategory, 
        on_delete=models.CASCADE,
        related_name='drinks'
    )
    description = models.TextField(blank=True)
    alcohol_content = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    class Meta:
        unique_together = ['name', 'category']
        ordering = ['name']

class Venue(TimestampedModel):
    VENUE_TYPES = [
        ('restaurant', 'Restaurant'),
        ('bar', 'Bar'),
        ('cafe', 'Cafe'),
        ('club', 'Club'),
        ('pub', 'Pub'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255, db_index=True)
    venue_type = models.CharField(
        max_length=20, 
        choices=VENUE_TYPES, 
        default='other'
    )
    location = geomodels.PointField(spatial_index=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    average_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    dishes = models.ManyToManyField(Dish, blank=True, related_name='venues')
    drinks = models.ManyToManyField(Drink, blank=True, related_name='venues')
    music_genres = models.ManyToManyField(
        MusicGenre, 
        blank=True, 
        related_name='venues'
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['venue_type']),
            models.Index(fields=['is_active']),
        ]