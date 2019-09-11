from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from os.path import exists
from uuid import uuid4
import pickle, argparse

def new_shared_drive(name=None,member=None,selfremove=False,token='token.pickle',credentials='credentials.json'):
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    creds = None
    if exists(token):
        with open(token, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token, 'wb') as token:
            pickle.dump(creds, token)

    drive = build('drive', 'v3', credentials=creds)
    request_id = str(uuid4())
    drive_metadata = {'name': name}

    td = drive.drives().create(body=drive_metadata,requestId=request_id,fields='id,name').execute()
    print('Created Shared Drive %s (%s)' % (td['name'],td['id']))

    my_id = drive.permissions().list(fileId=td['id'],supportsAllDrives=True).execute()['permissions'][0]['id']

    if member is not None:
        print('Added %s' % member)
        drive.permissions().create(fileId=td['id'],supportsAllDrives=True, body={
            "role": "organizer",
            "type": "user",
            "emailAddress": member
        }).execute()

    if selfremove:
        drive.permissions().delete(fileId=td['id'],permissionId=my_id,supportsAllDrives=True).execute()
        print('Removed self.')

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='A tool intended to create a new Shared Drive.')
    parse.add_argument('--member','-m',default=None,help='An additional member to add to the Shared Drive as a Manager.')
    parse.add_argument('--remove-self',default=False,action='store_true',help='Remove yourself from the Shared Drive.')
    parse.add_argument('--token',default='token.pickle',help='Specify the pickle token file path.')
    parse.add_argument('--credentials',default='credentials.json',help='Specify the credentials file path.')
    parsereq = parse.add_argument_group('required arguments')
    parsereq.add_argument('--name','-n',help='The name for the new Shared Drive.',required=True)
    args = parse.parse_args()
    new_shared_drive(
        name=args.name,
        member=args.member,
        selfremove=args.remove_self,
        token=args.token,
        credentials=args.credentials
    )
