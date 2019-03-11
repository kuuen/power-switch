#!/bin/sh


echo "Content-type: text/html\n"
echo "<html><head><meta charset='utf-8'/>"
echo "<style type='text/css'>"
echo "body {font-size: 1.4em;}"
echo "</style>"
echo "</head><body>"
echo "時間かかるので <br/>"

${PLOT_HOME_PATH}start2.sh

echo "<br/>完了したので<br/><br/>"
echo "<a href='../plot.html'>戻る</a>"
echo "</body></html>"

