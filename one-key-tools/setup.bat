@echo off
REM ======================================================================
REM 脚本名称: setup.bat
REM 作用: Hexo博客一键配置，用于自动化安装依赖、修改配置和替换密钥。
REM 放置位置: /one-key-tools/
REM ======================================================================

echo.
echo ===========================================
echo   Hexo博客一键配置工具
echo ===========================================
echo.

REM --- 第1步: 将源脚本文件复制到博客根目录 ---
echo.
echo ------------------------------------------
echo 1. 正在复制必要的脚本文件...
echo ------------------------------------------
echo.

copy /Y "gen_audio.py" ".."
copy /Y "gen_abstract.py" ".."
copy /Y "gen_tag.py" ".."
copy /Y "gen_site.sh" ".."

if %errorlevel% neq 0 (
    echo.
    echo 错误: 文件复制失败。请检查文件是否存在或权限问题。
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo √ 脚本文件复制成功。
)

REM --- 第2步: 检测并安装 Python 解释器 ---
REM 使用 'where' 命令检测Python是否已安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ------------------------------------------
    echo 2. 未检测到 Python，正在尝试使用 Windows 包管理器安装...
    echo ------------------------------------------
    echo.
    
    winget install -e --id Python.Python.3.11 --source winget
    
    if %errorlevel% neq 0 (
        echo.
        echo 错误: Python 安装失败。请手动访问 https://www.python.org/ 下载并安装。
        echo.
        pause
        exit /b 1
    ) else (
        echo.
        echo √ Python 安装成功。
    )
) else (
    echo.
    echo √ 已检测到 Python 解释器。
)

REM --- 第3步: 安装必要的 Python 模块 ---
echo.
echo ------------------------------------------
echo 3. 正在安装 Python 模块 (openai, aliyun-python-sdk-core)...
echo ------------------------------------------
echo.

python -m pip install openai aliyun-python-sdk-core
if %errorlevel% neq 0 (
    echo.
    echo 错误: pip 模块安装失败。请检查网络连接或手动运行 'pip install openai aliyun-python-sdk-core'。
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo √ 模块安装成功。
)

REM --- 第4步: 运行自动填充配置脚本 ---
echo.
echo ------------------------------------------
echo 4. 正在执行配置自动填充脚本 (auto_fill.py)...
echo ------------------------------------------
echo.

python auto_fill.py

if %errorlevel% neq 0 (
    echo.
    echo 错误: 配置脚本执行失败。请检查 auto_fill.py 文件是否存在或内容是否有误。
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo √ 配置脚本执行成功。
)


echo.
echo ===========================================
echo 所有配置已完成，你可以开始使用了！
echo ===========================================
echo.

pause
