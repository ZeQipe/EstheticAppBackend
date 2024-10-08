from .models import User
from templates.response import templates as mess
from service.authService import Authorization
from service.mediaService import Media
from utils.separament import Parser as pars
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
    request_data = MultiPartParser(request.META, request, request.upload_handlers).parse()
    try:
        user_data = User.get_data_in_request(request_data[0])
        user_data["password"] = request_data[0].get("password")

    except Exception as error:
        return mess[400]
    
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
    file = request_data[1].get("avatar")
    if file:
        path = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'avatars' / f'{user_id}.jpg'
        url = Media.get_image_url(request, f'{user_id}.jpg', "avatars")

    else:
        path = None
        url = None
        
    # Зашифровываем пароль
    try:
        cripto_password = encrypt_string(user_data.get("password"))

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

    except Exception as er:
        return mess[500]
    
    Media.save_media(file, path)
    return mess[200]
    

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
        return mess[401]

    if not isinstance(email_user, str) or "@" not in email_user or not email_user.endswith((".com", ".ru", ".eu")):
        return mess[401]
    
    try:
        user = User.objects.get(email=email_user)

    except Exception as er:
        return mess[401]
                
    # расшифровка пароля
    password = decrypt_string(user.password)
    if password != password_user:
        return mess[401]
    
    else:
        response = User.get_user_data_full(user)
        return response


def get_user_profile(request, profileId=''):
    cookie_user = Authorization.check_logining(request)
    
    if profileId:
        try:    
            user_profile = User.objects.get(id=profileId)

        except Exception as er:
            return mess[404]
    
    else:
        if isinstance(cookie_user, dict):
            return mess[401]
        
        response = {"user": User.get_user_data_full(cookie_user)}
        response['user']['email'] = cookie_user.email
        response['user']['tags'] = pars.unpacking_tags(cookie_user.tags_user)
        return response['user']
    
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
            "isSubscribe": not isinstance(cookie_user, dict) and cookie_user in user_profile.subscribers
        }
        
    return response
    

def edit_user_profile(request):
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        return mess[401]
    
    # Получение данных из запроса
    put_data = MultiPartParser(request.META, request, request.upload_handlers).parse()
    user_data = {'first_name': put_data[0].get("firstName"),
                 'last_name': put_data[0].get("lastName"), 
                 'user_name' : put_data[0].get("userName")
                 }

    # Валидация данных
    if user_data['first_name'] and len(user_data["first_name"]) <= 15 and len(user_data["first_name"]) >= 2:
        cookie_user.first_name = user_data["first_name"]

    if user_data["last_name"] and len(user_data["last_name"]) <= 20:
        cookie_user.last_name = user_data["last_name"]

    if user_data["user_name"]:
        if User.objects.filter(user_name=user_data["user_name"]).exists():
            response = mess[400].copy()
            response['message'] = response['message'] + f'. The Username is busy'
            return response
        else:
            cookie_user.user_name = user_data['user_name']
    
    # Подготовка тэгов
    pack_tags_json = put_data[0].get("tags")
    if pack_tags_json:
        try:
            pack_tags = json.loads(pack_tags_json)
        except:
            response = mess[400]
            response['message'] = f'Bad request. Invalid value for tags'
            return False, response
        
        tags = pars.packing_tags(pack_tags)
        cookie_user.tags_user = tags

    # Проверка наличия фото
    try:
        file = put_data[1].get('avatar')
        path = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'avatars' / f'{cookie_user.id}.jpg'
        Media.save_media(file, path)

    except:
        pass
    
    cookie_user.save()
    return mess[200]
        

def user_created_post_list(request, userID):
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0

    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20
    
    try:
        user = User.objects.get(id=userID)
    except Exception as er:
        response = mess[404].copy()
        response['message'] = "Not found User"
        return response
    
    posts_user = user.posts.all()

    response = pars.parse_posts(posts_user, offset, limit)
    
    return response