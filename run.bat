@echo off
echo 正在启动 MarkItDown GUI...
echo Python 版本: 
uv run python --version
echo.
uv run python gui_app.py
pause
