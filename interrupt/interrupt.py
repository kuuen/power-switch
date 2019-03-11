import RPi.GPIO as GPIO
import subprocess
import time

GPIO.setmode(GPIO.BCM)
pin = 21
GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)
try:
    pushTime = 0
    while(True):
        # 5秒遊びを入れる　ボタンを押して5秒待たないと応答しないことになる
        isr = GPIO.wait_for_edge(pin, GPIO.FALLING, timeout=5000)
        if isr is None:
            #print("5秒 間 割 り 込 み な し ")
            # ボタンを押されていた場合は　押されていた時間により処理を変える
            if pushTime == 0 :
                #print('count 0')
                continue
            elif pushTime < 10 :
                pushTime = 0
                # 1回押しはwifi再起動 GPIO.wait_for_edgeがうまく制御できないが大雑把にカウント設定すれば
                # 2パターンは分岐できる
                subprocess.call('interrupt/wifi-restart.sh')

                #print('ネットワーク再起動')
                # 処理中にボタン連打されても反応させないようにする
                time.sleep(30)
                continue
            else:
                # シャットダウン
                subprocess.call('interrupt/shut.sh')
                #print('シャットダウン')
                break
        else:
            #print("割 り 込 み あ り ")
            pushTime +=1

finally:
    GPIO.cleanup(pin)
