"""
Модуль с юнит-тестами для музыкального сервиса с тестированием загрузки данных
"""
import unittest
import os
import json
import tempfile
import shutil

from models import MusicService
from file_operations import FileOperations
from exceptions import *

class TestDataLoading(unittest.TestCase):
    """Тесты загрузки данных из файлов"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.service = MusicService()
        self.test_data_dir = tempfile.mkdtemp()

        # Создаем тестовые JSON и XML файлы
        self.create_test_json()
        self.create_test_xml()

    def tearDown(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.test_data_dir)

    def create_test_json(self):
        """Создание тестового JSON файла"""
        test_data = {
            "users": [
                {
                    "user_id": "test_user_1",
                    "username": "test_user",
                    "email": "test@example.com",
                    "premium": True,
                    "created_at": "2024-01-01T00:00:00"
                }
            ],
            "artists": [
                {
                    "artist_id": "test_artist_1",
                    "name": "Test Artist",
                    "bio": "Test bio"
                }
            ],
            "tracks": [
                {
                    "track_id": "test_track_1",
                    "title": "Test Track",
                    "duration": 180,
                    "artist": "Test Artist",
                    "file_path": "/music/test.mp3"
                }
            ],
            "albums": [
                {
                    "album_id": "test_album_1",
                    "title": "Test Album",
                    "artist": "Test Artist",
                    "release_date": "2024-01-01",
                    "genre": "Test"
                }
            ],
            "playlists": [
                {
                    "playlist_id": "test_playlist_1",
                    "name": "Test Playlist",
                    "description": "Test description",
                    "owner": "test_user",
                    "is_public": True,
                    "created_date": "2024-01-01T00:00:00",
                    "tracks": [
                        {
                            "track_id": "test_track_1",
                            "title": "Test Track",
                            "artist": "Test Artist",
                            "position": 1
                        }
                    ]
                }
            ]
        }

        json_file = os.path.join(self.test_data_dir, "test_data.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)

        self.json_file = json_file

    def create_test_xml(self):
        """Создание тестового XML файла"""
        xml_content = '''<?xml version='1.0' encoding='utf-8'?>
<MusicService>
  <Users>
    <User>
      <user_id>xml_user_1</user_id>
      <username>xml_user</username>
      <email>xml@example.com</email>
      <premium>false</premium>
      <created_at>2024-01-01T00:00:00</created_at>
    </User>
  </Users>
  <Artists>
    <Artist>
      <artist_id>xml_artist_1</artist_id>
      <name>XML Artist</name>
      <bio>XML bio</bio>
    </Artist>
  </Artists>
</MusicService>'''

        xml_file = os.path.join(self.test_data_dir, "test_data.xml")
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        self.xml_file = xml_file

    def test_load_from_json(self):
        """Тест загрузки данных из JSON"""
        loaded, errors = FileOperations.load_initial_data(self.service, self.json_file, None)

        self.assertGreater(loaded, 0)
        self.assertEqual(errors, 0)
        self.assertIn("test_user_1", self.service.users)
        self.assertIn("test_artist_1", self.service.artists)
        self.assertIn("test_track_1", self.service.tracks)
        self.assertIn("test_playlist_1", self.service.playlists)

    def test_load_from_xml(self):
        """Тест загрузки данных из XML"""
        loaded, errors = FileOperations.load_initial_data(self.service, None, self.xml_file)

        self.assertGreater(loaded, 0)
        self.assertEqual(errors, 0)
        self.assertIn("xml_user_1", self.service.users)
        self.assertIn("xml_artist_1", self.service.artists)

    def test_load_from_both(self):
        """Тест загрузки данных из обоих файлов"""
        loaded, errors = FileOperations.load_initial_data(self.service, self.json_file, self.xml_file)

        self.assertGreater(loaded, 0)
        # Должны быть загружены данные из обоих файлов
        self.assertIn("test_user_1", self.service.users)
        self.assertIn("xml_user_1", self.service.users)

    def test_load_nonexistent_file(self):
        """Тест загрузки из несуществующего файла"""
        loaded, errors =