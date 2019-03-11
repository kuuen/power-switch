'''
INA226の初期化
測定値の決定する平均化するために取得する回数を16回に変更している
ほかはデフォルト値
'''
# coding:utf-8
import RPi.GPIO as GPIO
import time
import subprocess
import struct



subprocess.getoutput("i2cset -y 1 0x41 0x00 0x47 0x27 i")
check = subprocess.getoutput("i2cset -y 1 0x41 0x05 0x0a 0x00 i")

if 'r:' == check[4:6] :
    print('機器その１No Connected Device')

subprocess.getoutput("i2cset -y 1 0x4c 0x00 0x47 0x27 i")
check = subprocess.getoutput("i2cset -y 1 0x4c 0x05 0x0a 0x00 i")
if 'r:' == check[4:6] :
    print('機器その２No Connected Device')
