# admin.py

from django.contrib import admin
# from django.contrib.gis.admin import OSMGeoAdmin #
from .models import (
    Profile, Interest, Artist, MusicGenre,
    Venue, Dish, Drink, DishCategory, DrinkCategory, Ingredient
)

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(MusicGenre)
class MusicGenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'visibility', 'streaming_service', 'created_at']
    list_filter = ['visibility', 'gender', 'streaming_service', 'created_at']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['interests', 'artists', 'genres', 'favorite_dishes', 'favorite_drinks']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'age', 'gender', 'bio')
        }),
        #('Location', {
         #   'fields': ('location',)
        #}),
        ('Preferences', {
            'fields': ('interests', 'artists', 'genres', 'streaming_service')
        }),
        ('Food & Drinks', {
            'fields': ('favorite_dishes', 'favorite_drinks', 
                      'preferred_dish_categories', 'preferred_drink_categories')
        }),
        ('Settings', {
            'fields': ('visibility',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DishCategory)
class DishCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(DrinkCategory)
class DrinkCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class DishIngredientInline(admin.TabularInline):
    model = Dish.ingredients.through
    extra = 1

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    filter_horizontal = ['ingredients']

@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'alcohol_content']
    list_filter = ['category']
    search_fields = ['name', 'category__name']

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin): # OSMGeoAdmin
    list_display = ['name', 'venue_type', 'is_active', 'created_at']
    list_filter = ['venue_type', 'is_active', 'created_at']
    search_fields = ['name', 'address']
    filter_horizontal = ['dishes', 'drinks', 'music_genres']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'venue_type', 'description', 'average_price')
        }),
        #('Location', {
        #    'fields': ('location', 'address')
        #}),
        ('Menu', {
            'fields': ('dishes', 'drinks')
        }),
        ('Atmosphere', {
            'fields': ('music_genres',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )