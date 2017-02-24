#!/bin/bash
set -e

cdir=`pwd`
projdir=""

if [ "$PROJECT" == "KD" ]; then
	projdir="android$CLONE_DIR/src/apps/sf_kad"
else
	projdir="android$CLONE_DIR/src/apps/sf_kv2"
fi
echo "projdir is $projdir"

## Clone and build Android application
if [ ! -d "android$CLONE_DIR" ]; then
	git clone git@github3.cisco.com:AND/android.git android$CLONE_DIR
	echo "Finish cloning Android project"
else
	echo "Android project already exist. Not clonning"
fi

cd "$projdir"
echo "building in: `pwd`"

if [ "$GIT_COMMIT_ID" != "" ] && [ "$GIT_COMMIT_ID" != "HEAD" ]; then
    echo "switching to commit ID $GIT_COMMIT_ID"
    git checkout $GIT_COMMIT_ID
fi

echo "last commit: "
git log -n 1

BUILD_FLAVORS="$HE_LABS" BUILD_TYPES="$BUILD_TYPE" ./build.sh

cd "$cdir"

echo "built apk name is: `ls "$projdir"/build/*.apk`"
if [ "$APP_BUNDLE_NAME" != "" ]; then
  cp "$projdir"/build/*.apk $APP_BUNDLE_NAME
fi