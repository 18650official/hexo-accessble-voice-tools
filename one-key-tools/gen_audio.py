# 此处存放阿里云的认证信息
ALIYUN_AK_ID = ''
ALIYUN_AK_SECRET = ''
ALIYUN_APPKEY = ''

# -*- coding: utf-8 -*-
import os
import re
import time
import json
import http.client
import urllib.request
import urllib.error
import sys
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import aliyunsdkcore.acs_exception as acs_exception

# 定义文件路径
# Define file paths
POSTS_DIR = 'source/_posts'
AUDIO_DIR = 'source/audio'
MAX_CHARS_PER_CHUNK = 1800

# 确保音频目录存在
# Ensure the audio directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# --------------------------------------------------------------
# 阿里云 TTS API 相关类和函数
# Aliyun TTS API related classes and functions
# --------------------------------------------------------------

class TtsHeader:
    def __init__(self, appkey, token):
        self.appkey = appkey
        self.token = token
    def tojson(self, e):
        return {'appkey': e.appkey, 'token': e.token}

class TtsContext:
    def __init__(self, device_id):
        self.device_id = device_id
    def tojson(self, e):
        return {'device_id': e.device_id}

class TtsRequest:
    def __init__(self, voice, sample_rate, speed, format, enable_subtitle, text):
        self.voice = voice
        self.sample_rate = sample_rate
        self.speed = speed
        self.format = format
        self.enable_subtitle = enable_subtitle
        self.text = text
    def tojson(self, e):
        return {'voice': e.voice, 'sample_rate': e.sample_rate, 'speech_rate': e.speed, 'format': e.format, 'enable_subtitle': e.enable_subtitle, 'text': e.text}

class TtsPayload:
    def __init__(self, enable_notify, notify_url, tts_request):
        self.enable_notify = enable_notify
        self.notify_url = notify_url
        self.tts_request = tts_request
    def tojson(self, e):
        return {'enable_notify': e.enable_notify, 'notify_url': e.notify_url, 'tts_request': e.tts_request.tojson(e.tts_request)}

class TtsBody:
    def __init__(self, tts_header, tts_context, tts_payload):
        self.tts_header = tts_header
        self.tts_context = tts_context
        self.tts_payload = tts_payload
    def tojson(self, e):
        return {'header': e.tts_header.tojson(e.tts_header), 'context': e.tts_context.tojson(e.tts_context), 'payload': e.tts_payload.tojson(e.tts_payload)}


def get_aliyun_token():
    """
    使用 AccessKey ID 和 AccessKey Secret 获取阿里云语音服务的 Token。
    Uses AccessKey ID and AccessKey Secret to get a token for Aliyun Speech Service.
    """
    if ALIYUN_AK_ID == 'your_ak_id' or ALIYUN_AK_SECRET == 'your_ak_secret':
        print("错误：请先在脚本中填写你的 ALIYUN_AK_ID 和 ALIYUN_AK_SECRET。")
        sys.exit(1)

    try:
        client = AcsClient(
            ALIYUN_AK_ID,
            ALIYUN_AK_SECRET,
            "cn-shanghai"
        )
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')
        response = client.do_action_with_exception(request)
        jss = json.loads(response.decode('utf-8'))

        if 'Token' in jss and 'Id' in jss['Token']:
            token = jss['Token']['Id']
            print("✅ Token 获取成功。")
            return token
        else:
            print("获取 Token 失败：响应格式不正确。")
            return None
    except acs_exception.exceptions.ClientException as e:
        print(f"获取 Token 失败：客户端异常，请检查你的 AK_ID 和 AK_SECRET。错误信息：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"获取 Token 失败：未知异常。错误信息：{e}")
        sys.exit(1)

def wait_for_completion(appkey, token, task_id, request_id):
    """
    轮询检查阿里云语音合成任务的状态，直到完成。
    Polls Aliyun TTS task status until completion.
    """
    host = 'nls-gateway-cn-shanghai.aliyuncs.com'
    url = f'https://{host}/rest/v1/tts/async'
    full_url = f"{url}?appkey={appkey}&task_id={task_id}&token={token}&request_id={request_id}"
    
    print("-> 正在等待语音合成任务完成...")
    while True:
        try:
            result = urllib.request.urlopen(full_url).read()
            jsonData = json.loads(result)

            if jsonData.get("data", {}).get("audio_address"):
                print("✅ 语音合成任务完成！")
                return jsonData["data"]["audio_address"]
            elif "error_code" in jsonData and jsonData["error_code"] == 20000000 and "data" in jsonData:
                print("-> 语音合成排队中...请等待...")
                time.sleep(10)
            else:
                print("-> 语音合成进行中...")
                time.sleep(10)
        except urllib.error.URLError as e:
            print(f"网络请求失败: {e.reason}")
            return None
        except Exception as e:
            print(f"查询状态时发生未知错误: {e}")
            return None

def synthesize_to_audio(appkey, token, text):
    """
    使用阿里云长文本语音合成 API 生成音频。
    Generates audio using Aliyun long-text TTS API.
    """
    if not text:
        return None
    
    host = 'nls-gateway.cn-shanghai.aliyuncs.com'
    url = f'https://{host}/rest/v1/tts/async'
    http_headers = {'Content-Type': 'application/json'}
    
    # 构造请求体
    tr = TtsRequest("aiqian", 16000, 35, "wav", False, text)
    tp = TtsPayload(False, "", tr) # 不使用回调，而是轮询
    th = TtsHeader(appkey, token)
    tc = TtsContext("mydevice")
    tb = TtsBody(th, tc, tp)
    body = json.dumps(tb, default=tb.tojson)
    
    try:
        conn = http.client.HTTPSConnection(host)
        conn.request(method='POST', url=url, body=body.encode('utf-8'), headers=http_headers)
        response = conn.getresponse()
        
        if response.status == 200:
            jsonData = json.loads(response.read().decode('utf-8'))
            if jsonData['error_code'] == 20000000:
                task_id = jsonData['data']['task_id']
                request_id = jsonData['request_id']
                
                # 轮询等待任务完成并获取音频URL
                audio_url = wait_for_completion(appkey, token, task_id, request_id)
                return audio_url
            else:
                print(f"x 语音合成请求失败: {jsonData['error_message']}")
                return None
        else:
            print(f"x HTTP 请求失败: {response.status} {response.reason}")
            print(f"响应内容: {response.read().decode('utf-8')}")
            return None
    except Exception as e:
        print(f"x 语音合成请求时发生错误: {e}")
        return None

# --------------------------------------------------------------
# Markdown 清理函数
# Markdown cleaning functions
# --------------------------------------------------------------

def clean_markdown_for_tts(markdown_text):
    """
    清洗 Markdown 文本，为 TTS 准备，移除代码块、链接、图片等非文本元素。
    Cleans Markdown text for TTS, removing code blocks, links, images, etc.
    """
    # 移除代码块
    cleaned_text = re.sub(r'```[\s\S]*?```', '', markdown_text)
    # 移除行内代码
    cleaned_text = re.sub(r'`([^`]+)`', r'\1', cleaned_text)
    # 移除标题
    cleaned_text = re.sub(r'^#+\s*', '', cleaned_text, flags=re.MULTILINE)
    # 移除图片和链接
    cleaned_text = re.sub(r'!*\[(.*?)\]\(.*?\)', r'\1', cleaned_text)
    # 移除粗体
    cleaned_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', cleaned_text)
    # 移除斜体
    cleaned_text = re.sub(r'(\*|_)(.*?)\1', r'\2', cleaned_text)
    # 移除列表项
    cleaned_text = re.sub(r'^\s*([*-]|\d+\.)\s+', '', cleaned_text, flags=re.MULTILINE)
    # 移除引用块
    cleaned_text = re.sub(r'^>\s*', '', cleaned_text, flags=re.MULTILINE)
    # 移除分隔线
    cleaned_text = re.sub(r'^(\s*[-*_]\s*){3,}\s*$', '', cleaned_text, flags=re.MULTILINE)
    # 移除空行
    cleaned_text = os.linesep.join([s for s in cleaned_text.splitlines() if s.strip()])
    return cleaned_text

def remove_tag(content):
    """
    接收全文内容，删除旧的meting HTML代码和meting Hexo控件代码，返回清理后的文本。
    Receives full text content, removes old meting HTML and Hexo tags, and returns the cleaned text.
    """
    # 匹配 aplayer 和 meting 标签的正则表达式模式，现在也包括了 meting-js HTML标签
    # Regex pattern to match aplayer and meting tags, now also includes meting-js HTML tags
    player_pattern = r'\{%\s*(aplayer|meting).*?%}\s*|<meting-js[\s\S]*?<\/meting-js>'
    return re.sub(player_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)

def process_markdown_file(md_path, aliyun_token):
    """
    处理单个 Markdown 文件，执行 TTS 生成。
    Processes a single Markdown file, performing TTS generation.
    """
    filename = os.path.basename(md_path)
    audio_filename = filename.replace('.md', '.wav')
    audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
    
    # 检查音频文件是否存在
    if os.path.exists(audio_filepath):
        print(f'√ 音频文件 {audio_filename} 已存在，跳过生成。')
        return

    print(f'开始处理：{filename}')
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 清除文件中现有的播放器标签
    md_content_cleaned = remove_tag(md_content)
    
    # 提取并清理文章正文
    text_to_speak = re.sub(r'^---[\s\S]*?---', '', md_content_cleaned, 1).strip()
    text_to_speak = clean_markdown_for_tts(text_to_speak)
    
    if not text_to_speak:
        print(f'-> {filename} 正文为空，跳过音频生成。')
        return
    
    # 调用阿里云 TTS API 生成音频，直接使用整个文本
    audio_url = synthesize_to_audio(ALIYUN_APPKEY, aliyun_token, text_to_speak)
    
    if audio_url:
        try:
            # 下载音频文件
            print("-> 正在下载音频文件...")
            urllib.request.urlretrieve(audio_url, audio_filepath)
            print(f'✅ 成功保存最终音频文件：{audio_filename}')
        except Exception as e:
            print(f"x 下载音频文件时发生错误: {e}")
            return
    else:
        print(f"x 语音合成失败，跳过。")
        return


def main():
    """
    主函数，遍历文章目录并处理每个文件。
    Main function to traverse the posts directory and process each file.
    """
    # 获取阿里云 Token
    aliyun_token = get_aliyun_token()
    if not aliyun_token:
        print("无法获取阿里云 Token，脚本终止。")
        sys.exit(1)

    print("\n开始扫描并处理 Markdown 文件...")
    start_time = time.time()
    
    if not os.path.isdir(POSTS_DIR):
        print(f"错误: 博客文章目录 '{POSTS_DIR}' 不存在。请修改 POSTS_DIR 变量。")
        return

    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            md_path = os.path.join(POSTS_DIR, filename)
            process_markdown_file(md_path, aliyun_token)
            print('-' * 20)
            
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"所有文件处理完毕。总耗时: {elapsed_time:.2f}秒。")


if __name__ == "__main__":
    main()
