from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = "pydrive/client_secrets.json"

gauth = GoogleAuth()

# Try to load saved client credentials
gauth.LoadCredentialsFile("pydrive/mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("pydrive/mycreds.txt")

drive = GoogleDrive(gauth)

# file1 = drive.CreateFile()  # Create GoogleDriveFile instance
# file1.SetContentFile('markdown/informePrueba.pdf') # Set content of the file from given string.
# file1.Upload()

folderName = 'informe'  # Please set the folder name.
filepath = 'markdown/informePrueba.pdf'
files_from_path = filepath.split('/')
filename = files_from_path[-1]

folders = drive.ListFile(
    {'q': "title='" + folderName + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
for folder in folders:
    if folder['title'] == folderName:
        file1 = drive.CreateFile({'title': filename,'parents': [{'id': folder['id']}]}) # Carpeta informe
        file1.SetContentFile(filepath)
        file1.Upload()