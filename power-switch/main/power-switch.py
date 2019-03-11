

# coding: utf-8

# In[1]:


import os
import RPi.GPIO as GPIO
import subprocess
import time
import datetime
from logging import getLogger, StreamHandler, FileHandler ,DEBUG, INFO, ERROR, Formatter
from logging.handlers import TimedRotatingFileHandler

I2C_ADDRESS_INA226_SOLAR = 0x41 # ソーラパネル 電気判定
I2C_ADDRESS_INA226_POWER = 0x4c # バッテリー電気判定
I2C_ADDRESS_INA226_NONE = 0xff


INTERVAL_EASUREMENT = 300 # 測定間隔

INTERVAL_GPIO_INIT = 3   # GPIO初期化時の待ち時間

VOLT_MIN = 12.5     # 最低電圧
VOLT_RETURN = 13.5  # 放電再開電圧
AMPERE_MAX = 7000   # 大電流量mA単位

# ログの出力レベル
logLevel = INFO

# ログ出力の設定------↓
logger = getLogger(__name__)
#handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler_format = Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 直接起動だとコンソールに、サービス起動だとsyslogに出力される
handler = StreamHandler()
handler.setLevel(ERROR) # ログレベルははERROR固定
handler.setFormatter(handler_format)

# ログファイルに設定
logFileName = 'log.txt'

# サービス起動時は環境変数の値から出力するパスを指定する
if 'SWITCH_LOG_FILE_PATH' in os.environ :
    logFileName = os.environ['SWITCH_LOG_FILE_PATH'] + logFileName
else:
    print('loggerError: There is no environment variable')
    quit()

# 日付が変更されるたびに呼び出す when='midnight'午前０時にロールオーバ
# when='D' は起動した24時間後にロールオーバー 24時間以上プロセスが動いてないとロールオーバ
# しないような気がする
def CreateLogFileHandler():
    newTrh = TimedRotatingFileHandler(
        filename = logFileName,
        backupCount = 6,
        when='midnight',
        encoding='utf-8')

    newTrh.setLevel(logLevel)
    newTrh.setFormatter(handler_format)
    return newTrh

timedRotatingFileH = CreateLogFileHandler()

logger.setLevel(logLevel)
logger.addHandler(handler)
logger.addHandler(timedRotatingFileH)
logger.propagate = False
logger.debug('logger 設定完了')



# In[3]:

class INA226:
    # 扱うアドレスを指定
    def __init__(self, i2cAddress = I2C_ADDRESS_INA226_NONE, dummy = False):
        self.i2cAdress = i2cAddress
        self.dummy = dummy

        if self.dummy == False :

            # i2cを指定。 0x00 アドレスへ　0x47 0x27 の値を書き込む
            # 各引数の意味
            # -y 対話モード
            # 1：I2C通信バス番号　ラズパイなら1固定
            # I2cのアドレス
            # アドレス0x05 に書き込む w指定なら 0x2747 となる※ バイトオーダを意識しないといけない
            #
            # 書き込むデータの長さを最後に指定
            # b：1バイト（8ビット）のデータ
            # w：1ワード（16ビット）のデータ
            # s：SMバスのデータブロックサイズ
            # i：I2Cのデータブロックサイズ アドレスの若い場所から書き込まれる wの場合は0x2747を指定する

            # 0x00は設定値を指定 測定値の方法を変更 値を16回取得して平均値を返す。他はデフォルト値
            subprocess.getoutput("i2cset -y 1 " + str(self.i2cAdress) + "  0x00 0x47 0x27 i")

            # 確認
            test1 = subprocess.getoutput("i2cget -y 1 " + str(self.i2cAdress) + " 0x00 w")
            logger.debug("設定値の内容:" + str(test1))

            # Calibration Register　アンペアがmAでするらしい
            check = subprocess.getoutput("i2cset -y 1 " + str(self.i2cAdress) + " 0x05 0x0a 0x00 i")

    # オブジェクトを文字列に変換して返します。
    # 役割とアドレスを返すようにする
    def __str__(self):
        return "i2c name: 未実装 Address:" + str(self.i2cAdress)

    # 機器が接続されてるか確認
    def isConnect(self):
        if self.dummy:
            return True

        check = subprocess.getoutput("i2cget -y 1 " + str(self.i2cAdress) + " 0x05 w")
        rst = True

        if self.dummy == False and ('r:' == check[4:6] or '/s' == check[4:6]):
            rst = False

        return rst

    # i2cgetで得た値をintに変換して返す
    def __ConvertValue(self, strHax, digit = 2):
        # リトルエンディアンでバイトに変換
        h = int(strHax, 16).to_bytes(digit, 'little')
        # intに変換
        return int.from_bytes(h, 'big')


    #電圧測定部分の関数
    # INA226が検出できない場合は例外を返す
    def GetV(self):
        if self.dummy == True :
            rst = testDummyData.getVolt()

        else:
            rst = self.__GetV()

        logger.debug("アドレス:" + str(self.i2cAdress) + " 電圧取得:"+ str(rst) + 'V')
        return rst

    def __GetV(self):
        if self.isConnect() == False :
            raise INA226ConnectionException("テストエラー")

        # i2cを指定。 0x02アドレスに書き込まれている値を取得
        # 取得値は実際の値とバイト単位で桁が反転(ラスパイのバイトオーダーはリトルエンディアン（LE)のためらしい)している
        # i2cの値0x2895　getoutputの値0x9528
        # ので　１バイト目と２バイト目を入れ替え(バイトスワップ)て0x2895 →　10進数にして1.25倍にする
        check = subprocess.getoutput("i2cget -y 1 " + str(self.i2cAdress) + " 0x02 w")
        return self.__ConvertValue(check) * 1.25 / 1000


    #電流測定部分の関数
    # INA226が検出できない場合は例外を返す
    def GetA(self):
        if self.dummy == True :
            # テストデータを取得する
            #rst = "5.5"
            rst = testDummyData.getCurrentLoad()
        else :
            rst = self.__GetA()

        logger.debug("アドレス:" + str(self.i2cAdress) + " 電流取得:"+ str(rst) + 'mA')
        return rst

    def __GetA(self):
        if self.isConnect() == False :
            raise INA226ConnectionException("テストエラー")

        check = subprocess.getoutput("i2cget -y 1 " + str(self.i2cAdress) + " 0x04 w")
        val = self.__ConvertValue(check)
        if val >= 0:
            rst = val
        else:
            rst = val * -1

        return rst

class INA226ConnectionException(Exception):
    def __str__(self):
        return "接続できてない"


class GPIOException(Exception):
    def __str__(self):
        return ""

# GPIOのコマンドを発行するときはこれで行う
# うまく行かない場合はGPIOExceptionを吐く
def gpioCommand(cmd) :

    rst = subprocess.getoutput(cmd)

    # 結果によって判定
    if 'Directory nonexistent' in rst :
        raise GPIOException('GPIOの初期化がされていない')
    elif '書き込みエラー' in rst :
        raise GPIOException('export,unexportが連続実行された')

def initGpio() :

    gpioCommand("sudo echo 18 > /sys/class/gpio/export")
    time.sleep(INTERVAL_GPIO_INIT)

    gpioCommand("sudo echo out > /sys/class/gpio/gpio18/direction")
    time.sleep(INTERVAL_GPIO_INIT)

def switchOn() :

    # ON
    gpioCommand("sudo echo 1 > /sys/class/gpio/gpio18/value")
    return "switchOn"

def switchOff() :
    gpioCommand("sudo echo 0 > /sys/class/gpio/gpio18/value")
    return "switchOff"

def chkPowerVoltageMotor() :
    return "chkPowerVoltageMotor"

# In[5]:

# サービス開始時に実行
def start():

    # 初期化
    logger.info('--------------------設定値--------------------')
    logger.info('供給時最低電圧：' + str(VOLT_MIN)   + 'V 放電再開電圧：' + str(VOLT_RETURN) + 'V')
    logger.info('大電流量      ：' + str(AMPERE_MAX) + 'mA 監視間隔   :' + str(INTERVAL_EASUREMENT) + '秒')

    initGpio()

    try :
        # 電源状態 0は供給Off
        powerState = 0

        # 無限ループ　外部からプロセス停止か大電流が流れた際に停止する
        while True:

            crenntVolt = chkPower.GetV()
            crenntAmpere = chkPower.GetA()

            solarVolt = chkSolar.GetV()
            solarAmpere = chkSolar.GetA()

            logger.info(',val,電圧(v),電流(mA),' + str(crenntVolt) + ',' + str(crenntAmpere) )
            logger.info(',val2,電圧(v),電流(mA),' + str(solarVolt) + ',' + str(solarAmpere) )
            if powerState == 0 :
                # 電圧は十分であれば電源供給
                if crenntVolt >= VOLT_RETURN :
                    logger.info("電圧回復　供給開始")
                    switchOn()
                    powerState = 1
            else:
                # 電流も監視。規定オーバーの場合は停止する もっと短い頻度で確認するべきでは？
                if crenntAmpere > AMPERE_MAX :
                    logger.info("電流許容量オーバのため終了")
                    break

                # 電圧低下していれば電源遮断
                if crenntVolt < VOLT_MIN :
                    logger.info("電圧低下　切断開始")
                    switchOff()
                    powerState = 0

            time.sleep(INTERVAL_EASUREMENT)

    except INA226ConnectionException as e:
        logger.critical('NA226でエラーのため終了')
        logger.error(e)

    except GPIOException as e:
        logger.critical('GPIOでエラーのため終了')
        logger.error(e)


# In[6]:


# サービス終了時に実行
def stop() :

    # ここで切断するのが適切か？
    try :
        switchOff()
    except GPIOException as e:
        # 例外があっても続行する
        logger.error('GPIOでエラー')
        logger.error(e)
    except Exception as e1:
        logger.critical(e)

    try :
        gpioCommand("sudo echo 18 > /sys/class/gpio/unexport")
    except GPIOException as e:
        # 例外があっても続行する
        logger.error('GPIOでエラー')
        logger.error(e)
    except Exception as e1:
        logger.critical(e)

    return "stop　実行"


# In[7]:


# こっちから開始
import sys
import argparse

# 起動引数
parser = argparse.ArgumentParser()

# 引数設定
parser.add_argument('-m', '--mode', help='start or stop', required = True)
args = parser.parse_args()


# 初期化
chkPower = INA226(I2C_ADDRESS_INA226_POWER)
chkSolar = INA226(I2C_ADDRESS_INA226_SOLAR)

if chkPower.isConnect() == True :
    if args.mode != None :
        if args.mode == 'start' :
            logger.info("起動モード start")
            start()
        elif args.mode == 'stop' :
            logger.info("起動モード stop")
            stop()
        else:
            logger.error('無効な引数: ' + args.mode)

