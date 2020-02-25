import authapi
import time
import os
import re
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
        options = webdriver.ChromeOptions()
#         options.add_argument(f"user-data-dir={self.opt_dir}")
        self.driver = webdriver.Chrome(DRIVER_LOC, options=options)
        self.logged_in = False

    def await_element(self, criteria,
                      by_type=By.CSS_SELECTOR,
                      ec_type=EC.element_to_be_clickable,
                      timeout=120):
        """
        Return an element on a page after it has finished rendering.
        """
        wdw = WebDriverWait(self.driver, timeout)
        ec = ec_type((by_type, criteria))
        element = wdw.until(ec)
        return element

    def login(self):
        """
        Sign in to Mint.com
        """
        self.driver.get(f'{MINT_URL}')
        sign_in_link = self.await_element("a[aria-label='Sign in']")
        sign_in_link.click()
        email_form = self.await_element('#ius-userid')
        email_form.send_keys(authapi.mint.email)
        pw_form = self.await_element('#ius-password')
        pw_form.send_keys(authapi.mint.password)
        sign_in_btn = self.await_element('#ius-sign-in-submit-btn')
        sign_in_btn.click()
        self.logged_in = True

    def refresh_accounts(self, login=None):
        if login is None:
            login = not self.logged_in
        if login:
            self.login()
        gear_btn = self.await_element('.actionsMenuIcon.icon.icon-gear-gray3')
        self.driver.execute_script("window.scrollTo(0, 250)")
        gear_btn.click()
        refresh_elem = self.await_element('[data-action=refreshAccounts]')
        refresh_elem.click()

    def download_transactions(self, login=None):
        if login is None:
            login = not self.logged_in
        if login:
            self.login()
        trans_link = self.await_element('li#transaction > a')
        trans_link.click()
        trans_exp = self.await_element('#transactionExport')
        time.sleep(10)
        bar_x = self.driver.find_element(By.CSS_SELECTOR,
                                         '.x.icon.icon-x-white')
        if bar_x:
            try:
                bar_x.click()
            except Exception as e:
                print(e)
        trans_exp.click()


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
