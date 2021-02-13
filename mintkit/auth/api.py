import mintkit.config as cfg
import mintkit.utils.logging
import mintkit.auth.cred
import mintkit.auth.manager
import os


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)

username = mintkit.auth.manager.get_username()
if os.path.isfile(cfg.paths.creds + 'mint.sec'):
    mint = mintkit.auth.cred.from_file('mint', username)
else:
    log.info('Mint credentials not loaded')
    mint = None


def reset():
    """Reset the API globals.

    """
    global mint
    if os.path.isfile(cfg.paths.creds + 'mint.sec'):
        mint = mintkit.auth.cred.from_file('mint', username)
        log.info('Mint credentials loaded.')
    else:
        log.info('Mint credentials not loaded.')


def setup():
    """Setup the credentials.

    """
    mintkit.auth.manager.setup_credentials()
