import mintkit.config as cfg
import mintkit.utils.logging
from mintkit.auth import authapi
import os
import re
import time


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)

# Regular Expressions
TRANSACT_PATTERN = r'transactions(?: \((?P<instance>\d+)\))?\.csv'
TRANSACT_RE = re.compile(TRANSACT_PATTERN)

# URLs
MINT_URL = 'http://www.mint.com'


# HELPER FUNCTIONS ############################################################

def _sort_files(x):
    """Return the sort key index for a transaction file.

    """
    match = TRANSACT_RE.match(x)
    if match['instance']:
        return int(match['instance'])
    else:
        return 0


def get_latest_file_location():
    """Return a string representing the location of the most
    recently downloaded transactions file.

    """
    dl_files = os.listdir(cfg.paths.downloads)
    trans_files = [x for x in dl_files if TRANSACT_RE.match(x)]
    trans_files.sort(key=_sort_files, reverse=True)
    trans_file = trans_files[0]
    return cfg.paths.downloads + trans_file


def delete_all_transaction_files():
    """
    Delete all transactions files in the Downloads folder.
    """
    dl_files = os.listdir(cfg.paths.downloads)
    trans_files = [x for x in dl_files if TRANSACT_RE.match(x)]
    for f in trans_files:
        try:
            fl_path = cfg.paths.downloads + f
            os.remove(str(fl_path))
        except Exception as e:
            print(e)


# MAIN FUNCTIONALITY ##########################################################

def login_mint(driver):
    """Sign in to Mint.com

    """
    log.info('Logging into Mint.')
    driver.get(f'{MINT_URL}')
    sign_in_link = driver.await_element("a[aria-label='Sign in']")
    driver.jsclick(sign_in_link)
    email_form = driver.await_element('#ius-userid')
    email_form.send_keys(authapi.mint.email)
    pw_form = driver.await_element('#ius-password')
    pw_form.send_keys(authapi.mint.password)
    sign_in_btn = driver.await_element('#ius-sign-in-submit-btn')
    driver.jsclick(sign_in_btn)
    log.info('Finished logging in.')


def refresh_accounts(driver, login=False):
    """Refresh Mint's account data.

    """
    if login:
        login_mint(driver)
    log.info('Refreshing Mint accounts.')
    gear_btn = driver.await_element('.actionsMenuIcon.icon.icon-gear-gray3')
    driver.execute_script("window.scrollTo(0, 250)")
    driver.jsclick(gear_btn)
    refresh_elem = driver.await_element('[data-action=refreshAccounts]')
    driver.jsclick(refresh_elem)
    log.info('Mint account refresh successful.')


def download_transactions(driver, login=False):
    """Download Mint's transaction data.

    """
    if login:
        login_mint(driver)
    log.info('Downloading Mint transaction data.')
    trans_link = driver.await_element('li#transaction > a')
    driver.jsclick(trans_link)
    time.sleep(10)
    alert_x = driver.find_element("button[aria-label='Close']")
    if alert_x is not None:
        driver.jsclick(alert_x, fatal=False)
    trans_exp = driver.await_element('#transactionExport')
    time.sleep(10)
    bar_x = driver.find_element(".x.icon.icon-x-white")
    if bar_x is not None:
        driver.jsclick(bar_x)
    driver.jsclick(trans_exp)
    log.info('Mint transactions exported successfully.')
