#! /usr/bin/env python

import os

if __name__ == '__main__':
    from PyInstaller.__main__ import run
    ops = ['main.py',
           '-F',
           '-w',
           '--paths=C:\\Program Files\\Python\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin',
           '--hidden-import=queue',
           ]
    # ops = [
    #     '--paths=C:\\Program Files\\Python\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin',
    #     '--windowed',
    #     '--onefile',
    #     '--clean',
    #     '--noconfirm',
    #     'main.py'
    # ]
    run(ops)