import mintkit.config as cfg
from mintkit.auth.api import auth_api
import mintkit.gmail.email

email = mintkit.gmail.email.EmailMessage()

email.add_image('one', cfg.paths.plots + 'spending.png')
email.to = auth_api.user.mobile + '@vzwpix.com'
email.body = 'test'
email.subject = 'spending'