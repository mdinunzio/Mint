"""A simple module for sending emails.

Notes:
https://code.activestate.com/recipes/473810/

"""
from mintkit.auth.api import auth_api
import base64
import googleapiclient.discovery
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage


def _to_list(x):
    """Return a list from the x parameter of ambiguous type.

    """
    if x is None:
        return []
    if isinstance(x, str):
        return [x]
    if isinstance(x, tuple):
        return list(x)
    return x


class Image:
    def __init__(self, name, cid, path):
        """An email-friendly image path.

        """
        self.name = name
        self.cid = cid
        self.path = path

    def __str__(self):
        """Represent as a string.

        """
        return f'Image {self.name} ({self.cid})'

    def __repr__(self):
        """Represent in the console.

        """
        ret = 'Image Object\n'
        ret += f'Name: {self.name}\n'
        ret += f'CID: {self.cid}\n'
        ret += f'Path: {self.path}'
        return ret

    def to_html(self):
        """Return the HTML string needed to reference an image in an email.

        """
        return f'<img src="cid:{self}">'


class EmailMessage:
    def __init__(self, subject='', to=[], body='', cc=[], sender=None,
                 subtype='html'):
        """A class for building and sending emails.

        """
        self.service = googleapiclient.discovery.build(
            'gmail', 'v1', credentials=auth_api.gmail)
        self._to = to
        self._cc = cc
        self.body = body
        self.subject = subject
        if sender is None:
            sender = auth_api.user.email
        self.sender = sender
        self.subtype = subtype
        self.images = dict()
        self.attachments = dict()

    @property
    def to(self):
        """Return the main recipients.

        """
        return self._to

    @to.setter
    def to(self, recipients):
        """Set the main recipients.

        """
        self._to = _to_list(recipients)

    @property
    def cc(self):
        """Return the carbon-copied recipients.

        """
        return self._cc

    @cc.setter
    def cc(self, recipients):
        """Set the carbon-copied recipients.

        """
        self._cc = _to_list(recipients)

    def add_image(self, name, path):
        """Add a image to the email that can be referenced.

        """
        if name in self.images:
            raise ValueError(f'"{name}" already in collection of images.')
        cid = len(self.images) + len(self.attachments) + 1
        self.images[name] = Image(name, cid, path)

    def add_attachment(self, name, path):
        """Add an attachment to the email.

        """
        # TODO
        pass

    def send(self):
        """Construct and send a MIME message.

        """
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = self.subject
        msg_root['From'] = self.sender
        msg_root['To'] = ', '.join(self.to)
        msg_root['Cc'] = ', '.join(self.cc)
        msg_root.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the
        # message body in an 'alternative' part, so message
        # agents can decide which they want to display.
        msg_alternative = MIMEMultipart('alternative')
        msg_root.attach(msg_alternative)

        msg_text = MIMEText(self.body, self.subtype)
        msg_alternative.attach(msg_text)

        for name in self.images:
            with open(self.images[name].path, 'rb') as file:
                msg_image = MIMEImage(file.read())
                msg_image.add_header(
                    'Content-ID', f'<Image{self.images[name].cid:.0f}>')
                msg_root.attach(msg_image)

        for attachment in self.attachments:
            # TODO
            # Open file in binary mode
            with open(attachment.path, "rb") as file:
                # Add file as application/octet-stream
                # Email client can usually download this
                # automatically as attachment
                msg_base = MIMEBase("application", "octet-stream")
                msg_base.set_payload(file.read())
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(msg_base)
            # Add header as key/value pair to attachment part
            msg_base.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment.filename}",
            )
            msg_base.add_header('X-Attachment-Id', f'{attachment.cid}')
            msg_base.add_header('Content-ID', f'<Attachment{attachment.cid}>')
            msg_root.attach(msg_base)

        raw = base64.urlsafe_b64encode(msg_root.as_bytes())
        raw = raw.decode()
        body = {'raw': raw}

        message = (self.service.users().messages().send(
            userId="me", body=body).execute())
        return message['id']
