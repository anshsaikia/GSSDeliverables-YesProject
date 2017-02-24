#!/usr/bin/env bash
mkdir ./crashes

build_id=$(echo $(ectool getProperty "build_version") | tr -s \./ _)_live
download_request="https://birdflightapp.com/apps/$(ectool getProperty "app_id")/app-builds/$build_id/crashlogs.json?apikey=6tqkv4rbthooc0ks4sc04gskk4g0cw4"

echo $download_request

curl -v -o parseBirdflightCrashesList.py "http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/ios/parseBirdflightCrashesList.py"

cd ./crashes
python ../parseBirdflightCrashesList.py $download_request ?apikey=6tqkv4rbthooc0ks4sc04gskk4g0cw4 $(ectool getProperty "last_crash_id")

cd ..

curl -v -o ProductKD-Prod.ipa "http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "build_version")/ios/KD_Pearl_live.ipa"

unzip ProductKD-Prod.ipa

curl -v -o ProductKD.app.dSYM.zip "http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "build_version")/ios/prod/ProductKD.app.dSYM.zip"

unzip ProductKD.app.dSYM.zip
