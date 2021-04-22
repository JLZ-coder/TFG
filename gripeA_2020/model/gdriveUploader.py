from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os.path

class gDriveUploader:
    def __init__(self):
        folder = "pydrive/"
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = folder + "client_secrets.json"
        
        self.gauth = GoogleAuth()

        # Try to load saved client credentials
        self.gauth.LoadCredentialsFile(folder + "mycreds.txt")
        if self.gauth.credentials is None:
            # Authenticate if they're not there
            self.gauth.LocalWebserverAuth()

            gauth.GetFlow()
            gauth.flow.params.update({'access_type': 'offline'})
            gauth.flow.params.update({'approval_prompt': 'force'})
        elif self.gauth.access_token_expired:
            # Refresh them if expired
            self.gauth.Refresh()
        else:
            # Initialize the saved creds
            self.gauth.Authorize()
        # Save the current credentials to a file
        self.gauth.SaveCredentialsFile(folder + "mycreds.txt")

        self.drive = GoogleDrive(self.gauth)

    def upload_file(self, filepath, title=None, dest_folder=None):
        if not os.path.isfile(filepath):
            return None

        create_dict = {}
        if title != None:
            create_dict['title'] = title

        if dest_folder == None:
            file1 = self.drive.CreateFile(create_dict)
            file1.SetContentFile(filepath) # Set content of the file from given string.
            file1.Upload()
        else:
            folderName = dest_folder  # Please set the folder name.

            folders = self.drive.ListFile(
                {'q': "title='" + folderName + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
            
            for folder in folders:
                if folder['title'] == folderName:
                    create_dict.update({'parents': [{'id': folder['id']}]})
                    file1 = self.drive.CreateFile(create_dict) # Carpeta informe
                    file1.SetContentFile(filepath)
                    file1.Upload()

        return 0



