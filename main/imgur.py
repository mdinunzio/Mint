import config as cfg
import authapi
import requests
import base64


class ImgurManager():
    def __init__(self):
        self.client_id = authapi.imgur.client_id
        self.client_secret = authapi.imgur.client_secret
        self.oauth_url = f'https://api.imgur.com/oauth2/'
        self.response = None

    def upload_image(self, img_path):
        fl = open(img_path, 'rb')
        img = fl.read()
        b64 = base64.b64encode(img)
        data = {'image': b64, 'type': 'base64'}
        headers = {'Authorization': f'Client-ID {self.client_id}'}
        self.response = requests.post(url=r'https://api.imgur.com/3/upload',
                                      data=data,
                                      headers=headers)
        img_link = self.response.json()['data']['link']
        return img_link
