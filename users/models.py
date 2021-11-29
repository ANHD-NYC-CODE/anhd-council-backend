from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models, transaction
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import Group
from users.tokens import password_reset_token
# https://gist.github.com/haxoza/7921eaf966a16ffb95a0
import uuid
import hashlib


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(
            self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class CustomUser(AbstractUser):
    # add additional fields in here
    user_request = models.OneToOneField('UserRequest', db_column='user_request', db_constraint=False,
                                        on_delete=models.SET_NULL, null=True, blank=True)
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


class UserRequest(models.Model):
    email = models.TextField(unique=True, blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    organization = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    approved = models.BooleanField(blank=True, null=True, default=False)

    def approve(self):
        user = CustomUser.objects.create(email=self.email, username=self.username,
                                         first_name=self.first_name, last_name=self.last_name)

        user.user_request = self
        user.save()
        self.approved = True
        self.save()


class AccessRequest(models.Model):
    user = models.OneToOneField('CustomUser', db_column='customuser', db_constraint=False,
                                on_delete=models.SET_NULL, null=True, blank=True)

    # Should be either "member organization", "government", "personal"
    access_type = models.CharField(max_length=25, blank=True, null=True)
    organization_email = models.TextField(blank=True, null=True)
    organization = models.TextField(blank=True, null=True)
    position = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    date_created = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    approved = models.BooleanField(blank=True, null=True, default=False)

    def approve(self):
        if len(self.organization_email) > 0:
            # Verify the user
            verification_token = password_reset_token.make_token(self.user)
            from app.tasks import async_send_user_verification_email
            async_send_user_verification_email.delay(self.id, verification_token)
        else:
            self.add_user_to_trusted()

        self.approved = True
        self.save()

    def add_user_to_trusted(self):
        trusted_group = Group.objects.get(name='trusted')
        trusted_group.user_set.add(self.user)
        from app.tasks import async_send_new_access_email
        async_send_new_access_email.delay(self.user.id)


class UserBookmarkedProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=255)
    bbl = models.CharField(blank=True, max_length=10, unique=True)


class DistrictDashboard(models.Model):
    query_string = models.TextField(blank=True, null=True)
    query_string_hash_digest = models.CharField(blank=True, max_length=64, unique=True)
    result_hash_digest = models.CharField(blank=True, max_length=64)

    def save(self, *args, **kwargs):
        encoded = str(self.query_string).encode("utf-8")
        encoded_hash = hashlib.sha256(encoded)
        self.query_string_hash_digest = encoded_hash.digest()
        super(DistrictDashboard, self).save(*args, **kwargs)


class UserDistrictDashboard(models.Model):
    NEVER = 'N'
    DAILY = 'D'
    WEEKLY = 'W'
    MONTHLY = 'M'

    FREQUENCY_CHOICES = (
        (NEVER, 'Never'),
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=255, unique=True)
    notification_frequency = models.CharField(max_length=8, choices=FREQUENCY_CHOICES, default=NEVER)
    last_notified_hash = models.CharField(blank=True, max_length=64)
    district_dashboard_view = models.ForeignKey(DistrictDashboard, on_delete=models.CASCADE)


class CustomSearch(models.Model):
    frontend_url = models.TextField(blank=True, null=True)
    query_string = models.TextField(blank=True, null=True)
    query_string_hash_digest = models.CharField(blank=True, max_length=64, unique=True)
    result_hash_digest = models.CharField(blank=True, max_length=64)

    def save(self, *args, **kwargs):
        encoded = str(self.query_string).encode('utf-8')
        encoded_hash = hashlib.sha256(encoded).hexdigest()
        self.query_string_hash_digest = encoded_hash
        super(CustomSearch, self).save(*args, **kwargs)


class UserCustomSearch(models.Model):
    NEVER = 'N'
    DAILY = 'D'
    WEEKLY = 'W'
    MONTHLY = 'M'

    FREQUENCY_CHOICES = (
        (NEVER, 'Never'),
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=255, unique=True)
    notification_frequency = models.CharField(max_length=8, choices=FREQUENCY_CHOICES, default=NEVER)
    last_notified_hash = models.CharField(blank=True, max_length=64)
    last_notified_date = models.DateTimeField(default=timezone.now)
    last_number_of_results = models.IntegerField(default=0, blank=True)
    custom_search_view = models.ForeignKey(CustomSearch, on_delete=models.CASCADE)


@receiver(models.signals.post_save, sender=AccessRequest)
def send_new_user_access_request_email_on_save(sender, instance, created, **kwargs):
    from app.tasks import async_send_new_user_access_email

    def on_commit():
        if created == True:
            async_send_new_user_access_email.delay(instance.id)

    transaction.on_commit(lambda: on_commit())


# @receiver(models.signals.post_save, sender=CustomUser)
# def create_profile_on_save(sender, instance, created, **kwargs):

#     def on_commit():
#         if created == True:
#             UserProfile.objects.create(user=instance)

#     transaction.on_commit(lambda: on_commit())


# @receiver(models.signals.post_save, sender=CustomUser)
# def send_email_on_save(sender, instance, created, **kwargs):
#     from app.tasks import async_send_new_user_email

#     def on_commit():
#         if created == True:
#             async_send_new_user_email.delay(instance.id)

#     transaction.on_commit(lambda: on_commit())


# @receiver(models.signals.post_save, sender=UserRequest)
# def send_new_user_request_email_on_save(sender, instance, created, **kwargs):
#     from app.tasks import async_send_new_user_request_email

#     def on_commit():
#         if created == True:
#             async_send_new_user_request_email.delay(instance.id)

#     transaction.on_commit(lambda: on_commit())
