from django.db import models
from templates.response import templates as mess
from utils.cripting import encrypt_string as encript
import re


class User(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    user_name = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=30, unique=True)
    password = models.TextField()
    avatar = models.TextField(unique=True, blank=True, null=True)
    tags_user = models.JSONField(default=list)
    subscribers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    
    
    @staticmethod
    def get_user_data_full(user) -> dict:
        user_data = {
                "userId": user.id,
                "subscribersAmount": user.subscribers.count(),
                "avatar": user.avatar,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "userName": user.user_name,
                }
        
        return user_data
    
    
    @staticmethod   
    def validate_data(data: dict) -> tuple:
        """
        Validate First and Last name, Username and Email adress
        :param user_data: list of user data
        :return: tuple - bool values of result and error message
        """
        regex_patterns = {
            'first_name': r'^.{2,15}$',
            'last_name': r'^.{0,15}$',
            'user_name': r'^.{5,20}$',
            'email': r'^[\w\.-]+@[\w\.-]+\.\w{2,30}$',
        }

        user_data = [data['first_name'], data['last_name'], data['user_name'], data['email']]
        field_names = ['first_name', 'last_name', 'user_name', 'email']

        if not isinstance(user_data[3], str) or "@" not in user_data[3] or not user_data[3].endswith((".com", ".ru", ".eu")):
            return mess[400]
        
        for i, field in enumerate(field_names):
            value = user_data[i]

            if field == "last_name" and (value is None or value == ''):
                continue
            
            if not isinstance(value, str):
                response = mess[400].copy()
                response['message'] = f'Bad request. {field} not correct'
                return False, response

            if not re.match(regex_patterns[field], value):
                response = mess[400].copy()
                response['message'] = f'Bad request. Invalid value for {field}'
                return False, response

        return True, "All data correct"
    
    
    @staticmethod
    def unique_data(userName, email_user) -> tuple:
        """
        Check unique data for user (ID, UserName and Email)
        :param user: list of user data
        :return: tuple - bool values of result and error message
        """
        if User.objects.filter(user_name=userName).exists():
            response = mess[400].copy()
            response['message'] = f'Bad request. The Username is busy'
            return False, response

        elif User.objects.filter(email=email_user).exists():
            response = mess[400].copy()
            response['message'] = f'Bad request. The email address is busy'
            return False, response

        else:
            return True, "All data correct"
        
    
    @staticmethod
    def get_data_in_request(data: dict):
        return {'first_name': data.get("firstName"),
                 'last_name': data.get("lastName"), 
                 'user_name' : data.get("userName"), 
                 'email' : data.get("email")}
