from .models import User
from templates.response import templates as mess
from service.authService import Authorization
from utils.tools import generate_string, save_media
from utils.separament import Parser as pars
from utils.validator import *
from utils.cripting import *
from pathlib import Path
from django.http.multipartparser import MultiPartParser
import json


def registration_users(request) -> dict:
    """
    Create a new user in the DB.

    :param data: Dictionary containing
    - firstName: First Name of user
    - lastName: Last Name of user
    - userName: NickName of user
    - email: Email address of user
    - avatar: Image binary string
    - password: <PASSWORD>
    - tags: List[string] of tags associated with user
    :return: Dictionary
    - status: HTTP Status Code
    - message: Message
    """
    # Генерируем уникальный ID 
    user_id = generate_string(30, User)

    # Получение данных из запроса
    user_data = User.get_data_in_request(request.POST)
    
    # Валидация данных
    validate, message_validate = User.validate_data(user_data)
    if not validate:
        return message_validate
    
    # Проверка на уникальность в базе данных
    correct_data, message_unique = User.unique_data(user_data['user_name'], user_data['email'])
    if not correct_data:
        return message_unique
    
    # Подготовка тэгов
    pack_tags_json = request.POST.get("tags")
    if pack_tags_json:
        pack_tags = json.loads(pack_tags_json)
        tags = pars.packing_tags(pack_tags)
    else:
        tags = []
    
    # Проверка наличия фото
    try:
        file = request.FILES.get['avatar']
        if file:
            url = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'avatars' / f'{user_id}.jpg'
        else:
            url = None
    except Exception as error:
        url = None
        
    # Зашифровываем пароль
    try:
        cripto_password = encrypt_string(request.POST.get("password"))
    
    except Exception as er:
        return mess[400]
    
    # Создание нового пользователя
    try:
        user = User.objects.create(
                                    id=user_id,
                                    first_name=user_data['first_name'],
                                    last_name=user_data['last_name'],
                                    user_name=user_data['user_name'],
                                    email=user_data["email"],
                                    password=cripto_password,
                                    avatar=url,
                                    tags_user=tags,
                                    )
        

        save_media(file, url)
        return mess[200]
    
    except Exception as er:
        return mess[500]
    

def login(request) -> dict:
    """
    Function to validate user login data
    :param data: dictionary with user login and password
    :return: dictionary with result
    """
    # Поиск нужного пользователя по EMail адресу    
    try:
        user_data = json.loads(request.body)
        email_user, password_user = user_data["email"], user_data["password"]
    except Exception as er:
        return mess[400]

    if not isinstance(email_user, str) or "@" not in email_user or not email_user.endswith((".com", ".ru", ".eu")):
        return mess[400]
    
    try:
        user = User.objects.get(email=email_user)
    except Exception as er:
        return mess[404]
                
    # расшифровка пароля
    password = decrypt_string(user.password)

    if password != password_user:
        return mess[400]
    
    else:
        response = User.get_user_data_full(user)
        return response


def get_user_profile(request, profileId):
    cookie_user = Authorization.check_logining(request)
    
    try:    
        user_profile = User.objects.get(id=decrypt_string(profileId))
    except Exception as er:
        return mess[404]
    
    response = {
        "user": User.get_user_data_full(user_profile)
    }
    
    if not isinstance(cookie_user, dict) and cookie_user.id == user_profile.id:
        response['user']['email'] = user_profile.email
        response['guest'] = {
            "isOwner": True,
            "isSubscribe": False
        }
        
    elif isinstance(cookie_user, dict):
        response['guest'] = {
            "isOwner": False,
            "isSubscribe": False
        }
        
    else:
        response['guest'] = {
            "isOwner" : False,
            # Доработать - "isSubscribe": True if not isinstance(cookie_user, dict) and cookie_user.id in user_profile.subscribers else False 
        }
        
    return response
    

def edit_user_profile(request, profileId):
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        return mess[401]
    
    try:
        user_profile = User.objects.get(id=decrypt_string(profileId))
    except:
        return mess(404)
    
    if cookie_user.id != user_profile.id:
        return mess[403]
    
    put_data = MultiPartParser(request.META, request, request.upload_handlers).parse()
    
    # Получение данных из запроса
    user_data = User.get_data_in_request(put_data[0])

    # Валидация данных
    validate, message_validate = User.validate_data(user_data)
    if not validate:
        return message_validate
    
    # Проверка на уникальность в базе данных
    if user_data['user_name'] != user_profile.user_name:
        if User.objects.filter(user_name=user_data["user_name"]).exists():
            response = mess[400]
            response['message'] = response['message'] + f'. The Username is busy'
            return response
        else:
            user_profile.user_name = user_data['user_name']
    
    # Подготовка тэгов
    pack_tags_json = request.POST.get("tags")
    if pack_tags_json:
        pack_tags = json.loads(pack_tags_json)
        tags = pars.packing_tags(pack_tags)
    else:
        tags = []
        
    ## Замена данных
    # Проверка наличия фото
    try:
        file = put_data[1].get('avatar')
        url = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'avatars' / f'{user_profile.id}.jpg'
        save_media(file, url)
    except:
        pass
        
    user_profile.first_name = user_data['first_name']
    user_profile.last_name = user_data['last_name']
    
    if tags:
        user_profile.tags_user = tags
    
    user_profile.save()
    return mess[200]
        

