from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv


def encrypt_string(key: str):
    """
    Шифрует данные c помощью ключа.

    :param user_id: Строка, содержащая данные пользователя.
    :return: Зашифрованные данные в виде строки.
    """
    
    load_dotenv()

    static_key = os.getenv('CRIPTO_KEY')
    cipher_suite = Fernet(static_key)

    encrypted_id = cipher_suite.encrypt(key.encode('utf-8'))
    return encrypted_id.decode('utf-8')


def decrypt_string(encrypted_str: str):
    """
    Дешифрует данные пользователя ключем

    :param encrypted_id: Строка, содержащая зашифрованные данные.
    :return: Расшифрованные данные пользователя.
    """
    
    load_dotenv()

    static_key = os.getenv('CRIPTO_KEY')
    cipher_suite = Fernet(static_key)

    decrypted_id = cipher_suite.decrypt(encrypted_str.encode('utf-8'))
    return decrypted_id.decode('utf-8')
