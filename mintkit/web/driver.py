"""A simplified webdriver module.

"""
import mintkit.config as cfg
import mintkit.utils.logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sys
import psutil
import subprocess


# Get logger
log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)


# HELPER FUNCTIONS ############################################################

def taskkill(image_name):
    """Kill a task with the given image name.

    """
    procs = [x for x in psutil.process_iter() if image_name in x.name()]
    for p in procs:
        p.kill()


def get_chrome_version():
    """Return the version of Chrome on this PC.

    """
    name = cfg.paths.chrome
    cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" ' \
          r'/v version'
    res = subprocess.run(cmd, capture_output=True)
    version = res.stdout.decode('utf-8')
    version = version.split(' ')[-1]
    version = version.strip()
    return version


# MODELS ######################################################################

class WebDriver:
    def __init__(self):
        """A tool for traversing webpages.

        """
        self.profile = cfg.paths.chrome_profile
        self.driver = None
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

    def get(self, url):
        """Get the requested url.

        """
        self.driver.get(url)

    def await_element(self, criteria, by_type=By.CSS_SELECTOR,
                      ec_type=EC.element_to_be_clickable, timeout=300,
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

    def execute_script(self, script):
        """Execute the given script.

        """
        self.driver.execute_script(script)

    def quit(self):
        """Quit the driver.

        """
        self.driver.quit()
