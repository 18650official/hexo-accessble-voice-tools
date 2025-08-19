import os
import re
import sys

# ======================================================================
# 脚本名称: auto_fill.py
# 作用: 自动替换密钥和修改 Hexo 配置文件。
# 放置位置: /one-key-tools/
# ======================================================================

# 获取当前脚本的父目录（即 /one-key-tools/）
# Get the parent directory of the current script (i.e., /one-key-tools/)
TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
# 博客根目录是 /one-key-tools/ 的父目录
# The blog root directory is the parent of /one-key-tools/
BLOG_ROOT = os.path.dirname(TOOL_DIR)

# 文件路径配置
# File path configuration
KEY_FILE = os.path.join(TOOL_DIR, 'key.txt')
GEN_ABSTRACT_SCRIPT = os.path.join(BLOG_ROOT, 'gen_abstract.py')
GEN_AUDIO_SCRIPT = os.path.join(BLOG_ROOT, 'gen_audio.py')
BUTTERFLY_CONFIG_FILE = os.path.join(BLOG_ROOT, '_config.butterfly.yml')

# YAML 注入代码块
# YAML injection code blocks
INJECT_HEAD_CODE = """
    - <!-- require APlayer -->
    - <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/aplayer/dist/APlayer.min.css">
    - <script src="https://cdn.jsdelivr.net/npm/aplayer/dist/APlayer.min.js"></script>
    - <!-- require MetingJS -->
    - <script src="https://cdn.jsdelivr.net/npm/meting@2/dist/Meting.min.js"></script>
    - '<style type="text/css">#toggle-sidebar {bottom: 80px}</style>'"""

PJAX_CODE = """
  enable: true
  exclude:"""


def replace_keys_in_scripts():
    """
    从 key.txt 读取密钥并替换 gen_abstract.py 和 gen_audio.py 中的占位符。
    Reads keys from key.txt and replaces placeholders in gen_abstract.py and gen_audio.py.
    """
    print("--- 正在替换脚本中的 API 密钥 ---")
    try:
        with open(KEY_FILE, 'r', encoding='utf-8') as f:
            keys = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"错误: 未找到 {KEY_FILE} 文件。请确保该文件存在并包含密钥。")
        sys.exit(1)

    # 检查密钥数量是否足够
    # Check if there are enough keys
    if len(keys) < 4:
        print(f"错误: {KEY_FILE} 文件中密钥数量不足（需要4行：通义千问APIKey，阿里云AK_ID，阿里云AK_SECRET，阿里云APPKEY）。")
        sys.exit(1)

    tongyi_key = keys[0]
    aliyun_ak_id = keys[1]
    aliyun_ak_secret = keys[2]
    aliyun_appkey = keys[3]

    # 替换 gen_abstract.py 中的 APIKey
    # Replace APIKey in gen_abstract.py
    try:
        with open(GEN_ABSTRACT_SCRIPT, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r"APIKey = '.*?'", f"APIKey = '{tongyi_key}'", content)
        with open(GEN_ABSTRACT_SCRIPT, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ gen_abstract.py 密钥替换成功。")
    except Exception as e:
        print(f"修改 gen_abstract.py 时出错: {e}")

    # 替换 gen_audio.py 中的阿里云密钥
    # Replace Aliyun keys in gen_audio.py
    try:
        with open(GEN_AUDIO_SCRIPT, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r"ALIYUN_AK_ID = '.*?'", f"ALIYUN_AK_ID = '{aliyun_ak_id}'", content)
        content = re.sub(r"ALIYUN_AK_SECRET = '.*?'", f"ALIYUN_AK_SECRET = '{aliyun_ak_secret}'", content)
        content = re.sub(r"ALIYUN_APPKEY = '.*?'", f"ALIYUN_APPKEY = '{aliyun_appkey}'", content)
        with open(GEN_AUDIO_SCRIPT, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ gen_audio.py 密钥替换成功。")
    except Exception as e:
        print(f"修改 gen_audio.py 时出错: {e}")


def update_butterfly_config():
    """
    将所需的配置字段插入到 _config.butterfly.yml 文件中。
    Inserts required configuration fields into the _config.butterfly.yml file.
    """
    print("\n--- 正在更新 _config.butterfly.yml 文件 ---")
    try:
        with open(BUTTERFLY_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_content = f.read()
    except FileNotFoundError:
        print(f"错误: 未找到 {BUTTERFLY_CONFIG_FILE} 文件。请确保该文件存在。")
        sys.exit(1)
    
    # --- 处理 inject: head: ---
    # 检查是否已包含MetingJS配置，如果已包含则不重复添加
    if re.search(r'Meting\.min\.js', config_content):
        print("✅ 检测到 MetingJS 配置已存在，跳过更新。")
    else:
        # 如果不存在，查找inject: head:字段
        if re.search(r'inject:\s*head:', config_content):
            # 找到inject: head:，在其下方插入新配置
            new_config_content = re.sub(r'(inject:\s*head:)', r'\1' + INJECT_HEAD_CODE, config_content)
            config_content = new_config_content
            print("✅ inject: head: 字段已更新。")
        else:
            # 如果不存在inject: head:，则在文件末尾添加完整的inject:head:
            config_content += f"\n\ninject:{INJECT_HEAD_CODE}"
            print("✅ inject: head: 字段已添加。")
    
    # --- 处理 pjax: ---
    # 查找 pjax: 字段
    pjax_match = re.search(r'pjax:[\s\S]*?(?=\n\S|$)', config_content)
    if pjax_match:
        # 如果 pjax 字段已存在
        pjax_block = pjax_match.group(0)
        if 'enable: true' in pjax_block:
            print("✅ pjax: 字段已配置，无需更新。")
        else:
            # 如果 pjax 存在但 enable: false 或未配置，则替换整个 pjax 块
            config_content = re.sub(r'pjax:[\s\S]*?(?=\n\S|$)', f'pjax:{PJAX_CODE}', config_content)
            print("✅ pjax: 字段已更新。")
    else:
        # 如果 pjax 字段不存在，则在文件末尾添加完整的 pjax: 块
        config_content += f"\n\npjax:{PJAX_CODE}"
        print("✅ pjax: 字段已添加。")

    try:
        with open(BUTTERFLY_CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ _config.butterfly.yml 文件修改成功。")
    except Exception as e:
        print(f"写入文件时出错: {e}")


if __name__ == "__main__":
    replace_keys_in_scripts()
    print("-" * 30)
    update_butterfly_config()
    print("\n所有配置已自动完成！")
