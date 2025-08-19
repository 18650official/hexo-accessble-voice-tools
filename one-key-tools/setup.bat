@echo off
REM ======================================================================
REM �ű�����: setup.bat
REM ����: Hexo����һ�����ã������Զ�����װ�������޸����ú��滻��Կ��
REM ����λ��: /one-key-tools/
REM ======================================================================

echo.
echo ===========================================
echo   Hexo����һ�����ù���
echo ===========================================
echo.

REM --- ��1��: ��Դ�ű��ļ����Ƶ����͸�Ŀ¼ ---
echo.
echo ------------------------------------------
echo 1. ���ڸ��Ʊ�Ҫ�Ľű��ļ�...
echo ------------------------------------------
echo.

copy /Y "gen_audio.py" ".."
copy /Y "gen_abstract.py" ".."
copy /Y "gen_tag.py" ".."
copy /Y "gen_site.sh" ".."

if %errorlevel% neq 0 (
    echo.
    echo ����: �ļ�����ʧ�ܡ������ļ��Ƿ���ڻ�Ȩ�����⡣
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo �� �ű��ļ����Ƴɹ���
)

REM --- ��2��: ��Ⲣ��װ Python ������ ---
REM ʹ�� 'where' ������Python�Ƿ��Ѱ�װ
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ------------------------------------------
    echo 2. δ��⵽ Python�����ڳ���ʹ�� Windows ����������װ...
    echo ------------------------------------------
    echo.
    
    winget install -e --id Python.Python.3.11 --source winget
    
    if %errorlevel% neq 0 (
        echo.
        echo ����: Python ��װʧ�ܡ����ֶ����� https://www.python.org/ ���ز���װ��
        echo.
        pause
        exit /b 1
    ) else (
        echo.
        echo �� Python ��װ�ɹ���
    )
) else (
    echo.
    echo �� �Ѽ�⵽ Python ��������
)

REM --- ��3��: ��װ��Ҫ�� Python ģ�� ---
echo.
echo ------------------------------------------
echo 3. ���ڰ�װ Python ģ�� (openai, aliyun-python-sdk-core)...
echo ------------------------------------------
echo.

python -m pip install openai aliyun-python-sdk-core
if %errorlevel% neq 0 (
    echo.
    echo ����: pip ģ�鰲װʧ�ܡ������������ӻ��ֶ����� 'pip install openai aliyun-python-sdk-core'��
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo �� ģ�鰲װ�ɹ���
)

REM --- ��4��: �����Զ�������ýű� ---
echo.
echo ------------------------------------------
echo 4. ����ִ�������Զ����ű� (auto_fill.py)...
echo ------------------------------------------
echo.

python auto_fill.py

if %errorlevel% neq 0 (
    echo.
    echo ����: ���ýű�ִ��ʧ�ܡ����� auto_fill.py �ļ��Ƿ���ڻ������Ƿ�����
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo �� ���ýű�ִ�гɹ���
)


echo.
echo ===========================================
echo ������������ɣ�����Կ�ʼʹ���ˣ�
echo ===========================================
echo.

pause
