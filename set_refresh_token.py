import datetime
import json
import os

import requests
from nacl import encoding, public
from base64 import b64encode


def get_time():
    utc_time = datetime.datetime.utcnow()
    time_delta = datetime.timedelta(hours=8)
    utc8_time = utc_time + time_delta
    strftime = utc8_time.strftime("%Y-%m-%d %H:%M:%S")
    return strftime


class SetRefreshToken:
    def __init__(self):
        self.github_token = os.getenv('GH_TOKEN')
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.old_refresh_token = os.getenv('ONEDRIVE_REFRESHTOKEN')

        self.key_info = self.get_publickey()
        self.new_refresh_token = self.get_new_refresh_token()
        self.encrypted_value = self.encrypt_secret()
        self.update_refresh_token()

    def get_publickey(self):
        print(f'[{get_time()}]正在获取publickey')
        url = 'https://api.github.com/repos/auqhjjqdo/Kano-Live-Record/actions/secrets/public-key'
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {self.github_token}'
        }
        response = requests.get(url=url, headers=headers)
        json_data = response.json()
        if 'key' in json_data:
            print(f'[{get_time()}]获取publickey成功')
            return json_data
        else:
            error_info = f'[{get_time()}]获取publickey失败：\n{json_data}'
            print(error_info)
            raise RuntimeError(error_info)

    def get_new_refresh_token(self):
        print(f'[{get_time()}]正在获取refresh_token')
        url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.old_refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(url=url, data=data)
        json_data = response.json()
        if 'refresh_token' in json_data:
            print(f'[{get_time()}]获取refresh_token成功')
            return json_data['refresh_token']
        else:
            error_info = f'[{get_time()}]获取refresh_token失败：\n{json_data}'
            print(error_info)
            raise RuntimeError(error_info)

    def encrypt_secret(self):
        print(f'[{get_time()}]正在加密refresh_token')
        public_key = public.PublicKey(self.key_info['key'].encode('utf-8'), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(self.new_refresh_token.encode('utf-8'))
        encrypted_value = b64encode(encrypted).decode('utf-8')
        return encrypted_value

    def update_refresh_token(self):
        print(f'[{get_time()}]正在上传refresh_token')
        url = 'https://api.github.com/repos/auqhjjqdo/Kano-Live-Record/actions/secrets/ONEDRIVE_REFRESHTOKEN'
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {self.github_token}'
        }
        data = {
            'encrypted_value': self.encrypted_value,
            'key_id': self.key_info['key_id']
        }
        response = requests.put(url=url, headers=headers, data=json.dumps(data))
        if response.status_code == 201:
            print(f'[{get_time()}]新建refresh_token成功')
        elif response.status_code == 204:
            print(f'[{get_time()}]refresh_token上传成功')
        else:
            error_info = f'[{get_time()}]refresh_token上传失败：\n{response.json()}'
            print(error_info)
            raise RuntimeError(error_info)


if __name__ == '__main__':
    SetRefreshToken()
