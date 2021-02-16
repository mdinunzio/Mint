import mintkit.config as cfg
import mintkit.utils.logging
import mintkit.core.analytics
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import datetime


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)


def plot_spending(transactions=None, recurring=None, month=None, year=None):
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
        month=month, year=year)
    discr_inc = cash_flow.loc[('Recurring', slice(None)), 'Remaining'].iloc[-1]
    discr_inc_dly = pd.DataFrame(
        data=zip(mintkit.core.analytics.get_date_index(start_date, end_date),
                 np.arange(discr_inc / days, discr_inc, discr_inc / days)),
        columns=['Date', 'Allocated'])
    fig, ax = plt.subplots()
    plt.plot_date(discr_inc_dly['Date'], discr_inc_dly['Allocated'], '-')
    plt.plot_date(discr_stats['Date'], discr_stats['Amount'], '-')
    plt.title('Spending By Day')
    plt.xticks(rotation=45)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.tight_layout()
    plt.savefig(str(cfg.paths.plots + r'spending.png'))
    plt.close()
