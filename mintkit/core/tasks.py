import mintkit.config as cfg
import mintkit.utils.logging
import mintkit.core.mint
import mintkit.core.analytics
import mintkit.core.plotting
import mintkit.gmail.email
from mintkit.auth.api import auth_api
import datetime


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)


def send_spending_update_text():
    """Send the spending update text message.

    """
    log.info('Preparing spending summary text')
    log.info('Downloading transactions')
    mintkit.core.mint.download_transactions()
    log.info('Retrieving files')
    transactions = mintkit.core.analytics.get_transactions()
    recurring = mintkit.core.analytics.get_recurring()
    log.info('Getting summaries')
    summary = mintkit.core.analytics.get_recent_spending_summary(
        transactions=transactions, recurring=recurring, lookback=5)
    mintkit.core.plotting.plot_spending(
        transactions=transactions, recurring=recurring)
    log.info('Constructing text message (email).')
    today = datetime.date.today()
    email = mintkit.gmail.email.EmailMessage()
    email.subject = f'Spending {today:%a, %b %d}'
    email.to = auth_api.user.mobile + '@vzwpix.com'
    email.body = summary
    email.add_image('spending', cfg.paths.plots + 'spending.png')
    email.send()
    log.info('Text update sent')
