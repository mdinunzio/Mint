import mintkit.utils.logging
import mintkit.utils.paths
import os
import pandas as pd

PROJECT_NAME = 'MintKit'

# logging setup

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# File locations
THIS_LOC = __file__
PARENT_DIR = os.path.abspath(os.path.join(THIS_LOC, '..'))
LOCAL_DIR = os.path.abspath(os.path.join(PARENT_DIR, '..', 'local'))

USR_DIR = os.path.expanduser('~')
DT_DIR = os.path.join(USR_DIR, 'Desktop')
AD_DIR = os.path.join(USR_DIR, 'AppData', 'Local')

DATA_DIR = os.path.join(AD_DIR, 'Mint')
