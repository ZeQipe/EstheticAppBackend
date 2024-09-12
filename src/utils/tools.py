import string
import random


def generate_string(len: int, model) -> str:
    characters = string.ascii_letters + string.digits
    key_length = len
    
    if not model:
        return ''.join(random.choice(characters) for _ in range(key_length))
    
    while True:
        create_id = ''.join(random.choice(characters) for _ in range(key_length))
        if not model.objects.filter(id=create_id).exists():
            return create_id