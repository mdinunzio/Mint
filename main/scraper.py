import authapi
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


MINT_URL = r'https://www.mint.com'

# File locations
# this_loc = __file__
# parent_dir = os.path.abspath(os.path.join(this_loc, '..'))
# local_dir = os.path.abspath(os.path.join(parent_dir, '..', 'local'))
# local_dir = r'C:\Users\mdinu\eclipse-workspace\Mint\local'


class MintScraper():
    def __init__(self):
        self.driver_loc = \
            r'C:\Program Files\chromedriver_win32\chromedriver.exe'
        self.user_dir = os.path.expanduser('~')
        self.username = self.user_dir.split('\\')[-1]
        self.opt_dir = os.path.join(
            self.user_dir,
            r'AppData\Local\Google\Chrome\User Data\Default')
        options = webdriver.ChromeOptions()
#         options.add_argument(f"user-data-dir={self.opt_dir}")
        self.driver = webdriver.Chrome(self.driver_loc, options=options)

    def await_element(self, criteria, by=By.CSS_SELECTOR, timeout=10):
        """
        Return an element on a page after it has finished rendering.
        """
        wdw = WebDriverWait(self.driver, timeout)
        ec = EC.presence_of_element_located((by, criteria))
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
