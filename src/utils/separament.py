from utils.tools import generate_string
from utils.cripting import encrypt_string as encript
from templates.response import templates as mess
from apps.users.models import User
from django.utils.dateformat import DateFormat
from django.utils.timezone import get_current_timezone


class Parser:
    @staticmethod
    def unpacking_tags(tags: list) -> list:
        if not tags:
            return tags

        id_list = []
        while len(id_list) < len(tags):
            id = generate_string(8, False)
            if id not in id_list:
                id_list.append(generate_string(8, False))
            
        tag_response = []
        for i in range(len(id_list)):
            tag_dict = {"id" : id_list[i],
                        "label" : tags[i]}
            
            tag_response.append(tag_dict)
        
        return tag_response

    @staticmethod
    def packing_tags(tags: list[dict]) -> list[str]:
        print(tags, type(tags))
        if not tags:
            return []
        
        prew_tags = []
        for i in tags:
            prew_tags.append(i["label"])
        
        return prew_tags


    @staticmethod
    def parse_posts(result) -> list[dict]:
        """
        Парсит результат и формирует список постов в нужном формате.
        :param result: результат запроса
        :param columns: список колонок
        :return: список отформатированных постов
        """
        formatted_posts = {"postsAmount": len(result),
                        "posts": []}
        
        for post in result:
            post = {
                "postId": post.id,
                "contentType": post.type_content,
                "url": post.url,
                "options": {
                    "aspectRatio": post.aspect_ratio,
                    "objectPosition": post.object_position
                    }
            }
            formatted_posts["posts"].append(post)

        return formatted_posts


    @staticmethod
    def parse_post(post, cookie_user: False) -> dict:    
        data = {
                "post": {
                    "postId": post.id,
                    "name": post.post_name,
                    "description": post.description,
                    "link": post.link,
                    "media": {
                        "type": post.type_content,
                        "url": post.url,
                        "options": {
                            "aspectRatio": post.aspect_ratio,
                            "objectPosition": post.object_position
                                    }
                            },
                    "likeCount": post.users_liked.count(),
                    "commentsCount": 0,
                    "tags": Parser.unpacking_tags(post.tags_list),
                    "author": {
                        "firstName": post.author.first_name,
                        "lastName": post.author.last_name,
                        "userName": post.author.user_name,
                        "userId": post.author.id,
                        "avatar": post.author.avatar
                            }
                        },
                "user": {
                    "isLike": not isinstance(cookie_user, dict) and cookie_user in post.users_liked.all(),
                    "isOwner": not isinstance(cookie_user, dict) and cookie_user.id == post.author.id
                        }
                }

        return data


    @staticmethod
    def parse_dashboard(board):
        # Получение и форматирование даты создания доски
        created_at = board.created_at
        formatted_date = DateFormat(created_at.astimezone(get_current_timezone())).format('Y-m-d\TH:i:sP')
        
        all_posts = board.posts.all()
        
        # Получение и форматирование постов
        posts = Parser.parse_posts(all_posts)
        
        # Получение данных поста
        data = {
                "dashboardInfo": {
                    "dashboardId": board.id,
                    "dashboardName": board.name,
                    "postsAmount": board.posts.count(),
                    "dateOfCreation": formatted_date,
                },
                "author":   {
                            "firstName": board.author.first_name,
                            "lastName": board.author.last_name,
                            "userName": board.author.user_name,
                            "userId": board.author.id,
                            "avatar": board.author.avatar
                            },
                "postsAmount": posts['postsAmount'],
                "posts": posts['posts']
                }
        
        return data
    
    
    @staticmethod
    def parse_dashboards(favorites_board, boards, start, end):
        data = {
            "dashboardsAmount": len(boards),
            "favorites": None,
            "dashboards": []
            }
        
        # Обработка доски Избранное (если есть)
        if favorites_board:
            created_at = favorites_board.created_at
            formatted_date = DateFormat(created_at.astimezone(get_current_timezone())).format('Y-m-d\TH:i:sP')
            
            url = []
            for i in favorites_board.posts.all():
                url.append(i.url)
            
            data["favorites"] = {
                    "dashboardId": favorites_board.id,
                    "dashboardName": favorites_board.name,
                    "postsAmount": favorites_board.posts.count(),
                    "dateOfCreation": formatted_date,
                    "url": url
            }
        print(boards )
        # Обработка всех остальных досок (если есть)
        for board in boards[start:start+end:]:
            created_at = board.created_at
            formatted_date = DateFormat(created_at.astimezone(get_current_timezone())).format('Y-m-d\TH:i:sP')
            
            url = []
            for i in reversed(board.posts.all()):
                url.append(i.url)
            
            data["dashboards"].append({
                    "dashboardId": board.id,
                    "dashboardName": board.name,
                    "postsAmount": board.posts.count(),
                    "dateOfCreation": formatted_date,
                    "url": url
            })
        
        return data