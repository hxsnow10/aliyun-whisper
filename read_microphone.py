import pyaudio
import wave
from datetime import datetime

# 定义音频参数
FORMAT = pyaudio.paInt16  # 音频格式（16位整数）
CHANNELS = 1  # 单声道
RATE = 16000  # 采样率（44.1kHz）
CHUNK = 1024  # 每次读取的音频数据块大小

# 生成输出文件名（使用时间戳）
output_filename = f"recording.pcm"
output_wav_filename = f"recording.wav" 

# 初始化pyaudio
audio = pyaudio.PyAudio()

# 打开音频流
stream = audio.open(format=FORMAT, channels=CHANNELS,
                   rate=RATE, input=True,
                   frames_per_buffer=CHUNK)

# print(f"开始录音... 保存到文件: {output_filename}")
frames = []

def microphone_data():
    try:
        # 直接写入PCM文件
        with open(output_filename, 'wb') as pcm_file:
            while True:
                # 读取音频数据
                data = stream.read(CHUNK)
                # 直接写入PCM数据
                pcm_file.write(data)
                frames.append(data)
                yield data
                
    except KeyboardInterrupt:
        print("\n录音结束。")

    finally:
        # 关闭音频流
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print(f"录音已保存到: {output_filename}")

    # 保存录音到WAV文件

    print(f"正在保存录音到 {output_filename}...")
    with wave.open(output_filename, 'wb') as wave_file:
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))
if __name__ == "__main__":
    for _ in microphone_data():
        pass

