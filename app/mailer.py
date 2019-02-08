import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import *

import logging

logger = logging.getLogger('app')


def send_mail(to_email, subject, content_string):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    from_email = Email(settings.EMAIL_HOST_USER)
    to_email = Email(to_email)
    content = Content("text/plain", content_string)

    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    logger.debug('Sending mail from {} to {} subject {}'.format(from_email, to_email, subject))
    return response


def send_update_error_mail(error):
    subject = "DAP Council Admin Update Error!"
    content = "An update failed with error: \n\n{}".format(error)

    if len(settings.ADMINS) > 1:
        for admin in settings.ADMINS:
            to = admin[1]
            send_mail(to, subject, content)

    else:
        to = settings.ADMINS[1]
        send_mail(to, subject, content)
