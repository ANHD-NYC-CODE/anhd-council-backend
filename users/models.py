from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models, transaction
from django.dispatch import receiver
# https://gist.github.com/haxoza/7921eaf966a16ffb95a0


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class CustomUser(AbstractUser):
    # add additional fields in here
    objects = CustomUserManager()

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


@receiver(models.signals.post_save, sender=CustomUser)
def send_email_on_save(sender, instance, created, **kwargs):
    from app.tasks import async_send_new_user_email

    def on_commit():
        if created == True:
            async_send_new_user_email.delay(instance.id)

    transaction.on_commit(lambda: on_commit())
