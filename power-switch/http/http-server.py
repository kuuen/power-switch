# -*- coding:utf-8 -*-
import os #OSの間でやり取りするのに必要なモジュール
from http.server import HTTPServer, CGIHTTPRequestHandler
import socketserver

PORT = 8000
os.chdir(os.environ['HTTP_DOC_PATH']) #ドキュメントルートとなるディレクトりに移動
server_address = ("localhost", 8000)

class Handler(CGIHTTPRequestHandler):
    cgi_directories = ["/cgi-bin"]

# ↓ withの指定だとエラーで動かない。server_close()を書くことにした close()が無い臭い
#with socketserver.TCPServer(("", PORT), Handler) as httpd:

httpd = HTTPServer(("", PORT), Handler)

try :
    httpd.serve_forever()
finally :
    httpd.server_close()
    print('後処理')
