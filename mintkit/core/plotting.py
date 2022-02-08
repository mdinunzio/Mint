import mintkit.settings as cfg
import mintkit.utils.logs
import mintkit.core.analytics
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
import pandas as pd
import numpy as np
import datetime


log = mintkit.utils.logs.get_logger(cfg.PROJECT_NAME)
register_matplotlib_converters()


def plot_spending(transactions=None, recurring=None, investments=None,
                  month=None, year=None):
    """Plot actual spending by day alongside the linear prorated spending
    rate.

    """
    today = datetime.date.today()
    if month is None:
        month = today.month
    if year is None:
        year = today.year
    if transactions is None:
        transactions = mintkit.core.analytics.get_transactions()
    if recurring is None:
        recurring = mintkit.core.analytics.get_recurring()
    if investments is None:
        investments = mintkit.core.analytics.get_investments()
    start_date = datetime.date(year, month, 1)
    next_start = mintkit.core.analytics.get_next_month_start(month, year)
    end_date = next_start - datetime.timedelta(days=1)
    days = mintkit.core.analytics.get_days_in_month(month, year)
    discr = transactions.copy(deep=True)
    discr = discr[discr['Group'] == 'Discretionary']
    discr = discr[discr['Date'] >= start_date]
    discr = discr[discr['Date'] <= end_date]
    discr_grp = discr.groupby('Date')
    discr_stats = discr_grp[['Amount']].sum()
    discr_max_date = discr_stats.index.max()
    if not isinstance(discr_max_date, datetime.date):
        discr_max_date = pd.NaT
    latest_date = max(datetime.date.today(), discr_max_date)
    latest_date = min(latest_date, end_date)
    lhs = pd.DataFrame(
        columns=['Date'],
        data=mintkit.core.analytics.get_date_index(start_date, latest_date))
    discr_stats = pd.merge(lhs, discr_stats, how='left', on='Date')
    discr_stats['Amount'] = discr_stats['Amount'].fillna(0)
    discr_stats['Amount'] = discr_stats['Amount'].cumsum()
    discr_stats['Amount'] *= -1
    cash_flow = mintkit.core.analytics.get_cash_flow_summary(
        transactions=transactions, recurring=recurring,
        investments=investments, month=month, year=year)
    discr_cf = cash_flow.loc[('Investments', slice(None)),
                             'RemainingCF'].iloc[-1]
    discr_nw = cash_flow.loc[('Recurring', slice(None)),
                             'RemainingNW'].iloc[-1]
    # Adjust for over-investment
    inv_exp = cash_flow.loc[('Investments', slice(None)),
                            'Expected'].sum()
    recur_rem_cf = cash_flow.loc[('Recurring', slice(None)),
                                 'RemainingCF'].iloc[-1]
    discr_cf_exp = recur_rem_cf + inv_exp
    discr_dly = pd.DataFrame(
        data=zip(mintkit.core.analytics.get_date_index(start_date, end_date),
                 np.arange(discr_cf / days,
                           discr_cf,
                           discr_cf / days),
                 np.arange(discr_nw / days,
                           discr_nw,
                           discr_nw / days),
                 np.arange(discr_cf_exp / days,
                           discr_cf_exp,
                           discr_cf_exp / days)),
        columns=['Date', 'AllocatedCF', 'AllocatedNW', 'AllocatedCFExp'])
    fig, ax = plt.subplots()
    plt.plot_date(discr_dly['Date'], discr_dly['AllocatedNW'], '-')
    # Dotted line will only appear when spending on investments exceeds
    # expectations
    plt.plot_date(discr_dly['Date'], discr_dly['AllocatedCFExp'], '--')
    plt.plot_date(discr_dly['Date'], discr_dly['AllocatedCF'], '-')
    plt.plot_date(discr_stats['Date'], discr_stats['Amount'], '-')
    plt.title('Spending By Day')
    plt.xticks(rotation=45)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.tight_layout()
    plt.savefig(str(cfg.paths.plots + r'spending.png'))
    plt.close()
