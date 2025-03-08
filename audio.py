#! /usr/bin/env python
# coding=utf-8
import time
import threading
import sys
import json
import nls
import os
import time
import json
import pyperclip
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from read_microphone import microphone_data
from pynput import keyboard
from pynput.keyboard import Key, Listener  # pip install pynput==1.7.6
import pyautogui

URL="wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1"
APPKEY=os.getenv('ALIYUN_APPKEY')

CHUNK = 1024  # 每次读取的音频数据块大小

# 创建AcsClient实例
client = AcsClient(
   os.getenv('ALIYUN_AK_ID'),
   os.getenv('ALIYUN_AK_SECRET'),
   "cn-shanghai"
);

# 创建request，并设置参数。
request = CommonRequest()
request.set_method('POST')
request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
request.set_version('2019-02-28')
request.set_action_name('CreateToken')

try :
   response = client.do_action_with_exception(request)
   print(response)

   jss = json.loads(response)
   if 'Token' in jss and 'Id' in jss['Token']:
      token = jss['Token']['Id']
      expireTime = jss['Token']['ExpireTime']
      print("token = " + token)
      print("expireTime = " + str(expireTime))
except Exception as e:
   print(e)
TOKEN = token


#以下代码会根据音频文件内容反复进行实时语音识别（文件转写）
class TestSt:
    def __init__(self, tid):
        # self.__th = threading.Thread(target=self.__test_run)
        self.__id = tid
        self.sentences = []
        self.sr = nls.NlsSpeechTranscriber(
            url=URL,
            token=TOKEN,
            appkey=APPKEY,
            on_sentence_begin=self.test_on_sentence_begin,
            on_sentence_end=self.test_on_sentence_end,
            on_start=self.test_on_start,
            on_result_changed=self.test_on_result_chg,
            on_completed=self.test_on_completed,
            on_error=self.test_on_error,
            on_close=self.test_on_close,
            callback_args=[self.__id]
        )

   
    def clear(self):
        self.times = [int(time.time())]
        self.sentences = []

    def test_on_sentence_begin(self, message, *args):
        # print("test_on_sentence_begin:{}".format(message))
        pass

    def test_on_sentence_end(self, message, *args):
        message = json.loads(message)
        self.sentences.append(message["payload"]["result"])
        self.times.append(int(time.time()))
        pyperclip.copy(self.sentences[-1])
        # 模拟按下 Ctrl+V（Windows/Linux）或 Command+V（Mac）
        if pyautogui.platform == "darwin":  # macOS
            pyautogui.hotkey("command", "v")
        else:  # Windows/Linux
            pyautogui.hotkey("ctrl", "v")
        print(f"sentence_end {self.sentences}")
        # print("test_on_sentence_end:{}".format(message))

    def test_on_start(self, message, *args):
        # print("test_on_start:{}".format(message))
        pass

    def test_on_error(self, message, *args):
        # print("on_error args=>{}".format(args))
        pass

    def test_on_close(self, *args):
        # print("on_close: args=>{}".format(args))
        pass

    def test_on_result_chg(self, message, *args):
        # print("test_on_chg:{}".format(message))
        pass

    def test_on_completed(self, message, *args):
        print(f"complete {self.sentences}")
        # print("on_completed:args=>{} message=>{}".format(args, message))
        
    def __test_run(self):
        print("thread:{} start..".format(self.__id))

    def process(self, file_path = None, data= None ):
        if file_path is not None:
            with open(file_path,"rb") as f:
                self.__data = f.read()
                self.__slices = zip(*(iter(self.__data),) * CHUNK)
        else:  
            self.__slices = data

        print("{}: session start".format(self.__id))
        r = self.sr.start(aformat="pcm",
        enable_intermediate_result=True,
        enable_punctuation_prediction=True,
        enable_inverse_text_normalization=True)
        self.stop = False
        def on_press(key):
            if key == keyboard.Key.esc:
                print("ESC 键被按下")
                self.stop = True
                self.clear()
        listener = Listener(on_press=on_press)
        listener.start()
        for i in self.__slices:
            self.sr.send_audio(bytes(i))
            time.sleep(0.01)
            # 捕获一个退出的信号，免的一直在数据浪费计算资源
            # 要么监控按键，要么一段时间没新sentence自动退出
            if (int(time.time())-self.times[-1])>=10:
                self.stop = True
            if self.stop:
                break
            
        print("audio session stop")
        self.sr.ctrl(ex={"test":"tttt"})
        time.sleep(1)

        r = self.sr.stop()
        time.sleep(1)

def multiruntest():
    # 监听F5
    # F5被按下则触发micro听取
    # F6按下怎表示这段时间的语音要被记录，且历史的语音被清空
    t = TestSt("1")

    def on_press(key):
        if key == keyboard.Key.f5:
            print("F5 键被按下")
            data = microphone_data()
            t.clear()
            t.process(data = data)
        elif key == Key.esc:
            pass

    while True:
        with Listener(on_press=on_press) as listener:
            listener.join()

    # t = TestSt("1", test_file = "recording.pcm")
    t.start()


"""
def on_press(key):
    try:
        if key == keyboard.Key.f5:
            print("F5 按键被按下")
    except AttributeError:
        pass

def on_release(key):
    try:
        if key == keyboard.Key.f5:
            print("F5 按键被释放")
    except AttributeError:
        pass

    if key == keyboard.Key.esc:
        return False  # 按下 Esc 键退出监听

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
"""
nls.enableTrace(False)
multiruntest()
