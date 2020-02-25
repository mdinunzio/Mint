import config as cfg
import scrapekit
import pandas as pd
import datetime
import json
import os


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# File locations
FIN_LOC = os.path.join(cfg.LOCAL_DIR, 'finances.json')
with open(FIN_LOC, 'r') as f:
    FIN_JSON = json.load(f)
CF_LOC = FIN_JSON['cf_loc']


def get_utility_patterns():
    """
    Return a dictionary of utility line items and their regex patterns.
    """
    utils = pd.read_excel(CF_LOC, sheet_name="Dashboard",
                          header=17, usecols="H:I")
    utils = utils.dropna(subset=['Column'])
    utils = utils.set_index('Column')['Pattern']
    utils = utils.map(lambda x: x.replace('*', '*.'))
    util_patterns = utils.to_dict()
    return util_patterns


class TransactionManager():
    def __init__(self, month=None, year=None, fl_loc=None):
        self.month = month
        self.year = year
        if self.month is None:
            self.month = datetime.date.today().month
        if self.year is None:
            self.year = datetime.date.today().year
        self.fl_loc = fl_loc
        self.set_df()

    def set_df(self):
        """
        Set the dataframe of transactions and refine its contents.
        """
        if self.fl_loc is None:
            self.fl_loc = scrapekit.get_latest_file_location()
        self.transactions = pd.read_csv(self.fl_loc)
        self.transactions['Date'] = self.transactions['Date'].map(
            lambda x: pd.Timestamp(x).date())
        self.transactions['Amount'] = self.transactions.apply(
            lambda x: -x['Amount'] if x['Transaction Type'] == 'debit'
            else x['Amount'], axis=1)

    def __repr__(self):
        return f'Tranasactions {self.month:.0f}/{self.year:.0f}'
