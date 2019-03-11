#!/bin/sh

#sudo /etc/ifplugd/action.d/action_wpa wlan0 down
#sudo ifdown wlan0
#sleep 3s
#sudo systemctl restart networking.service
#sleep 3s
#sudo /etc/ifplugd/action.d/action_wpa wlan0 up
#sudo ifup wlan0

# つながらないのはwifiデバイス省電力モードせいらしい
# 自らネット接続行為を行えば省電力から復帰する？→しなかった
#ping -c 5 192.168.15.1 > /home/pi/work/python/interrupt/result.txt


#sudo ifconfig wlan0 down
#sleep(3)
#sudo systemctl restart  networking.service
#sleep(3)
#sudo ifconfig wlan0 up

#sleep(20)
#sudo reboot

# スキャンさせようとしたら復帰する？１回に復帰したがそれ以外うまく行かず
# アクセスポイントからの受信のみの場合は省電力モードを維持したままで機能するからか？
#sudo iwlist wlan0 scan > interrupt/result.txt
#iwconfig >> interrupt/result.txt

# 論理的にUSBトングルを抜き差しする うまく機能したがその後は暫く反応が悪い
# 全くつながらないこともあり強引なやり方臭い
#echo -n "1-1" > /sys/bus/usb/drivers/usb/unbind
#sleep(10)
#echo -n "1-1" > /sys/bus/usb/drivers/usb/bind

# なにかしら自身から通信を行えば省電力モードは解除されるか？
#sudo iwconfig wlan0 mode ad-hoc
sudo iwconfig wlan0 mode managed
