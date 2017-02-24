#!/bin/bash
set -e

## Clone and build Android application
git clone ssh://bwarshaw@jrsm-apl-grt17.cisco.com:29418/Android && scp -p -P 29418 bwarshaw@jrsm-apl-grt17.cisco.com:hooks/commit-msg Android/.git/hooks/
echo "Finish cloning Android project"

veapp_code_review=$1
if [ -z "$veapp_code_review" ] ; then
    echo "No code review";
else
    cd Android
    veapp_code_review=`echo "$veapp_code_review" | sed 's/ssh:.*@/ssh:\/\/bwarshaw@/'`
    echo "$veapp_code_review";
    eval "$veapp_code_review"
    cd ..
fi
cdir=`pwd`
cd Android/src/apps/sf_kad/
git log -1
## this is a quirk for Android manifast xml creation needed by next step
./config.sh dummy debug
android update project -p .

BUILD_FLAVORS="$HE_LABS" BUILD_TYPES="$BUILD_TYPE" ./build.sh

if [ "$APP_BUNDLE_NAME" != "" ]; then
  cd "$cdir"
  cp Android/src/apps/sf_kad/build/*.apk $APP_BUNDLE_NAME
fi
