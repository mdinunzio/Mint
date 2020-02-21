import json
import os
import sys
import getpass
from dataclasses import dataclass


# SETUP ######################################################################

# File locations
this_loc = __file__
parent_dir = os.path.abspath(os.path.join(this_loc, '..'))
local_dir = os.path.abspath(os.path.join(parent_dir, '..', 'local'))

# Globals
mint = None
twilio = None
user_data = None


# MAIN #######################################################################

# Objects
@dataclass
class MintCredentials:
    email: str
    password: str


@dataclass
class TwilioCredentials:
    account_sid: str
    auth_token: str
    number: str


@dataclass
class UserData:
    number: str


def _setup_mint():
    """
    Set up the MintCredentials global instance.
    """
    global mint
    mint_fl = os.path.join(local_dir, 'mint.json')
    with open(mint_fl, 'r') as f:
        mint_json = json.load(f)
    mint = MintCredentials(**mint_json)


def _setup_twilio():
    """
    Set up the TwilioCredentials global instance.
    """
    global twilio
    twilio_fl = os.path.join(local_dir, 'twilio.json')
    with open(twilio_fl, 'r') as f:
        twilio_json = json.load(f)
    twilio = TwilioCredentials(**twilio_json)


def _setup_user():
    """
    Set up the UserData global instance.
    """
    global user_data
    user_fl = os.path.join(local_dir, 'user_data.json')
    with open(user_fl, 'r') as f:
        user_json = json.load(f)
    user_data = UserData(**user_json)


_setup_mint()
_setup_twilio()
_setup_user()
