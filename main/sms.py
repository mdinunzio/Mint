import authapi
from twilio.rest import Client


class SmsManager():

    def __init__(self):
        self.account_sid = authapi.twilio.account_sid
        self.auth_token = authapi.twilio.auth_token
        self.number = authapi.twilio.number
        self.client = Client(self.account_sid,
                             self.auth_token)

    def send(self, body, to=None):
        if to is None:
            to = authapi.user_data.number
        self.message = self.client.messages.create(
            to=to,
            from_=self.number,
            body=body)
