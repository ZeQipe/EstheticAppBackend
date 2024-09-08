from templates.response import templates as mess
from apps.users.models import User
from utils.cripting import decrypt_string as decript

class Authorization:
    @staticmethod
    def check_logining(request) -> bool:
        authKey = request.COOKIES.get("auth_key")
        if not authKey:
            return mess[401]
        
        cookie_id = decript(authKey)
        try:
            user = User.objects.get(id=cookie_id)
        
        except Exception as er:
            return mess[404]
        
        return user
    
    @staticmethod
    def set_key_in_coockies(response, coockies_key):
        response.set_cookie(
                            key='auth_key',
                            value=coockies_key,
                            httponly=True,
                            secure=False,
                            samesite='Lax',
                            max_age=604800  # срок жизни куки. число - 1 неделя в секундах
                            )
        return response
