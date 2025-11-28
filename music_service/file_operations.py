"""
Модуль для работы с файлами и сериализацией данных
"""
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Tuple
import os

from models import MusicService, User, Artist, Track, Album, Playlist, PlaylistTrack
from exceptions import InvalidFileFormatError


class FileOperations:
    """Класс для операций с файлами"""

    @staticmethod
    def load_initial_data(service: MusicService, json_file: str = None, xml_file: str = None) -> Tuple[int, int]:
        """
        Загрузка начальных данных из JSON и XML файлов
        Возвращает кортеж (количество_загруженных_объектов, общее_количество_ошибок)
        """
        total_loaded = 0
        total_errors = 0

        if json_file and os.path.exists(json_file):
            loaded, errors = FileOperations._load_from_json(service, json_file)
            total_loaded += loaded
            total_errors += errors

        if xml_file and os.path.exists(xml_file):
            loaded, errors = FileOperations._load_from_xml(service, xml_file)
            total_loaded += loaded
            total_errors += errors

        return total_loaded, total_errors

    @staticmethod
    def _load_from_json(service: MusicService, filename: str) -> Tuple[int, int]:
        """Загрузка данных из JSON файла"""
        loaded_count = 0
        error_count = 0

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"\nЗагрузка данных из JSON: {filename}")

            # Загрузка пользователей
            for user_data in data.get('users', []):
                try:
                    user = User(
                        user_data['user_id'],
                        user_data['username'],
                        user_data['email'],
                        "default_password",  # Пароль не хранится в открытом виде
                        user_data.get('premium', False)
                    )
                    service.users[user.user_id] = user
                    loaded_count += 1
                except Exception as e:
                    print(f"Ошибка загрузки пользователя {user_data.get('username', 'Unknown')}: {e}")
                    error_count += 1

            # Загрузка артистов
            for artist_data in data.get('artists', []):
                try:
                    artist = Artist(
                        artist_data['artist_id'],
                        artist_data['name'],
                        artist_data.get('bio', '')
                    )
                    service.artists[artist.artist_id] = artist
                    loaded_count += 1
                except Exception as e:
                    print(f"Ошибка загрузки артиста {artist_data.get('name', 'Unknown')}: {e}")
                    error_count += 1

            # Загрузка треков (после артистов)
            for track_data in data.get('tracks', []):
                try:
                    artist_name = track_data['artist']
                    artist = next((a for a in service.artists.values() if a.name == artist_name), None)

                    if artist:
                        track = Track(
                            track_data['track_id'],
                            track_data['title'],
                            track_data['duration'],
                            track_data.get('file_path', ''),
                            artist
                        )
                        service.tracks[track.track_id] = track
                        loaded_count += 1
                    else:
                        print(f"Артист '{artist_name}' не найден для трека '{track_data['title']}'")
                        error_count += 1
                except Exception as e:
                    print(f"Ошибка загрузки трека {track_data.get('title', 'Unknown')}: {e}")
                    error_count += 1

            # Загрузка альбомов
            for album_data in data.get('albums', []):
                try:
                    artist_name = album_data['artist']
                    artist = next((a for a in service.artists.values() if a.name == artist_name), None)

                    if artist:
                        album = Album(
                            album_data['album_id'],
                            album_data['title'],
                            artist,
                            album_data['release_date'],
                            album_data.get('genre', '')
                        )
                        service.albums[album.album_id] = album
                        loaded_count += 1
                    else:
                        print(f"Артист '{artist_name}' не найден для альбома '{album_data['title']}'")
                        error_count += 1
                except Exception as e:
                    print(f"Ошибка загрузки альбома {album_data.get('title', 'Unknown')}: {e}")
                    error_count += 1

            # Загрузка плейлистов (после пользователей и треков)
            for playlist_data in data.get('playlists', []):
                try:
                    owner_name = playlist_data['owner']
                    owner = next((u for u in service.users.values() if u.username == owner_name), None)

                    if owner:
                        playlist = Playlist(
                            playlist_data['playlist_id'],
                            playlist_data['name'],
                            playlist_data.get('description', ''),
                            owner,
                            playlist_data.get('is_public', True)
                        )

                        # Добавление треков в плейлист
                        for track_info in playlist_data.get('tracks', []):
                            track = service.tracks.get(track_info['track_id'])
                            if track:
                                playlist.add_track(track)

                        service.playlists[playlist.playlist_id] = playlist
                        loaded_count += 1
                    else:
                        print(f"Владелец '{owner_name}' не найден для плейлиста '{playlist_data['name']}'")
                        error_count += 1
                except Exception as e:
                    print(f"Ошибка загрузки плейлиста {playlist_data.get('name', 'Unknown')}: {e}")
                    error_count += 1

            print(f"Успешно загружено: {loaded_count} объектов")
            if error_count > 0:
                print(f"Ошибок при загрузке: {error_count}")

        except json.JSONDecodeError as e:
            raise InvalidFileFormatError(f"Ошибка декодирования JSON: {str(e)}")
        except Exception as e:
            raise InvalidFileFormatError(f"Ошибка при загрузке из JSON: {str(e)}")

        return loaded_count, error_count

    @staticmethod
    def _load_from_xml(service: MusicService, filename: str) -> Tuple[int, int]:
        """Загрузка данных из XML файла"""
        loaded_count = 0
        error_count = 0

        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            print(f"\nЗагрузка данных из XML: {filename}")

            # Загрузка пользователей из XML
            users_elem = root.find('Users')
            if users_elem is not None:
                for user_elem in users_elem.findall('User'):
                    try:
                        user_id = user_elem.find('user_id').text
                        username = user_elem.find('username').text
                        email = user_elem.find('email').text
                        premium = user_elem.find('premium').text.lower() == 'true'

                        # Проверяем, не существует ли уже пользователь
                        if user_id not in service.users:
                            user = User(user_id, username, email, "default_password", premium)
                            service.users[user_id] = user
                            loaded_count += 1
                    except Exception as e:
                        print(f"Ошибка загрузки пользователя из XML: {e}")
                        error_count += 1

            # Загрузка артистов из XML
            artists_elem = root.find('Artists')
            if artists_elem is not None:
                for artist_elem in artists_elem.findall('Artist'):
                    try:
                        artist_id = artist_elem.find('artist_id').text
                        name = artist_elem.find('name').text
                        bio_elem = artist_elem.find('bio')
                        bio = bio_elem.text if bio_elem is not None else ""

                        if artist_id not in service.artists:
                            artist = Artist(artist_id, name, bio)
                            service.artists[artist_id] = artist
                            loaded_count += 1
                    except Exception as e:
                        print(f"Ошибка загрузки артиста из XML: {e}")
                        error_count += 1

            # Загрузка треков из XML
            tracks_elem = root.find('Tracks')
            if tracks_elem is not None:
                for track_elem in tracks_elem.findall('Track'):
                    try:
                        track_id = track_elem.find('track_id').text
                        title = track_elem.find('title').text
                        duration = int(track_elem.find('duration').text)
                        artist_name = track_elem.find('artist').text
                        file_path_elem = track_elem.find('file_path')
                        file_path = file_path_elem.text if file_path_elem is not None else ""

                        artist = next((a for a in service.artists.values() if a.name == artist_name), None)

                        if artist and track_id not in service.tracks:
                            track = Track(track_id, title, duration, file_path, artist)
                            service.tracks[track_id] = track
                            loaded_count += 1
                        elif not artist:
                            print(f"Артист '{artist_name}' не найден для трека '{title}'")
                            error_count += 1
                    except Exception as e:
                        print(f"Ошибка загрузки трека из XML: {e}")
                        error_count += 1

            # Загрузка альбомов из XML
            albums_elem = root.find('Albums')
            if albums_elem is not None:
                for album_elem in albums_elem.findall('Album'):
                    try:
                        album_id = album_elem.find('album_id').text
                        title = album_elem.find('title').text
                        artist_name = album_elem.find('artist').text
                        release_date = album_elem.find('release_date').text
                        genre_elem = album_elem.find('genre')
                        genre = genre_elem.text if genre_elem is not None else ""

                        artist = next((a for a in service.artists.values() if a.name == artist_name), None)

                        if artist and album_id not in service.albums:
                            album = Album(album_id, title, artist, release_date, genre)
                            service.albums[album_id] = album
                            loaded_count += 1
                        elif not artist:
                            print(f"Артист '{artist_name}' не найден для альбома '{title}'")
                            error_count += 1
                    except Exception as e:
                        print(f"Ошибка загрузки альбома из XML: {e}")
                        error_count += 1

            print(f"Успешно загружено из XML: {loaded_count} объектов")
            if error_count > 0:
                print(f"Ошибок при загрузке из XML: {error_count}")

        except ET.ParseError as e:
            raise InvalidFileFormatError(f"Ошибка парсинга XML: {str(e)}")
        except Exception as e:
            raise InvalidFileFormatError(f"Ошибка при загрузке из XML: {str(e)}")

        return loaded_count, error_count

    @staticmethod
    def export_to_json(service: MusicService, filename: str):
        """Экспорт данных в JSON"""
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

            data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'users': [user.to_dict() for user in service.users.values()],
                'artists': [artist.to_dict() for artist in service.artists.values()],
                'tracks': [track.to_dict() for track in service.tracks.values()],
                'albums': [album.to_dict() for album in service.albums.values()],
                'playlists': [playlist.to_dict() for playlist in service.playlists.values()],
                'statistics': service.get_statistics()
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Данные экспортированы в {filename}")
        except Exception as e:
            raise InvalidFileFormatError(f"Ошибка при экспорте в JSON: {str(e)}")

    @staticmethod
    def export_to_xml(service: MusicService, filename: str):
        """Экспорт данных в XML"""
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

            root = ET.Element('MusicService')

            # Метаданные
            metadata = ET.SubElement(root, 'Metadata')
            ET.SubElement(metadata, 'ExportDate').text = datetime.now().isoformat()
            ET.SubElement(metadata, 'Version').text = '1.0'

            # Статистика
            stats = service.get_statistics()
            statistics_elem = ET.SubElement(root, 'Statistics')
            for key, value in stats.items():
                ET.SubElement(statistics_elem, key).text = str(value)

            # Пользователи
            users_elem = ET.SubElement(root, 'Users')
            for user in service.users.values():
                user_elem = ET.SubElement(users_elem, 'User')
                for key, value in user.to_dict().items():
                    ET.SubElement(user_elem, key).text = str(value)

            # Артисты
            artists_elem = ET.SubElement(root, 'Artists')
            for artist in service.artists.values():
                artist_elem = ET.SubElement(artists_elem, 'Artist')
                for key, value in artist.to_dict().items():
                    ET.SubElement(artist_elem, key).text = str(value)

            # Треки
            tracks_elem = ET.SubElement(root, 'Tracks')
            for track in service.tracks.values():
                track_elem = ET.SubElement(tracks_elem, 'Track')
                for key, value in track.to_dict().items():
                    ET.SubElement(track_elem, key).text = str(value)

            # Альбомы
            albums_elem = ET.SubElement(root, 'Albums')
            for album in service.albums.values():
                album_elem = ET.SubElement(albums_elem, 'Album')
                for key, value in album.to_dict().items():
                    ET.SubElement(album_elem, key).text = str(value)

            # Плейлисты
            playlists_elem = ET.SubElement(root, 'Playlists')
            for playlist in service.playlists.values():
                playlist_elem = ET.SubElement(playlists_elem, 'Playlist')
                for key, value in playlist.to_dict().items():
                    if key == 'tracks':
                        tracks_elem = ET.SubElement(playlist_elem, 'Tracks')
                        for track_info in value:
                            track_elem = ET.SubElement(tracks_elem, 'TrackInfo')
                            for track_key, track_value in track_info.items():
                                ET.SubElement(track_elem, track_key).text = str(track_value)
                    else:
                        ET.SubElement(playlist_elem, key).text = str(value)

            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            print(f"Данные экспортированы в {filename}")
        except Exception as e:
            raise InvalidFileFormatError(f"Ошибка при экспорте в XML: {str(e)}")

    @staticmethod
    def create_backup(service: MusicService, backup_dir: str = "backups"):
        """Создание резервной копии данных"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(backup_dir, exist_ok=True)

            json_file = f"{backup_dir}/music_backup_{timestamp}.json"
            xml_file = f"{backup_dir}/music_backup_{timestamp}.xml"

            FileOperations.export_to_json(service, json_file)
            FileOperations.export_to_xml(service, xml_file)

            print(f"Резервная копия создана: {json_file}, {xml_file}")
            return json_file, xml_file
        except Exception as e:
            raise InvalidFileFormatError(f"Ошибка при создании резервной копии: {str(e)}")