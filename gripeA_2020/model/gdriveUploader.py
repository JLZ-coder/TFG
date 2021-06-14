from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os.path

class gDriveUploader:
    def __init__(self):
        # folder = "pydrive/"
        # GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = folder + "client_secrets.json"
        
        self.gauth = GoogleAuth()

        # # Try to load saved client credentials
        # self.gauth.LoadCredentialsFile(folder + "mycreds.txt")
        # if self.gauth.credentials is None:
        #     # Authenticate if they're not there
        #     self.gauth.GetFlow()
        #     self.gauth.flow.params.update({'access_type': 'offline'})
        #     self.gauth.flow.params.update({'approval_prompt': 'force'})
        #     self.gauth.LocalWebserverAuth()
        # elif self.gauth.access_token_expired:
        #     # Refresh them if expired
        #     self.gauth.Refresh()
        # else:
        #     # Initialize the saved creds
        #     self.gauth.Authorize()
        # # Save the current credentials to a file
        # self.gauth.SaveCredentialsFile(folder + "mycreds.txt")

        self.drive = GoogleDrive(self.gauth)

    def re_auth(self):
        self.gauth = GoogleAuth()
        self.drive = GoogleDrive(self.gauth)

        file = "re_auth.txt"
        text_file = open(file, "w", encoding="utf-8")
        n = text_file.write("Fichero para subida a Drive y forzar el proceso de reautentificacion.")
        text_file.close()

        self.upload_file(file)
        self.trash_file(file)

    # Puede crear la carpeta si no existe, pero solo dentro de la carpeta principal del drive
    # Returns lista de urls para compartir
    def upload_file(self, filepath, title=None, dest_folder=None):
        if not os.path.isfile(filepath):
            return None

        params = {}
        if title != None:
            params['title'] = title
        else:
            title = filepath.split("/")[-1]

        existing_id = self.get_id_from(title, dest_folder)

        for file_id in existing_id:
            file1 = self.drive.CreateFile({"id": file_id})
            file1.Trash()

        if dest_folder == None:
            file1 = self.drive.CreateFile(params)
            file1.SetContentFile(filepath) # Set content of the file from given string.
            file1.Upload()
        else:
            folderName = dest_folder  # Please set the folder name.

            folders = self.drive.ListFile(
                {'q': "title='" + folderName + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()

            if len(folders) == 0:
                self.createFolder(folderName)
                folders = self.drive.ListFile(
                    {'q': "title='" + folderName + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()

            for folder in folders:
                if folder['title'] == folderName:
                    params.update({'parents': [{'id': folder['id']}]})
                    file1 = self.drive.CreateFile(params) # Carpeta informe
                    file1.SetContentFile(filepath)
                    file1.Upload()

        return 0

    # Puede crear la carpeta si no existe, pero solo dentro de la carpeta principal del drive
    # Returns lista de urls para compartir
    def trash_file(self, title, dest_folder=None):
        existing_id = self.get_id_from(title, dest_folder)

        for file_id in existing_id:
            file1 = self.drive.CreateFile({"id": file_id})
            file1.Trash()

        return 0

    # Puede crear la carpeta si no existe, pero solo dentro de la carpeta principal del drive
    # Returns lista de urls para compartir
    def download_file(self, filename, foldername=None, rec_folder=None):
        localfolder = ""
        if rec_folder != None:
            localfolder = rec_folder

        files = self.get_file_from(filename, foldername)

        if len(files) == 0:
            return None

        for file in files:
            file.GetContentFile(localfolder + "/" + file['title'])

        return 0

    def createFolder(self, folderName, parentID = None):
        # Create a folder on Drive, returns the newely created folders ID
        body = {
          'title': folderName,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parentID:
            body['parents'] = [{'id': parentID}]

        file1 = self.drive.CreateFile(body)
        file1.Upload()

    # Busca ficheros de la carpeta principal o de una carpeta hija de la principal como maximo
    def get_url_from(self, filename, foldername=None):

        lista_fileurl = []
        files = []

        if foldername == None:
            files = self.drive.ListFile(
                {'q': "title='" + filename + "' and trashed=false"}).GetList()
        else:
            folders = self.drive.ListFile(
                {'q': "title='" + foldername + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()

            for folder in folders:
                if folder['title'] == foldername:
                    files = self.drive.ListFile(
                        {'q': "title='" + filename + "' and '"+ folder['id'] +"' in parents and trashed=false"}).GetList()

        for file in files:
            lista_fileurl.append(file['alternateLink'])

        return lista_fileurl

    def get_id_from(self, filename, foldername=None):

        lista_fileurl = []
        files = []

        if foldername == None:
            files = self.drive.ListFile(
                {'q': "title='" + filename + "' and trashed=false"}).GetList()
        else:
            folders = self.drive.ListFile(
                {'q': "title='" + foldername + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()

            for folder in folders:
                if folder['title'] == foldername:
                    files = self.drive.ListFile(
                        {'q': "title='" + filename + "' and '"+ folder['id'] +"' in parents and trashed=false"}).GetList()

        for file in files:
            lista_fileurl.append(file['id'])

        return lista_fileurl

    def get_file_from(self, filename=None, foldername=None):

        files = []

        if filename == None and foldername == None:
            return files

        if filename == None:
            folders = self.drive.ListFile(
                {'q': "title='" + foldername + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()

            for folder in folders:
                if folder['title'] == foldername:
                    files = self.drive.ListFile(
                        {'q': "'"+ folder['id'] +"' in parents and trashed=false"}).GetList()

        else:
            if foldername == None:
                files = self.drive.ListFile(
                    {'q': "title='" + filename + "' and trashed=false"}).GetList()
            else:
                folders = self.drive.ListFile(
                    {'q': "title='" + foldername + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()

                for folder in folders:
                    if folder['title'] == foldername:
                        files = self.drive.ListFile(
                            {'q': "title='" + filename + "' and '"+ folder['id'] +"' in parents and trashed=false"}).GetList()

        return files


