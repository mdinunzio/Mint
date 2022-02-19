import logging
import time
import chromekit.driver
import mintkit.auth.api


log = logging.getLogger(__name__)


# URLs
MINT_URL = 'http://www.mint.com'


def login_mint(driver: chromekit.driver.WebDriver):
    """Sign in to Mint.com"""
    log.info('Logging into Mint.')
    driver.get(f'{MINT_URL}')
    sign_in_link_id = "a[data-identifier='sign-in']"
    sign_in_link = driver.await_element(sign_in_link_id)
    driver.jsclick(sign_in_link)
    # Enter email.
    email_form_id = '#ius-identifier'
    email_form = driver.await_element(email_form_id)
    email_form.clear()
    email_form.send_keys(mintkit.auth.api.auth_api.mint.email)
    # Uncheck "Remember me" box.
    check_box_id = '#ius-signin-label-checkbox'
    check_box = driver.await_element(check_box_id)
    check_box.click()
    # Click "Sign In" button.
    sign_in_button_id = '#ius-sign-in-submit-btn'
    sign_in_button = driver.await_element(sign_in_button_id)
    sign_in_button.click()
    # Click password form.
    pw_form_id = '#ius-sign-in-mfa-password-collection-current-password'
    pw_form = driver.await_element(pw_form_id)
    driver.jsclick(pw_form)
    pw_form.clear()
    pw_form.send_keys(mintkit.auth.api.auth_api.mint.password)
    # Click "Continue" button.
    continue_btn_id = '#ius-sign-in-mfa-password-collection-continue-btn'
    sign_in_btn = driver.await_element(continue_btn_id)
    driver.jsclick(sign_in_btn)
    log.info('Finished logging in.')


def refresh_accounts(driver: chromekit.driver.WebDriver = None,
                     log_in: bool = True):
    """Refresh Mint's account data."""
    if driver is None:
        driver = chromekit.driver.WebDriver()
        driver.start()
    if log_in:
        login_mint(driver)
    log.info('Refreshing Mint accounts.')
    gear_btn_class = '.actionsMenuIcon.icon.icon-gear-gray3'
    gear_btn = driver.await_element(gear_btn_class)
    driver.execute_script("window.scrollTo(0, 250)")
    driver.jsclick(gear_btn)
    refresh_accounts_selector = '[data-action=refreshAccounts]'
    refresh_elem = driver.await_element(refresh_accounts_selector)
    driver.jsclick(refresh_elem)
    time.sleep(10)
    driver.quit()
    log.info('Mint account refresh successful.')


def download_transactions(driver: chromekit.driver.WebDriver = None,
                          log_in: bool = True):
    """Download Mint's transaction data."""
    if driver is None:
        driver = chromekit.driver.WebDriver()
        driver.start()
    if log_in:
        login_mint(driver)
    log.info('Downloading Mint transaction data.')
    transaction_link_selector = 'li#transaction > a'
    trans_link = driver.await_element(transaction_link_selector)
    driver.jsclick(trans_link)
    time.sleep(10)
    transaction_export_id = '#transactionExport'
    trans_exp = driver.await_element(transaction_export_id)
    time.sleep(10)
    driver.jsclick(trans_exp)
    time.sleep(10)
    driver.quit()
    log.info('Mint transactions exported successfully.')
