import mintkit.config as cfg
import mintkit.utils.logging
import requests
import psutil
import subprocess
import zipfile
from bs4 import BeautifulSoup
import re


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)

CHROMEDRIVER_URL = r'https://chromedriver.chromium.org'


def taskkill(image_name):
    """Kill a task with the given image name.

    """
    procs = [x for x in psutil.process_iter() if image_name in x.name()]
    for p in procs:
        p.kill()


def get_chrome_version():
    """Return the version of Chrome on this PC.

    """
    cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" ' \
          r'/v version'
    res = subprocess.run(cmd, capture_output=True)
    version = res.stdout.decode('utf-8')
    version = version.split(' ')[-1]
    version = version.strip()
    return version


def get_chromedriver_version_map():
    """Return a dictionary mapping Chrome versions to Chromedriver versions.

    """
    dl_url = f'{CHROMEDRIVER_URL}/downloads'
    req = requests.get(dl_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    li_list = soup.find_all(
        lambda x:
        x.name == 'li'
        and 'If you are using Chrome version' in x.text)

    def extract_ver(x):
        return re.match(r'.* (?P<ver>\d*),.*', x.text).group('ver')

    def extract_href(x):
        return x.findChild('a').get('href')

    ver_map = {extract_ver(x): extract_href(x) for x in li_list}
    return ver_map


def download_chromedriver_zip(version, chunk_size=128):
    """Download the zip containing the specified Chromedriver version.

    """
    log.info('Downloading Chromedriver zip file.')
    ver_map = get_chromedriver_version_map()
    if version not in ver_map:
        raise ValueError(f'Chromedriver for Chrome version {version} '
                         f'not available. Please update Chrome.')
    base_url = ver_map[version]
    cd_version = base_url.split('path=')[-1].strip().replace('/', '')
    dl_url = f'https://chromedriver.storage.googleapis.com/'
    dl_url += f'{cd_version}/chromedriver_win32.zip'
    zip_path = str(cfg.paths.downloads + f'chromedriver_win32.zip')
    req = requests.get(dl_url, stream=True)
    with open(zip_path, 'wb') as file:
        for chunk in req.iter_content(chunk_size=chunk_size):
            file.write(chunk)
    log.info('Finished downloading Chromedriver zip file.')
    return zip_path


def extract_chromedriver_zip(zip_path):
    """Extract the chromedriver zip file to is appropriate location in
    the Program Files (x86) folder.
    May require elevated admin permissions

    """
    log.info(f'Extracting chromedriver zip: {zip_path}')
    if not cfg.paths.chromedriver.parent().exists():
        log.info(f'Creating chromedriver parent directory')
        cfg.paths.chromedriver.parent().create()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(str(cfg.paths.chromedriver.parent()))
    log.info(f'Finished extracting chromedriver.')


def setup_chromedriver():
    """Setup Chromedriver for this computer (this may require elevated
    privileges.

    """
    log.info('Setting up Chromedriver.')
    chrome_ver = get_chrome_version()
    log.info(f'Chrome version is {chrome_ver}')
    chrome_ver_short = chrome_ver.split('.')[0]
    zip_path = download_chromedriver_zip(chrome_ver_short)
    extract_chromedriver_zip(zip_path)
    log.info('Chromedriver setup complete.')
