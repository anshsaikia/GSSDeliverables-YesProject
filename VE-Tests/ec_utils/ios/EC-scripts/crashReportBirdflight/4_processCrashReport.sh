#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:/opt/X11/bin
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
set -x
cp ~/Public/ytv-kd-ios-app/WhitelabelApps/ProductKD/QuincyKit-iOS/symbolicatecrash/symbolicatecrash3 .

ls ./crashes

mkdir ./crash_reports

#ls ./crashes | awk '{ system("./symbolicatecrash3 -v ./crashes/"$1" ./ProductKD-Prod.app.dSYM/Contents/Resources/DWARF/ProductKD-Prod ./Payload/KD_Pearl_live.app>./crash_reports/"$1" 2>crash_reports/"$1".stderr")}'
ls ./crashes | awk '{ system("./symbolicatecrash3 -v ./crashes/"$1" ./ProductKD-Prod.app.dSYM/Contents/Resources/DWARF/ProductKD-Prod>./crash_reports/"$1" 2>crash_reports/"$1".stderr")}'

#ls ./crashes | awk '{ system("./symbolicatecrash.pl -v -o ./crash_reports/"$1" ./crashes/"$1" ./ProductKD-Prod.app.dSYM/Contents/Resources/DWARF/ProductKD-Prod")}'
