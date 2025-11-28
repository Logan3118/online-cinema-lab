
    #Модуль с пользовательскими исключениями для музыкального сервиса

class MusicServiceError(Exception):
    #Базовое исключение для музыкального сервиса
    pass

class UserNotFoundError(MusicServiceError):
    #Пользователь не найден
    pass

class TrackNotFoundError(MusicServiceError):
    #Трек не найден
    pass

class InsufficientPermissionsError(MusicServiceError):
    #Недостаточно прав
    pass

class InvalidFileFormatError(MusicServiceError):
    #Неверный формат файла
    pass

class AuthenticationError(MusicServiceError):
    #Ошибка аутентификации
    pass

class PlaylistNotFoundError(MusicServiceError):
    #Плейлист не найден
    pass

class AlbumNotFoundError(MusicServiceError):
    #Альбом не найден
    pass

class ArtistNotFoundError(MusicServiceError):
    #Артист не найден
    pass