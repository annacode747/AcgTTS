import os
import datetime
import shutil
import time
from hashlib import md5
from random import randint

from flask_cors import CORS
from flask import Flask, request

from Flask_Threadpool import FlaskThreadPool
from interact import *
from response import ResponseData

app = Flask(__name__,
            static_url_path='/',  # 配置静态文件的访问 url 前缀
            static_folder='static',  # 配置静态文件的文件夹
            )
CORS(app, resources=r'/*')
async_task = FlaskThreadPool()
Path = os.path.dirname(os.path.realpath(__file__))
timeConfig = "%Y%m%d"



def getPid():
    return os.getpid()


def getSpeakers(config="config/config.json"):
    global api_hps_ms
    if config != "config/config.json":
        api_hps_ms = utils.get_hparams_from_file(config)
    return api_hps_ms.speakers


def GetTime(t=time.localtime(time.time())):
    return time.strftime(timeConfig, t)


def GetMd5(t):
    return md5(t.encode("utf-8")).hexdigest()


@app.route('/getPid', methods=['GET', 'POST'])
def pid():
    """
    获取项目Pid
    """
    return ResponseData().renderSuccess(getPid())


@app.route('/wifeVoice', methods=['GET', 'POST'])
def wifeVoice():
    """
    生成老婆语音
    """
    t = time.time()
    text = request.values.get("text")
    speaker_id = request.values.get("speaker_id", randint(0, len(getSpeakers()) - 1))
    choice = request.values.get("choice", 't')
    model = request.values.get("model", 'model/1374_epochs.pth')
    Config = request.values.get("config", 'config/config.json')
    time_str = GetTime()
    path_src = Path + "/static/" + time_str
    if not os.path.exists(path_src):  # 是否存在这个文件夹
        os.makedirs(path_src)  # 如果没有这个文件夹，那就创建一个
    out_path = "{}/{}.wav".format(path_src, GetMd5(text))
    Interact(
        text=text,
        out_path=out_path,
        # hps_ms=hps_ms,
        speaker_id=speaker_id,
        choice=choice,
        model=model,
        config=Config
    )
    t = time.time() - t
    size = os.stat(out_path).st_size
    ret = {
        "time": t,
        "size": size,
        "path": out_path,
        "url": "{}/{}/{}.wav".format(request.host, time_str, GetMd5(text))
    }
    print(ret)
    # delFile()
    return ResponseData().renderSuccess(ret)


def callback(future):
    e = future.exception()
    print("异步任务的错误：" + str(e))


@async_task.submit(callback)
def delFile(i=3):
    """
    删除大于多少天的文件
    """
    path = "{}/static".format(Path)
    for file_name in os.listdir(path):
        try:
            print(file_name)
            if datetime.datetime.now() + datetime.timedelta(days=-i) < datetime.datetime(*time.strptime(file_name, timeConfig)[:6]):
                shutil.rmtree("{}/{}".format(path, file_name))
        except EOFError:
            print(EOFError)


if __name__ == '__main__':
    app.run('127.0.0.1', 34337)
