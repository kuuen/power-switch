# power-switch

12v鉛バッテリー放電管理

## Description 説明
指定の電圧以下になると放電カットを行う  
放電再開の電圧の指定が可能

おまけ機能  
バッテリー電圧、消費電流、発電電流をログに保存、グラフにしてhttpで確認が可能。セキュリティ的配慮は全く無し  
物理スイッチ追加でRaspberry Piをシャットダウン  

## Requirement
・ソフト  
作動環境  
OS raspbian 9.4  
python 3.5.3  
NumPy 1.16.1  
i2c-tools3.1.2-3  

・ハード  
Raspberry Pi Zero Rev 1.3
wifiドンクル　PLANEX GW-USValue-EZ 802.11n Wireless Adapter [Realtek RTL8188CUS]  
電流、電圧、電力モジュール INA226 ２個  
スイッチングモジュール 953-1C-12DG-1  
モータドライバ TA7291P (ラズベリーパイのGPIOの低電流ではスイッチングモジュールの切り替えができなかった為、12vバッテリーの電気を使う)  
降圧電源モジュール 型番わすれた　モータドライバで電圧調整はできたがこれを使えば容易だから使用  
ケーブル、ケーブルコネクタ等  
DC12vからUSB電源に変換できるソケット  

## Install
・ソフト  
ソースを適当なディレクトリに配置(インストーラを作成すれば手作業は省けるはずね  
各environmentFile.txt,とshファイルにあるパスを変更  
power-switch/main/power-switch.pyの以下を適切なな値に設定する  
 VOLT_MIN = 12.5     # 最低電圧  
 VOLT_RETURN = 13.5  # 放電再開電圧  

以下を/etc/systemd/system/にシンボリックリンクとして配置。systemctl disableすると削除されるからシンボリックリンクのほうが面倒くさくない  
 power-switch/main/power-switch.service  
 power-switch/http/http-server.service  
 interrupt/shutdown-switch.service  
 コマンド sudo ln -s フルパス/各ファイル.service /etc/systemd/system/各ファイル.service  
sudo systemctl enable 各サービス  

crontabにグラフ作成実行を記述  
　# 0時10分にグラフ作成を行う  
 10 0 * * * フルパス/power-switch/plot/start.sh

httpサーバのポート変更(初期値は8000)  
 power-switch/http/http-server.pyの以下を変更  
 server_address = ("localhost", 8000)  
 
i2cを有効化  
 sudo raspi-config -> Interfacing Options -> I2C をEnable  
 
・ハード  
INA226  
 i2cのアドレス設定 はんだづけする  
 ●がはんだ付ける場所
 
 アドレス0x4c  
 1  
 G 　 ●  
 C ●  
 D  
 /A1 A0  
 
 アドレス0x41  
 1 　 ●  
 G ●  
 C  
 D  
 /A1 A0  
 sudo i2cdetect -y 1 で接続確認、アドレスを参照できる  
 
他のモジュールをバッテリーや充電ケーブルに接続する  

全体図をどうにかして書いてみる
![図](https://github.com/kuuen/power-switch/blob/master/DSC_0063.JPG)
やる気がでたら後で清書する

