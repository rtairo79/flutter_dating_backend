# tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import Profile, Interest, Artist, MusicGenre, Venue

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_user_registration(self):
        """Test user registration creates user and profile"""
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        user = User.objects.get(username='testuser')
        self.assertTrue(hasattr(user, 'profile'))
    
    def test_user_login(self):
        """Test user login returns token"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=user)
        
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

class ProfileTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            location=Point(-122.4194, 37.7749),  # San Francisco
            age=25,
            gender='male'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_update_profile_location(self):
        """Test updating profile location"""
        response = self.client.patch(f'/api/profiles/{self.profile.id}/', {
            'location_input': [-122.4194, 37.7749]
        })
        
        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.location)

class MatchingTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users with profiles
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'pass')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'pass')
        
        # Create interests
        self.interest1 = Interest.objects.create(name='Music')
        self.interest2 = Interest.objects.create(name='Food')
        
        # Create profiles with locations
        self.profile1 = Profile.objects.create(
            user=self.user1,
            location=Point(-122.4194, 37.7749),  # San Francisco
            visibility='public'
        )
        self.profile1.interests.add(self.interest1, self.interest2)
        
        self.profile2 = Profile.objects.create(
            user=self.user2,
            location=Point(-122.4190, 37.7745),  # Nearby location
            visibility='public'
        )
        self.profile2.interests.add(self.interest1)
        
        # Authenticate as user1
        self.token = Token.objects.create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_nearby_matches(self):
        """Test finding nearby users with shared interests"""
        response = self.client.get(f'/api/users/{self.user1.id}/nearby-matches/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.user2.id)

class VenueTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.venue = Venue.objects.create(
            name='Test Restaurant',
            venue_type='restaurant',
            location=Point(-122.4194, 37.7749),
            address='123 Test St'
        )
    
    def test_venue_list_with_location_filter(self):
        """Test filtering venues by location"""
        response = self.client.get('/api/venues/', {
            'lat': 37.7749,
            'lon': -122.4194,
            'distance': 5
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Restaurant')

class SpotifySyncTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.profile = Profile.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_sync_spotify_data(self):
        """Test syncing Spotify data (mock)"""
        # This would need to be mocked since it requires real Spotify token
        from unittest.mock import patch, MagicMock
        
        mock_spotify_data = {
            'items': [
                {
                    'name': 'The Beatles',
                    'genres': ['rock', 'pop']
                },
                {
                    'name': 'Pink Floyd',
                    'genres': ['rock', 'psychedelic']
                }
            ]
        }
        
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = MagicMock()
            mock_sp_instance.current_user_top_artists.return_value = mock_spotify_data
            mock_spotify.return_value = mock_sp_instance
            
            response = self.client.post('/api/spotify/sync/', {
                'spotify_token': 'mock_token'
            })
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            self.profile.refresh_from_db()
            self.assertEqual(self.profile.artists.count(), 2)
            self.assertTrue(self.profile.artists.filter(name='The Beatles').exists())