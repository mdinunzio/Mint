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
paths.appdata = paths.home + 'AppData' + 'Local' + PROJECT_NAME
paths.logs = paths.appdata + 'logs'
# path creation
if not paths.appdata.exists():
    paths.appdata.create()
if not paths.logs.exists():
    paths.logs.create()

# debug settings
DEBUG = os.environ.get('MINTKITDEBUG') == 1

# logging setup
mintkit.utils.logging.set_logging_directory(paths.logs)
mintkit.utils.logging.set_debug_mode(DEBUG)
log = mintkit.utils.logging.get_logger(PROJECT_NAME)

# pandas setup
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

