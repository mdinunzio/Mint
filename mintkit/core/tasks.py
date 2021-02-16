import mintkit.config as cfg
import mintkit.utils.logging
import mintkit.web.driver
from mintkit.auth.api import auth_api
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
    email_form.clear()
    email_form.send_keys(auth_api.mint.email)
    pw_form = driver.await_element('#ius-password')
    pw_form.clear()
    pw_form.send_keys(auth_api.mint.password)
    sign_in_btn = driver.await_element('#ius-sign-in-submit-btn')
    driver.jsclick(sign_in_btn)
    log.info('Finished logging in.')


def refresh_accounts(driver=None, logged_in=False):
    """Refresh Mint's account data.

    """
    if driver is None:
        driver = mintkit.web.driver.WebDriver()
    if not logged_in:
        login_mint(driver)
    log.info('Refreshing Mint accounts.')
    gear_btn = driver.await_element('.actionsMenuIcon.icon.icon-gear-gray3')
    driver.execute_script("window.scrollTo(0, 250)")
    driver.jsclick(gear_btn)
    refresh_elem = driver.await_element('[data-action=refreshAccounts]')
    driver.jsclick(refresh_elem)
    time.sleep(10)
    driver.quit()
    log.info('Mint account refresh successful.')


def download_transactions(driver=None, logged_in=False):
    """Download Mint's transaction data.

    """
    if driver is None:
        driver = mintkit.web.driver.WebDriver()
    if not logged_in:
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
    time.sleep(10)
    driver.quit()
    log.info('Mint transactions exported successfully.')


def send_spending_update_text():
    """Send the spending update text message.

    """
    log.info('Preparing spending summary text')
    log.info('Downloading transactions')
    mintkit.core.tasks.download_transactions()
    log.info('Retrieving files')
    transactions = mintkit.core.analytics.get_transactions()
    recurring = mintkit.core.analytics.get_recurring()
    log.info('Getting summaries')
    summary = mintkit.core.analytics.get_recent_spending_summary(
        transactions=transactions, recurring=recurring, lookback=5)
    mintkit.core.plotting.plot_spending(
        transactions=transactions, recurring=recurring)
    log.info('Constructing text message (email).')
    today = datetime.date.today()
    email = mintkit.gmail.email.EmailMessage()
    email.subject = f'Spending {today:%a, %b %d}'
    email.to = auth_api.user.mobile + '@vzwpix.com'
    email.body = summary
    email.add_image('spending', cfg.paths.plots + 'spending.png')
    email.send()
    log.info('Text update sent')
