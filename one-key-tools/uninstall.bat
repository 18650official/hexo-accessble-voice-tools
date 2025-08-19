@echo off
CHCP 65001

echo.
echo ===================================================
echo    正在启动 Hexo 博客有声化自动化工具卸载程序
echo ===================================================
echo.

set /P "CHOICE=此操作将永久删除文件。你确定要继续吗？ (Y/N): "

IF /I "%CHOICE%" NEQ "Y" (
    echo.
    echo 操作已取消。
    echo.
    goto :end
)

echo.
echo =========================
echo 步骤 1/4: 删除文章中的播放器标签
echo =========================
echo.
python "%~dp0\remove_player_tags.py"
echo.
echo 步骤 1 已完成：文章中的播放器标签已删除。
echo.

set /P "CHOICE=你确定要删除 audio 文件夹中的所有音频文件吗？ (Y/N): "
IF /I "%CHOICE%" NEQ "Y" (
    echo.
    echo 操作已取消。
    echo.
    goto :end
)

echo.
echo =========================
echo 步骤 2/4: 删除 audio 文件夹中的所有 .wav 文件
echo =========================
echo.
DEL /Q /S "..\source\audio\*.wav"
echo.
echo 步骤 2 已完成：音频文件已删除。
echo.

set /P "CHOICE=你确定要删除博客根目录下的脚本文件吗？ (Y/N): "
IF /I "%CHOICE%" NEQ "Y" (
    echo.
    echo 操作已取消。
    echo.
    goto :end
)

echo.
echo =========================
echo 步骤 3/4: 删除脚本文件
echo =========================
echo.
DEL /Q "..\gen_audio.py"
DEL /Q "..\gen_tag.py"
DEL /Q "..\gen_abstract.py"
DEL /Q "..\gen_site.sh"
DEL /Q "..\gen_site.bat"
echo.
echo 步骤 3 已完成：脚本文件已删除。
echo.

set /P "CHOICE=所有文件已删除。你确定要删除此工具文件夹吗？ (Y/N): "
IF /I "%CHOICE%" NEQ "Y" (
    echo.
    echo 操作已取消。
    echo.
    goto :end
)

echo.
echo =========================
echo 步骤 4/4: 删除工具文件夹
echo =========================
echo.
RD /S /Q "%~dp0"
echo.
echo 步骤 4 已完成：工具文件夹已删除。
echo.

:end
echo.
echo ===================================================
echo    卸载程序已完成。感谢使用！
echo ===================================================
echo.
pause
