from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle, os, sys

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
            'portal.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

drive = build('drive', 'v3', credentials=creds)

def ls(parent, searchTerms=""):
    files = []
    resp = drive.files().list(q=f"'{parent}' in parents" + searchTerms, pageSize=1000, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    files += resp["files"]
    while "nextPageToken" in resp:
        resp = drive.files().list(q=f"'{parent}' in parents" + searchTerms, pageSize=1000, supportsAllDrives=True, includeItemsFromAllDrives=True, pageToken=resp["nextPageToken"]).execute()
        files += resp["files"]
    return files

def lsd(parent):
    
    return ls(parent, searchTerms=" and mimeType contains 'application/vnd.google-apps.folder'")

def lsf(parent):
    
    return ls(parent, searchTerms=" and not mimeType contains 'application/vnd.google-apps.folder'")

def getf(fileid):
    
    return drive.files().get(fileId=fileid, supportsAllDrives=True).execute()

def strip_perms(fileid):
    
    resp = drive.permissions().list(fileId=fileid, supportsAllDrives=True).execute()
    for i in resp["permissions"]:
        if i.get("role") != "owner":
            drive.permissions().delete(fileId=fileid, permissionId=i["id"]).execute()

def recurse_folder(folderid):
    
    strip_perms(folderid)
    files = ls(folderid)
    for i in files:
        if i["mimeType"] == "application/vnd.google-apps.folder":
            recurse_folder(i["id"])
        else:
            strip_perms(i["id"])
    
recurse_folder(sys.argv[1])