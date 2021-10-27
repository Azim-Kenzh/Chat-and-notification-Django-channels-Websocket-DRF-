from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    image = models.ImageField(upload_to='profile', blank=True, null=True)
    username = models.CharField(max_length=70)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.get_username()
