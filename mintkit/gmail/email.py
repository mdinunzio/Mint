"""A simple module for sending emails.

Notes:
https://code.activestate.com/recipes/473810/

"""

import authapi
import base64
import googleapiclient.discovery
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage


class EmailMessage():
    """
    An interface for sending emails.
    """
    def __init__(self, to, message, subject='', from_=None, mode='html',
                 images=[], attachments=[]):
        self.service = googleapiclient.discovery.build(
            'gmail', 'v1', credentials=authapi.gmail.creds)
        self.to = to
        self.message = message
        self.subject = subject
        if from_ is None:
            from_ = authapi.user_data.email
        self.from_ = from_
        self.mode = mode
        self.images = images
        self.attachments = attachments

    def send(self):
        """
        Construct and send a MIME message.
        """
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = self.subject
        msgRoot['From'] = self.from_
        msgRoot['To'] = self.to
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the
        # message body in an 'alternative' part, so message
        # agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText(self.message, self.mode)
        msgAlternative.attach(msgText)

        for i, filename in enumerate(self.images):
            fp = open(filename, 'rb')
            msg_image = MIMEImage(fp.read())
            fp.close()

            # Define the image's ID as referenced above
            msg_image.add_header('Content-ID', f'<image{i+1}>')
            msgRoot.attach(msg_image)

        for i, filename in enumerate(self.attachments):
            # Open file in binary mode
            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this
                # automatically as attachment
                msg_base = MIMEBase("application", "octet-stream")
                msg_base.set_payload(attachment.read())
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(msg_base)
            # Add header as key/value pair to attachment part
            msg_base.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg_base.add_header('X-Attachment-Id', f'{i+1}')
            msg_base.add_header('Content-ID', f'<Attachment{i+1}>')
            msgRoot.attach(msg_base)

        raw = base64.urlsafe_b64encode(msgRoot.as_bytes())
        raw = raw.decode()
        body = {'raw': raw}

        message = (self.service.users().messages().send(
            userId="me", body=body).execute())
        return message['id']
