from django.urls import path
from . import views

urlpatterns = [
    # POSTS
    path("posts", views.posts, name="posts"),
    path("posts/toggle-like/<str:postID>", views.postsToggleLike, name="postsToggleLike"),
    path("posts/<str:postID>", views.posts_param, name="posts_param"),

    # USERS
    path("users", views.users, name="users"),
    path("users/registration", views.usersRegistration, name="user_registration"),
    path("users/login", views.usersLogin, name="user_login"),
    path("users/logout", views.usersLogout, name="user_logout"),
    path("users/private-profile", views.privateProfile, name="privateProfile"),
    path("users/public-profile/<str:userID>", views.publicProfile, name="publicProfile"),
    path("users/<str:userID>/created-posts", views.usersCreatedPosts, name="userCreatedPosts"),
    path("users/<str:profileID>", views.users_param, name="users_param"),
    
    # DASHBOARDS
    path("dashboards", views.dashboards, name='dashboards'),
    path("dashboards/check-posts", views.post_in_boards, name="post_in_boards"),
    path("dashboards/favorites", views.add_in_favorites, name="add_in_favorites"),
    path("dashboards/delete-posts/<str:boardID>", views.dashboardsDeletePosts, name="dashboardsDeletePosts"),
    path("dashboards/<str:boardID>", views.dashboards_param, name="dashboards_param"),
    path("dashboards/<str:userID>/list", views.dashboards_list, name="dashboards_param"),
    
    # Other
    path("auth/check", views.check_auth, name="check_auth")
]