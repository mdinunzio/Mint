import mintkit.config as cfg
import mintkit.utils.logging
from mintkit.auth import authapi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import re
import sys
import psutil


# Get logger
log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)

# URLS
MINT_URL = r'https://www.mint.com'

# Regular Expressions
TRANSACT_PATTERN = r'transactions(?: \((?P<instance>\d+)\))?\.csv'
TRANSACT_RE = re.compile(TRANSACT_PATTERN)


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


def taskkill(image_name):
    """Kill a task with the given image name.

    """
    procs = [x for x in psutil.process_iter() if image_name in x.name()]
    for p in procs:
        p.kill()


# MODELS ######################################################################

class MintScraper():
    def __init__(self):
        """A tool for scraping Mint webpages.

        """
        self.username = cfg.paths.home[-1]
        self.profile = cfg.paths.chrome_profile
        self.driver = None
        self.logged_in = False
        try:
            self.start_driver()
        except Exception as e:
            print(e)
            taskkill('chrome')
            self.start_driver()

    def start_driver(self):
        """Start the chromedriver.

        """
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={self.profile}")
        self.driver = webdriver.Chrome(cfg.paths.chromedriver, options=options)
        self.driver.maximize_window()

    def await_element(self, criteria,
                      by_type=By.CSS_SELECTOR,
                      ec_type=EC.element_to_be_clickable,
                      timeout=300,
                      fatal=True):
        """Return an element on a page after it has finished rendering.

        """
        try:
            wdw = WebDriverWait(self.driver, timeout)
            ec = ec_type((by_type, criteria))
            element = wdw.until(ec)
            return element
        except TimeoutException:
            print('TimeoutException: Element not found.')
            if fatal:
                self.driver.quit()
                sys.exit(1)

    def find_element(self, criteria):
        """Return an element if it exists, otherwise return None.

        """
        elements = self.driver.find_elements(By.CSS_SELECTOR, criteria)
        if len(elements) > 0:
            return elements[0]
        else:
            return None
            
    def jsclick(self, element, fatal=True):
        """Click an element using javascript
        (avoids ElementClickInterceptedException).

        """
        try:
            js = 'arguments[0].click();'
            self.driver.execute_script(js, element)
        except Exception as e:
            print(e)
            if fatal:
                self.driver.quit()
                sys.exit(1)

    def login(self):
        """Sign in to Mint.com

        """
        self.driver.get(f'{MINT_URL}')
        sign_in_link = self.await_element("a[aria-label='Sign in']")
        self.jsclick(sign_in_link)
        email_form = self.await_element('#ius-userid')
        email_form.send_keys(authapi.mint.email)
        pw_form = self.await_element('#ius-password')
        pw_form.send_keys(authapi.mint.password)
        sign_in_btn = self.await_element('#ius-sign-in-submit-btn')
        self.jsclick(sign_in_btn)
        self.logged_in = True

    def refresh_accounts(self, login=None):
        """Refresh Mint's account data.

        """
        if login is None:
            login = not self.logged_in
        if login:
            self.login()
        gear_btn = self.await_element('.actionsMenuIcon.icon.icon-gear-gray3')
        self.driver.execute_script("window.scrollTo(0, 250)")
        self.jsclick(gear_btn)
        refresh_elem = self.await_element('[data-action=refreshAccounts]')
        self.jsclick(refresh_elem)

    def download_transactions(self, login=None):
        """Download Mint's transaction data.

        """
        if login is None:
            login = not self.logged_in
        if login:
            self.login()
        trans_link = self.await_element('li#transaction > a')
        self.jsclick(trans_link)
        time.sleep(10)
        alert_x = self.find_element("button[aria-label='Close']")
        if alert_x is not None:
            self.jsclick(alert_x, fatal=False)
        trans_exp = self.await_element('#transactionExport')
        time.sleep(10)
        bar_x = self.find_element(".x.icon.icon-x-white")
        if bar_x is not None:
            self.jsclick(bar_x)
        self.jsclick(trans_exp)
