"""Tools for getting setup with the gmail API.

"""
import mintkit.config as cfg
import mintkit.utils.logging
from google_auth_oauthlib.flow import InstalledAppFlow
import subprocess
import pickle
import os

log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)


def open_enable_api_page():
    """Open the webpage needed to enable the Gmail API.

    """
    cmds = [str(cfg.paths.chrome),
            'https://developers.google.com/gmail/api/quickstart/python']
    subprocess.run(cmds)


def create_credentials_pickle(json_path):
    """Setup the credentials pickle file using a json client secrets file.

    """
    log.info('Creating gmail credentials pickle file')
    SCOPES = ['https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/gmail.modify']
    flow = InstalledAppFlow.from_client_secrets_file(json_path, SCOPES)
    creds = flow.run_local_server(port=0)
    pickle_path = cfg.paths.user + 'gmail.pickle'
    with open(pickle_path, 'wb') as token:
        pickle.dump(creds, token)
    log.info('Finished creating gmail credentials pickle file:')
    log.info(pickle_path)
