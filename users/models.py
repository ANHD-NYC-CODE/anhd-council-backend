from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# https://gist.github.com/haxoza/7921eaf966a16ffb95a0


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_superuser = user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    # add additional fields in here
    objects = UserManager()

    def __str__(self):
        return self.email
