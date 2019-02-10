import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import *
import os
import logging

logger = logging.getLogger('app')


def send_mail(to_email, subject, content_string):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY', ''))
    from_email = Email(os.environ.get('EMAIL_USER', ''))
    to_email = Email(to_email)
    content = Content("text/plain", content_string)
    if settings.DEBUG:
        subject = "(DEVELOPMENT) " + subject
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    logger.info('Mail sent from {} to {} subject {}'.format(from_email, to_email, subject))
    return response


def send_hello_world_email():
    subject = "Council Portal is live!"
    content = "The app is running."
    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)


def send_update_error_mail(error):
    subject = "Council Portal Admin Update Error!"
    content = "An update failed with error: \n\n{}".format(error)

    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)


def send_update_success_mail(update):
    subject = "{} update complete".format(update.dataset.name)
    content = "!@#$Table: {} \n\n Rows created: {} \n\n Rows updated: {} \n\n:)".format(
        update.dataset.name, update.rows_created, update.rows_updated)

    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)
