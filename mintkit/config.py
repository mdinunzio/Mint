import mintkit.utils.paths
import mintkit.utils.logging
import os
import pandas as pd

PROJECT_NAME = 'MintKit'

# path definition
paths = mintkit.utils.paths.PathManager()
paths.base = mintkit.utils.paths.Path(__file__) + '..'
paths.home = mintkit.utils.paths.Path(os.path.expanduser('~'))
paths.desktop = paths.home + 'Desktop'
paths.downloads = paths.home + 'Downloads'
paths.local = paths.home + 'AppData' + 'Local'
paths.appdata = paths.local + PROJECT_NAME
paths.logs = paths.appdata + 'logs'
paths.user = paths.appdata + paths.home[-1]
paths.creds = paths.user + 'creds'
paths.plots = paths.user + 'plots'
paths.x86 = mintkit.utils.paths.Path(r"C:\Program Files (x86)")
paths.chrome = paths.x86 + r'Google\Chrome\Application\chrome.exe'
paths.chrome_profile = paths.local + r'Google\Chrome\User Data\Default'
paths.chromedriver = paths.x86 + r'chromedriver_win32\chromedriver.exe'
paths.template = paths.home + r'Google Drive\Finances\Cash Flow.xlsm'

# path creation
if not paths.appdata.exists():
    paths.appdata.create()
if not paths.logs.exists():
    paths.logs.create()
if not paths.creds.exists():
    paths.creds.create()
if not paths.plots.exists():
    paths.plots.create()

# debug settings
DEBUG = os.environ.get('MINTKITDEBUG') == 1

# logging setup
mintkit.utils.logging.set_logging_directory(paths.logs)
mintkit.utils.logging.set_debug_mode(DEBUG)
log = mintkit.utils.logging.get_logger(PROJECT_NAME)

# pandas setup
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
