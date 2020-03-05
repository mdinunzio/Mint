import config as cfg
import scrapekit
import pandas as pd
import datetime
import json
import os
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# File locations
FIN_LOC = os.path.join(cfg.LOCAL_DIR, 'finances.json')
with open(FIN_LOC, 'r') as f:
    FIN_JSON = json.load(f)
CF_LOC = FIN_JSON['cf_loc']

# Establish patterns for identifying recurring expenses
recurring = pd.read_excel(CF_LOC, sheet_name="Dashboard", usecols="K:M")
first_col = recurring.columns[0]
col_idx = recurring[recurring[first_col] == 'Column'].index[0]
recurring.columns = recurring.loc[col_idx, :]
recurring.columns.name = None
recurring = recurring.drop(col_idx)
recurring = recurring.dropna(subset=['Column'])
recurring = recurring.reset_index(drop=True)
recurring_patterns = [(r['Column'], r['Pattern'])
                      for _, r in recurring.iterrows()]
# Income categories
income_categories = ['Income', 'Bonus', 'Interest Income', 'Paycheck',
                     'Reimbursement', 'Rental Income', 'Returned Purchase']

# Bookkeeping categories
bookkeeping_categories = ['Credit Card Payment', 'Transfer']


# FUNCTIONS #################################################################

def apply_transaction_groups(x):
    """
    Label a transaction as income, rent, recurring, or
    discretionary spending.
    """
    # Check if rent
    if x['Category'] == 'Mortgage & Rent':
        return 'Rent'
    # Check if income
    if x['Category'] in income_categories:
        return 'Income'
    # Check if bookkeeping
    if x['Category'] in bookkeeping_categories:
        return 'Bookkeeping'
    # Check if recurring
    if any([re.match(y[1], x[y[0]]) for y in recurring_patterns]):
        return 'Recurring'
    # Otherwise, must be discretionary
    return 'Discretionary'

def apply_transaction_subgroups():
    pass

def get_cash_flow_model():
    """
    Return a DataFrame of expected monthly cash flow.
    """
    cfm = pd.read_excel(CF_LOC, usecols='A:E', header=5)
    cfm = cfm.rename(columns={'Unnamed: 0': 'Item'})
    cfm = cfm.dropna(subset=['Item'])
    cfm = cfm.drop('Realized', axis=1)
    return cfm


# MODELS #####################################################################

class TransactionManager():
    def __init__(self, fl_loc=None):
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

    def summarize_month(self, month, year=None):
        """
        Return a DataFrame summarizing monthly cash flow.
        """
        if year is None:
            year = datetime.datetime.today().year
        month_df = self.df.copy()
        month_df = month_df[month_df['Date'].map(lambda x: x.year) == year]
        month_df = month_df[month_df['Date'].map(lambda x: x.month) == month]
        mgrp = month_df.groupby(['Group', 'Transaction Type'])
        mstats = mgrp.agg('sum')
        mstats = mstats.unstack(level=1)
        mstats = mstats.fillna(0)
        mstats.columns = [x[1] for x in mstats.columns]
        mstats['net'] = mstats.sum(axis=1)
        mstats = mstats.drop('Bookkeeping')
        mstats.loc['Net', :] = mstats.sum()
        return mstats

    def get_month_pacing(self, month=None):
        

    def graph_discretionary(self, start_date=None, end_date=None):
        """
        Graph discretionary spending by day for a given time period.
        """
        if start_date is None:
            today = datetime.date.today()
            start_date = datetime.date(today.year, today.month, 1)
        if end_date is None:
            next_start = datetime.date(
                start_date.year, start_date.month + 1, 1)
            end_date = next_start - datetime.timedelta(days=1)
        period_df = self.df.copy()
        period_df = period_df[period_df['Date'] >= start_date]
        period_df = period_df[period_df['Date'] <= end_date]
        discr = period_df[period_df['Group'] == 'Discretionary']
        dgrp = discr.groupby('Date')
        dsum = -dgrp['Amount'].sum()
        plt.figure()
        ax = plt.subplot(111)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.bar(dsum.index, dsum.values)
        ax.xaxis_date()
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(cfg.DT_DIR + r'\spending.png')

    def __repr__(self):
        max_date = self.df['Date'].max()
        return f'Tranasactions up to {max_date}'
