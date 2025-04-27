from django.contrib.auth.models import User
from django.contrib.gis.db import models as geomodels
from django.db import models

class Interest(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class MusicGenre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = geomodels.PointField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    age = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    interests = models.ManyToManyField(Interest, blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    genres = models.ManyToManyField(MusicGenre, blank=True)
    streaming_service = models.CharField(max_length=30, choices=STREAMING_CHOICES, blank=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    favorite_dishes = models.ManyToManyField('Dish', blank=True)
    favorite_drinks = models.ManyToManyField('Drink', blank=True)
    preferred_dish_categories = models.ManyToManyField('DishCategory', blank=True)
    preferred_drink_categories = models.ManyToManyField('DrinkCategory', blank=True)

    def __str__(self):
        return self.user.username

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

class DishCategory(models.Model):
    name = models.CharField(max_length=50)  # Например, итальянская, азиатская, вегетарианская и т.д.

class DrinkCategory(models.Model):
    name = models.CharField(max_length=50)  # Вино, коктейли, пиво и т.д.

class Dish(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.ManyToManyField(Ingredient)
    category = models.ForeignKey(DishCategory, on_delete=models.CASCADE)

class Drink(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(DrinkCategory, on_delete=models.CASCADE)

class Venue(models.Model):
    name = models.CharField(max_length=255)
    location = geomodels.PointField()
    dishes = models.ManyToManyField(Dish, blank=True)
    drinks = models.ManyToManyField(Drink, blank=True)
    music_genres = models.ManyToManyField(MusicGenre, blank=True)