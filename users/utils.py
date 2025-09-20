# utils.py - Complete fixed version:

from .models import Artist, MusicGenre
import logging

logger = logging.getLogger(__name__)

def extract_artists(service, service_data):
    """Extract artist names from different music service APIs"""
    try:
        if service == 'spotify':
            return [artist['name'] for artist in service_data.get('items', [])]
        elif service == 'apple_music':
            return [item['attributes']['artistName'] 
                   for item in service_data.get('data', [])]
        elif service == 'youtube_music':
            # Add YouTube Music parsing when needed
            return []
    except (KeyError, TypeError) as e:
        logger.error(f"Error extracting artists from {service}: {e}")
    return []

def extract_genres(service, service_data):
    """Extract genre names from different music service APIs"""
    genres = set()
    try:
        if service == 'spotify':
            for artist in service_data.get('items', []):
                if 'genres' in artist:
                    genres.update(artist['genres'])
        elif service == 'apple_music':
            for item in service_data.get('data', []):
                if 'attributes' in item and 'genreNames' in item['attributes']:
                    genres.add(item['attributes']['genreNames'][0])
        elif service == 'youtube_music':
            # Add YouTube Music parsing when needed
            pass
    except (KeyError, TypeError, IndexError) as e:
        logger.error(f"Error extracting genres from {service}: {e}")
    return list(genres)

def sync_user_music(user_profile, service, service_data):
    """Sync user's music preferences from streaming service"""
    try:
        artists_list = extract_artists(service, service_data)
        genres_list = extract_genres(service, service_data)
        
        # Clear existing artists and genres if doing full sync
        # Optional: comment out if you want to accumulate instead
        # user_profile.artists.clear()
        # user_profile.genres.clear()
        
        # Add artists
        for artist_name in artists_list:
            if artist_name:  # Skip empty strings
                artist, created = Artist.objects.get_or_create(name=artist_name)
                user_profile.artists.add(artist)
                if created:
                    logger.info(f"Created new artist: {artist_name}")
        
        # Add genres
        for genre_name in genres_list:
            if genre_name:  # Skip empty strings
                genre, created = MusicGenre.objects.get_or_create(name=genre_name)
                user_profile.genres.add(genre)
                if created:
                    logger.info(f"Created new genre: {genre_name}")
        
        # Update streaming service
        user_profile.streaming_service = service
        user_profile.save()
        
        logger.info(f"Synced {len(artists_list)} artists and {len(genres_list)} genres for user {user_profile.user.username}")
        
        return {
            'artists_synced': len(artists_list),
            'genres_synced': len(genres_list)
        }
        
    except Exception as e:
        logger.error(f"Error syncing music for user {user_profile.user.username}: {e}")
        raise