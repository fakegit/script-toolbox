from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json, glob, uuid, pickle, os.path

SCOPES = ["https://www.googleapis.com/auth/drive"]

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

drive = build('drive', 'v3', credentials=creds)
tdnm = input('Name? ')
request_id = str(uuid.uuid4())
drive_metadata = {'name': tdnm}

print('Creating Team Drive')
td = drive.drives().create(body=drive_metadata,requestId=request_id,fields='id').execute()
print('Created Team Drive named %s (%s)' % (tdnm,td['id']))

my_id = drive.permissions().list(fileId=td['id'],supportsAllDrives=True).execute()['permissions'][0]['id']
print(my_id)

email = input('Email? ')
pid = drive.permissions().create(fileId=td['id'],supportsAllDrives=True, body={
    "role": "organizer",
    "type": "user",
    "emailAddress": email
}).execute()

print('Email Added.')
rem = input('Remove self? ')
while not rem.startswith('y') and not rem.startswith('n'):
	rem = input('Remove self (y/n)? ')
if rem.startswith('y'):
	drive.permissions().delete(fileId=td['id'],permissionId=my_id,supportsAllDrives=True).execute()
print('Done.')