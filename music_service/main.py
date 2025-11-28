"""
Основной модуль музыкального сервиса с загрузкой данных из файлов
"""
import os
from models import MusicService
from file_operations import FileOperations
from exceptions import *

def load_initial_data(service: MusicService):
    """Загрузка начальных данных из файлов"""
    print("="*50)
    print("ЗАГРУЗКА НАЧАЛЬНЫХ ДАННЫХ")
    print("="*50)

    # Пути к заранее созданным файлам
    json_file = "data/initial_data.json"
    xml_file = "data/initial_data.xml"

    try:
        # Загрузка данных из файлов
        total_loaded, total_errors = FileOperations.load_initial_data(service, json_file, xml_file)

        print(f"\nИтоги загрузки:")
        print(f"Успешно загружено объектов: {total_loaded}")
        print(f"Ошибок при загрузке: {total_errors}")

        # Показываем загруженные данные
        stats = service.get_statistics()
        print(f"\nЗагруженные данные:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    except InvalidFileFormatError as e:
        print(f"Ошибка при загрузке данных: {e}")
        return False

    return True

def demo_basic_operations(service: MusicService):
    """Демонстрация базовых операций"""
    try:
        print("\n" + "="*50)
        print("ДЕМОНСТРАЦИЯ ОСНОВНЫХ ОПЕРАЦИЙ")
        print("="*50)

        # Вход пользователя (берем первого пользователя из загруженных)
        if service.users:
            first_user = list(service.users.values())[0]
            service.login(first_user.email, "default_password")
            print(f"Вошел пользователь: {first_user.username}")

        # Поиск и воспроизведение треков
        print("\nПоиск треков Queen:")
        queen_tracks = service.search_tracks("queen")
        for track in queen_tracks:
            print(f"  - {track.title} ({track.duration} сек)")
            track.play()

        # Показ плейлистов
        if service.playlists:
            print("\nСуществующие плейлисты:")
            for playlist in service.playlists.values():
                print(f"  - {playlist.name}: {len(playlist.tracks)} треков")

        # Создание нового плейлиста
        if service.current_user:
            new_playlist = service.create_playlist("My New Playlist", "Созданный программой")
            if queen_tracks:
                new_playlist.add_track(queen_tracks[0])
                print(f"\nСоздан новый плейлист: {new_playlist.name}")

    except MusicServiceError as e:
        print(f"Ошибка при выполнении операций: {e}")

def demo_file_operations(service: MusicService):
    """Демонстрация работы с файлами"""
    try:
        print("\n" + "="*50)
        print("РАБОТА С ФАЙЛАМИ")
        print("="*50)

        # Экспорт текущих данных
        FileOperations.export_to_json(service, "current_data.json")
        FileOperations.export_to_xml(service, "current_data.xml")

        # Создание резервной копии
        FileOperations.create_backup(service)

        # Экспорт данных текущего пользователя
        if service.current_user:
            FileOperations.export_user_data(service, service.current_user.user_id, "my_data.json")

        print("\nСозданные файлы:")
        for file in ['current_data.json', 'current_data.xml', 'my_data.json']:
            if os.path.exists(file):
                print(f"  - {file}")
        if os.path.exists('backups'):
            print("  - backups/ (директория с резервными копиями)")

    except InvalidFileFormatError as e:
        print(f"Ошибка при работе с файлами: {e}")

def demo_advanced_features(service: MusicService):
    """Демонстрация дополнительных возможностей"""
    try:
        print("\n" + "="*50)
        print("ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ")
        print("="*50)

        # Работа с альбомами
        if service.albums:
            print("Доступные альбомы:")
            for album in service.albums.values():
                print(f"  - {album.title} by {album.artist.name} ({album.release_date})")

        # Статистика прослушиваний
        print("\nСтатистика прослушиваний:")
        for track in list(service.tracks.values())[:3]:  # Первые 3 трека
            print(f"  - {track.title}: {track.stream_count} прослушиваний")

        # Поиск по артистам
        print("\nПоиск артистов:")
        for artist_name in ["Queen", "The Beatles"]:
            tracks = service.search_tracks(artist_name)
            if tracks:
                print(f"  - {artist_name}: {len(tracks)} треков")

    except MusicServiceError as e:
        print(f"Ошибка при демонстрации возможностей: {e}")

def main():
    """Основная функция"""
    print("МУЗЫКАЛЬНЫЙ ОНЛАЙН-СЕРВИС")
    print("Загрузка данных из файлов...")
    print("=" * 50)

    # Инициализация сервиса
    service = MusicService()

    try:
        # Загрузка начальных данных
        if not load_initial_data(service):
            print("Не удалось загрузить начальные данные. Продолжение невозможно.")
            return

        # Демонстрация функционала
        demo_basic_operations(service)
        demo_advanced_features(service)
        demo_file_operations(service)

        print("\n" + "="*50)
        print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("="*50)

        # Финальная статистика
        final_stats = service.get_statistics()
        print("\nФинальная статистика сервиса:")
        for key, value in final_stats.items():
            print(f"  {key}: {value}")

    except MusicServiceError as e:
        print(f"Критическая ошибка в музыкальном сервисе: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    # Создаем директорию data если не существует
    os.makedirs("data", exist_ok=True)

    # Проверяем существование файлов с данными
    if not os.path.exists("data/initial_data.json"):
        print("ВНИМАНИЕ: Файл data/initial_data.json не найден!")
        print("Создайте файлы данных как указано в документации")
    else:
        main()