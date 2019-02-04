from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# https://gist.github.com/haxoza/7921eaf966a16ffb95a0


class CustomUser(AbstractUser):
    # add additional fields in here

    def __str__(self):
        return self.email
