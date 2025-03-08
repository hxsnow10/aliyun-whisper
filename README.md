# aliyun-whisper

audio.py: 
- 按F5后触发语音解析；按ESC或者10S没有解析出句子，则清空历史退出模块，循环；
- 模块：从microphone读取数据，交互阿里云服务，每解析完的一句话会被复制到光标处。
```
sentence_end ['你好。']
sentence_end ['你好。', '你能告诉我北京天安门在哪个城市吗？']
sentence_end ['你好。', '你能告诉我北京天安门在哪个城市吗？', 'Hello, world. ']

你好。你能告诉我北京天安门在哪个城市吗？哇，666。
```
