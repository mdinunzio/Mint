import config as cfg
import json
import os


class AuthManager():
    def __init__(self, json_file=None):
        self.username = None
        self.password = None
        self.client_id = None
        self.token = None
        self.email = None
        self.number = None
        if json_file is None:
            return
        json_path = os.path.join(cfg.LOCAL_DIR, json_file)
        self.init_with_file(json_path)

    def init_with_file(self, json_path):
        with open(json_path, 'r') as f:
            self.auth_dict = json.load(f)
        for k, v in self.auth_dict.items():
            setattr(self, k, v)

    def __str__(self):
        ret = ''
        for k, v in self.auth_dict.items():
            ret += f'{k}: {v}\n'
        return ret

    def __repr__(self):
        return self.__str__()


mint = AuthManager('mint.json')
twilio = mint = AuthManager('twilio.json')
imgur = AuthManager('imgur.json')
user_data = AuthManager('user_data.json')
