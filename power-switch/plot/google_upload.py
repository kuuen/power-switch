#!/usr/bin/env python3

#import argparse
import os
import datetime
import pprint
import socket
import glob
import time
import json
from operator import itemgetter

from datetime import datetime as dt
import datetime
import pprint

# カレントディレクトリの変更
#os.chdir(os.environ['GOOLE_UPLOAD_HOME']) 

# 1つのメソッドでいろんなことをしてるから処理を分割する
def uploadFile(fileName, saveFileName):

  # 保存先フォルダを指定する　何故かブラウザから作成したフォルダが取得できない
  # google drive api で作成したフォルダには保存ができる
  folder_id = drive.ListFile({'q': 'title = "battery_log"'}).GetList()[0]['id']

  # ロード処理
  f = drive.CreateFile({"parents": [{"id": folder_id}]})
  f.SetContentFile(fileName)
#  f['title'] = os.path.basename(fileName)
  f['title'] = saveFileName

  try :
    # エラーになることがあった。0サイズのファイルがありそこでコケる
#    logger.debug("upload start: " + datetime.datetime.now().strftime("%H:%M:%S"))
    f.Upload()
#    logger.debug("upload end: " + datetime.datetime.now().strftime("%H:%M:%S"))

#    print(type(f['parents']))
#    pprint.pprint(f['parents'])

    # アップしたファイルはローカルから削除する
    # os.remove(fileName)

  except ApiRequestError as e:
    # エラーしたことをマークする
    os.rename(fileName, fileName + ".error")
    import traceback
    logger.error("ApiRequestError")

def OrganizeGooleDrive():

  # 保存先フォルダを指定する　何故かブラウザから作成したフォルダが取得できない
  # google drive api で作成したフォルダには保存ができる
  folder_id = drive.ListFile({'q': 'title = "battery_log"'}).GetList()[0]['id']

  # gooeleDriveにあるファイルリストを取得。サブフォルダは見ない
#  file_list = drive.ListFile({'q': '"{}" in parents and trashed = false'.format(folder_id)}).GetList()
  pprint.pprint(folder_id)
  file_list = []
  query = "'{}' in parents and trashed=false".format(folder_id)

  for i, list in enumerate(  drive.ListFile({'q': query, 'maxResults': 50}) )  :
    for file in list:
      print(file['title'])
      file_list.append(file)

  print(str(len(file_list)))
#  quit()
  # 容量を確認
  size = 0
  for f in file_list:
    #print(f['title'], ' \t', f['id'], ' \t', f['createdDate'], ' \t', f['fileSize'])
    size = size + int(f['fileSize'])

  # 削除ファイルリスト
#  delFileList = []


  MAX_SIZE = 300000000

  if size > MAX_SIZE:

    # 作成日付の昇順で並び替え
    dsp_list = sorted(file_list, key=lambda x:x['createdDate'])

    # 
    for f in dsp_list:
      if size < MAX_SIZE - 50000000:
        break

      # ファイルを特定
      f = drive.CreateFile({'id': f['id']})
      size = size - int(f['fileSize'])

#      logger.debug("google drive Delete: " + f['title'])
      # gooleDriveを削除する。ゴミ箱にも入らない。ゴミ箱に移動はf.Trash() ゴミ箱から戻すにはf.UnTrash()
      f.Delete()
#      delFileList.append(f)
#      logger.debug('upload total size(整理後)= ' + str(size / 1000000) + "MB")
#  else :
#    dsp_list = file_list

  # 削除したファイルがあればリストから除外する
#  for f in delFileList:
#    dsp_list.remove(f)


# ★ここから

# ファイル指定して起動。仮実装。アップロードしそこなったものをまとめてアップする、motionからの
# 呼び出しから指定ファイルのアップロードの2通りを実現したい
#　→実現方法。
# １．起動時にソケット待受 motionからの応答を待つ。受けたファイル名はリストに保持。リストはstaticで他スレッドからの操作を考慮する
# 2.１とは別のスレッドで動作 動画保存ディレクトリ確認。動画が2以上ある場合は、googleDriveにアップロードする
#   その際googleDriveの容量確認して規定量を超えていたら古いファイルから削除していく

# importに10秒がかかる
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError, GoogleDriveFile

# OAutt
gauth = GoogleAuth()
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)


#createFileList()
#OrganizeGooleDrive()

#try : 
#  uploadFile(targetFile)
#except Exception as e:

