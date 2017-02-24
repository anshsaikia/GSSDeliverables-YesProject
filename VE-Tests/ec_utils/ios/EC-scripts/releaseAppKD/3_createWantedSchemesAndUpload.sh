#!/usr/bin/env bash
set -x
SIGN_ID='iPhone Developer: Nadav Hassan'
mypwd=$(pwd)
APPSPOT_TARGET_PATH=KD-Release/$(ectool getProperty "version")
workspaceDir=$(ectool getProperty "/myParent/parent/workspace_dir")
#====================================
#      debug version
#====================================
cd $workspaceDir/WhitelabelApps/ProductKD/
if [[ "$(ectool getProperty "create_debug")" == "true" ]] || [[ "$(ectool getProperty "create_pipeline_bundle")" == "true" ]]; then
	echo "#@#@# build debug"
#	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_DBG" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_DBG" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO

	if [[ "$(ectool getProperty "create_pipeline_bundle")" == "true" ]]; then
		echo "#@#@# uploading .app for pipeline"
		cp -rf $mypwd/derived/Build/Products/Debug-iphoneos/ProductKD.app .
		zip -r $mypwd/ProductKD.app.zip ./ProductKD.app
		rm -rf ProductKD.app
		python $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/../common/publish_file_to_artifactory.py $mypwd/ProductKD.app.zip  $(ectool getProperty "version")/ios release
		echo pipeline version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/ProductKD.app.zip >> $mypwd/uploaded.txt
	fi


	#-sdk iphoneos8.4
	echo "#@#@# sign and create ipa"
	cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
	./releaseSigning.sh $mypwd/derived/Build/Products/Debug-iphoneos/ProductKD.app KD_Pearl_debug

	echo "#@#@# upload to releases"
	python ../common/publish_file_to_artifactory.py ./KD_Pearl_debug.ipa  $(ectool getProperty "version")/ios release
	echo debug version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/KD_Pearl_debug.ipa >> $mypwd/uploaded.txt
	echo "#@#@# zip dsym + upload"
	cp -R $mypwd/derived/Build/Products/Debug-iphoneos/ProductKD.app.dSYM ./
	zip -r ProductKD.app.dSYM.zip ./ProductKD.app.dSYM
	rm -r ProductKD.app.dSYM
	python ../common/publish_file_to_artifactory.py ProductKD.app.dSYM.zip  $(ectool getProperty "version")/ios/debug release
	echo debug version dsym uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/debug/ProductKD.app.dSYM >> $mypwd/uploaded.txt

	echo "#@#@# upload debug to appspot"
	./upload-to-appspot.sh ./KD_Pearl_debug.ipa KD_app/ci/$APPSPOT_TARGET_PATH/debug>> $mypwd/appspot.txt;

	rm -r KD_Pearl_debug.ipa
	rm -r ProductKD.app.dSYM.zip
fi

#====================================
#      release version
#====================================
echo "#@#@# ==== release version ===="

cd $workspaceDir/WhitelabelApps/ProductKD/
if [[ "$(ectool getProperty "create_release")" == "true" ]]; then
	echo "#@#@# build release"
#	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_REL" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
	#-sdk iphoneos8.4
	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_REL" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO
    #-sdk iphoneos8.4

	echo "#@#@# sign and create ipa"
	cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
	./releaseSigning.sh $mypwd/derived/Build/Products/Release-iphoneos/ProductKD.app KD_Pearl_release

	python ../common/publish_file_to_artifactory.py ./KD_Pearl_release.ipa  $(ectool getProperty "version")/ios release
	echo release version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/KD_Pearl_release.ipa >> $mypwd/uploaded.txt
	echo "#@#@# zip dsym + upload"
	cp -R $mypwd/derived/Build/Products/Release-iphoneos/ProductKD.app.dSYM ./
	zip -r ProductKD.app.dSYM.zip ./ProductKD.app.dSYM
	rm -r ProductKD.app.dSYM
	python ../common/publish_file_to_artifactory.py ProductKD.app.dSYM.zip  $(ectool getProperty "version")/ios/release release
	echo release version dsym uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/release/ProductKD.app.dSYM >> $mypwd/uploaded.txt

	echo "#@#@# upload release to appspot"
	./upload-to-appspot.sh ./KD_Pearl_release.ipa KD_app/ci/$APPSPOT_TARGET_PATH/release>> $mypwd/appspot.txt;

	rm -r KD_Pearl_release.ipa
	rm -r ProductKD.app.dSYM.zip
fi

#===============================================
#      prod version with prod keys
#===============================================
echo "#@#@# ==== prod version with prod keys ===="
HE_options=""
if [[ "$(ectool getProperty "create_prod_live")" == "true" ]]; then
	HE_options=$HE_options" live"
fi
if [[ "$(ectool getProperty "create_prod_staging")" == "true" ]]; then
	HE_options=$HE_options" staging"
fi

echo $HE_options
for i in $HE_options; do
    echo "#@#@# creating for $i"

	cd $workspaceDir/WhitelabelApps/ProductKD/Resources
	#lab for production is taken from ProductionHeadEnd.plist
	plutil -replace HE -string $i ProductionHeadEnd.plist

	cd $workspaceDir/WhitelabelApps/ProductKD/
	echo "#@#@# build production with prod keys"
#	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_Prod" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_Prod" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO

	if [ $i == live ]; then
		echo "#@#@# zip + upload dsym"
		cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
		cp -R $mypwd/derived/Build/Products/Release-iphoneos/ProductKD-Prod.app.dSYM ./
		zip -r ProductKD.app.dSYM.zip ./ProductKD-Prod.app.dSYM
		rm -r ProductKD-Prod.app.dSYM
		python ../common/publish_file_to_artifactory.py ProductKD.app.dSYM.zip  $(ectool getProperty "version")/ios/prod release
		echo production version dsym uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/prod/ProductKD.app.dSYM >> $mypwd/uploaded.txt
		rm -r ProductKD.app.dSYM.zip
	fi

    echo #@#@# sign and create ipa
    cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
    appName="KD_Pearl_"$i
    ./releaseSigning.sh $mypwd/derived/Build/Products/Release-iphoneos/ProductKD-Prod.app $appName
    echo "#@#@# upload to releases"
    python ../common/publish_file_to_artifactory.py "./KD_Pearl_"$i".ipa"  $(ectool getProperty "version")/ios release
    echo production version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/$appName.ipa >> $mypwd/uploaded.txt

    echo "#@#@# upload prod $i to appspot"
    ./upload-to-appspot.sh ./$appName.ipa KD_app/ci/$APPSPOT_TARGET_PATH/$appName>> $mypwd/appspot.txt;
    rm -r $appName.ipa
done

#===============================================
#      prod-dbg version with prod keys
#===============================================
echo "#@#@# ==== prod-dbg version with prod keys ===="

if [ "$(ectool getProperty "create_prod_dbg")" == "true" ]; then
	echo "#@#@# building prod-dbg"
	cd $workspaceDir/WhitelabelApps/ProductKD/Resources
	#force live as HE before compiling. will force production keys
	plutil -replace HE -string live ProductionHeadEnd.plist
        echo 15

	cd $workspaceDir/WhitelabelApps/ProductKD/
	echo "#@#@# build production with prod keys"
#	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_Prod_DBG" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_Prod_DBG" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO
        echo 16

	echo "#@#@# zip + upload dsym"
	cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
	cp -R $mypwd/derived/Build/Products/Debug-iphoneos/ProductKD-Prod.app.dSYM ./
	zip -r ProductKD.app.dSYM.zip ./ProductKD-Prod.app.dSYM
	rm -r ProductKD-Prod.app.dSYM
	python ../common/publish_file_to_artifactory.py ProductKD.app.dSYM.zip  $(ectool getProperty "version")/ios/prod_dbg release
	echo prod_dbg version dsym uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/prod_dbg/ProductKD.app.dSYM >> $mypwd/uploaded.txt
	rm -r ProductKD.app.dSYM.zip

    echo "#@#@# sign and create ipa"
    cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
    appName=KD_Pearl_live_dbg
    ./releaseSigning.sh $mypwd/derived/Build/Products/Debug-iphoneos/ProductKD-Prod.app $appName
    echo "#@#@# upload to releases"
    python ../common/publish_file_to_artifactory.py ./$appName.ipa  $(ectool getProperty "version")/ios release
    echo prod-dbg version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/$appName.ipa >> $mypwd/uploaded.txt

    echo "#@#@# upload $appName to appspot"
    ./upload-to-appspot.sh ./$appName.ipa KD_app/ci/$APPSPOT_TARGET_PATH/$appName>> $mypwd/appspot.txt;
    rm -r $appName.ipa
fi

echo "#@#@# done"

#===============================================
#      appstore version with prod keys
#===============================================

if [ "$(ectool getProperty "create_appstore")" == "true" ]; then
	echo "#@#@# build appstore version with production keys"

	cd $workspaceDir/WhitelabelApps/ProductKD/SupportingFiles
	plutil -replace CFBundleIdentifier -string "com.vodafone.pearl" Info.plist

	cd $workspaceDir/WhitelabelApps/ProductKD/
	echo "#@#@# build appstore with production keys"
#	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_Prod" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
	xcodebuild -project ProductKD.xcodeproj -scheme "PKD_Prod" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO

	echo "#@#@# sign and create ipa"
	cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
	appName="KD_Pearl_live_appstore"
	#Using KD keys
	./releaseSigning.sh $mypwd/derived/Build/Products/Release-iphoneos/ProductKD-Prod.app $appName "Pearl.mobileprovision" "iPhone Distribution: Vodafone Kabel Deutschland GmbH (3JSSX9L6QV)"

	echo "#@#@# upload to releases"
	python ../common/publish_file_to_artifactory.py ./$appName.ipa  $(ectool getProperty "version")/ios release
	echo appstore version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/$appName.ipa >> $mypwd/uploaded.txt

	echo "#@#@# upload prod to appspot"
	./upload-to-appspot.sh ./$appName.ipa KD_app/ci/$APPSPOT_TARGET_PATH/$appName>> $mypwd/appspot.txt;
	rm -r $appName.ipa
	link=$(cat $mypwd/appspot.txt)
	ectool setProperty "/myJob/uploadLink" --value "$link"
fi