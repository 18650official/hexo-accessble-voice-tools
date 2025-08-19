# -*- coding: utf-8 -*-
import os
import re

# ====================
# 配置部分
# Configuration Section
# ====================
# 请将此路径替换为你的Hexo博客文章目录，通常是 'source/_posts'
# Please replace this with the path to your Hexo blog posts, usually 'source/_posts'
POSTS_DIRECTORY = 'source/_posts'

# 正则表达式用于匹配和删除所有已知的音频播放器标签
# Regex to match and delete all known audio player tags
# 这个模式匹配 aplayer Hexo标签、meting Hexo标签和 meting-js HTML标签
PLAYER_TAG_PATTERN = re.compile(
    r'\{\s*%\s*(aplayer|meting).*?%\s*\}|(<meting-js[\s\S]*?<\/meting-js>)',
    re.DOTALL | re.IGNORECASE
)

def remove_tags_from_file(filepath):
    """
    读取文件，删除指定的播放器标签，并将更改写回。
    This function reads a file, removes specified player tags, and writes back the changes.
    """
    try:
        # Read the entire file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 使用正则表达式替换所有匹配到的标签
        new_content = PLAYER_TAG_PATTERN.sub('', content)
        
        # 检查是否发生了任何更改
        if new_content != original_content:
            # 将修改后的内容写回文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 已从文件中移除播放器标签: {filepath}")
        else:
            print(f"文件没有发现需要删除的标签，没有变化: {filepath}")

    except Exception as e:
        print(f"处理文件 {filepath} 时发生错误: {e}")

def main():
    """
    主函数，遍历文章目录并处理每个文件。
    Main function to traverse the posts directory and process each file.
    """
    # 检查目录是否存在
    if not os.path.isdir(POSTS_DIRECTORY):
        print(f"错误: 博客文章目录 '{POSTS_DIRECTORY}' 不存在。请修改 POSTS_DIRECTORY 变量。")
        return

    print("开始扫描并删除文章中的播放器标签...")

    # 遍历指定目录下的所有文件
    for root, _, files in os.walk(POSTS_DIRECTORY):
        for filename in files:
            # 只处理 Markdown 文件
            if filename.endswith(('.md', '.markdown')):
                filepath = os.path.join(root, filename)
                remove_tags_from_file(filepath)

    print("\n所有文件处理完毕。")
    print("请检查你的文章以确认修改成功，并重新生成博客。")


if __name__ == '__main__':
    # 强烈建议在运行脚本前备份你的 Hexo 项目
    print("警告：此脚本将直接修改你的文件。强烈建议在运行前备份你的整个 Hexo 文件夹。\n")
    # input("按 Enter 键开始执行...")
    main()
