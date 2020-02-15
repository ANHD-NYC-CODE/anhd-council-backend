import sendgrid
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from users.models import CustomUser
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
    logger.info('Mail sent from {} to {} subject {}'.format(
        from_email, to_email, subject))
    return response


def send_hello_world_email():
    subject = "Council Portal is live!"
    content = "The app is running."
    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)


def send_new_user_email(user=None):
    to = user.email
    new_password = CustomUser.objects.make_random_password()
    user.set_password(new_password)
    user.save()
    subject = "Welcome to DAP Portal!"
    content = "<h3>Your new account has been created!</h3><p>Please reset your password at your earliest convenience at <a href='https://api.displacementalert.org/password_reset' target='_blank'>here</a></p><p><b>Username:</b> {}</p><p><b>Password:</b> {}</p><p>Thank you for signing up and please reach out to dapadmin@anhd.org if you have any questions or feedback.</p><p>- ANHD</p>".format(
        user.username, new_password)
    send_mail(to, subject, content)


def send_user_message_email(bug_report=None):
    subject = "DAP Portal - * New DAP message received."
    content = "<p>Hello!</p><p>We've received a new message from {}</p><p>Please <a href='https://api.displacementalert.org/admin/core/usermessage/{}/change' target='_blank'>visit this link</a> and update its status.</p><p>Have a nice day!</p><p>- DAP Portal Admin</p><hr><p><b>Details</b></p><p><b>From:</b> {}</p><p><b>Description:</b> {}</p><p><b>Status:</b> {}</p><p><b>Date created:</b> {}</p>".format(
        bug_report.from_email, bug_report.id, bug_report.from_email, bug_report.description, bug_report.status, bug_report.date_created)

    for user in us.CustomUser.objects.filter(is_staff=True):
        to = user.email
        send_mail(to, subject, content)


def send_new_user_request_email(user_request):
    subject = "DAP Portal - New user request received."
    content = "<p>Hello!</p><p>We've received a request for a user account from {}</p><p>Please <a href='https://api.displacementalert.org/admin/users/userrequest/{}/change' target='_blank'>visit this link</a> and approve the request to send them a registration email.</p><p>Have a nice day!</p><p>- DAP Portal Admin</p><hr><p><b>Details</b></p><p><b>Email:</b> {}</p><p><b>Username:</b> {}</p><p><b>Organization:</b> {}</p><p><b>Description:</b> {}</p><p><b>First name:</b> {}</p><p><b>Last name:</b> {}</p>".format(
        user_request.email, user_request.id, user_request.email, user_request.username, user_request.organization, user_request.description, user_request.first_name, user_request.last_name)

    for user in us.CustomUser.objects.filter(is_staff=True):
        to = user.email
        send_mail(to, subject, content)


def send_general_task_error_mail(error):
    subject = "DAP Portal - * Error * During Council Portal Update"
    content = "A task error occurred: \n\n{} \n\n Please visit the task manager to investigate.".format(
        error)

    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)


def send_update_error_mail(update, error):
    subject = "DAP Portal - * Error * During Council Portal Update"
    content = "Update {} for {} failed with error: \n\n{}".format(
        update.id, update.dataset, error)

    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)


def send_update_success_mail(update):
    subject = "{} update complete".format(update.dataset.name)
    content = "Table: {} \n\n Rows created: {} \n\n Rows updated: {} \n\n:)".format(
        update.dataset.name, update.rows_created, update.rows_updated)

    for admin in settings.ADMINS:
        to = admin[1]
        send_mail(to, subject, content)
