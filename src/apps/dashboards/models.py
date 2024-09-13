from django.db import models
from apps.users.models import User
from apps.posts.models import Post
from django.db.models import Q
from templates.response import templates as mess
from utils.cripting import generate_string
from django.utils import timezone
import json


class Board(models.Model):
    id = models.CharField(max_length=45, primary_key=True)
    name = models.CharField(max_length=35)
    posts = models.ManyToManyField(Post, related_name='boards', blank=True)
    author = models.ForeignKey(User, related_name='boards', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    @staticmethod
    def check_board_name(user, name) -> bool:
        """
        Функция проверяет, существует ли доска с указанным именем среди досок пользователя.
        
        :param user: объект пользователя, которому принадлежат доски
        :param name: имя доски, которое нужно проверить
        :return: bool
        """
        # Если список id пустой, возвращаем False
        if not user.boards.all():
            return False
        
        # Ищем доски пользователя по списку id и имени доски
        if Board.objects.filter(
            Q(author=user) & Q(name=name)
        ).exists():
            return True
        
        # Если совпадений нет
        return False
    

    @staticmethod
    def create_board(boardName, author_model):
        id_board = generate_string(35, Board)
        
        board = Board.objects.create(
                            id=id_board,
                            name=boardName,
                            author=author_model
                            )
        
        return board