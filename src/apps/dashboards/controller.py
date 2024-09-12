from .models import Board
from apps.posts.models import Post
from apps.users.models import User
from templates.response import templates as mess
from service.authService import Authorization
from utils.separament import Parser as pars
from utils.cripting import *
import json


def create_dashboards(request):
    # Поиск автора доски
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        return mess[401]
    
    # Извлечение данных доски из формы
    try:
        data = json.loads(request.body)
        boardName = data.get("dashboardName")
    except Exception as er:
        return mess[400]
        
    result = Board.check_board_name(cookie_user, boardName)
    if result:
        response = mess[400].copy()
        response['message'] = "It's dashboard name is busy."
        return response
    
    # Создание доски
    try:
        Board.create_board(boardName, cookie_user)
    except Exception as er:
        print(er)
        return mess[500]
    
    return mess[200]
    

def add_post_in_board(request, board_id):
    # Проверка авторизации пользователя
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        return mess[401]
    
    # Поиск доски в базе данных
    if board_id == "favorites":
        try:
            board = Board.objects.get(author_id=cookie_user.id, name="Избранное")
        except Exception as er:
            try:
                board = Board.create_board("Избранное", cookie_user)
            except Exception as er:
                return mess[500]
    else:
        try:
            board = Board.objects.get(id=board_id, author=cookie_user)
        except Exception as er:
            return mess[404]
    
    # Поиск поста в базе данных
    data = json.loads(request.body)
    try:
        post = Post.objects.get(id=data.get('postsId', ''))
    except Exception as er:
        return mess[404]
    
    if post in board.posts.all():
        response = mess[400].copy()
        response['message'] = f"This post has already been added"
        return response
    
    # Добавления поста в доску
    board.posts.add(post)
    
    return mess[200]
        
    
def get_dashboard_detail(request, id_board):
    # Поиск доски в базе данных
    try:
        board = Board.objects.get(id=id_board)
    except Exception as er:
        return mess[404]
    
    response = pars.parse_dashboard(board)
    
    return response


def get_user_dashboards(request, user_id):
    # Получаем query параметры offset и limit из запроса и пытаемся привести их к int.
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0

    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20
    
    # Поиск пользователя в базе данных
    try:
        user = User.objects.get(id=user_id)
    except Exception as er:
        return mess[404]
    
    # Получение 
    favorites_board = user.boards.filter(name="Избранное").first()

    # Получение всех досок пользователя, кроме "Избранное"
    boards = user.boards.exclude(name="Избранное")

    response = pars.parse_dashboards(favorites_board, boards, offset, limit)
        
    return response


def user_created_post_list(request, userID):
    user = User.objects.get(id=userID)
    
    if isinstance(user, dict):
        response = mess[404].copy()
        response['message'] = "Not found User"
        return response
    
    posts_user = user.posts.all()

    response = pars.parse_posts(posts_user)
    
    return response


def remove_posts_in_board(request, boardID):
    cookie_user = Authorization.check_logining(request)
    
    if isinstance(cookie_user, dict):
        return mess[401]
    
    try:
        postID = json.loads(request.body).get("postsId")
        post = Post.objects.get(id=postID)
        
        board = Board.objects.get(id=boardID)
    except Exception as er:
        return mess[404]
    
    if not board.posts.filter(id=post.id).exists():
        return mess[404]
    
    board.posts.remove()
    
    return mess[200]