#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:~/Downloads/libimobiledevice-1.2.0
LOG_DIR=$(ectool getProperty "/myCall/logDir")
cd $LOG_DIR
echo "---> start logcat"
idevicesyslog -u $(ectool getProperty "/myParent/DEVICE_SERIAL") > log_$(ectool getProperty "/myParent/DEVICE_SERIAL").txt & echo $! > pid_$(ectool getProperty "/myParent/DEVICE_SERIAL").txt
echo "logcat PID="`echo $!`
exit 0