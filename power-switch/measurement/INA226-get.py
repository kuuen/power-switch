'''
電圧、電流を取得
'''

# coding:utf-8
import time
import subprocess
import struct


# i2cgetで得た値をintに変換して返す
def ConvertValue(strHax):
    h = int(strHax, 16).to_bytes(2, 'little')
    return int.from_bytes(h, 'big')

#電圧測定部分の関数
def GetV(address):
    check = subprocess.getoutput("i2cget -y 1 " + address + " 0x02 w")
    test = ConvertValue(check) * 1.25 / 1000
    result = ( int(check[4:6], 16) * 256 + int(check[2:4], 16)) * 1.25/1000
    return result

#電流測定部分の関数
def GetA(address):
    check = subprocess.getoutput("i2cget -y 1 " + address + " 0x04 w")

    val = ConvertValue(check)

    kekka = 0
    print('生データ:' + str(val))
    if val >= 0:
        kekka =  val
    else:
        kekka =  val * -1

    return kekka


print("計器その1 " + str(GetV("0x41")) + " V, " + str(GetA("0x41")) + " mA ")
print("計器その2 " + str(GetV("0x4c")) + " V, " + str(GetA("0x4c")) + " mA ")


