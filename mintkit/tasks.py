"""Tools for getting setup with the gmail API.

"""
import mintkit.settings as cfg
import mintkit.logs
from google_auth_oauthlib.flow import InstalledAppFlow
import subprocess
import pickle
import os

log = mintkit.logs.get_logger(cfg.PROJECT_NAME)


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
    pickle_path = cfg.paths.creds + 'gmail.pickle'
    with open(pickle_path, 'wb') as token:
        pickle.dump(creds, token)
    log.info('Finished creating gmail credentials pickle file:')
    log.info(pickle_path)


def setup_gmail_credentials():
    """Interactively setup Gmail credentials.

    """
    print('Please enable the gmail API for your account.')
    print('1. Click "Enable the Gmail API" on the webpage that opens.')
    print('2. Name the project "MintKit".')
    print('3. Configure the project as a "Desktop App".')
    print('4. Click "DOWNLOAD CLIENT CONFIGURATION".')
    open_enable_api_page()
    print('5. After downloading, please provide the path the the file below.')
    file_path = input('Configuration file path: ')
    while not os.path.isfile(file_path):
        print('File path not valid')
        file_path = input('Configuration file path: ')
    create_credentials_pickle(file_path)
    print('6. In the webpage that opens click "Advanced" at the bottom left.')
    print('7. Click "Go to Quickstart (unsafe)".')
    print('8. Click "Allow".')
    print('Gmail credential setup complete.')
