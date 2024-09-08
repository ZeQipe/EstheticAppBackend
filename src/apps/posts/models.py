from django.db import models
from apps.users.models import User
from templates.response import templates as mess
from django.db.models import Q
from random import shuffle
import json
import re


class Post(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    post_name = models.CharField(max_length=20)
    description = models.CharField(max_length=50, blank=True, null=True)
    users_liked = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    type_content = models.TextField()
    url = models.TextField(unique=True)
    tags_list = models.JSONField(default=list)
    aspect_ratio = models.TextField(blank=True, null=True)
    object_position = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=100)
    
    
    @staticmethod
    def get_posts(user_tags, offset=0, limit=10):
        """
        Возвращает список уникальных постов на основе списка тегов пользователя.
        
        Параметры:
        - user_tags (list): список тегов пользователя для поиска.
        - offset (int): количество постов, которые нужно пропустить.
        - limit (int): количество постов, которое нужно вернуть.
        
        Возвращает:
        - List[Post]: список объектов Post.
        """
        # Приводим теги пользователя к нижнему регистру для поиска без учета регистра
        user_tags_normalized = [tag.lower() for tag in user_tags]
        
        if not user_tags_normalized:
            random_posts = Post.objects.order_by('?')[offset:offset+limit]
            return list(random_posts)
        
        # 1. Точное совпадение тегов (поиск по JSON полю tags_list)
        exact_match = Q()
        for tag in user_tags_normalized:
            exact_match |= Q(tags_list__icontains=tag)
        
        exact_posts = Post.objects.filter(exact_match).order_by('-id')

        # 2. Если не хватило постов, ищем частичное совпадение
        partial_posts = Post.objects.none()
        if exact_posts.count() < limit:
            partial_match = Q()
            for tag in user_tags_normalized:
                # Поиск по первым 3 символам для частичного совпадения
                partial_match |= Q(tags_list__icontains=tag[:3])
            
            # Фильтруем посты с частичным совпадением, исключая те, которые уже в точных совпадениях
            partial_posts = Post.objects.filter(partial_match).exclude(id__in=exact_posts).order_by('-id')
        
        # 3. Объединяем точные и частичные совпадения
        combined_posts = exact_posts | partial_posts

        # 4. Если и после частичных совпадений не набрали посты — добавляем случайные посты
        if combined_posts.count() < limit:
            remaining_limit = limit - combined_posts.count()
            random_posts = Post.objects.exclude(id__in=combined_posts).order_by('?')[:remaining_limit]
            combined_posts = combined_posts | random_posts

        # 5. Применяем distinct() после объединения всех запросов
        posts = combined_posts.distinct()[offset:offset+limit]
        
        return list(posts)
    
    
    @staticmethod
    def edit_post(post, new_data):
        post.post_name = new_data['postName']
        post.description = new_data['description']
        post.link = new_data['link']
        post.aspect_ratio = new_data['aspectRatio']
        post.object_position = new_data['objectPosition']
        post.tags_list = new_data["tags"]
        
        post.save()


    @staticmethod
    def validate_post_data(post_data: dict) -> tuple:
        """
        Validate post data
        :param post_data: list of post data
        :return: tuple - bool values of result and error message
        """
        regex_patterns = {
            'post_name': r'^.{2,20}$',
            'description': r'^.{0,50}$',  # Допускает пустую строку или строку до 50 символов
            'aspect_ratio': r'^.*$',  # Любая строка
            'object_position': r'^.*$',  # Любая строка
        }
        
        checking_data = [post_data['postName'], post_data['description'], 
                         post_data['aspectRatio'], post_data['objectPosition']]

        field_names = ['post_name', 'description', 'aspect_ratio', 'object_position']

        for i, field in enumerate(field_names):
            value = checking_data[i]

            if field == "description" and (value is None or value == ''):
                # Пропускаем проверку, если description не указан
                continue
            
            if not isinstance(value, str):
                response = mess[400]
                response['message'] = response['message'] + f'. {field} not correct'
                return False, response

            if not re.match(regex_patterns[field], value):
                response = mess[400]
                response['message'] = response['message'] + f'. Invalid value for {field}'
                return False, response

        return True, "All data correct"


    @staticmethod
    def create_new_posts(user_data: dict) -> dict:
        post = Post.objects.create(
                            id=user_data["id"],  # ID поста
                            author=user_data["author_id"],  # ID автора поста
                            post_name=user_data["postName"],  # Название поста
                            description=user_data["description"],  # Описание поста
                            type_content=user_data["type_file"],  # Тип поста
                            url=user_data["url"],  # URL файла на сервере
                            tags_list=user_data["tags"], # Список комментариев
                            aspect_ratio=user_data["aspectRatio"], # параметр, которые передается с фронта
                            object_position=user_data["objectPosition"], # Позиция изображения
                            link=user_data["link"] # Ссылка для сохранения
                            )
        return post
    
    
    @staticmethod
    def get_data_in_request(data):
        fileOptions = json.loads(data.get("fileOptions"))

        return {
                "postName": data.get("name"),
                "description": data.get("description"),
                "link": data.get("link"),
                "aspectRatio": fileOptions["aspectRatio"],
                "objectPosition": fileOptions["objectPosition"]
        }