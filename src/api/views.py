from templates.response import templates as mess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from service.authService import Authorization
from service.deleteService import DeletterObject as deletter
from apps.users.controller import *
from apps.posts.controller import *
from apps.dashboards.controller import *
from service.generate import start


# Методы работы с пользователем
@csrf_exempt
def publicProfile(request, userID):
    if request.method == "GET":                                         # Get Public profile by userID
        response = get_user_profile(request, userID)

    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))


@csrf_exempt
def privateProfile(request):
    if request.method == "GET":                                         # Get Private profile by cookie
        response = get_user_profile(request) 
        
    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))

@csrf_exempt
@require_http_methods(["POST"])
def usersRegistration(request): 
    if request.method == "POST":                                        # Create user profile
        response = registration_users(request)
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))


@csrf_exempt
@require_http_methods(["POST"])
def usersLogin(request): 
    if request.method == "POST":                                        # LogIn user
        response = login(request)

        if response.get("userId", False):
            cook_keys = encrypt_string(response.get("userId"))
            response = JsonResponse(response, status=200)
            response = Authorization.set_key_in_coockies(response, cook_keys)

        else:
            response = JsonResponse(response, status=response.get("status"))

    else:
        response = JsonResponse(mess[405], status=405)

    return response


@csrf_exempt
@require_http_methods(["POST"])
def usersLogout(request):
    if request.method == "POST":                                        # LogOut user
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
def usersCreatedPosts(request, userID):
    if request.method == "GET":                                         # Get created users posts
        response = user_created_post_list(request, userID)

    else:
        response = mess[405]

    return JsonResponse(response, status=response.get("status", 200))


@csrf_exempt
def users(request):
    if request.method == "DELETE":                                      # Delete object
        response = deletter.del_object(request, User)

    elif request.method == "PUT":
        response = edit_user_profile(request)                           # Edit User Profile
    
    else:
        response = mess[405]

    return JsonResponse(response, status=response.get("status", 200))
     

# ---------------------------- ---------------------------- ----------------------------
# Методы постов
@csrf_exempt
def posts(request): 
    if request.method == "GET":                                         # Get all posts
        response = search_posts(request)
    
    elif request.method == "POST":                                      # Create post
        response = create_post(request)

    else:
        response = mess[405]
    
    return JsonResponse(response, status=response.get("status", 200))


@csrf_exempt
def posts_param(request, postID): 
    if request.method == "GET":                                         # Get post by postID
        response = get_post_by_id(request, postID)
    
    elif request.method == "PUT":                                       # Changing post information by postID
        response = edit_post_by_id(request, postID)
    
    elif request.method == "DELETE":                                    # Delete post
        response = deletter.del_object(request, Post, postID)

    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))

@csrf_exempt
def postsToggleLike(request, postID): 
    if request.method == "PUT":                                         # set like post
        response = toggle_like(request, postID)
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))


# ---------------------------- ---------------------------- ----------------------------
# Методы Досок
@csrf_exempt
def dashboards(request): 
    if request.method == "GET":                                           # Get compact board list 
        response = get_boards_user_by_cookie(request)

    elif request.method == "POST":                                        # Create board
        response = create_dashboards(request)

    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))


@csrf_exempt
def dashboards_param(request, boardID): 
    if request.method == "GET":                                         # Get all information by board
        response = get_dashboard_detail(request, boardID)

    elif request.method == "POST":                                      # Add post in board by boardID
        response = add_post_in_board(request, boardID)
    
    elif request.method == "DELETE":                                    # Delete dashboard
        response = deletter.del_object(request, Board, boardID)

    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))


@csrf_exempt
def dashboards_list(request, userID): 
    if request.method == "GET":                                         # Get list information by boards
        response = get_user_dashboards(request, userID)
        
    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))
        


@csrf_exempt
def dashboardsDeletePosts(request, boardID): 
    if request.method == "DELETE":                                      # Delete post in board
        response = remove_posts_in_board(request, boardID)
    
    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))


@csrf_exempt
def post_in_boards(request):
    if request.method == "GET":
        response = check_post_in_boards(request)

    else:
        response = mess[405]
        
    return JsonResponse(response, status=response.get("status", 200))


# ---------------------------- ---------------------------- ----------------------------
# Прочие методы
@csrf_exempt
def check_auth(request): 
    if request.method == "GET":                                         # Check authorization from user
        if isinstance(Authorization.check_logining(request), dict):
            mess = {"isAuth": False}
            response = JsonResponse(mess, status=401)
        else:
            mess = {"isAuth": True}
            response = JsonResponse(mess, status=200)
    else:
        response = JsonResponse(mess[405], status=405)
        
    return response

# ---------------------------- ---------------------------- ----------------------------
# Метод для администратора
@csrf_exempt
def admin(request):
    if request.method == "GET":
        try: 
            response = start(request)

        except Exception as er:
            response = mess[400].copy()
            response["error"] = f"{er}"
            print(response)

    else:
        response = mess[405]

    return JsonResponse(response, status=response.get("status", 200))