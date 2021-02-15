import mintkit.config as cfg
import mintkit.utils.logging
import mintkit.auth.cred
import mintkit.auth.manager
import os


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)


class AuthApi:
    def __init__(self):
        """An API class for abstracting the use of all credentials."""
        self.username = None
        self.mint = None
        self.set_credentials()

    def set_mint(self):
        """Set the Mint credentials.

        """
        if os.path.isfile(cfg.paths.creds + 'mint.sec'):
            self.mint = mintkit.auth.cred.from_file('mint', self.username)
        else:
            log.info('Mint credentials not loaded')

    def set_credentials(self):
        """Set all credentials simultaneously.

        """
        self.username = mintkit.auth.manager.get_username()
        self.set_mint()


auth_api = AuthApi()
