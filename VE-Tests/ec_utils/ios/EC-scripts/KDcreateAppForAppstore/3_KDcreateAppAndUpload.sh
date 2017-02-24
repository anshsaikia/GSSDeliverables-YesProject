#!/usr/bin/env bash
set -x
SIGN_ID='iPhone Developer: Nadav Hassan'
mypwd=$(pwd)
APPSPOT_TARGET_PATH=KD-Release/$(ectool getProperty "version")
workspaceDir=$(ectool getProperty "/myParent/parent/workspace_dir")

#===============================================
#      prod version with production keys
#===============================================

cd $workspaceDir/WhitelabelApps/ProductKD/
echo "#@#@# build production with production keys"
xcodebuild -project ProductKD.xcodeproj -scheme "PKD_Prod" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"

echo "#@#@# sign and create ipa"
cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
appName="KD_Pearl_live_appstore"
#using cisco sign in (Ehuds sign-in identity)
if [[ $(ectool getProperty "use_cisco_signing") == "true" ]]; then
	./releaseSigning.sh $mypwd/derived/Build/Products/Release-iphoneos/ProductKD-Prod.app $appName "Vodafone_Giga-4.mobileprovision" "iPhone Distribution: Cisco Video Technologies Israel Ltd (B2K9DE64W6)" "com.cisco.GigaiOS"
else
	#Using KD
	./releaseSigning.sh $mypwd/derived/Build/Products/Release-iphoneos/ProductKD-Prod.app $appName "Pearl.mobileprovision" "iPhone Distribution: Vodafone Kabel Deutschland GmbH (3JSSX9L6QV)"
fi

echo "#@#@# upload to releases"
python ../common/publish_file_to_artifactory.py ./$appName.ipa  $(ectool getProperty "version")/ios release
echo appstore version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/$appName.ipa >> $mypwd/uploaded.txt

echo "#@#@# upload prod to appspot"
./upload-to-appspot.sh ./$appName.ipa KD_app/ci/$APPSPOT_TARGET_PATH/$appName>> $mypwd/appspot.txt;
rm -r $appName.ipa
link=$(cat $mypwd/appspot.txt)
ectool setProperty "/myJob/uploadLink" --value $link