from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models, transaction
from django.dispatch import receiver

# https://gist.github.com/haxoza/7921eaf966a16ffb95a0


class CustomUser(AbstractUser):
    # add additional fields in here

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField('CustomUser', db_column='user', db_constraint=False,
                                on_delete=models.CASCADE, null=True, blank=True)
    council = models.ForeignKey('datasets.council', on_delete=models.SET_NULL, null=True,
                                db_column='council', db_constraint=False)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=CustomUser)
def create_profile_on_save(sender, instance, created, **kwargs):

    def on_commit():
        if created == True:
            UserProfile.objects.create(user=instance)

    transaction.on_commit(lambda: on_commit())
