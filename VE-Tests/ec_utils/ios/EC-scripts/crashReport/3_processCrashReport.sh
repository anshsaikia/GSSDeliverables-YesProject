#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:/opt/X11/bin
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
set -x
cp ~/Public/ytv-kd-ios-app/WhitelabelApps/ProductKD/QuincyKit-iOS/symbolicatecrash/symbolicatecrash3 .
Python ~/Public/ytv-kd-ios-app/WhitelabelApps/ProductKD/QuincyKit-iOS/symbolicatecrash/CrashReportsLogger.py download $(ectool getProperty "crash_count")

machine_name=$(ectool getProperty "/myResource/hostName")

crash_url="http://"$machine_name"/$(ectool getProperty "/myJob/jobName")/crashes/"
ectool setProperty "/myParent/report-urls/crash" --value $crash_url