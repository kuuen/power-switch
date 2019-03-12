# power-switch

12v鉛バッテリー放電管理

## Description 説明
指定の電圧以下になると放電カットを行う  
放電再開の電圧の指定が可能

おまけ機能  
バッテリー電圧、消費電流、発電電流をログに保存、グラフにしてhttpで確認が可能  
物理スイッチ追加でRaspberry Piをシャットダウン  

## Requirement
・ソフト  
作動環境  
OS raspbian 9.4  
python 3.5.3  
NumPy 1.16.1  

・ハード  
Raspberry Pi Zero　(バージョン忘れた)  
wifiドンクル　PLANEX GW-USValue-EZ 802.11n Wireless Adapter [Realtek RTL8188CUS]  
電流、電圧、電力モジュール INA226 ２個  
スイッチングモジュール 953-1C-12DG-1  
モータドライバ TA7291P (ラズベリーパイのGPIOの低電流ではスイッチングモジュールの切り替えができなかった為、12vバッテリーの電気を使う)  
降圧電源モジュール 型番わすれた　モータドライバで電圧調整はできたがこれを使えば容易だから使用  

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


・ハード

