from .authService import Authorization
from templates.response import templates as mess
from apps.comments.models import Comment
from apps.dashboards.models import Board
from apps.posts.models import Post
from apps.users.models import User


class DeletterObject:
    @staticmethod
    def del_object(request, model, targetID=None):
        cookie_user = Authorization.check_logining(request)
        
        if isinstance(cookie_user, dict):
            return mess[401]
        
        elif isinstance(model, User):
            cookie_user.delete()
        
        else:
            try:
                target = model.objects.get(id=targetID)
                
            except Exception as er:
                return mess[400]
        
            if cookie_user.id != target.author.id:
                return mess[403]
            
            target.delete()
            
        return mess[200]