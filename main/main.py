import config as cfg
import scrapekit
import sms
import time
import pandas as pd
import datetime
import argparse


def refresh_accounts_and_kill():
    """
    Refresh Mint accounts then kill the driver.
    """
    ms = scrapekit.MintScraper()
    ms.refresh_accounts()
    time.sleep(15 * 60)
    ms.driver.quit()


def download_and_kill():
    """
    Download Mint transactions then kill the driver.
    """
    ms = scrapekit.MintScraper()
    ms.download_transactions()
    time.sleep(30)
    ms.driver.quit()


def send_daily_update():
    download_and_kill()
    fl_loc = scrapekit.get_latest_file_location()
    trans = pd.read_csv(fl_loc)
    trans['Date'] = trans['Date'].map(lambda x: pd.Timestamp(x).date())
    today = datetime.date.today()
    tm5 = today - datetime.timedelta(days=5)
    spend = trans[trans['Transaction Type'] == 'debit']
    spend5d = spend[spend['Date'] >= tm5]
    sg = spend5d.groupby('Date')
    dspend = sg[['Amount']].sum()
    dspend = dspend.reset_index()
    dspend = dspend.sort_values('Date', ascending=False)
    dspend['Day'] = dspend['Date'].map(lambda x: '{:%a %d}'.format(x))
    dspend = dspend[['Day', 'Amount']]
    sm = sms.SmsManager()
    send_str = dspend.to_string(header=False, index=False)
    send_str = 'Spending:\n' + send_str
    sm.send(send_str)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description='Handle the run parameters.')
    argparser.add_argument(
        '-u', '--update', action='store_true',
        help='Indicate that a SMS update should be sent')
    args = argparser.parse_args()
    if args.update:
        send_daily_update()
    else:
        refresh_accounts_and_kill()
