#!/usr/bin/env bash
LOG_DIR=$(ectool getProperty "/myCall/logDir")
echo "---> LOG_DIR=$LOG_DIR"

cd $LOG_DIR
echo "---> stop logcat"
kill -9 `cat pid_$(ectool getProperty "/myParent/DEVICE_SERIAL").txt`
rm -f pid_$(ectool getProperty "/myParent/DEVICE_SERIAL").txt