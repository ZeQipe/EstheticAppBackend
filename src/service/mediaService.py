from django.conf import settings
from django.utils.http import urlencode
from django.urls import reverse
from django.http import HttpRequest


class Media:
    @staticmethod
    def save_media(image_file, file_path):
        if not file_path:
            return

        # Сохраняем файл на сервере
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
                
    
    @staticmethod
    def get_image_url(request: HttpRequest, filename: str, subdir: str) -> str:
        # Формируем путь к файлу
        relative_path = f"{settings.MEDIA_URL}{subdir}/{filename}"

        # Генерация полного URL
        full_url = request.build_absolute_uri(relative_path)
        return full_url