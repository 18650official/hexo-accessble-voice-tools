#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

# ===============================================
# 脚本名称：update_metingjs_tags.py
# 作用：移除所有Markdown文件中的旧播放器标签，并添加新的Meting-js HTML标签。
# ===============================================

# 文章文件夹的相对路径
# Relative path to the posts directory
POSTS_DIR = './source/_posts'
# 音频文件夹的相对路径，确保它与你的音频文件位置匹配
# Relative path to the audio directory, make sure it matches your audio file location
AUDIO_DIR = './source/audio'

# 请在这里填入你的封面图片URL
# Please fill in your cover image URL here
# Example: COVER_URL = "https://cdn.jsdelivr.net/gh/example/image.jpg"
COVER_URL = "https://snowmiku-blog-1326916956.cos.ap-hongkong.myqcloud.com/Screenshot_2024-08-15-00-35-26-521_com.tencent.mm.jpg?imageSlim"

def remove_and_add_meting_js_tag():
    """
    遍历Markdown文件，移除旧的APlayer和Meting标签，并添加新的Meting-js HTML标签。
    Iterates through Markdown files, removes old APlayer and Meting tags, and adds new Meting-js HTML tags.
    """
    # 匹配 aplayer 和 meting 标签的正则表达式模式，现在也包括了 meting-js HTML标签
    # Regex pattern to match aplayer and meting tags, now also includes meting-js HTML tags
    player_pattern = r'\{%\s*(aplayer|meting).*?%}\s*|<meting-js[\s\S]*?<\/meting-js>'
    # 匹配 <!-- more --> 标签
    # Match the <!-- more --> tag
    more_pattern = r'(<!--\s*more\s*-->)'
    # 匹配 Front-matter 部分
    # Match the Front-matter section
    front_matter_pattern = re.compile(r'^(---[\s\S]*?---)\s*', re.MULTILINE)

    print(f"开始扫描文件夹 '{POSTS_DIR}' 以更新标签...")
    
    # 遍历文件夹中的所有文件
    # Iterate through all files in the directory
    for filename in os.listdir(POSTS_DIR):
        # 确保只处理 .md 文件
        # Ensure only .md files are processed
        if filename.endswith(".md"):
            md_path = os.path.join(POSTS_DIR, filename)

            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 移除所有已存在的播放器标签（Hexo标签和HTML标签）
                # Remove all existing player tags (Hexo tags and HTML tags)
                content = re.sub(player_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
                
                # 新增逻辑：清理多余的空白行，将连续三行或更多的空行压缩为两行
                # New logic: Clean up extra blank lines, compressing three or more consecutive newlines into two
                content = re.sub(r'[\r\n]{3,}', '\n\n', content)

                # 获取文件名（不包含扩展名）
                # Get the filename without the extension
                file_name_without_ext = os.path.splitext(filename)[0]
                
                # 检查对应的.wav文件是否存在
                # Check if the corresponding .wav file exists
                wav_file_path = os.path.join(AUDIO_DIR, f"{file_name_without_ext}.wav")
                if not os.path.exists(wav_file_path):
                    print(f"跳过 {filename}：未找到对应的 .wav 文件。")
                    continue

                # 构造Meting-js HTML标签
                # Construct the Meting-js HTML tag
                meting_js_tag = f'''
<meting-js
    name="朗读"
    artist="Azure"
    url="/audio/{file_name_without_ext}.wav"
    cover="{COVER_URL}"
    fixed="false">
</meting-js>
'''
                # 查找 <!-- more --> 标签
                # Find the <!-- more --> tag
                more_match = re.search(more_pattern, content)

                if more_match:
                    # 如果找到了 <!-- more --> 标签，在其后插入 meting 标签
                    # If the <!-- more --> tag is found, insert the meting tag after it
                    more_tag_end = more_match.end()
                    new_content = content[:more_tag_end] + '\n\n' + meting_js_tag + content[more_tag_end:]
                else:
                    # 如果没有找到 <!-- more --> 标签，则在 front-matter 之后插入
                    # If the <!-- more --> tag is not found, insert after the front-matter
                    match = front_matter_pattern.search(content)
                    if match:
                        front_matter = match.group(1)
                        body = content[match.end():]
                        new_content = front_matter + '\n\n' + meting_js_tag + body
                    else:
                        # 如果没有 Front-matter，则直接加到开头
                        # If there's no Front-matter, add it directly to the beginning
                        new_content = meting_js_tag + content

                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"-> 成功更新 {filename}，已替换为 Meting-js HTML 标签。")

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")

if __name__ == "__main__":
    if COVER_URL == "https://example.com/your-default-cover.jpg":
        print("警告：请在脚本中设置 COVER_URL，否则无法正常工作！")
    else:
        remove_and_add_meting_js_tag()
