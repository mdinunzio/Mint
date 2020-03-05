import config as cfg
import scrapekit
import pandas as pd
import numpy as np
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

# Income categories
INCOME_CAT = ['Income', 'Bonus', 'Interest Income', 'Paycheck',
              'Reimbursement', 'Rental Income', 'Returned Purchase']

# Bookkeeping categories
BOOKKEEPING_CAT = ['Credit Card Payment', 'Transfer']


# FUNCTIONS #################################################################

def get_cash_flow_model():
    """
    Return a DataFrame of expected monthly cash flow.
    """
    cfm = pd.read_excel(CF_LOC, usecols='A:E', header=5)
    cfm = cfm.rename(columns={'Unnamed: 0': 'Item'})
    cfm = cfm.dropna(subset=['Item'])
    cfm = cfm.drop('Realized', axis=1)
    return cfm


def get_cash_flow_structure(recur_mgr):
    """
    Return a DataFrame with Groups and Subgroups that should be
    left-mergeable with summaries derived from Transaction data.
    """
    # Get income pairs
    paycheck_sg = ['Middle-of-Month', 'End-of-Month']
    other_income_sg = ['Bonus', 'Interest Income', 'Reimbursement',
                       'Rental Income', 'Returned Purchase', 'Income']
    income_sg = paycheck_sg + other_income_sg
    income_pairs = [('Income', sg) for sg in income_sg]
    rent_pairs = [('Mortgage & Rent', 'Mortgage & Rent')]
    recurring_pairs = [('Recurring', sg) for sg in
                       recur_mgr.df['Subgroup'].tolist()]
    disc_pairs = [('Discretionary', 'Discretionary')]
    all_pairs = income_pairs + rent_pairs + recurring_pairs + disc_pairs
    cf_structure = pd.DataFrame(columns=['Group', 'Subgroup'],
                                data=all_pairs)
    return cf_structure
    # Get


# MODELS #####################################################################

class RecurringManager():
    def __init__(self):
        # Recurring categories setup
        df = pd.read_excel(CF_LOC,
                           sheet_name="Dashboard",
                           usecols="A:M")
        col_map = {'Month': 'Subgroup',
                   'Unnamed: 10': 'Column',
                   'Unnamed: 11': 'Pattern'}
        df = df.rename(columns=col_map)
        df = df.dropna(subset=list(col_map.values()))
        cols = ['Subgroup', 'Column', 'Pattern']
        df = df[cols]
        df = df.reset_index(drop=True)
        self.df = df

    def get_subgroup(self, row):
        """
        Return the subgroup for a Transaction Manager's DataFrame
        if the row corresponds to a recurring transaction, otherwise
        return None
        """
        for _, (subgroup, column, pattern) in self.df.iterrows():
            if re.match(pattern, row[column]):
                return subgroup
        return None


class TransactionManager():
    def __init__(self, fl_loc=None):
        self.fl_loc = fl_loc
        self.set_df()

    def apply_transaction_groups(self, x):
        """
        Label a transaction as income, rent, recurring, or
        discretionary spending, as well as it's subgroup.
        This may fail if the number of income or bookkeeping
        categories are expanded by Mint.
        """
        # Check if rent
        if x['Category'] == 'Mortgage & Rent':
            return 'Rent', x['Category']
        # Check if income
        if x['Category'] in INCOME_CAT:
            if x['Category'] != 'Paycheck':
                return 'Income', x['Category']
            if x['Date'].day <= 20:
                return 'Income', 'Middle-of-Month'
            if x['Date'].day > 20:
                return 'Income', 'End-of-Month'
        # Check if bookkeeping
        if x['Category'] in BOOKKEEPING_CAT:
            return 'Bookkeeping', x['Category']
        # Check if recurring
        recur_subgroup = self.recur_mgr.get_subgroup(x)
        if recur_subgroup:
            return 'Recurring', recur_subgroup
        # Otherwise, must be discretionary
        return 'Discretionary', 'Discretionary'

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
        self.recur_mgr = RecurringManager()
        self.df[['Group', 'Subgroup']] = self.df.apply(
            self.apply_transaction_groups, axis=1, result_type='expand')

    def get_spending_by_day(self, n=5, total=False, count=False):
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

    def get_short_summary(self, month, year=None, net=True):
        """
        Return a short DataFrame summarizing monthly cash flow.
        """
        if year is None:
            year = datetime.datetime.today().year
        month_df = self.df.copy()
        month_df = month_df[month_df['Date'].map(lambda x: x.year) == year]
        month_df = month_df[month_df['Date'].map(lambda x: x.month) == month]
        mgrp = month_df.groupby(['Group', 'Transaction Type'])
        mstats = mgrp.agg('sum')
        mstats = mstats.unstack(level=1)
        mstats.columns = [x[1] for x in mstats.columns]
        cols = ['debit', 'credit']
        for c in cols:
            if c not in mstats.columns:
                mstats[c] = 0
        mstats['net'] = mstats.sum(axis=1)
        idx_order = ['Income', 'Rent', 'Recurring', 'Discretionary']
        mstats = mstats.reindex(idx_order)
        mstats = mstats.fillna(0)
        if net:
            mstats.loc['Net', :] = mstats.sum()
        return mstats

    def get_long_summary(self, month, year=None, net=True):
        """
        Return a detailed DataFrame summarizing monthly cash flow.
        """
        if year is None:
            year = datetime.datetime.today().year
        month_df = self.df.copy()
        month_df = month_df[month_df['Date'].map(lambda x: x.year) == year]
        month_df = month_df[month_df['Date'].map(lambda x: x.month) == month]
        mgrp = month_df.groupby(['Group', 'Subgroup', 'Transaction Type'])
        mstats = mgrp.agg('sum')
        mstats = mstats.unstack(level=2)
        mstats.columns = [x[1] for x in mstats.columns]
        cols = ['debit', 'credit']
        for c in cols:
            if c not in mstats.columns:
                mstats[c] = 0
        idx_order = ['Income', 'Rent', 'Recurring', 'Discretionary']
        mstats = mstats.unstack(level=1)
        mstats = mstats.reindex(idx_order)
        mstats = mstats.stack(level=1)
        mstats = mstats.fillna(0)
        mstats['net'] = mstats.sum(axis=1)
        if net:
            mstats.loc['Net', 'net'] = mstats['net'].sum()
        return mstats

    def get_cash_flow_summary(self, month=None, year=None):
        """
        Return a DataFrame that replicates the Cash Flow Excel sheet.
        """
        if month is None:
            month = datetime.date.today().month
        if year is None:
            year = datetime.date.today().year

        cf_struct = get_cash_flow_structure(self.recur_mgr)
        cf_model = get_cash_flow_model()
        cf_model = cf_model[['Item', 'Expected']]
        cf_model = cf_model.rename(columns={'Item': 'Subgroup'})

        ls = self.get_long_summary(month, year, net=False)
        ls = ls.reset_index()
        ls = ls.drop(['debit', 'credit'], axis=1)
        ls = ls.rename(columns={'net': 'Realized'})

        cf_smry = pd.merge(cf_struct, cf_model,
                           how='left',
                           on='Subgroup')
        cf_smry = pd.merge(cf_smry, ls,
                           how='left',
                           on=['Group', 'Subgroup'])
        cf_smry = cf_smry.fillna(0)

        def apply_cf_projections(x):
            """
            If the line item is income, return any nonzero realized items,
            otherwise return the expected column's value.
            If item is an expense, return the minimum between expected
            and realized.
            """
            if x['Group'] == 'Income':
                if x['Realized'] != 0:
                    return x['Realized']
                else:
                    return x['Expected']
            else:
                return min(x['Expected'], x['Realized'])

        cf_smry['Projected'] = cf_smry.apply(apply_cf_projections, axis=1)

        cf_smry['Remaining'] = np.NaN
        cf_smry = cf_smry.set_index(['Group', 'Subgroup'])
        # Remaining after income
        income_rem = cf_smry.loc[('Income', slice(None)), 'Projected'].sum()
        last_idx = [x[1] for x in cf_smry.index if x[0] == 'Income'][-1]
        cf_smry.loc[('Income', last_idx), 'Remaining'] = income_rem
        # Remaining after rent
        proj_rent = cf_smry.loc[
            ('Mortgage & Rent', 'Mortgage & Rent'), 'Projected']
        rent_rem = income_rem + proj_rent
        cf_smry.loc['Mortgage & Rent', 'Remaining'] = rent_rem
        # Remaining after recurring
        proj_recur = cf_smry.loc[
            ('Recurring', slice(None)), 'Projected'].sum()
        proj_rem = rent_rem + proj_recur
        last_idx = [x[1] for x in cf_smry.index if x[0] == 'Recurring'][-1]
        cf_smry.loc[('Recurring', last_idx), 'Remaining'] = proj_rem
        # Remaining after discretionary
        real_disc = cf_smry.loc[('Discretionary',
                                 'Discretionary'),
                                'Realized']
        disc_rem = proj_rem + real_disc
        cf_smry.loc['Discretionary', 'Remaining'] = disc_rem
        return cf_smry

    def get_month_pacing(self, month=None, year=None):
        if month is None:
            month = datetime.date.today().month
        if year is None:
            year = datetime.date.today().year
        lsum = self.get_long_summary(month, year)

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
        plt.close()

    def __repr__(self):
        max_date = self.df['Date'].max()
        return f'Tranasactions up to {max_date}'
