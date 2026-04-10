@echo off
:: 设置极简启动逻辑，避免 CMD 编码解析错误
echo 正在准备启动 Python 控制器...

python launcher.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 启动失败。
    echo 请确认是否安装了 Python。
    pause
)
