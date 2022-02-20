import mintkit.settings as cfg
import mintkit.logs
import mintkit.analytics
import mintkit.plotting
import mintkit.gmail
from mintkit.auth.api import auth_api
import datetime
import time


log = mintkit.logs.get_logger(cfg.PROJECT_NAME)

# URLs
MINT_URL = 'http://www.mint.com'


def login_mint(driver):
    """Sign in to Mint.com

    """
    log.info('Logging into Mint.')
    driver.get(f'{MINT_URL}')
    sign_in_link = driver.await_element("a[data-identifier='sign-in']")
    driver.jsclick(sign_in_link)
    email_div = driver.await_element('#ius-account-chooser-option-b-text-0')
    driver.jsclick(email_div)
    pw_id = '#ius-sign-in-mfa-password-collection-current-password'
    pw_form = driver.await_element(pw_id)
    pw_form.clear()
    pw_form.send_keys(auth_api.mint.password)
    btn_id = '#ius-sign-in-mfa-password-collection-continue-btn'
    sign_in_btn = driver.await_element(btn_id)
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


def send_spending_update_text(download=True):
    """Send the spending update text message.

    """
    log.info('Preparing spending summary text')
    if download:
        log.info('Downloading transactions')
        download_transactions()
    log.info('Retrieving files')
    transactions = mintkit.analytics.get_transactions()
    investments = mintkit.analytics.get_investments()
    recurring = mintkit.analytics.get_recurring()
    log.info('Getting summaries')
    summary = mintkit.analytics.get_recent_spending_summary(
        transactions=transactions, recurring=recurring,
        investments=investments, lookback=5)
    mintkit.plotting.plot_spending(
        transactions=transactions, recurring=recurring)
    log.info('Constructing text message (email).')
    today = datetime.date.today()
    email = mintkit.gmail.EmailMessage()
    email.subject = f'Spending {today:%a, %b %d}'
    email.to = auth_api.user.mobile + '@vzwpix.com'
    email.body = summary
    email.add_image('spending', cfg.paths.plots + 'spending.png')
    email.send()
    log.info('Text update sent')


def send_auto_spending_text(download=False):
    """Send the auto spending update text message.

    """
    log.info('Preparing auto spending summary text')
    if download:
        log.info('Downloading transactions')
        download_transactions()
    transactions = mintkit.analytics.get_transactions()
    auto_stats = mintkit.analytics.get_current_auto_spending_stats(
        transactions)
    auto_stats = auto_stats.reset_index()
    auto_smry = auto_stats.to_html(index=False, header=False)
    today = datetime.date.today()
    email = mintkit.gmail.EmailMessage()
    email.subject = f'Auto Spending {today:%a, %b %d}'
    email.to = auth_api.user.mobile + '@vzwpix.com'
    email.body = auto_smry
    email.send()


def send_texts():
    """Send all texts.

    """
    send_spending_update_text(download=True)
    send_auto_spending_text(download=False)
