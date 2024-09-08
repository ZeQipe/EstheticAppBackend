from django.urls import path
from . import views

urlpatterns = [
    # POSTS
    path("posts", views.posts, name="posts"),
    path("posts/toggle-like/<str:postID>", views.postsToggleLike, name="postsToggleLike"),
    path("posts/<str:postID>", views.posts_param, name="posts_param"),

    # USERS
    path("users/registration", views.usersRegistration, name="user_registration"),
    path("users/login", views.usersLogin, name="user_login"),
    path("users/logout", views.usersLogout, name="user_logout"),
    path("users/<str:userID>/created-posts", views.usersCreatedPosts, name="userCreatedPosts"),
    path("users/<str:userID>/dashboards", views.usersDashboards, name="usersDashboards"),
    path("users/<str:profileID>", views.users_param, name="users_param"),
    
    # DASHBOARDS
    path("dashboards", views.dashboards, name='dashboards'),
    path("dashboards/favorites", views.add_in_favorites, name="add_in_favorites"),
    path("dashboards/delete-posts/<str:boardID>", views.dashboardsDeletePosts, name="dashboardsDeletePosts"),
    path("dashboards/<str:boadID>", views.dashboards_param, name="dashboards_param"),
    path("dashboards/<str:userID>/list", views.dashboards_list, name="dashboards_param"),
    # OTHER
    path("auth/check", views.check_auth, name="check_auth")
]