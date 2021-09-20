import mintkit.utils.paths
import mintkit.utils.logging
import os
import pandas as pd


PROJECT_NAME = 'MintKit'

# path definition
paths = mintkit.utils.paths.PathManager()
paths.app = mintkit.utils.paths.Path(__file__) + '..'
paths.base = paths.app + '..'
paths.home = mintkit.utils.paths.Path(os.path.expanduser('~'))
paths.desktop = paths.home + 'Desktop'
paths.downloads = paths.home + 'Downloads'
paths.local = paths.home + 'AppData' + 'Local'
paths.appdata = paths.local + PROJECT_NAME
paths.logs = paths.appdata + 'logs'
paths.user = paths.appdata + paths.home[-1]
paths.settings = paths.user + 'settings'
paths.creds = paths.user + 'creds'
paths.plots = paths.user + 'plots'
paths.x86 = mintkit.utils.paths.Path(r"C:\Program Files (x86)")
paths.chrome = paths.x86 + r'Google\Chrome\Application\chrome.exe'
paths.chrome_profile = paths.local + r'Google\Chrome\User Data\Default'
paths.chromedriver = paths.user + r'chromedriver_win32\chromedriver.exe'
# ensure paths exist
mintkit.utils.paths.create_key_paths(paths)
# get template path
paths.template = mintkit.utils.paths.get_template_path(paths)


# debug settings
DEBUG = os.environ.get('MINTKITDEBUG') == 1

# logging setup
mintkit.utils.logging.set_logging_directory(paths.logs)
mintkit.utils.logging.set_debug_mode(DEBUG)
log = mintkit.utils.logging.get_logger(PROJECT_NAME)

# pandas setup
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
