import os
import subprocess
import sys

def run_build():
    print("[*] Checking dependencies...")
    # 安装必要库
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "pyinstaller", "openpyxl", 
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
    except Exception as e:
        print(f"[-] Error installing dependencies: {e}")
        return

    print("[*] Starting PyInstaller build process...")
    
    # 构建指令列表，避免 Shell 字符转义问题
    # 数据分隔符在 Windows 上是分号 ;
    data_sep = ";"
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--add-data", f"styles.qss{data_sep}.",
        "--name", "自动化排课系统",
        "--clean",
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n[+] SUCCESS: Your executable is ready in the 'dist' folder.")
    except Exception as e:
        print(f"\n[-] ERROR: Build failed. Details: {e}")

if __name__ == "__main__":
    run_build()
