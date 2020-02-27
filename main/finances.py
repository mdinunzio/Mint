import config as cfg
import scrapekit
import pandas as pd
import datetime
import json
import os
import re


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# File locations
FIN_LOC = os.path.join(cfg.LOCAL_DIR, 'finances.json')
with open(FIN_LOC, 'r') as f:
    FIN_JSON = json.load(f)
CF_LOC = FIN_JSON['cf_loc']

# Establish patterns for identifying utility expenses
utils = pd.read_excel(CF_LOC, sheet_name="Dashboard",
                      header=17, usecols="H:I")
utils = utils.dropna(subset=['Column'])
util_patterns = [(r['Column'], r['Pattern']) for _, r in utils.iterrows()]


def apply_transaction_groups(x):
    """
    Label a transaction as income, rent, utilities, or
    discretionary spending.
    """
    # Check if rent
    if x['Category'] == 'Mortgage & Rent':
        return 'Rent'
    # Check if income
    if x['Category'] == 'Income':
        return 'Income'
    # Check if utility
    if any([re.match(y[1], x[y[0]]) for y in util_patterns]):
        return 'Utilities'
    # Otherwise, must be discretionary
    return 'Discretionary'


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
        self.df = pd.read_csv(self.fl_loc)
        self.df['Date'] = self.df['Date'].map(
            lambda x: pd.Timestamp(x).date())
        self.df['Amount'] = self.df.apply(
            lambda x: -x['Amount'] if x['Transaction Type'] == 'debit'
            else x['Amount'], axis=1)
        self.df['Group'] = self.df.apply(apply_transaction_groups, axis=1)

    def get_spending_summary(self, n=5, total=False, count=False):
        """
        Return a DataFrame containing an n-day summary of
        discretionary spending.
        Optionally return the count of tranactions.
        """
        today = datetime.date.today()
        tmn = today - datetime.timedelta(days=n)
        spend = self.df[self.df['Group'] == 'Discretionary']
        spend5d = spend[spend['Date'] >= tmn]
        spend_count = len(spend5d)
        spend_grp = spend5d.groupby('Date')
        spend_stats = spend_grp[['Amount']].sum()
        spend_stats = spend_stats.reset_index()
        spend_stats = spend_stats.sort_values('Date', ascending=False)
        spend_stats['Day'] = spend_stats['Date'].map(
            lambda x: '{:%a %d}'.format(x))
        spend_stats = spend_stats[['Day', 'Amount']]
        spend_stats = spend_stats.reset_index(drop=True)
        if total:
            slen = len(spend_stats)
            spend_stats.loc[slen, 'Day'] = 'Total'
            spend_stats.loc[slen, 'Amount'] = spend_stats['Amount'].sum()
        if count:
            return spend_stats, spend_count
        return spend_stats

    def __repr__(self):
        return f'Tranasactions {self.month:.0f}/{self.year:.0f}'
