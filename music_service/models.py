"""
Модуль с основными классами музыкального сервиса
"""
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from exceptions import *


class User:
    def __init__(self, user_id: str, username: str, email: str, password: str, premium: bool = False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self._password = password
        self.premium = premium
        self.created_at = datetime.now()

    def login(self, email: str, password: str) -> bool:
        """Аутентификация пользователя"""
        try:
            if email == self.email and password == self._password:
                print(f"Пользователь {self.username} успешно вошел в систему")
                return True
            return False
        except Exception as e:
            raise MusicServiceError(f"Ошибка при входе: {str(e)}")

    def upgrade_to_premium(self):
        """Обновление до премиум-аккаунта"""
        try:
            if not self.premium:
                self.premium = True
                print(f"Пользователь {self.username} upgraded to premium")
            else:
                print("Аккаунт уже премиум")
        except Exception as e:
            raise MusicServiceError(f"Ошибка при обновлении: {str(e)}")

    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'premium': self.premium,
            'created_at': self.created_at.isoformat()
        }

    def __str__(self):
        return f"User({self.username}, {self.email}, premium: {self.premium})"


class Artist:
    def __init__(self, artist_id: str, name: str, bio: str = ""):
        self.artist_id = artist_id
        self.name = name
        self.bio = bio
        self.albums: List['Album'] = []

    def add_album(self, album: 'Album'):
        """Добавление альбома артисту"""
        try:
            if album not in self.albums:
                self.albums.append(album)
        except Exception as e:
            raise MusicServiceError(f"Ошибка при добавлении альбома: {str(e)}")

    def get_albums(self) -> List['Album']:
        return self.albums

    def to_dict(self) -> Dict:
        return {
            'artist_id': self.artist_id,
            'name': self.name,
            'bio': self.bio,
            'albums_count': len(self.albums)
        }

    def __str__(self):
        return f"Artist({self.name}, albums: {len(self.albums)})"


class Track:
    def __init__(self, track_id: str, title: str, duration: int, file_path: str, artist: Artist):
        self.track_id = track_id
        self.title = title
        self.duration = duration  # в секундах
        self.file_path = file_path
        self.artist = artist
        self.stream_count = 0
        self.album: Optional[Album] = None

    def play(self):
        """Воспроизведение трека"""
        try:
            self.stream_count += 1
            print(f"Воспроизведение: {self.title} - {self.artist.name}")
        except Exception as e:
            raise MusicServiceError(f"Ошибка при воспроизведении: {str(e)}")

    def download(self, user: User) -> str:
        """Скачивание трека"""
        try:
            if not user.premium:
                raise InsufficientPermissionsError("Требуется премиум-аккаунт для скачивания")
            print(f"Скачивание: {self.title}")
            return self.file_path
        except InsufficientPermissionsError:
            raise
        except Exception as e:
            raise MusicServiceError(f"Ошибка при скачивании: {str(e)}")

    def to_dict(self) -> Dict:
        return {
            'track_id': self.track_id,
            'title': self.title,
            'duration': self.duration,
            'artist': self.artist.name,
            'stream_count': self.stream_count,
            'album': self.album.title if self.album else None
        }

    def __str__(self):
        return f"Track({self.title}, {self.duration}s, by {self.artist.name})"


class Album:
    def __init__(self, album_id: str, title: str, artist: Artist, release_date: str, genre: str = ""):
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.release_date = release_date
        self.genre = genre
        self.tracks: List[Track] = []
        artist.add_album(self)

    def add_track(self, track: Track):
        """Добавление трека в альбом"""
        try:
            if track not in self.tracks:
                self.tracks.append(track)
                track.album = self
        except Exception as e:
            raise MusicServiceError(f"Ошибка при добавлении трека: {str(e)}")

    def get_tracks(self) -> List[Track]:
        return self.tracks

    def to_dict(self) -> Dict:
        return {
            'album_id': self.album_id,
            'title': self.title,
            'artist': self.artist.name,
            'release_date': self.release_date,
            'genre': self.genre,
            'tracks_count': len(self.tracks)
        }

    def __str__(self):
        return f"Album({self.title}, {self.artist.name}, tracks: {len(self.tracks)})"


class PlaylistTrack:
    """Промежуточный класс для связи плейлиста и трека с позицией"""

    def __init__(self, track: Track, position: int):
        self.track = track
        self.position = position

    def to_dict(self) -> Dict:
        return {
            'track_id': self.track.track_id,
            'title': self.track.title,
            'artist': self.track.artist.name,
            'position': self.position
        }


class Playlist:
    def __init__(self, playlist_id: str, name: str, description: str, owner: User, is_public: bool = True):
        self.playlist_id = playlist_id
        self.name = name
        self.description = description
        self.owner = owner
        self.is_public = is_public
        self.created_date = datetime.now()
        self.tracks: List[PlaylistTrack] = []

    def add_track(self, track: Track):
        """Добавление трека в плейлист"""
        try:
            position = len(self.tracks) + 1
            playlist_track = PlaylistTrack(track, position)
            self.tracks.append(playlist_track)
            print(f"Трек {track.title} добавлен в плейлист {self.name}")
        except Exception as e:
            raise MusicServiceError(f"Ошибка при добавлении трека: {str(e)}")

    def remove_track(self, track_id: str):
        """Удаление трека из плейлиста"""
        try:
            for i, playlist_track in enumerate(self.tracks):
                if playlist_track.track.track_id == track_id:
                    self.tracks.pop(i)
                    # Обновляем позиции оставшихся треков
                    for j, pt in enumerate(self.tracks[i:], start=i + 1):
                        pt.position = j
                    print(f"Трек удален из плейлиста {self.name}")
                    return
            raise TrackNotFoundError(f"Трек с ID {track_id} не найден в плейлисте")
        except TrackNotFoundError:
            raise
        except Exception as e:
            raise MusicServiceError(f"Ошибка при удалении трека: {str(e)}")

    def get_tracks_info(self) -> List[Dict]:
        """Получение информации о треках в плейлисте"""
        return [pt.to_dict() for pt in self.tracks]

    def to_dict(self) -> Dict:
        return {
            'playlist_id': self.playlist_id,
            'name': self.name,
            'description': self.description,
            'owner': self.owner.username,
            'is_public': self.is_public,
            'created_date': self.created_date.isoformat(),
            'tracks_count': len(self.tracks),
            'tracks': self.get_tracks_info()
        }

    def __str__(self):
        return f"Playlist({self.name}, owner: {self.owner.username}, tracks: {len(self.tracks)})"


class MusicService:
    """Основной класс музыкального сервиса"""

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.artists: Dict[str, Artist] = {}
        self.tracks: Dict[str, Track] = {}
        self.albums: Dict[str, Album] = {}
        self.playlists: Dict[str, Playlist] = {}
        self.current_user: Optional[User] = None

    def register_user(self, username: str, email: str, password: str) -> User:
        """Регистрация нового пользователя"""
        try:
            # Проверка на существующий email
            for user in self.users.values():
                if user.email == email:
                    raise MusicServiceError(f"Пользователь с email {email} уже существует")

            user_id = str(uuid.uuid4())
            user = User(user_id, username, email, password)
            self.users[user_id] = user
            print(f"Пользователь {username} успешно зарегистрирован")
            return user
        except MusicServiceError:
            raise
        except Exception as e:
            raise MusicServiceError(f"Ошибка при регистрации: {str(e)}")

    def login(self, email: str, password: str) -> bool:
        """Вход пользователя в систему"""
        try:
            for user in self.users.values():
                if user.login(email, password):
                    self.current_user = user
                    return True
            raise AuthenticationError("Неверный email или пароль")
        except AuthenticationError:
            raise
        except Exception as e:
            raise MusicServiceError(f"Ошибка при входе: {str(e)}")

    def logout(self):
        """Выход пользователя из системы"""
        self.current_user = None
        print("Пользователь вышел из системы")

    def add_track(self, title: str, duration: int, file_path: str, artist_name: str) -> Track:
        """Добавление нового трека"""
        try:
            if not self.current_user:
                raise InsufficientPermissionsError("Требуется вход в систему")

            # Создаем или находим артиста
            artist = next((a for a in self.artists.values() if a.name == artist_name), None)
            if not artist:
                artist_id = str(uuid.uuid4())
                artist = Artist(artist_id, artist_name)
                self.artists[artist_id] = artist

            track_id = str(uuid.uuid4())
            track = Track(track_id, title, duration, file_path, artist)
            self.tracks[track_id] = track
            return track
        except InsufficientPermissionsError:
            raise
        except Exception as e:
            raise MusicServiceError(f"Ошибка при добавлении трека: {str(e)}")

    def create_playlist(self, name: str, description: str = "", is_public: bool = True) -> Playlist:
        """Создание плейлиста"""
        try:
            if not self.current_user:
                raise InsufficientPermissionsError("Требуется вход в систему")

            playlist_id = str(uuid.uuid4())
            playlist = Playlist(playlist_id, name, description, self.current_user, is_public)
            self.playlists[playlist_id] = playlist
            print(f"Плейлист {name} создан")
            return playlist
        except InsufficientPermissionsError:
            raise
        except Exception as e:
            raise MusicServiceError(f"Ошибка при создании плейлиста: {str(e)}")

    def get_user_playlists(self, user_id: str = None) -> List[Playlist]:
        """Получение плейлистов пользователя"""
        try:
            if not user_id and self.current_user:
                user_id = self.current_user.user_id

            if not user_id:
                raise InsufficientPermissionsError("Требуется указать user_id или войти в систему")

            user_playlists = []
            for playlist in self.playlists.values():
                if playlist.owner.user_id == user_id:
                    user_playlists.append(playlist)

            return user_playlists
        except Exception as e:
            raise MusicServiceError(f"Ошибка при получении плейлистов: {str(e)}")

    def search_tracks(self, query: str) -> List[Track]:
        """Поиск треков по названию или артисту"""
        try:
            results = []
            query_lower = query.lower()

            for track in self.tracks.values():
                if (query_lower in track.title.lower() or
                        query_lower in track.artist.name.lower()):
                    results.append(track)

            return results
        except Exception as e:
            raise MusicServiceError(f"Ошибка при поиске: {str(e)}")

    def get_statistics(self) -> Dict:
        """Получение статистики сервиса"""
        return {
            'users_count': len(self.users),
            'artists_count': len(self.artists),
            'tracks_count': len(self.tracks),
            'albums_count': len(self.albums),
            'playlists_count': len(self.playlists),
            'total_streams': sum(track.stream_count for track in self.tracks.values())
        }