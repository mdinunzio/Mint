import authapi
import time
import os
import re
import sys
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# URLS
MINT_URL = r'https://www.mint.com'

# Paths
DRIVER_LOC = r'C:\Program Files (x86)\chromedriver_win32\chromedriver.exe'
USER_DIR = os.path.expanduser('~')
DL_DIR = os.path.join(USER_DIR, 'Downloads')
OPT_DIR = os.path.join(
    USER_DIR, r'AppData\Local\Google\Chrome\User Data\Default')

# Regular Expressions
trans_pattern = r'transactions(?: \((?P<instance>\d+)\))?\.csv'
trans_re = re.compile(trans_pattern)


# MODELS #####################################################################

class MintScraper():
    def __init__(self):
        self.username = USER_DIR.split('\\')[-1]
        self.opt_dir = os.path.join(
            USER_DIR,
            r'AppData\Local\Google\Chrome\User Data\Default')
        try:
            self.start_driver()
        except Exception as e:
            print(e)
            self.taskkill('chrome')
            self.start_driver()

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={self.opt_dir}")
        self.driver = webdriver.Chrome(DRIVER_LOC, options=options)
        self.driver.maximize_window()
        self.logged_in = False

    def taskkill(self, imgname):
        procs = [x for x in psutil.process_iter() if imgname in x.name()]
        for p in procs:
            p.kill()

    def await_element(self, criteria,
                      by_type=By.CSS_SELECTOR,
                      ec_type=EC.element_to_be_clickable,
                      timeout=300,
                      fatal=True):
        """
        Return an element on a page after it has finished rendering.
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
        """
        Return an element if it exists, otherwise return None.
        """
        elements = self.driver.find_elements(By.CSS_SELECTOR, criteria)
        if len(elements) > 0:
            return elements[0]
        else:
            return None
            
    def jsclick(self, element, fatal=True):
        """
        Click an element using javascript
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
        """
        Sign in to Mint.com
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
        """
        Refresh Mint's account data.
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
        """
        Download Mint's transaction data.
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


# FUNCTIONS ##################################################################

def _sort_files(x):
    """
    Return the sort key index for a transaction file.
    """
    mtch = trans_re.match(x)
    if mtch['instance']:
        return int(mtch['instance'])
    else:
        return 0


def get_latest_file_location():
    """
    Return a string representing the location of the most recently
    downloaded transactions file.
    """
    dl_files = os.listdir(DL_DIR)
    trans_files = [x for x in dl_files if trans_re.match(x)]
    trans_files.sort(key=_sort_files, reverse=True)
    trans_file = trans_files[0]
    return os.path.join(DL_DIR, trans_file)


def delete_all_tranaction_files():
    """
    Delete all transactions files in the Downloads folder.
    """
    dl_files = os.listdir(DL_DIR)
    trans_files = [x for x in dl_files if trans_re.match(x)]
    for f in trans_files:
        try:
            fl_path = os.path.join(DL_DIR, f)
            os.remove(fl_path)
        except Exception as e:
            print(e)
