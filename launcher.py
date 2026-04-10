import subprocess
import sys
import os

def check_and_install_dependencies():
    required = ["PyQt5", "openpyxl"]
    missing = []
    
    for lib in required:
        try:
            if lib == "PyQt5":
                import PyQt5.QtWidgets
            else:
                __import__(lib)
        except ImportError:
            missing.append(lib)
    
    if missing:
        print(f"检测到缺失依赖库: {', '.join(missing)}")
        print("正在尝试为您自动安装，请稍候...")
        try:
            # 使用当前 Python 运行环境安装
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("依赖库安装成功！")
        except Exception as e:
            print(f"自动安装失败: {e}")
            print("请尝试手动运行: pip install -r requirements.txt")
            return False
    return True

def main():
    print("==========================================")
    print("      自动化排课系统 - 启动自检程序")
    print("==========================================")
    
    # 记录当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    if check_and_install_dependencies():
        print("\n正在启动主程序窗口...")
        try:
            # 导入并运行 main.py 的逻辑
            # 这里使用 subprocess 以确保 UI 进程独立，或者直接导入
            import main
            # 假设 main.py 中有主入口逻辑（在 __main__ 中）
            # 由于 main.py 已经有了 if __name__ == "__main__": 逻辑，
            # 如果直接 import main，它里面的 app.exec() 可能会跑起来，
            # 但为了稳妥起见，我们直接用 subprocess 启动它
            subprocess.Popen([sys.executable, "main.py"])
        except Exception as e:
            print(f"启动失败: {e}")
            input("\n按回车键退出...")
    else:
        input("\n检测到环境问题，无法启动。按回车键退出...")

if __name__ == "__main__":
    main()
