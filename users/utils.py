from .models import Artist, MusicGenre

def extract_artists(service, service_data):
    # Реализуй парсинг данных разных сервисов
    if service == 'spotify':
        return [artist['name'] for artist in service_data['items']]
    elif service == 'apple_music':
        return [item['attributes']['artistName'] for item in service_data['data']]
    # добавь другие сервисы...
    return []

def extract_genres(service, service_data):
    # Реализуй парсинг жанров
    genres = set()
    if service == 'spotify':
        for artist in service_data['items']:
            genres.update(artist['genres'])
    elif service == 'apple_music':
        genres.update(item['attributes']['genreNames'][0] for item in service_data['data'])
    # добавь другие сервисы...
    return list(genres)

def sync_user_music(user_profile, service, service_data):
    artists_list = extract_artists(service, service_data)
    genres_list = extract_genres(service, service_data)

    for artist_name in artists_list:
        artist, _ = Artist.objects.get_or_create(name=artist_name)
        user_profile.artists.add(artist)

    for genre_name in genres_list:
        genre, _ = MusicGenre.objects.get_or_create(name=genre_name)
        user_profile.genres.add(genre)

    user_profile.save()