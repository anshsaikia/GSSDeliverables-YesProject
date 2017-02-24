#!/bin/bash
##set -e

## Clone and build Android application
git clone ssh://bwarshaw@jrsm-apl-grt17.cisco.com:29418/Android && scp -p -P 29418 bwarshaw@jrsm-apl-grt17.cisco.com:hooks/commit-msg Android/.git/hooks/
echo "Finish cloning Android project"

cd Android/src/apps/sf_kad/
## this is a quirk for Android manifast xml creation needed by next step
./config.sh dummy debug
android update project -p .

BUILD_FLAVORS="$HE_LAB" BUILD_TYPE="debug" ./build.sh

cd  -
cp Android/src/apps/sf_kad/build/*.apk $APP_BUNDLE_NAME


## Clone and 'build' VE-Tests
git clone ssh://bwarshaw@jrsm-apl-grt17.cisco.com:29418/VE-Tests && scp -p -P 29418 bwarshaw@jrsm-apl-grt17.cisco.com:hooks/commit-msg VE-Tests/.git/hooks/

    
##================================================================================================
## WORKAROUND, UNTIL A CSWCI wILL BE CREATED!
sed -i 's/jrsm-apl-grt17.cisco.com/bwarshaw@jrsm-apl-grt17.cisco.com/g' VE-Tests/requirements.txt
##================================================================================================
    
cd VE-Tests
pip install -r requirements.txt
cd -





