
# coding: utf-8

# In[28]:




# In[1]:


# In[27]:


import numpy as np
import matplotlib.pyplot as plt
import datetime
import csv
from decimal import Decimal
import glob
import sys
import argparse
import os
from PIL import Image

from logging import getLogger, StreamHandler, FileHandler ,DEBUG, INFO, ERROR, Formatter
from logging.handlers import TimedRotatingFileHandler

# ログファイルに設定
logFileName = 'create-plot-log.txt'

# ログの出力レベル
logLevel = INFO

# サービス起動時は環境変数の値から出力するパスを指定する
if 'LOG_FILE_PATH_PLOT' in os.environ :
    logFileName = os.environ['LOG_FILE_PATH_PLOT'] + logFileName

# ログ出力の設定------↓
logger = getLogger(__name__)
handler_format = Formatter('%(asctime)s - %(levelname)s - %(message)s')

# StreamHandlerはprint()と同じ働きではない。実行環境によってsyslogや
# コンソールに出力されることはあっても現状ではhttpのレスポンスに流せるない
handler = StreamHandler()
handler.setLevel(logLevel)
handler.setFormatter(handler_format)

trfh = TimedRotatingFileHandler(
    filename = logFileName,
    backupCount = 6,
    when='midnight',
    encoding='utf-8')

trfh.setLevel(logLevel)
trfh.setFormatter(handler_format)

logger.setLevel(logLevel)
logger.addHandler(handler)
logger.addHandler(trfh)
logger.propagate = False

# logFileName:   参照するログファイルをフルパスで指定
# imageFileName: グラフファイルの保存先をフルパスで指定
def createPlot(logFileName, imageFileName):
    print('グラフ作成承りドスエ　対象はこれ' + os.path.basename(logFileName) + 'な<br/>')

    # 電圧の変化がグラフで見やすいようにこれで減算する
    # 0v〜10v　くらいまで省略した形に見える
    VOLT_CHENGE = 10.0
    #VOLT_CHENGE = Decimal(0)
    VOLT_MAX_CORRECTION = 5.0

    csv_obj = csv.reader(open(logFileName, "r"))
    datas = [ v for v in csv_obj]

    # 時間、電流、電圧を分ける
    l = list()
    l2 = list()

    for data in datas:
        if len(data) > 2 and data[2] == 'val':
            try :
                if data[5] == '65535' or  data[6] == '65535' :
                    logger.error(logFileName + " センサー異常値値あり:" + data[0])
                    print('センサー異常値値あり、省きます ' + data[0] + '<br/>')
                    # 異常値の場合は前回の内容を使用する
                    if len(l) > 0 :
                        pr = l[len(l) - 1]
                        l.append({'t':data[0], 'v':pr.get('v'), 'a':pr.get('a')})
                    continue

                l.append({'t':data[0], 'v':float(data[5]) - VOLT_CHENGE, 'a':float(data[6])})
            except ValueError as e:
                logger.error(logFileName + " 無効なデータ:" + data + e.args)
                print('アイエエー。こんなデータ聞いてないよぉ <br/>')
                print(data)
                print(e.args)
                print('<br/>次に進むドスエ<br/>')
        elif len(data) > 2 and data[2] == 'val2':
            try :
                if data[5] == '65535' or  data[6] == '65535' :
                    logger.error(logFileName + " センサー異常値値あり:" + data[0])
                    print('センサー異常値値あり、省きます ' + data[0] + '<br/>')
                    # 異常値の場合は前回の内容を使用する
                    if len(l2) > 0 :
                        pr = l2[len(l2) - 1]
                        l2.append({'t':data[0], 'v':pr.get('v'), 'a':pr.get('a')})
                    continue

                l2.append({'t':data[0], 'a':float(data[6])})
            except ValueError as e:
                logger.error(logFileName + " 無効なデータ:" + data + e.args)
                print('アイエエー。こんなデータ聞いてないよぉ')
                print(data)
                print(e.args)
                print('<br/>次に進むドスエ<br/>')

    if len(l) < 1:
        print('対象が無いドスエ')
        return

    l_v = [d.get('v') for d in l]
    l_t = [d.get('t') for d in l]
    l_a = [d.get('a') for d in l]
    l_a2 = [d.get('a') for d in l2]

    # 折れ線グラフを出力

    # matplot用のリストに格納
    left = np.array(l_t)
    height = np.array(l_v)
    height2 = np.array(l_a)

    bar_height = np.array(l_v)
    line_height = np.array(l_a)
    line_height2 = np.array(l_a2)

    # 出力されるグラフ画像の大きさを調整したい
    # subplots()でfigsizeを指定しないとうまく行かない
    # ★plt.figure(figsize=(150, 140)) #subplotsでサイズ指定後にこれをするとpngは真っ白になる　単位はインチ

    fig, ax1 = plt.subplots(figsize=(20,15))

    # 背景色を指定 グラフ内の色指定もできるらしいが理解できん
    rect = fig.patch
    rect.set_facecolor('azure')

    # 背景に画像を指定 内容が崩れた
#     img = Image.open('/home/kuuen/work/log/1550955515373.jpg')
#     # 画像をarrayに変換
#     haikei = np.array(img)
#     ax1.imshow(haikei)

    # 電圧******************************************************
    ax1.bar(left, bar_height)
    ax1.set_ylabel('Vlt for bar', fontsize = 18)
    ax1.set_facecolor('gray')

    # 電圧y軸のラベルの修正
    # matplotに渡している値は実値から最低電圧を引いいた値になっているから左側のyラベルは実値の目安に
    # する必要がある

    # 最大値を5 (VOLT_CHENGE+で15.0v)にする
    ax1.set_yticks([x  for x in np.arange(VOLT_MAX_CORRECTION)])

    # 描画する値を設定 12.5v以下を省略した値を加算して表示する
    ax1.set_yticklabels([x + float(VOLT_CHENGE) for x in np.arange(VOLT_MAX_CORRECTION)], fontsize=18, color='black')

    # 電流******************************************************
    ax2 = ax1.twinx()
    ax2.plot(left, line_height, linewidth=5, color="crimson", label = 'Consumption')
    ax2.plot(left, line_height2, linewidth=5, color="yellow", linestyle='dashed', label='Generation')
    ax2.tick_params(axis = 'y', which = 'major', labelsize = 18)
    ax2.set_ylabel('Ampere for line(mA)', fontsize = 18)
    # 判例のタイトル
    ax2.legend(title='Precedents', fontsize = 18)

    # x軸(時間)のラベルを作成　他にやりようがある気がする
    xlabel = [''] * len(l_t)
    HOUR_CONT = 12
    count = HOUR_CONT
    for t in l_t:
        if count % HOUR_CONT == 0:
            # 文字列の時間をdatetimeにキャストして 月/日 時分秒に変換
            xlabel[count - HOUR_CONT] = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S').strftime('%m/%d %H:%M')
        count += 1

    ax1.set_xticklabels(xlabel, rotation=90, fontsize=18)


    # タイトル******************************************************
    title = 'Voltage and output current \n'
    title += 'Period range : ' + l_t[0] + ' -> ' + l_t[len(l_t) - 1]
    title += "\n Volt Max = " + str(max(l_v) + VOLT_CHENGE) + "V Min = " + str( min(l_v) + VOLT_CHENGE) + 'V '
    title += "Consumption Ampere Max = " + str(max(l_a)) + 'mA Generation Ampere Max = ' + str(max(l_a2)) + 'mA'
    plt.title(title, fontsize=18)

    plt.savefig(imageFileName, facecolor=fig.get_facecolor())


# 現在のログ
dataFileName = 'log.txt'
imageFile = 'plot'
# サービス起動時は環境変数の値から出力するパスを指定する
if 'PLOT_PATH' in os.environ :
    dataFileName = os.environ['PLOT_PATH'] + dataFileName
    imageFile = os.environ['PLOT_PATH'] + imageFile

#createPlot(dataFileName, imageFile + '.png')

# 起動引数
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', help='現在のログのみ作成 -m now' ,required=False)
args = parser.parse_args()

mode = 0;
if args.mode != None and args.mode.find('now') > -1:
    mode = 1

try :
    createPlot(dataFileName, imageFile + '.png')
except Exception as e:
    logger.error('例外発生:' + dataFileName + e.args)
    # 1ファイルで例外が起きても続行する
    print('アイエエー。予期せぬエラーな')
    print(e.args)

# 現在のログのみの場合はこれで終了
if mode == 1:
    quit()

files = glob.glob(dataFileName + '.*')

# ファイル名の日付を元に降順で並べてから作成する
files.sort(reverse = True)
i = 1
for f in files:
    try :
        createPlot(f, imageFile + str(i) + '.png')
    except Exception as e:
        logger.error('例外発生:' + f + e.args)
        # 1ファイルで例外が起きても続行する
        print('アイエエー。予期せぬエラーな')
        print(e.args)
    i += 1



