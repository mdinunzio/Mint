import mintkit.config as cfg
import mintkit.utils.logging
import mintkit.core.tasks
from mintkit.utils.formatting import usd
import pandas as pd
import numpy as np
import datetime
import re
import os


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)


# Income categories
INCOME = ['Income', 'Bonus', 'Interest Income', 'Paycheck', 'Reimbursement',
          'Rental Income', 'Returned Purchase']
# Wash categories
WASH = ['Credit Card Payment', 'Transfer', 'Investments']
# Transaction groups
GROUPS = ['Income', 'Rent', 'Recurring', 'Investments', 'Discretionary']

# Regular Expressions
TRANSACT_PATTERN = r'transactions(?: \((?P<instance>\d+)\))?\.csv'
TRANSACT_RE = re.compile(TRANSACT_PATTERN)


def _sort_files(x):
    """Return the sort key index for a transaction file.

    """
    match = TRANSACT_RE.match(x)
    if match['instance']:
        return int(match['instance'])
    else:
        return 0


def get_latest_file_location():
    """Return a string representing the location of the most
    recently downloaded transactions file.

    """
    dl_files = os.listdir(cfg.paths.downloads)
    trans_files = [x for x in dl_files if TRANSACT_RE.match(x)]
    trans_files.sort(key=_sort_files, reverse=True)
    trans_file = trans_files[0]
    return cfg.paths.downloads + trans_file


def delete_all_transaction_files():
    """Delete all transactions files in the Downloads folder.

    """
    dl_files = os.listdir(cfg.paths.downloads)
    trans_files = [x for x in dl_files if TRANSACT_RE.match(x)]
    for f in trans_files:
        try:
            fl_path = cfg.paths.downloads + f
            os.remove(str(fl_path))
        except Exception as e:
            print(e)


def get_next_month_start(month, year):
    """Return the date of the next month's first day.

    """
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year = year + 1
    next_month_start = datetime.date(next_year, next_month, 1)
    return next_month_start


def get_days_in_month(month, year):
    """Return the days in the given month.

    """
    curr_month_start = datetime.date(year, month, 1)
    next_start_of_month = get_next_month_start(month, year)
    tdelta = next_start_of_month - curr_month_start
    return tdelta.days


def get_recurring(template_path=None):
    """Return a dataframe of recurring transactions as outlined in
    the template file.

    """
    if template_path is None:
        template_path = cfg.paths.template
    recurring = pd.read_excel(str(template_path),
                              sheet_name='Recurring',
                              skiprows=2)
    recurring = recurring.dropna(subset=['Pattern'])
    return recurring


def match_recurring(x, recurring):
    """Return the subgroup of recurring transactions only.
    Otherwise return None.

    """
    for _, (subgroup, column, pattern, _, _) in recurring.iterrows():
        if re.match(pattern, x[column]):
            return subgroup
    return None


def get_investments(template_path=None):
    """Return a dataframe of investment transactions as outlined in
    the template file.

    """
    if template_path is None:
        template_path = cfg.paths.template
    investments = pd.read_excel(str(template_path),
                                sheet_name='Investments',
                                skiprows=2)
    investments = investments.dropna(subset=['Pattern'])
    return investments


def match_investments(x, investments):
    """Return the subgroup of investment transactions only.
    Otherwise return None.

    """
    for _, (subgroup, column, pattern, _, _) in investments.iterrows():
        if re.match(pattern, x[column]):
            return subgroup
    return None


def apply_transaction_groups(x, recurring, investments):
    """Return a transactions group and subgroup.
    Transaction groups can be either income, rent, recurring, or
    discretionary spending.
    This function may fail if the number of income or wash
    categories are expanded by Mint in the future.

    """
    # Check if rent
    if x['Category'] == 'Mortgage & Rent':
        return 'Rent', x['Category']
    # Check if income
    if x['Category'] in INCOME:
        if x['Category'] != 'Paycheck':
            return 'Income', x['Category']
        if x['Date'].day <= 20:
            return 'Income', 'Middle-of-Month'
        if x['Date'].day > 20:
            return 'Income', 'End-of-Month'
    # Check if investment
    invest_subgroup = match_investments(x, investments)
    if invest_subgroup:
        return 'Investments', invest_subgroup
    # Check if wash
    if x['Category'] in WASH:
        return 'Wash', x['Category']
    # Check if recurring
    recur_subgroup = match_recurring(x, recurring)
    if recur_subgroup:
        return 'Recurring', recur_subgroup
    # Otherwise, must be discretionary
    return 'Discretionary', 'Discretionary'


def get_transactions(file_path=None, refine=True):
    """Return a dataframe of the most specified Mint transactions file.
    If refine is set to True, then column types and values will be
    adjusted and the new Group and Subgroup columns will be added.

    """
    if file_path is None:
        file_path = get_latest_file_location()
    transactions = pd.read_csv(file_path)
    if not refine:
        return transactions
    transactions['Date'] = transactions['Date'].map(
        lambda x: pd.Timestamp(x).date())
    transactions['Amount'] = transactions.apply(
        lambda x:
        -x['Amount'] if x['Transaction Type'] == 'debit'
        else x['Amount'], axis=1)
    recurring = get_recurring()
    investments = get_investments()
    transactions[['Group', 'Subgroup']] = transactions.apply(
        apply_transaction_groups,
        axis=1,
        result_type='expand',
        args=(recurring, investments))
    return transactions


def get_date_index(start_date, end_date):
    """Return a Index with dates spanning the given start and end dates.

    """
    date_index = pd.date_range(start_date, end_date)
    date_index = date_index.map(lambda x: x.date())
    return date_index


def get_group_index(recurring, investments):
    """Return a MultiIndex with Groups and Subgroups that should be
    left-mergeable with summaries derived from Transaction data.
    This function could break if Mint later modifies their categories.

    """
    # Get income pairs
    paycheck_sg = ['Middle-of-Month', 'End-of-Month']
    other_income_sg = ['Bonus', 'Interest Income', 'Reimbursement',
                       'Rental Income', 'Returned Purchase', 'Income']
    income_sg = paycheck_sg + other_income_sg
    income_pairs = [('Income', sg) for sg in income_sg]
    rent_pairs = [('Rent', 'Mortgage & Rent')]
    recurring_pairs = [('Recurring', sg) for sg in
                       recurring['Subgroup'].tolist()]
    investment_pairs = [('Investments', sg) for sg in
                        investments['Subgroup'].tolist()]
    disc_pairs = [('Discretionary', 'Discretionary')]
    all_pairs = income_pairs + rent_pairs + recurring_pairs + \
        investment_pairs + disc_pairs
    group_index = pd.MultiIndex.from_tuples(
        all_pairs, names=['Group', 'Subgroup'])
    return group_index


def get_spending_by_day(transactions=None, lookback=5, append_total=False):
    """Return a DataFrame containing a summary of discretionary
    spending over the given lookback period.
    If total is set to True, the total spending sum over the lookback period
    will be included at the bottom of the returned dataframe.

    """
    if transactions is None:
        transactions = get_transactions()
    today = datetime.date.today()
    lookback_date = today - datetime.timedelta(days=lookback)
    discr = transactions[transactions['Group'] == 'Discretionary']
    discr = discr[discr['Date'] >= lookback_date]
    discretionary_count = len(discr)
    day_grp = discr.groupby('Date')
    day_spend = day_grp[['Amount']].sum()
    date_index = get_date_index(lookback_date, today)
    day_spend = day_spend.reindex(date_index)
    day_spend = day_spend.sort_index(ascending=False)
    day_spend['Day'] = day_spend.index.map(lambda x: '{:%a %d}'.format(x))
    day_spend = day_spend[['Day', 'Amount']]
    day_spend = day_spend.reset_index(drop=True)
    day_spend['Amount'] = day_spend['Amount'].fillna(0)
    if append_total:
        statlen = len(day_spend)
        day_spend.loc[statlen, 'Day'] = 'Total'
        day_spend.loc[statlen, 'Amount'] = day_spend['Amount'].sum()
    return day_spend, discretionary_count


def get_spending_by_group(transactions=None, month=None,
                          year=None, append_net=True):
    """Return a detailed DataFrame detailing transaction totals by group
    and subgroup.

    """
    if transactions is None:
        transactions = get_transactions()
    if month is None:
        month = datetime.date.today().month
    if year is None:
        year = datetime.datetime.today().year
    month_df = transactions.copy()
    month_df = month_df[month_df['Date'].map(lambda x: x.year) == year]
    month_df = month_df[month_df['Date'].map(lambda x: x.month) == month]
    group_grp = month_df.groupby(['Group', 'Subgroup', 'Transaction Type'])
    group_spend = group_grp.agg('sum')
    group_spend = group_spend.unstack(level=2)
    group_spend.columns = [x[1] for x in group_spend.columns]
    cols = ['debit', 'credit']
    for c in cols:
        if c not in group_spend.columns:
            group_spend[c] = 0
    group_spend = group_spend.reindex(GROUPS, level=0)
    group_spend = group_spend.fillna(0)
    group_spend['net'] = group_spend.sum(axis=1)
    if append_net:
        group_spend.loc['Net', 'net'] = group_spend['net'].sum()
    return group_spend


def get_excel_template_df(template_path=None):
    """Return a DataFrame of the the data from the template Excel sheet
    (Cash Flow.xlsm).

    """
    if template_path is None:
        template_path = cfg.paths.template
    template = pd.read_excel(template_path, usecols='A:E', header=5)
    template = template.rename(columns={'Unnamed: 0': 'Subgroup'})
    template = template.dropna(subset=['Subgroup'])
    template = template.drop('Realized', axis=1)
    return template


def apply_cash_flow_projections(x):
    """If the line item is income, return any nonzero realized items,
    otherwise return the expected column's value.
    If item is an expense, return the minimum between the expected
    and realized values.

    """
    if x['Group'] == 'Income':
        if x['Realized'] != 0:
            return x['Realized']
        else:
            return x['Expected']
    else:
        return min(x['Expected'], x['Realized'])


def get_cash_flow_summary(transactions=None, recurring=None, investments=None,
                          template_path=None, month=None, year=None):
    """Return a DataFrame that replicates the cash flow summary
    as it would be structured in the template Excel sheet (Cash Flow.xlsm).

    """
    if transactions is None:
        transactions = get_transactions()
    if recurring is None:
        recurring = get_recurring()
    if investments is None:
        investments = get_investments()

    template = get_excel_template_df(template_path)
    template = template[['Subgroup', 'Expected']]

    group_spend = get_spending_by_group(
        transactions, month, year, append_net=False)
    group_spend = group_spend.drop(['debit', 'credit'], axis=1)
    group_spend = group_spend.rename(columns={'net': 'Realized'})
    group_index = get_group_index(recurring, investments)
    group_spend = group_spend.reindex(group_index)
    group_spend = group_spend.reset_index()

    cash_flow = pd.merge(group_spend, template,
                         how='left',
                         on='Subgroup')
    cash_flow = cash_flow.fillna(0)
    cash_flow['Projected'] = cash_flow.apply(
        apply_cash_flow_projections, axis=1)
    cash_flow['RemainingCF'] = np.NaN
    cash_flow['RemainingNW'] = np.NaN
    cash_flow = cash_flow.set_index(['Group', 'Subgroup'])
    # Remaining after income
    paycheck_rem = cash_flow.loc[('Income', 'Middle-of-Month'), 'Projected']
    paycheck_rem += cash_flow.loc[('Income', 'End-of-Month'), 'Projected']
    cash_flow.loc[('Income', 'End-of-Month'), 'RemainingCF'] = paycheck_rem
    last_idx = [x[1] for x in cash_flow.index if x[0] == 'Income'][-1]
    income_rem = cash_flow.loc[('Income', slice(None)), 'Projected'].sum()
    cash_flow.loc[('Income', last_idx), 'RemainingNW'] = income_rem
    # Remaining after rent
    proj_rent = cash_flow.loc[('Rent', 'Mortgage & Rent'), 'Projected']
    rent_rem_cf = paycheck_rem + proj_rent
    rent_rem_nw = income_rem + proj_rent
    cash_flow.loc[('Rent', 'Mortgage & Rent'), 'RemainingCF'] = rent_rem_cf
    cash_flow.loc[('Rent', 'Mortgage & Rent'), 'RemainingNW'] = rent_rem_nw
    # Remaining after recurring
    proj_recur = cash_flow.loc[('Recurring', slice(None)), 'Projected'].sum()
    recur_rem_cf = rent_rem_cf + proj_recur
    recur_rem_nw = rent_rem_nw + proj_recur
    last_idx = [x[1] for x in cash_flow.index if x[0] == 'Recurring'][-1]
    cash_flow.loc[('Recurring', last_idx), 'RemainingCF'] = recur_rem_cf
    cash_flow.loc[('Recurring', last_idx), 'RemainingNW'] = recur_rem_nw
    # Remaining after investments
    proj_invest = cash_flow.loc[('Investments', slice(None)),
                                'Projected'].sum()
    invest_rem_cf = recur_rem_cf + proj_invest
    last_idx = [x[1] for x in cash_flow.index if x[0] == 'Investments'][-1]
    cash_flow.loc[('Investments', last_idx), 'RemainingCF'] = invest_rem_cf
    # Remaining after discretionary
    real_disc = cash_flow.loc[('Discretionary', 'Discretionary'), 'Realized']
    disc_rem_cf = invest_rem_cf + real_disc
    disc_rem_nw = recur_rem_nw + real_disc
    cash_flow.loc[('Discretionary', 'Discretionary'),
                  'RemainingCF'] = disc_rem_cf
    cash_flow.loc[('Discretionary', 'Discretionary'),
                  'RemainingNW'] = disc_rem_nw
    # Adjust special Discretionary expected case
    cash_flow.loc[('Discretionary', 'Discretionary'),
                  'Expected'] = min(-invest_rem_cf, 0)
    return cash_flow


def get_current_month_spending_stats(transactions=None, recurring=None,
                                     investments=None):
    """Return the amount spent, amount remaining, amount spent
    per day, and amount remaining per day for the given month.

    """
    if transactions is None:
        transactions = get_transactions()
    if recurring is None:
        recurring = get_recurring()
    if investments is None:
        investments = get_investments()
    today = datetime.date.today()
    day = today.day
    month = today.month
    year = today.year
    cash_flow = get_cash_flow_summary(
        transactions=transactions, recurring=recurring,
        investments=investments, month=month, year=year)
    spent = cash_flow.loc[('Discretionary', 'Discretionary'), 'Realized']
    rem_cf = cash_flow.loc[('Discretionary', 'Discretionary'), 'RemainingCF']
    rem_nw = cash_flow.loc[('Discretionary', 'Discretionary'), 'RemainingNW']
    days_in_month = get_days_in_month(month, year)
    # Only days left includes today
    days_left = days_in_month - day + 1
    spent_pace = spent / (day - 1)
    rem_cf_pace = rem_cf / days_left
    rem_nw_pace = rem_nw / days_left
    return spent, spent_pace, rem_cf, rem_cf_pace, rem_nw, rem_nw_pace


def get_recent_spending_summary(transactions=None, recurring=None, lookback=5):
    """Return an HTML string summarizing recent discretionary spending
    activity.

    """
    if transactions is None:
        transactions = get_transactions()
    if recurring is None:
        recurring = get_recurring()
    df_lookback, count_lookback = get_spending_by_day(
        transactions=transactions, lookback=lookback, append_total=False)
    spent_lookback = df_lookback['Amount'].sum()
    spent_lookback_pace = spent_lookback / len(df_lookback)
    (spent,
     spent_pace,
     rem_cf,
     rem_cf_pace,
     rem_nw,
     rem_nw_pace) = get_current_month_spending_stats(
        transactions=transactions, recurring=recurring)
    today = datetime.date.today()
    summary = f'{lookback:.0f}d: ({count_lookback:.0f} items)<br><br>'
    summary += df_lookback.to_html(header=False, index=False)
    summary += f'<br><br>Spent {lookback:.0f}d: {usd(spent_lookback, 0)}<br>'
    summary += f'Pace {lookback:.0f}d: {usd(spent_lookback_pace, 0)}<br><br>'
    summary += f'Spent {today:%b}: {usd(spent, 0)}<br>'
    summary += f'Spent {today:%b}/Day: {usd(spent_pace, 0)}<br>'
    summary += f'Remaining NW {today:%b}: {usd(rem_nw, 0)}<br>'
    summary += f'Remaining NW/Day: {usd(rem_nw_pace, 0)}<br>'
    summary += f'Remaining CF {today:%b}: {usd(rem_cf, 0)}<br>'
    summary += f'Remaining CF/Day: {usd(rem_cf_pace, 0)}<br>'
    return summary
