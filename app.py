# coding=gbk
import os
import datetime
import shutil
import time
import logging
import logging.handlers
from hashlib import md5
from random import randint

from flask_cors import CORS
from flask import Flask, request

import utils
from Flask_Threadpool import FlaskThreadPool
from interact import Interact, api_hps_ms, api_net_g_ms
from response import ResponseData
from pydub import AudioSegment

app = Flask(__name__,
            static_url_path='/',  # 配置静态文件的访问 url 前缀
            static_folder='static',  # 配置静态文件的文件夹
            )
CORS(app, resources=r'/*')
async_task = FlaskThreadPool()
Path = os.path.dirname(os.path.realpath(__file__))
timeConfig = "%Y%m%d"
async_task.init_app(app)


def create_logger(log_path="log/interact"):
    """
    将日志输出到日志文件和控制台
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(process)d - %(filename)s_[line:%(lineno)d] - %(levelname)s - %(message)s',
        datefmt="%Y-%m-%d %X"
    )
    fh = logging.handlers.TimedRotatingFileHandler(filename=log_path, when='S', interval=1, backupCount=3,
                                                   encoding="utf-8")
    fh.suffix = "%Y-%m-%d_%H-%M-%S.log"
    ch = logging.StreamHandler()
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


log = create_logger()


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

    global hps_ms
    hps_ms = None
    t = time.time()
    text = request.values.get("text")
    speaker_id = int(request.values.get("speaker_id", randint(0, len(getSpeakers()) - 1)))
    choice = request.values.get("choice", 't')
    model = request.values.get("model", 'model/1374_epochs.pth')
    Config = request.values.get("config")
    if Config is not None:
        hps_ms = utils.get_hparams_from_file(Config)
    time_str = GetTime(time.localtime(time.time()))
    path_src = Path + "/static/" + time_str
    if not os.path.exists(path_src):  # 是否存在这个文件夹
        os.makedirs(path_src)  # 如果没有这个文件夹，那就创建一个
    fileName = GetMd5(text)
    out_path = "{}/{}.wav".format(path_src, fileName)
    Interact(
        text=text,
        out_path=out_path,
        hps_ms=hps_ms,
        speaker_id=speaker_id,
        choice=choice,
        model=model
    )
    t = time.time() - t
    size = os.stat(out_path).st_size
    wav2mp3(out_path, path_src)
    ret = {
        "time": t,
        "size": size,
        "path": out_path,
        "mp3": "{}/{}.mp3".format(path_src, fileName),
        "url": "{}/{}/{}.wav".format(request.host, time_str, fileName)
    }
    log.info(ret)
    delFile()
    return ResponseData().renderSuccess(ret)


def wav2mp3(filepath, savepath):
    sourcefile = AudioSegment.from_wav(filepath)
    filename = filepath.split('/')[-1].split('.wav')[0].replace(' ', '_') + '.mp3'
    print("filename:", filename)
    sourcefile.export("{}/{}".format(savepath, filename), format="mp3").close()


def callback(future):
    e = future.exception()
    # log.error("异步任务的错误：{}".format(e))



@async_task.submit(callback)
def delFile(i=3):
    """
    删除大于多少天的文件
    """
    path = "{}/static".format(Path)
    for file_name in os.listdir(path):
        if '.' in file_name:
            continue
        try:
            if datetime.datetime.now() + datetime.timedelta(days=-i) > datetime.datetime(
                    *time.strptime(file_name, timeConfig)[:6]):
                shutil.rmtree("{}/{}".format(path, file_name))
                log.warning("删除的文件夹名称:{}".format(file_name))
        except Exception:
            log.error("删除文件失败：{}\t{}".format(file_name, Exception))


if __name__ == '__main__':
    app.run('0.0.0.0', 34337)