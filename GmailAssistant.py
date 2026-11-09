from __future__ import print_function

import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Gmail label constants for reference:
# INBOX: Primary inbox
# SPAM: Spam folder
# TRASH: Trash folder
# IMPORTANT: Marked as important
# STARRED: Starred emails
# SENT: Sent emails
# DRAFT: Draft emails
# CATEGORY_PERSONAL: Personal category
# CATEGORY_SOCIAL: Social category
# CATEGORY_PROMOTIONS: Promotions category
# CATEGORY_UPDATES: Updates category
# CATEGORY_FORUMS: Forums category
# UNREAD: Unread emails

def main():
    creds = None
    credentialsJsonPath = (open_file_with_getcwd('credentials.json'))
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentialsJsonPath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # By default, only unread emails in 'INBOX' are retrieved.
    unread_mail = get_unread(service)

    if unread_mail:
        move_to_folder(service, unread_mail, 'UNREAD', 'TRASH', "🗑️")
        input("Ok!")
    else:
        print("No unread emails to move to TRASH! ✅")
        input("Ok!")

def open_file_with_getcwd(file_name):
    """
    Generates the absolute file path for a given file name, relative to the script's directory.
    If the script is not being run from its own directory, prints a warning along with the script's directory and the current working directory.
    Args:
        file_name (str): The name of the file for which to generate the absolute path.
    Returns:
        str: The absolute path to the specified file, located in the script's directory.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()

    if script_dir != cwd:
      print("Warning: The script is not running from its own directory.")
      print(f"Script Directory: {script_dir}")
      print(f"Current Working Directory: {cwd}")

    file_path = os.path.join(script_dir, file_name)

    return file_path

def get_labels(service):
    """
    Retrieves and prints the list of labels from the user's Gmail account.
    Args:
        service: Authorized Gmail API service instance.
    Returns:
        None. Prints the labels to the console in a formatted table.
    """
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print("╒════════╕\n│ Labels │\n╞════════╧═════════╕")
        for label in labels:
            print("│ {}".format(label['name']))
        print("╘══════════════════╛\n")

def move_to_folder(service, mail_to_move, current_label, new_label, icon):
    """
    Moves a list of emails to a specified Gmail label (folder) after user confirmation.
    Args:
        service: The authenticated Gmail API service instance.
        mail_to_move (list): List of email message objects to be moved.
        type (str): Type or category of the emails (not used in the function logic).
        new_label (str): The Gmail label ID to which the emails will be moved.
        icon (str): An icon or emoji to display in the confirmation message.
    Returns:
        None
    Side Effects:
        - Prompts the user for confirmation via input.
        - Prints status messages to the console.
        - Moves emails in batches of 1000 using the Gmail API.
    """
    num_mail_to_move = len(mail_to_move)
    confirm = input("Move {} {} email(s) to {}? 📧 \n [Y]es | [N]o: ".format(num_mail_to_move, current_label, new_label))
    confirm = confirm.upper()
    if confirm == "N":
        print("Moveing to {} cancelled. ❌".format(new_label))
        return
    elif confirm == "Y":
        print("{} email(s) moved to {}. {}".format(len(mail_to_move), new_label, icon))

        # Split mail_to_move into batches of 1000 emails
        batch_size = 1000
        batches = [mail_to_move[i:i + batch_size] for i in range(0, len(mail_to_move), batch_size)]

        for batch in batches:
            service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': [msg['id'] for msg in batch],
                    'addLabelIds': [new_label]
                }
            ).execute()

        return
    else:
        print("move-to_foder function error!")

def get_unread(service):
    """
    Retrieve all unread messages from the user's Gmail inbox.

    Args:
        service: Authorized Gmail API service instance.

    Returns:
        List of unread message objects from the inbox.
    """
    all_messages = []
    page_token = None
    while True:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=500, q="is:unread", pageToken=page_token).execute()
        all_messages.extend(results.get('messages', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    return all_messages
    while True:
        results = service.users().messages().list(
            userId='me',
            labelIds=label_ids,
            maxResults=500,
            q="is:unread",
            pageToken=page_token
        ).execute()
        all_messages.extend(results.get('messages', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    return all_messages


if __name__ == '__main__':
    main()
