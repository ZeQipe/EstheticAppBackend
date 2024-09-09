from templates.response import templates as mess
from service.authService import Authorization
from apps.users.models import User
from apps.posts.models import Post
from utils.separament import Parser as pars
from pathlib import Path
from django.http.multipartparser import MultiPartParser
from utils.tools import generate_string, save_media
import json


def create_post(request):
    # Поиск автора поста
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        return mess[401]

    request_data = MultiPartParser(request.META, request, request.upload_handlers).parse()
    post_data = Post.get_data_in_request(request_data[0])

    # Валидация данных для создания постов
    result_validate, message_validate = Post.validate_post_data(post_data)
    if not result_validate:
        return message_validate
    
    # Подготовка тэгов
    pack_tags_json = request_data[0].get("tags")
    if pack_tags_json:
        post_data["tags"] = pars.packing_tags(json.loads(pack_tags_json))
    else:
        post_data["tags"] = []
    
    post_data["id"] = generate_string(35, Post)
    post_data["author"] = cookie_user

    # Данные о файле
    file = request_data[1].get('file')
    if file:
        if file.content_type.startswith('image/'):
            post_data["type_file"] = "img"
    else:
        return mess[204]
    
    name_file = f"{post_data['id']}.{'jpg' if post_data['type_file'] == 'img' else 'mp4'}"
    post_data["url"] = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'img' / name_file
    
    # Отправляем в базу все данные
    try:
        post = Post.create_new_posts(post_data)
        save_media(file, post_data["url"])
        return mess[200]
        
    except Exception as er:
        return mess[500]


def search_posts(request):
    """
    Обрабатывает запрос на получение постов учитывая теги пользователя.
    """
    # Получаем query параметры offset и limit из запроса и пытаемся привести их к int.
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0

    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    # Поиск автора поста через auth_key из cookies
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        tags_user = []
    else:
        tags_user = cookie_user.tags_user
    
    # Получаем посты из базы данных с учетом тегов, offset и limit
    try:
        result = Post.get_posts(tags_user, offset, limit)
    except Exception as e:
        return mess[500]

    if not result:
        return mess[404]

    response = pars.parse_posts(result)
    return response


def get_post_by_id(request, post_id):
    cookie_user = Authorization.check_logining(request)
    
    try:
        post = Post.objects.get(id=post_id)
    except Exception as er:
        return mess[404]
    
    response = pars.parse_post(post, cookie_user)
    
    return response


def edit_post_by_id(request, post_id):
    # Поиск автора поста
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        return mess[401]
    
    # Ищем пост, который необходимо изменить
    try:
        post = Post.objects.get(id=post_id)
    except:
        return mess[404]

    if cookie_user.id != post.author.id:
        return mess[403]
    
    # Получаем данные для редактирования
    request_data = MultiPartParser(request.META, request, request.upload_handlers).parse()
    post_data = Post.get_data_in_request(request_data[0])
    
    # Подготовка тэгов
    pack_tags_json = request_data[0].get("tags")
    if pack_tags_json:
        post_data["tags"] = pars.packing_tags(json.loads(pack_tags_json))
    else:
        post_data["tags"] = []
    
    # Валидация данных для создания постов
    result_validate, message_validate = Post.validate_post_data(post_data)
    if not result_validate:
        return message_validate

    # Отправляем в базу все данные
    try:
        Post.edit_post(post, post_data)
    except Exception as er:
        print(er )
        return mess[500]
        
    return mess[200]