import datetime
import json
import os
import random
import re
import time
import traceback
from threading import Thread

import requests


def get_time(date=False):
    utc_time = datetime.datetime.utcnow()
    time_delta = datetime.timedelta(hours=8)
    utc8_time = utc_time + time_delta
    if date:
        return utc8_time.strftime('%Y.%m.%d')
    else:
        return utc8_time.strftime('%Y-%m-%d %H:%M:%S')


def set_onedrive_auth():
    print(f'[{get_time()}]正在初始化OneDriveUploader授权')
    onedrive_refresh_token = os.getenv('ONEDRIVE_REFRESHTOKEN')
    if '0.A' in onedrive_refresh_token:
        onedrive_auth = {
            'RefreshToken': onedrive_refresh_token,
            'RefreshInterval': 1500,
            'ThreadNum': '8',
            'BlockSize': '16',
            'SigleFile': '100',
            'MainLand': False,
            'MSAccount': False
        }
        with open('auth.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(onedrive_auth))
        print(f'[{get_time()}]成功写入onedrive_refreshtoken')
    else:
        error_info = f'[{get_time()}]写入onedrive_refreshtoken失败'
        print(error_info)
        raise RuntimeError(error_info)


class KanoLiveRecord:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        if 'bilibili' in self.url:
            self.live_type = 'bilibili'
        if 'youtube' in self.url:
            self.live_type = 'youtube'
        print(f'[{get_time()}][{self.name}]正在检测直播状态')
        while True:
            try:
                self.live_info = self.live_status()
                if self.live_info:
                    self.temp_name = self.live_record()
                    # if os.path.exists(self.temp_name):
                    if self.temp_name:
                        self.live_title = self.live_info[0]
                        self.ffmpeg_transcoding()
                        Thread(target=self.file_upload).start()
                time.sleep(random.randint(5, 15))
            except:
                traceback.print_exc()

    def live_status(self):
        if self.live_type == 'bilibili':
            room_id = re.findall(r'live.bilibili.com/(\d*)', self.url)[0]
            response = requests.get(f'https://api.live.bilibili.com/room/v1/Room/get_info?room_id={room_id}', headers=headers)
            json_data = response.json()
            if json_data['code'] == 0:
                live_status = json_data['data']['live_status']
                if live_status == 1:
                    live_title = json_data['data']['title']
                    live_url = self.url
                    msg = f'[{get_time()}][{self.name}]检测到直播流：\n{live_title}\n{live_url}'
                    self.send_qsmg(msg)
                    return live_title, live_url
            else:
                print(f'[{get_time()}][{self.name}]检测直播流失败：{json_data}')
        if self.live_type == 'youtube':
            response = requests.get(f'{self.url}/videos?view=2&live_view=501', headers=headers, cookies={'PREF': 'hl=zh-CN'})
            if response.status_code == 200:
                text = response.text
                if '正在直播' in text:
                    live_title = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', text)[0]
                    video_id = re.findall(r'"gridVideoRenderer":\{"videoId":"(.*?)"', text)[0]
                    live_url = f'https://www.youtube.com/watch?v={video_id}'
                    msg = f'[{get_time()}][{self.name}]检测到直播流\n{live_title}\n{live_url}'
                    self.send_qsmg(msg)
                    return live_title, live_url
            else:
                print(f'[{get_time()}][{self.name}]检测直播流失败：{response}')

    def live_record(self):
        msg = f'[{get_time()}][{self.name}]开始录制直播'
        self.send_qsmg(msg)
        live_url = self.live_info[1]
        temp_name = int(time.time())
        os.system(f'streamlink "{live_url}" best -o "{temp_name}" -l debug | tee Streamlink.txt')
        with open('Streamlink.txt', 'r', encoding='utf-8') as f:
            record_result = f.read()
        if 'ended' in record_result:
            msg = f'[{get_time()}][{self.name}]直播录制结束'
            self.send_qsmg(msg)
            return temp_name
        if 'error' in record_result:
            error_info = re.findall(r'error:(.*)', record_result)[0]
            msg = f'[{get_time()}][{self.name}]直播录制失败：\n{error_info}'
            self.send_qsmg(msg)

    def ffmpeg_transcoding(self):
        msg = f'[{get_time()}][{self.name}]开始ffmpeg转码'
        self.send_qsmg(msg)
        os.system(f'ffmpeg -i "{self.temp_name}" -c copy "{self.temp_name}.mp4"')

    def file_upload(self):
        for i in '"*:<>?/\|':
            self.live_title = self.live_title.replace(i, ' ')
        date = get_time(date=True)
        save_name = f'[{self.temp_name}][{date}][{self.live_type}]{self.live_title}.mp4'
        msg = f'[{get_time()}][{self.name}]\n{self.live_title}\n开始上传到OneDrive'
        self.send_qsmg(msg)
        os.system(f'./OneDriveUploader -f -s "{self.temp_name}.mp4" -r "/鹿乃歌曲合集/直播录屏" -n "{save_name}" | tee OneDriveUploader.txt')
        with open('OneDriveUploader.txt', 'r', encoding='utf-8') as f:
            upload_result = f.read()
        if '100%' in upload_result:
            msg = f'[{get_time()}][{self.name}]\n{self.live_title}\n成功上传到OneDrive'
            self.send_qsmg(msg)
        else:
            msg = f'[{get_time()}][{self.name}]\n{self.live_title}\n上传到OneDrive失败：{upload_result}'
            self.send_qsmg(msg)

    def send_qsmg(self, msg):
        print(msg)
        qsmg_token = os.getenv('QSMG_TOKEN')
        qmsg_url = f'https://qmsg.zendee.cn/send/{qsmg_token}'
        qmsg_data = {
            'msg': msg
        }
        requests.post(url=qmsg_url, data=qmsg_data)


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    data = {
        'bilibili_鹿乃': 'https://live.bilibili.com/15152878',
        'youtube_歌手鹿乃': 'https://www.youtube.com/channel/UCShXNLMXCfstmWKH_q86B8w',
        'youtube_花寄鹿乃': 'https://www.youtube.com/channel/UCfuz6xYbYFGsWWBi3SpJI1w'
    }
    set_onedrive_auth()

    # KanoLiveRecord('泠鸢yousa', 'https://live.bilibili.com/47377')
    # KanoLiveRecord('ChilledCow', 'https://www.youtube.com/channel/UCSJ4gkVC6NrvII8umztf0Ow')
    for name, url in data.items():
        Thread(target=KanoLiveRecord, args=(name, url)).start()
