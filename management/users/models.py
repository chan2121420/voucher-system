from django.db import models
from django.contrib.auth.models import AbstractUser

choices = (
    ('Staff', 'staff'),
    ('Manager', 'manager'),
    ('Administrator', 'administrator')
)
class User(AbstractUser):

    username = models.CharField(max_length=32, unique=True)
    image = models.ImageField(upload_to='profiles', default='profiles/user.png')
    position = models.CharField(choices = choices, default='staff', max_length=20)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username