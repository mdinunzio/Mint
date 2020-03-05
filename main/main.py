import config as cfg
import scrapekit
import finances
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
    """
    Download the most recent record of transactions and
    send a 5-day summary via SMS.
    """
    download_and_kill()
    tmgr = finances.TransactionManager()
    sm = sms.SmsManager()
    # Get 5-Day stats
    spend_smry, spend_count = tmgr.get_spending_by_day(
        n=5, total=False, count=True)
    five_d_ttl = spend_smry['Amount'].sum()
    five_d_pace = five_d_ttl / len(spend_smry)
    send_str = f'{spend_count:,.0f} items:\n\n'
    send_str += spend_smry.to_string(header=False, index=False)
    send_str += f'\n\nSpent 5d: ${five_d_ttl:,.2f}\n'
    send_str += f'Pace 5d: ${five_d_pace:,.2f}\n\n'
    today = datetime.date.today()
    spent, remaining, spent_per_day, rem_per_day = tmgr.get_monthly_pacing()
    send_str += f'Spent {today:%b}: ${spent:,.2f}\n'
    send_str += f'Spent/Day: ${spent_per_day:,.2f}\n\n'
    send_str += f'Remaining {today:%b}: ${remaining:,.2f}\n'
    send_str += f'Remaining/Day: ${rem_per_day:,.2f}\n\n'
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
