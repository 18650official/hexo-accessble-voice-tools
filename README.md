# Hexo 博客有声化自动化工具

详细使用方法请参考 [【文档】](https://snowmiku-home.top/2025/08/19/post-2025819/)

本项目提供了一套专为 Hexo 博客框架设计的自动化脚本，旨在简化为文章添加旁白和音频播放功能的过程。

无论您是想为博客文章生成音频版本，还是只想添加一个精致的音频播放器，这个工具都能自动处理整个工作流程。

## ✨ 功能特性

- **自动化语音合成 (TTS):** 使用强大的 TTS 引擎将您的 Markdown 博客文章转换为高质量的音频文件。
- **智能音频播放器管理:** 自动在您的文章中插入现代化的音频播放器 (`meting-js`)，同时移除旧的标签 (`aplayer`, `meting`) 以避免冲突。
- **智能摘要生成:** 调用大型语言模型 (LLM) 为您的文章生成精炼摘要，并将其添加到 `<!-- more -->` 标签之前，以提升 SEO 和读者体验。
- **高效工作流:** 跳过已处理过的文件，在后续运行中节省时间和资源。
- **云集成准备:** 轻松配置云端 TTS 和 LLM 服务。

## 🚀 使用方法

1.  **配置 API 密钥:** 按照脚本文档中的说明，将所需的 API 密钥添加到 `key.txt` 文件中。
2.  **运行安装脚本:** 执行 `setup.bat` 安装所有必需的 Python 依赖。
3.  **处理您的文章:** 运行 `gen_audio.py` 脚本，即可自动生成音频文件、摘要并插入音频播放器标签。运行`gen_site.sh`可以自动化完成整个配置工作
4.  **部署:** 您的 Hexo 博客现在已经具备完整的音频播放功能。
5.  **卸载：** 执行工具目录的`uninstall.bat`可以完成整个工具链的卸载和音频文件的移除操作。

### 示例

[【我的个人主页】](https://snowmiku-home.top/)

---
由社区以 ❤️ 制作。

# Hexo Voice-over Automation Tool

This project provides a suite of automation scripts for the Hexo blogging framework, designed to streamline the process of adding voice-over and audio playback features to your articles.

Whether you're looking to create an audio version of your blog posts or just want to add a polished audio player, this tool handles the entire workflow automatically.

## ✨ Features

- **Automated Text-to-Speech (TTS):** Converts your markdown blog posts into high-quality audio files using a powerful TTS engine.
- **Intelligent Audio Player Management:** Automatically inserts a modern audio player (`meting-js`) into your articles, removing old tags (`aplayer`, `meting`) to prevent conflicts.
- **Smart Summary Generation:** Calls a Large Language Model (LLM) to generate a concise summary of your article, which is then added before the `<!-- more -->` tag for better SEO and reader experience.
- **Efficient Workflow:** Skips files that have already been processed, saving time and resources during subsequent runs.
- **Ready for Cloud Integration:** Easily configurable with cloud-based TTS and LLM services.

## 🚀 How to Use

1.  **Configure API Keys:** Add your required API keys to a `key.txt` file as specified in the script documentation.
2.  **Run the Setup Script:** Execute `setup.bat` to install all necessary Python dependencies.
3.  **Process Your Blog Posts:** Run `gen_audio.py` to generate audio files, summaries, and insert the audio player tags automatically.
4.  **Deploy:** Your Hexo blog is now ready with a full-featured audio playback experience.

### Example

[Click to my Blog](https://snowmiku-home.top/)

---
Made with ❤️ by the community.