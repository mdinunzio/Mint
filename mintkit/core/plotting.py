import matplotlib.pyplot as plt


def graph_discretionary(self, start_date=None, end_date=None,
                        appdata=False):
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
    if appdata:
        plt.savefig(cfg.DATA_DIR + r'\spending.png')
    else:
        plt.savefig(cfg.DT_DIR + r'\spending.png')
    plt.close()


def plot_spending(self, month, year, appdata=False):
    if month is None:
        month = datetime.date.today().month
    if year is None:
        year = datetime.date.today().year
    start_date = datetime.date(year, month, 1)
    next_start = get_next_month_start(month, year)
    end_date = next_start - datetime.timedelta(days=1)
    days = get_days_in_month(month, year)
    discr = self.df[self.df['Group'] == 'Discretionary']
    discr = discr[discr['Date'] >= start_date]
    discr = discr[discr['Date'] <= end_date]
    discr_dly = discr.groupby('Date')[['Amount']].sum()
    discr_max = discr_dly.index.max()
    if not isinstance(discr_max, datetime.date):
        discr_max = pd.NaT
    latest_date = max(datetime.date.today(), discr_max)
    latest_date = min(latest_date, end_date)
    lhs = pd.DataFrame(columns=['Date'],
                       data=pd.date_range(start_date, latest_date))
    lhs['Date'] = lhs['Date'].map(lambda x: x.date())
    discr_dly = pd.merge(lhs, discr_dly, how='left', on='Date')
    discr_dly['Amount'] = discr_dly['Amount'].fillna(0)
    discr_dly['Amount'] = discr_dly['Amount'].cumsum()
    discr_dly['Amount'] *= -1
    cash_ws = get_cash_flow_sheet()
    cash_ws = cash_ws.set_index('Item')
    discr_inc = cash_ws.loc['Recurring', 'Remaining']
    discr_inc_dly = pd.DataFrame(
        data=zip(pd.date_range(start_date, end_date),
                 [discr_inc / days] * days),
        columns=['Date', 'Income'])
    discr_inc_dly['Date'] = discr_inc_dly['Date'].map(lambda x: x.date())
    discr_inc_dly['Income'] = discr_inc_dly['Income'].cumsum()
    fig = plt.figure()
    ax = plt.subplot(111)
    plt.plot_date(discr_inc_dly['Date'], discr_inc_dly['Income'], '-')
    plt.plot_date(discr_dly['Date'], discr_dly['Amount'], '-')
    plt.title('Spending By Day')
    plt.xticks(rotation=45)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.tight_layout()
    if appdata:
        plt.savefig(cfg.DATA_DIR + r'\spending.png')
    else:
        plt.savefig(cfg.DT_DIR + r'\spending.png')
    plt.close()