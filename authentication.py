import os.path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/userinfo.email', 'openid']


def listFiles(creds, no_files):
  try:
    service = build("drive", "v3", credentials=creds)
    oauth2_service = build('oauth2', 'v2', credentials=creds)
    user_info = oauth2_service.userinfo().get().execute()

    # Extract the email address from the user info
    email = user_info.get('email')
    # Call the Drive v3 API
    query = f"'{email}' in owners"
    results = (
        service.files()
        .list(pageSize=no_files, q=query, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
      return "No Files Found"
    else:
      return items
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    return f"An error occurred: {error}"

def downloadFile(creds, file_id, file_name):
  try:
    service = build("drive", "v3", credentials=creds)
    request = service.files().get_media(fileId=file_id)
    file = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
      status, done = downloader.next_chunk()
      print(f"Download {int(status.progress() * 100)}%.")

    

    return f"File downloaded as: {file_name}"


  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    return f"An error occurred: {error}"
  
#   def uploadFile(creds, file_path, file_name):


def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  while True:
    print("1. List Files")
    print("2. Download File")
    print("3. List Drive")
    print("4. Exit")
    choice = int(input("Enter your choice: "))

    if choice == 1:
      no_files = int(input("Enter the number of files you want to list: "))
      files = listFiles(creds, no_files)
    #   print(files)
      for file in files:
        print(f"File Name: {file['name']} File ID: {file['id']}")
      
    elif choice == 2:
      file_id = input("Enter the file id to download: ")
      file_name = input("Enter the name of the file: ")
      print(downloadFile(creds, file_id, file_name))

    elif choice == 4:
      break
    else:
      print("Invalid choice")


if __name__ == "__main__":
  main()