import mintkit.settings as cfg
import mintkit.logs
import mintkit.auth.cred
import mintkit.utils
import pickle
import os


log = mintkit.logs.get_logger(cfg.PROJECT_NAME)


class AuthApi:
    def __init__(self):
        """An API class for abstracting the use of all credentials."""
        self.username = None
        self.mint = None
        self.gmail = None
        self.user = None
        self.set_credentials()

    def set_mint(self):
        """Set the Mint credentials.

        """
        if os.path.isfile(cfg.paths.creds + 'mint.sec'):
            self.mint = mintkit.auth.cred.from_file('mint', self.username)
        else:
            log.info('Mint credentials not loaded')

    def set_user(self):
        """Set the user's credentials.

        """
        if os.path.isfile(cfg.paths.creds + 'user.sec'):
            self.user = mintkit.auth.cred.from_file('user', self.username)
        else:
            log.info('User credentials not loaded')

    def set_gmail(self):
        """Set the Gmail credentials.

        """
        if os.path.isfile(cfg.paths.creds + 'gmail.pickle'):
            with open(cfg.paths.creds + 'gmail.pickle', 'rb') as file:
                self.gmail = pickle.load(file)
        else:
            log.info('Gmail credentials not loaded')

    def set_credentials(self):
        """Set all credentials simultaneously.

        """
        self.username = mintkit.utils.get_username()
        self.set_mint()
        self.set_user()
        self.set_gmail()

    def __str__(self):
        """Represetn as a string.

        """
        return "Authorization API."

    def __repr__(self):
        """Represent in the console.

        """
        ret = 'Authorization API\n'
        mint_status = 'not loaded' if self.mint is None else 'loaded'
        ret += f'mint: {mint_status}\n'
        user_status = 'not loaded' if self.user is None else 'loaded'
        ret += f'user: {user_status}\n'
        gmail_status = 'not loaded' if self.gmail is None else 'loaded'
        ret += f'gmail: {gmail_status}'
        return ret


auth_api = AuthApi()
