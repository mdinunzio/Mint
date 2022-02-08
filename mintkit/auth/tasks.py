import mintkit.settings as cfg
import mintkit.utils.logs
import mintkit.auth.cred
import mintkit.gmail.tasks
import mintkit.utils.env


log = mintkit.utils.logs.get_logger(cfg.PROJECT_NAME)


def save_mint_credentials(email, password):
    """Save the user's Mint credentials.

    """
    cred = mintkit.auth.cred.Credential('mint')
    cred.email = email
    cred.password = password
    key = mintkit.utils.env.get_username()
    cred.save(key)


def setup_mint_credentials():
    """Interactively setup the user's Mint credentials.

    """
    print('Please provide your credentials for Mint.com')
    email = input('email: ')
    password = input('password: ')
    save_mint_credentials(email, password)
    print('Mint credentials successfully saved.')


def save_user_credentials(email, mobile):
    """Save the user's credentials.

    """
    cred = mintkit.auth.cred.Credential('user')
    cred.email = email
    cred.mobile = mobile
    key = mintkit.utils.env.get_username()
    cred.save(key)


def setup_user_credentials():
    """Interactively setup the user's personal credentials.

    """
    print('Please provide your personal email.')
    email = input('email: ')
    print('Please provide your mobile phone number.')
    mobile = input('mobile phone: ')
    save_user_credentials(email, mobile)
    print("User's credentials successfully saved.")


def setup_credentials():
    """Interactively setup all of the user's credentials.

    """
    setup_mint_credentials()
    setup_user_credentials()
    mintkit.gmail.tasks.setup_gmail_credentials()
