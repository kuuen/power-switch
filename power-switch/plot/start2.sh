#!/bin/sh

export LOG_FILE_PATH_PLOT=/nano/power-switch/log/
export PLOT_PATH=/nano/power-switch/log/

python3 ${PLOT_HOME_PATH}plot.py -m now

