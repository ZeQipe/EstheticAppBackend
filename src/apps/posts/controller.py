from templates.response import templates as mess
from service.authService import Authorization
from apps.users.models import User
from apps.posts.models import Post
from utils.separament import Parser as pars
from pathlib import Path
from django.http.multipartparser import MultiPartParser
from utils.cripting import generate_string
from service.mediaService import Media
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
        post_data["type_file"] = "img"
        name_file = f"{post_data['id']}.{'jpg' if post_data['type_file'] == 'img' else 'mp4'}"
        post_data["url"] = Media.get_image_url(request, name_file, "img")
        path = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'img' / name_file
    
    else:
        return mess[204]
    
    # Отправляем в базу все данные
    try:
        Post.create_new_posts(post_data)
        Media.save_media(file, path)
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

    response = pars.parse_posts(result, offset, limit)
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
    post_data = {
                "postName": request_data[0].get("name"),
                "description": request_data[0].get("description"),
                "link": request_data[0].get("link"),
                "aspectRatio": request_data[0].get("aspectRatio")
                }
    
    if post_data["postName"]:
        if len(post_data["postName"]) <= 20:
            post.post_name = post_data["postName"]

    if post_data["description"]:
        if len(post_data["description"]) <= 100:
            post.description = post_data["description"]
        else:
            response = mess[400]
            response['message'] = f'Bad request. Invalid value for name Post'
            return False, response
        
    if post_data["link"]:
        if len(post_data["link"]) <= 100:
            post.link = post_data["link"]
        else:
            response = mess[400]
            response['message'] = f'Bad request. Invalid value for link'
            return False, response
        
    if post_data["aspectRatio"]:
        post.aspect_ratio = post_data["aspectRatio"]

    # Подготовка тэгов
    pack_tags_json = request_data[0].get("tags")
    if pack_tags_json:
        tags = pars.packing_tags(json.loads(pack_tags_json))
        post.tags_list = tags

    post.save()
        
    return mess[200]


def toggle_like(request, postID):
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        return mess[401]
    
    try: 
        post = Post.objects.get(id=postID)
        
    except Exception as er:
        return mess[404]
    
    if post.users_liked.filter(id=cookie_user.id).exists():
        post.users_liked.remove(cookie_user)
    
    else:
        post.users_liked.add(cookie_user)
        
    return mess[200]