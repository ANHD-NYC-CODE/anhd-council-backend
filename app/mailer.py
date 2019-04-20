import sendgrid
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email

import os
import logging
from users import models as us
logger = logging.getLogger('app')


def send_mail(to_email, subject, content_string):
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY', ''))
    from_email = os.environ.get('EMAIL_USER', '')
    if settings.DEBUG:
        subject = "(DEVELOPMENT) " + subject
    message = Mail(from_email=from_email,
                   to_emails=to_email,
                   subject=subject,
                   html_content=content_string)
    response = sg.send(message)
    logger.info('Mail sent from {} to {} subject {}'.format(from_email, to_email, subject))
    return response


def send_hello_world_email():
    subject = "Council Portal is live!"
    content = "The app is running."
    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)


def send_new_user_email(email=None, username=None, password=None):
    if not email or not username or not password:
        raise Exception("Missing email, username or password when sending email! {}-{}".format(email, username))
    to = email
    subject = "Welcome to DAP Portal!"
    content = "<h3>Your new account has been created!</h3><p><b>Username:</b> {}</p><p><b>Password:</b> {}</p><p>Please reset your password at your earliest convenience at <a href='https://api.displacementalert.org/password_reset' target='_blank'>here</a></p><p>Thank you for signing up and please reach out to anhd.tech@gmail.com if you have any questions or feedback.</p><p>- ANHD</p>".format(
        username, password)
    send_mail(to, subject, content)


def send_general_task_error_mail(error):
    subject = "* Error * During Council Portal Update"
    content = "A task error occurred: \n\n{} \n\n Please visit the task manager to investigate.".format(error)

    for user in us.CustomUser.objects.filter(is_staff=True):
        to = user.email
        send_mail(to, subject, content)


def send_update_error_mail(update, error):
    subject = "* Error * During Council Portal Update"
    content = "Update {} for {} failed with error: \n\n{}".format(update.id, update.dataset, error)

    for user in us.CustomUser.objects.filter(is_staff=True):
        to = user.email
        send_mail(to, subject, content)


def send_update_success_mail(update):
    subject = "{} update complete".format(update.dataset.name)
    content = "Table: {} \n\n Rows created: {} \n\n Rows updated: {} \n\n:)".format(
        update.dataset.name, update.rows_created, update.rows_updated)

    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)
