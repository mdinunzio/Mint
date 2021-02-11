import config as cfg
import json
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


class AuthManager():
    """
    A generic Authentication manager.
    """

    def __init__(self, json_file=None):
        self.username = None
        self.password = None
        self.client_id = None
        self.token = None
        self.email = None
        self.number = None
        if json_file is None:
            return
        json_path = os.path.join(cfg.LOCAL_DIR, json_file)
        self.init_with_file(json_path)

    def init_with_file(self, json_path):
        with open(json_path, 'r') as f:
            self.auth_dict = json.load(f)
        for k, v in self.auth_dict.items():
            setattr(self, k, v)

    def __str__(self):
        ret = ''
        for k, v in self.auth_dict.items():
            ret += f'{k}: {v}\n'
        return ret

    def __repr__(self):
        return self.__str__()


class GmailOuath2Manager():
    """
    A Google-specific Oauth2 manager.
    """

    def __init__(self):
        self.cred_path = os.path.join(cfg.LOCAL_DIR, 'gmail.pickle')
        self.set_creds()

    def set_creds(self):
        """
        Set the credentials from a credentials pickle file.
        """
        if not os.path.exists(self.cred_path):
            self.setup_creds_file()

        with open(self.cred_path, 'rb') as token:
            creds = pickle.load(token)

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                self.setup_creds_file()
                with open(self.cred_path, 'rb') as token:
                    creds = pickle.load(token)

        self.creds = creds

    def setup_creds_file(self):
        """
        Generate the pickle file needed for Gmail API communication.
        """

        # Specify permissions to send and read/write messages
        # Find more information at:
        # https://developers.google.com/gmail/api/auth/scopes
        SCOPES = ['https://www.googleapis.com/auth/gmail.send',
                  'https://www.googleapis.com/auth/gmail.modify']

        json_path = os.path.join(cfg.LOCAL_DIR, 'gmail.json')

        # Indicate to the API how we will be generating our credentials
        flow = InstalledAppFlow.from_client_secrets_file(json_path, SCOPES)

        # Get the credentials from Google
        creds = flow.run_local_server(port=0)

        # We are going to store the credentials in the user's home directory
        self.cred_path = os.path.join(cfg.LOCAL_DIR, 'gmail.pickle')
        with open(self.cred_path, 'wb') as token:
            pickle.dump(creds, token)


mint = AuthManager('mint.json')
imgur = AuthManager('imgur.json')
user_data = AuthManager('user_data.json')
gmail = GmailOuath2Manager()
