import json
import os
import sys
import getpass
from dataclasses import dataclass


# SETUP ######################################################################

# File locations
auth_loc = __file__
parent_dir = os.path.abspath(os.path.join(auth_loc, '..'))
local_dir = os.path.abspath(os.path.join(parent_dir, '..', 'local'))

# Globals
mint = None


# MAIN #######################################################################

# Objects
@dataclass
class MintCredentials:
    email: str
    password: str


# PredictIt Cookies and header authorization
def _setup_mint():
    """
    Set up the PredictItCredentials global variable.
    """
    global mint
    mint_fl = os.path.join(local_dir, 'mint.json')
    with open(mint_fl, 'r') as f:
        mint_json = json.load(f)
    mint = MintCredentials(**mint_json)


_setup_mint()
