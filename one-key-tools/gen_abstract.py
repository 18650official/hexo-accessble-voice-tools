# APIKey定义
APIKey = ''
# -*- coding: utf-8 -*-
import os
import re
import time
from openai import OpenAI

# ====================
# 配置部分
# Configuration Section
# ====================
# 请将此路径替换为你的Hexo博客文章目录，通常是 'source/_posts'
# Please replace this with the path to your Hexo blog posts, usually 'source/_posts'
POSTS_DIR = 'source/_posts'
# 传递给大模型进行摘要生成的文章内容最大字符数
# Maximum number of characters for the summary to be sent to the LLM
SUMMARY_CHARS_LIMIT = 250

# 配置通义千问 API
# Configure Tongyi Qianwen API
try:
    client = OpenAI(
        # 如果没有配置环境变量，请用你的阿里云百炼API Key替换os.getenv()
        # Replace with your actual Dashscope API Key if not set as an environment variable
        api_key=APIKey,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
except Exception as e:
    print(f"Failed to initialize Tongyi Qianwen client: {e}")
    client = None

# 用于匹配和查找 '<!-- more -->' 标签的字符串
# String to match and find the '<!-- more -->' tag
MORE_TAG = '<!-- more -->'
# 用于匹配 Front-matter 块的正则表达式
# Regex to match the Front-matter block at the beginning of the file
FRONT_MATTER_PATTERN = re.compile(r'^(---[\s\S]*?---)\s*', re.MULTILINE)
# 用于匹配 Hexo 的 APlayer 标签的正则表达式
# Regex to match Hexo's APlayer tags
APLAYER_TAG_PATTERN = re.compile(r'\{\s*%\s*aplayer.*?%\s*\}', re.DOTALL)
# 用于匹配 Markdown 代码块的正则表达式
# Regex to match markdown code blocks
CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]*?```', re.DOTALL)
# 新增：用于匹配 meting-js HTML 标签和 meting Hexo 标签的正则表达式
# New: Regex to match both meting-js HTML tags and meting Hexo tags
METING_PLAYER_PATTERN = re.compile(r'\{\s*%\s*meting.*?%\s*\}|<meting-js[\s\S]*?<\/meting-js>', re.DOTALL)


def clean_markdown_for_llm(markdown_text):
    """
    清洗 Markdown 文本，为大模型处理做准备。
    移除代码块、链接、图片和其他非文本元素。
    """
    cleaned_text = CODE_BLOCK_PATTERN.sub('', markdown_text)
    cleaned_text = re.sub(r'`([^`]+)`', r'\1', cleaned_text)
    cleaned_text = re.sub(r'^#+\s*', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'!*\[(.*?)\]\(.*?\)', r'\1', cleaned_text)
    cleaned_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', cleaned_text)
    cleaned_text = re.sub(r'(\*|_)(.*?)\1', r'\2', cleaned_text)
    cleaned_text = re.sub(r'^\s*([*-]|\d+\.)\s+', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'^>\s*', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'^(\s*[-*_]\s*){3,}\s*$', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = os.linesep.join([s for s in cleaned_text.splitlines() if s.strip()])
    return cleaned_text

def get_summary_from_llm(text):
    """
    使用通义千问 API 生成文本摘要。
    """
    if not client:
        print("x 通义千问客户端未初始化。跳过摘要生成。")
        return None
    
    prompt = f"请根据以下文章内容，用中文生成一篇不超过100字的精炼摘要，以便于读者快速了解文章主旨。\n\n文章内容：\n{text}"
    
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': '你是一个善于提炼文章要点的助手，能够根据文章内容生成高质量的摘要。'},
                {'role': 'user', 'content': prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"x 调用通义千问API失败：{e}")
        return None

def process_markdown_file(md_path):
    """
    处理单个 Markdown 文件，插入摘要和 more 标签（如果缺失）。
    """
    filename = os.path.basename(md_path)
    print(f'开始处理：{filename}')

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 1. 检查文章是否已经有 <!-- more --> 标签
    if MORE_TAG in md_content:
        print(f'√ {filename} 已经包含 "{MORE_TAG}" 标签，跳过。')
        return

    # 2. 找到 front-matter 和正文
    match = FRONT_MATTER_PATTERN.search(md_content)
    if not match:
        print(f'x {filename} 格式异常，无法找到Front-matter。跳过。')
        return

    front_matter = match.group(1).strip()
    front_matter_end_index = match.end()
    body_with_player = md_content[front_matter_end_index:]
    
    # 3. 找到 Meting 标签的位置，如果未找到则跳过
    player_match = METING_PLAYER_PATTERN.search(body_with_player)
    if not player_match:
        print(f'x {filename} 未找到 Meting 标签，跳过摘要生成。')
        return

    # 4. 提取 Meting 标签**之后**的内容作为摘要源
    text_after_player = body_with_player[player_match.end():].strip()
    text_for_summary = clean_markdown_for_llm(text_after_player)
    text_for_summary = text_for_summary[:SUMMARY_CHARS_LIMIT]
    
    if not text_for_summary:
        print(f'-> {filename} Meting 标签后正文为空，无法生成摘要。跳过。')
        return

    # 5. 调用大模型生成摘要
    print(f'-> 正在调用大模型为 {filename} 生成摘要...')
    generated_summary = get_summary_from_llm(text_for_summary)

    if not generated_summary:
        print(f'x {filename} 摘要生成失败，跳过。')
        return

    # 6. 重新构造文章内容
    body_before_player = body_with_player[:player_match.start()]
    player_tag = player_match.group(0)
    body_after_player = body_with_player[player_match.end():]

    new_content_body = f"{body_before_player}\n\n{generated_summary}\n\n{MORE_TAG}\n\n{player_tag}{body_after_player}"
    final_content = f"{front_matter}\n\n{new_content_body.strip()}"

    # 7. 写入修改后的文件
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f'✅ 已为 {filename} 成功插入摘要和 "{MORE_TAG}" 标签。')
    

def main():
    """
    主函数，遍历文章目录并处理每个文件。
    """
    print("开始扫描并处理 Markdown 文件...")
    start_time = time.time()
    
    if not os.path.isdir(POSTS_DIR):
        print(f"错误: 博客文章目录 '{POSTS_DIR}' 不存在。请修改 POSTS_DIR 变量。")
        return

    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            md_path = os.path.join(POSTS_DIR, filename)
            process_markdown_file(md_path)
            print('-' * 20)
            
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"所有文件处理完毕。总耗时: {elapsed_time:.2f}秒。")


if __name__ == "__main__":
    # print("警告：此脚本将直接修改你的文件。强烈建议在运行前备份你的整个 Hexo 文件夹。\n")
    # input("按 Enter 键开始执行...")
    main()
