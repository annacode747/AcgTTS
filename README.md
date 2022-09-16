# AcgTTS api
- 该项目是作者 [``CjangCjengh`` 🤗](https://github.com/CjangCjengh) 的 [原项目 ``MoeGoe``](https://github.com/CjangCjengh/MoeGoe) 修改而成的
# Online demo
- Integrated into [Huggingface Spaces 🤗](https://huggingface.co/spaces) using [Gradio](https://github.com/gradio-app/gradio). Try it out [![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/skytnt/moe-japanese-tts)
- Integrated into Azure Cloud Function by [fumiama](https://github.com/fumiama), see API [here](https://github.com/fumiama/MoeGoe).
- Integrated into Android APP using Azure Cloud Function API by [fumiama](https://github.com/fumiama) [![MoeGoe-Android](https://img.shields.io/badge/MoeGoe-Android-orange)](https://github.com/fumiama/MoeGoe-Android)
# 环境安装
- 当前环境 ubuntu 20
- python3.8以上，本地环境python3.9
- ````shell
  sudo apt-get-d install ffmpeg
  ````
- pip 环境
- ````shell
  pip install -r requirements.txt
  ````
- 可能还有部分pip包没有安装，请根据报错安装

## 也可以手动安装ffmpeg
- 官网下载地址``https://ffmpeg.org/download.html#build-linux``
- 选择``Linux Static Builds``下的构建选项，进入详情页
- 选在直接合适的下载地址 复制 wget下载 效果如下
- ````shell
  wget https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz
  ````
- 可以看到下载完成的文件后缀名为 ``.tar.xz`` ，执行对应解压命令解压文件
- ````shell
  xz -d ffmpeg-git-amd64-static.tar.xz
  ````
- 经过一次解压，``.xz`` 后缀名已经被去掉。接下来执行
- ````shell
  tar -xvf ffmpeg-git-amd64-static.tar
  ````
- 解压完成后进入解压出来的这个目录``cd`` ``ffmpeg-git-20190424-amd64-static``
- 运行 接下来执行下命令试试 ``ffmpeg``
- 最后在配置命令全局可用
