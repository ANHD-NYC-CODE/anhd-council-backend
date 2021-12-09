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
    reset_password_link = user.get_password_reset_url()
    subject = "Welcome to DAP Portal!"
    content = ''.join((
        '<h3>Your new account has been created!</h3>',
        f"<p>Please reset your password at your earliest convenience at <a href='{reset_password_link}' target='_blank'>here</a></p>",
        f"<p><b>Username:</b> {user.username}</p>",
        f"<p><b>Temporary Password:</b> {new_password}</p>",
        "<p>Thank you for signing up and please reach out to dapadmin@anhd.org if you have any questions or feedback.</p>",
        "<p>- ANHD</p>"
    ))
    send_mail(to, subject, content)


def send_new_access_email(user=None):
    to = user.email
    subject = "DAP Portal - Data access granted!"

    content = ''.join((
        '<h3>Your new account has been granted access!</h3>',
        "<p>Your request to access housing court and foreclosures data has been approved! You will now see these changes reflected when you <a href='https://portal.displacementalert.org' target='_blank'>log in to DAP Portal</a>.</p>",
        '<p>This email was sent from the ANHD DAP Portal. If you have questions, email dapadmin@anhd.org.</p>'
    ))

    send_mail(to, subject, content)


def send_user_verification_email(access_request=None, verification_token=None):
    root_url = 'http://localhost:8000/' if settings.DEBUG else 'https://api.displacementalert.org/'
    to = access_request.organization_email
    subject = "DAP Portal - Please verify your new email"
    content = ''.join((
        '<h3>Your account has been granted access pending verification</h3>',
        f"<p>Your request to access housing court and foreclosures data has been approved! Please <a href='https://api.displacementalert.org/users/verify/{access_request.user.username}/{verification_token}/' target='_blank'>click this link</a> to verify that you submitted this request and to access the data.</p>",
        '<iframe name="dummyframe" id="dummyframe" style="display: none;"></iframe>',
        f'<form method="post" action="{root_url}user-messages/" class="inline" target="dummyframe" onsubmit="alert(\'Thanks, your report has been noted.\');">',
        f'<input type="hidden" name="from_email" value="{access_request.organization_email}">',
        '<input type="hidden" name="description" value="Auto: I was asked to verify an email unprompted.">',
        '<button type="submit" name="submit_param" value="submit_value" class="link-button">If this wasn’t you, click here to let us know.</button>',
        '</form>',
        '<p>This email was sent from the ANHD DAP Portal. If you have questions, email dapadmin@anhd.org.</p>'
    ))

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
    content = "<p>Hello!</p><p>We've received a request for a user account from {}</p><p>Please <a href='https://api.displacementalert.org/admin/users/userrequest/{}/change' target='_blank'>visit this link</a> and approve the request to send them a registration email.</p><p>Have a nice day!</p><p>- DAP Portal Admin</p><hr><p><b>Details</b></p><p><b>Email:</b> {}</p><p><b>Username:</b> {}</p><p><b>Organization:</b> {}</p><p><b>Position:</b> {}</p><p><b>Description:</b> {}</p><p><b>First name:</b> {}</p><p><b>Last name:</b> {}</p>".format(
        user_request.email, user_request.id, user_request.email, user_request.username, user_request.organization, user_request.description, user_request.long_description, user_request.first_name, user_request.last_name)

    for user in us.CustomUser.objects.filter(is_staff=True):
        to = user.email
        send_mail(to, subject, content)


def send_new_user_access_request_email(access_request):
    root_url = 'http://localhost:8000/' if settings.DEBUG else 'https://api.displacementalert.org/'
    subject = f"DAP Portal - New user access request received for {access_request.user.username}"
    content = ''.join((
        '<p>Hello!</p>',
        f"<p>We've received a request for a access from {access_request.user.email}</p>",
        f"<p>Please <a href='{root_url}admin/users/accessrequest/{access_request.id}/change' target='_blank'>visit this link</a> and approve the request to send them a registration email.</p>",
        '<p>Have a nice day!</p>',
        '<p>- DAP Portal Admin</p>',
        '<hr><p><b>Details</b></p>',
        f'<p><b>Email:</b> {access_request.user.email}</p>',
        f'<p><b>Organizational Email:</b> {access_request.organization_email}</p>',
        f'<p><b>Username:</b> {access_request.user.username}</p>',
        f'<p><b>Organization:</b> {access_request.organization}</p>',
        f'<p><b>Position:</b> {access_request.position}</p>',
        f'<p><b>Description:</b> {access_request.description}</p>',
        f'<p><b>First name:</b> {access_request.user.first_name}</p>',
        f'<p><b>Last name:</b> {access_request.user.last_name}</p>'
    ))

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
