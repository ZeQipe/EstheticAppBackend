from templates.response import templates as mess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from service.authService import Authorization
from apps.users.controller import *
from apps.posts.controller import *
from apps.dashboards.controller import *


# Методы работы с пользователем
@csrf_exempt
def users_param(request, profileID): # Работает
    if request.method == "GET":
        response = get_user_profile(request, profileID)
    
    elif request.method == "PUT":
        response = edit_user_profile(request, profileID)
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))


@csrf_exempt
@require_http_methods(["POST"])
def usersRegistration(request): # Работает
    if request.method == "POST":
        response = registration_users(request)
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))


@csrf_exempt
@require_http_methods(["POST"])
def usersLogin(request): # Работает
    if request.method == "POST":
        response = login(request)

        if response.get("userId", False):
            cook_keys = response.get("userId")
            response = JsonResponse(response, status=200)
            response = Authorization.set_key_in_coockies(response, cook_keys)

        else:
            response = JsonResponse(response, status=response.get("status"))

    else:
        response = JsonResponse(mess[405])

    return response


@csrf_exempt
@require_http_methods(["POST"])
def usersLogout(request): # Работает
    if request.method == "POST":
        user = Authorization.check_logining(request)
        if isinstance(user, dict):
            response = JsonResponse(mess[401], status=401)
        else:
            response = JsonResponse(mess[200], status=200)
            response.delete_cookie("auth_key")
        
    else:
        response = JsonResponse(mess[405], status=405)

    return response


@csrf_exempt
def usersCreatedPosts(request): # не доделано, не проверено
    if request.method == "GET":
        response = mess[501]

    else:
        response = mess[405]

    return JsonResponse(response, status=mess.get("status", 200))


@csrf_exempt
def usersDashboards(request): # не доделано, не проверено
    if request.method == "GET":
        response = mess[501]
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))


# Методы постов
@csrf_exempt
def posts(request): # Работает
    if request.method == "GET":
        response = search_posts(request)
    
    elif request.method == "POST":
        response = create_post(request)

    else:
        response = mess[405]
    
    return JsonResponse(response, status=mess.get("status", 200))


@csrf_exempt
def posts_param(request, postID): # не доделано, сделанные - работают
    if request.method == "GET":
        response = get_post_by_id(request, postID)
    
    elif request.method == "PUT":
        response = edit_post_by_id(request, postID)
    
    elif request.method == "DELETE":
        response = mess[501]
    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))

@csrf_exempt
def postsToggleLike(request, postsID): # не доделано, не проверено
    if request.method == "PUT":
        pass
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))


# Методы Досок
@csrf_exempt
@require_http_methods(["POST"])
def dashboards(request): # не проверено
    if request.method == "POST":
        response = create_dashboards(request)

    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))


@csrf_exempt
@require_http_methods(["POST"])
def add_in_favorites(request):
    if request.method == "POST":
        response = add_post_in_board(request, "favorites")

    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))


@csrf_exempt
@require_http_methods(["POST"])
def dashboards_param(request, boardID): # не доделано, не проверено
    if request.method == "GET":
        response = get_dashboard_detail(request, boardID)

    elif request.method == "POST":
        response = add_post_in_board(request, boardID)
    
    elif request.method == "DELETE":
        return mess[501]

    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))


@csrf_exempt
def dashboards_list(request, userID): # не доделано, не проверено
    if request.method == "GET":
        response = get_user_dashboards(request, userID)
        
    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))
        


@csrf_exempt
def dashboardsDeletePosts(request, boardID): # не доделано, не проверено
    if request.method == "DELETE":
        pass
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))


# Прочие методы
@csrf_exempt
def check_auth(request): # не доделано, не проверено
    if request.method == "GET":
        response = {
            "status": 200,
            "isAuth": not isinstance(Authorization.check_logining(request), dict)
        }
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=mess.get("status", 200))