# http://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.html
from __future__ import print_function
import pickle
import base64

import os.path
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from django.conf import settings
import logging

logger = logging.getLogger('app')


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.labels']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('gmail_token.pickle'):
        with open('gmail_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gmail_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('gmail_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


# stars
def stars_gmail_message(message):
    service = main()
    # results = service.users().labels().list(userId='me').execute()
    # labels = results.get('labels', [])

    # uploaded_label = None
    # for label in labels:
    #     if label['name'] == 'Uploaded':
    #         uploaded_label = label

    # if uploaded_label:

    service.users().messages().modify(userId='me', id=message['id'], body={
        'addLabelIds': ['STARRED']}).execute()


def get_property_shark_links():
    # Call the Gmail API
    # gets non-starred messages from support@propertyshark.com
    service = main()
    results = service.users().messages().list(userId='me', labelIds=[
        'INBOX'], q="-:starred from:support@propertyshark.com").execute()
    messages = results.get('messages', [])

    # Extract all property shark emails
    # retrieve the links with export_email.html in the href
    # download the xls file from the link and save as a DataFile
    property_shark_emails = []
    links = []
    try:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            for header in msg['payload']['headers']:
                if header['name'] == 'From' and header['value'] == 'support@propertyshark.com':
                    if 'data' in msg['payload']['body']:
                        msg_str = base64.urlsafe_b64decode(msg['payload']['body']['data'].encode('UTF8')).decode('UTF8')
                        if 'Your list has been successfully exported' in msg_str:
                            property_shark_emails.append({'msg': msg, 'message': message})

        for ps_msg in property_shark_emails:
            msg_str = base64.urlsafe_b64decode(ps_msg['msg']['payload']['body']['data'].encode('UTF8')).decode('UTF8')
            soup = BeautifulSoup(msg_str)
            link = ""
            for l in soup.findAll('a'):
                if 'export_email.html' in l.get('href'):
                    link = l.get('href')

            if link:
                links.append(link)

                # Only star real email if in production
                if not settings.DEBUG:
                    stars_gmail_message(ps_msg['message'])

        return links

    except Exception as e:
        logger.warning(e)
        raise e


if __name__ == '__main__':
    main()
