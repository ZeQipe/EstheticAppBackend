import string
import random


def generate_string(len: int, model) -> str:
    characters = string.ascii_letters + string.digits
    key_length = len
    
    while True:
        create_id = ''.join(random.choice(characters) for _ in range(key_length))
        if not model.objects.filter(id=create_id).exists():
            return create_id
 
def save_media(image_file, file_path):
        if not file_path:
            return

        # Сохраняем файл на сервере
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)