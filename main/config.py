import os

# File locations
THIS_LOC = __file__
PARENT_DIR = os.path.abspath(os.path.join(THIS_LOC, '..'))
LOCAL_DIR = os.path.abspath(os.path.join(PARENT_DIR, '..', 'local'))

USR_DIR = os.path.expanduser('~')
DT_DIR = os.path.join(USR_DIR, 'Desktop')
