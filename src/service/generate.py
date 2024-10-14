from apps.users.models import User
from apps.posts.models import Post
from apps.dashboards.models import Board
from django.http.multipartparser import MultiPartParser
from templates.response import templates as mess
from pathlib import Path
from utils.cripting import generate_string, encrypt_string
from django.conf import settings
from django.http import HttpRequest
import random
import os
import shutil


tags_list = ["AI", "Deep Learning", "Neural Networks", "Data Science", "Python", "Statistics",
             "Web Development", "JavaScript", "HTML", "CSS", "Blockchain", "Cryptocurrency", 
             "Decentralization", "Cloud Computing", "AWS", "Azure", "Google Cloud", 
             "Mobile Development", "iOS", "Android", "DevOps", "CI/CD", "Automation", 
             "Game Development", "Unity", "Unreal Engine", "Cybersecurity", "Penetration Testing", 
             "Encryption"]

board_names = [
    "Tech Innovations", "Digital Marketing", "Travel Adventures", "Photography Portfolio", 
    "Personal Finance", "Startup Ideas", "Book Reviews", "Gaming Strategies", "Design Inspirations", 
    "Fashion Trends", "Fitness Challenges", "Creative Writing", "Movie Reviews", "Art Gallery", 
    "Gardening Tips", "Coding Projects", "Social Media Marketing", "Food and Drinks", "Life Hacks", 
    "Business Plans", "Career Growth", "Education Resources"
]

# Функция, возвращающая случайное имя доски
def get_random_board_name():
    return random.choice(board_names)


# Функция для копирования и переименования файлов
def copy_and_rename_file(src_folder, dest_folder, old_name, new_name):
    src_file = os.path.join(src_folder, old_name)

    # Проверка, существует ли исходный файл
    if not os.path.exists(src_file):
        print(f"Файл {old_name} не найден в папке {src_folder}")
        return

    # Создаем папку, если её нет
    os.makedirs(dest_folder, exist_ok=True)
    
    dest_file = os.path.join(dest_folder, new_name)
    
    shutil.copy(src_file, dest_file)


# Генерация постов
def generate_posts():
    posts = []

    listRatio = ["9/16", "2/3", "3/4", "4/5", "1/1"]

    for i in range(80):
        post = {
            "postName": f"Post Title {i+1}",
            "description": f"Description for post {i+1}",
            "aspectRatio": random.choice(listRatio),
            "tags": random.sample(tags_list, random.randint(1, 3)),
            "link": random.choice([f"https://example.com/post{i+1}", None])
        }
        posts.append(post)

    return posts


# Генерация пользователей
def generate_users():
    lastName = ["Johnson", "Smith", "Davis", "Anderson", "Brown", "Miller", "Wilson", 
                "Martinez", "Taylor", "Moore", "Clark", "Lewis", "Robinson", "Walker", 
                "Young", "Allen", "King", "Scott", "Green", "Baker", "Adams", "Nelson", 
                "Carter", "Mitchell", "Perez", "Turner", "Phillips", "Campbell", "Parker", 
                "Evans"]

    firstName = ["Alexander", "Olivia", "Benjamin", "Emma", "William", "Sophia", "James", 
                 "Isabella", "Henry", "Mia", "Michael", "Amelia", "Daniel", "Charlotte", 
                 "Ethan", "Harper", "Matthew", "Evelyn", "Andrew", "Lily", "Christ", 
                 "Grace", "David", "Aria", "Joseph", "Chloe", "Samuel", "Nora", "Lucas", 
                 "Zoe"]

    users = []

    for i in range(20):
        FN = random.choice(firstName)
        LN = random.choice(lastName)

        user = {
            "first_name": FN,
            "last_name": LN,
            "user_name": f"{FN}{LN}{generate_string(3, False)}",
            "email": f"{FN.lower()}{generate_string(5, False)}@mail.com",
            "tags": random.sample(tags_list, random.randint(1, 3))
        }
        users.append(user)

    return users


def parse_result(users, posts):
    result = {}
    for i in users:
        data = {"email": i.email,
                "pass": "example123"}
        result["id"] =  data

    return result



# ================= ================ =============== ============== ================= ================

# Основная функция запуска
def start(request: HttpRequest):
    request_data = MultiPartParser(request.META, request, request.upload_handlers).parse()
    key = request_data[0].get("key")
    if key != "True start":
        return mess[401]
    
    list_users, list_posts, list_boards = [], [], []

    path_images = Path(settings.BASE_DIR, 'media', 'testImages')
    images = os.listdir(path_images)
    posts = generate_posts()
    users = generate_users()

    password = encrypt_string("example123")

    print("----------1---------")

    # Создание пользователей
    new_path_images = Path(settings.BASE_DIR, 'media', 'avatars')
    for user_data in users:
        user_id = generate_string(30, User)

        avatar_url = None
        if random.choice([True, False]):
            file_name = f"{user_id}{generate_string(3, False)}.jpg"
            relative_path = f"{settings.MEDIA_URL}avatar/{file_name}"
            avatar_url = request.build_absolute_uri(relative_path)
            copy_and_rename_file(path_images, new_path_images, random.choice(images), file_name)

        user = User.objects.create(
            id=user_id,
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            user_name=user_data["user_name"],
            email=user_data["email"],
            password=password,
            avatar=avatar_url,
            tags_user=user_data["tags"]
        )

        
        list_users.append(user)

    
    print("----------2---------")

    # Создание постов
    new_path_images = Path(settings.BASE_DIR, 'media', 'img')

    for post_data in posts:
        author = random.choice(list_users)
        if author.posts.count() >= 10:
            continue

        post_id = generate_string(35, Post)
        file_name = f"я{generate_string(3, False)}.jpg"
        relative_path = f"{settings.MEDIA_URL}img/{file_name}"
        image_url = request.build_absolute_uri(relative_path)
        copy_and_rename_file(path_images, new_path_images, random.choice(images), file_name)

        post = Post.objects.create(
            id=post_id,
            author=author,
            post_name=post_data["postName"],
            description=post_data["description"],
            type_content="img",
            url=image_url,
            tags_list=post_data["tags"],
            aspect_ratio=post_data["aspectRatio"],
            link=post_data["link"]
        )

        
        list_posts.append(post)

    print("----------3---------")

    # Создание досок
    for user in list_users:
        for i in range(random.randint(9, 12)):
            board_name = f"{random.choice(board_names)} {random.randint(100, 999)}"
            board = Board.objects.create(
                id=generate_string(35, Board),
                name=board_name,
                author=user
            )
            list_boards.append(board)

    print("----------4---------")

    # Добавление постов в доски
    for board in list_boards:
        board_posts = random.sample(list_posts, random.randint(15, 20))
        board.posts.add(*board_posts)

    print("----------5---------")

    # Возвращаем результат
    return parse_result(list_users, list_posts)

    


