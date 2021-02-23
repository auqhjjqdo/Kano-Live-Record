# 鹿乃直播监控录制

## 环境变量

### python环境变量

```shell
export PATH=/home/runner/.local/bin:$PATH
```

### 工作目录环境变量

```shell
export PATH=/home/runner/work/Kano-Live-Record/Kano-Live-Record:$PATH
```

## 环境安装

### 安装ffmpeg

#### snap安装方式

```shell
sudo snap install ffmpeg --channel=latest/edge
```

#### apt安装方式

```shell
sudo add-apt-repository ppa:jonathonf/ffmpeg-4
sudo apt update
sudo apt install ffmpeg
```

### 安装streamlink

#### pip安装方式

```shell
pip3 install setuptools
pip3 install streamlink
```

#### apt安装方式

```shell
sudo add-apt-repository ppa:nilarimogard/webupd8
sudo apt update
sudo apt install streamlink
```

### 安装youtube-dl

#### pip安装方式

```shell
pip3 install youtube-dl
```

#### snap安装方式

```shell
sudo snap install youtube-dl --channel=latest/edge
```

#### wget安装方式：

```shell
sudo wget https://yt-dl.org/downloads/latest/youtube-dl -O youtube-dl
sudo chmod 777 youtube-dl
```

### 安装magic-wormhole

#### pip安装方式

```shell
pip3 install magic-wormhole
```

#### apt安装方式

```shell
sudo apt install magic-wormhole
```

## 运行直播录制

```shell
wget https://raw.githubusercontent.com/auqhjjqdo/Kano-Live-Record/master/kano_live_record.py -O kano_live_record.py
python3 kano_live_record.py
```

### OneDriveUploader上传文件

```shell
wget https://raw.githubusercontent.com/auqhjjqdo/Kano-Live-Record/master/OneDriveUploader -O OneDriveUploader
wget https://raw.githubusercontent.com/auqhjjqdo/Kano-Live-Record/master/auth.json -O auth.json
chmod 777 OneDriveUploader
OneDriveUploader -s *mp4 -f
```

### wormhole发送文件

```shell
wormhole send *mp4
```
