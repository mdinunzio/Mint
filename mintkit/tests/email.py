import mintkit.settings as cfg
from mintkit.auth.api import auth_api
import mintkit.gmail.email

email = mintkit.gmail.email.EmailMessage()

email.add_image('one', cfg.paths.plots + 'spending.png')
email.to = auth_api.user.mobile + '@vzwpix.com'
email.body = 'test'
email.body = '<a href="https://mint.intuit.com/transaction.event?startDate' \
             '=02/01/2021&endDate=02/28/2021">url</a>'
email.subject = 'spending'
email.send()