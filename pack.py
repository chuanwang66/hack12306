#-*- coding:utf-8 -*-
import os
import platform
import shutil, subprocess, sys

if __name__ == "__main__":
    # 1. clear previous build
    previous_build = ['__pycache__', 'build', 'dist']
    for p in previous_build:
        if os.path.exists(p):
            shutil.rmtree(p)

    osname = platform.system()
    if 'windows' in osname.lower():
        process = subprocess.Popen(
            ['C:\Python35\Scripts\pyinstaller.exe', 'main_win.spec'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)

    elif 'darwin' in osname.lower():
        process = subprocess.Popen(
            ['/Library/Frameworks/Python.framework/Versions/3.5/bin/pyinstaller', 'main_mac.spec'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)

    while True:
        output = process.stdout.read(1)
        output = output.decode('utf-8')
        if output == '':
            break
        else:
            sys.stdout.write(output)
            sys.stdout.flush()

    #改名
    os.rename('./dist/qiangpiao/qiangpiao.txt', './dist/qiangpiao/抢票说明.txt')