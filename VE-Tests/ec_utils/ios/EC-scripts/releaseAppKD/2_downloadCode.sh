#!/usr/bin/env bash
set -x
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:/opt/X11/bin

workspaceDir=$(ectool getProperty "/myParent/parent/workspace_dir")

#curVersion=$(ectool getProperty "/projects/VE_iOS/curBuildNumber")
#echo $curVersion
#curVersion=$(($curVersion+1))
#echo cur version is $curVersion
#ectool setProperty "/projects/VE_iOS/curBuildNumber" --value $curVersion

pwd=$(pwd)
#clone of tests
echo " -- pulling Test --"
testsDir=$(ectool getProperty "/myParent/tests_dir")
cd $testsDir
git pull

cd $workspaceDir
git reset --hard
git checkout master
git pull
git checkout $(ectool getProperty "commitId")
git status

#Itay.Sh: we don't want debug of DRM in EC. so will override debug with release
#orig#workaround!! copy drm lib to correct place
#orig#echo workaround. copying DRM lib
#orig#
#mkdir -p ./WhitelabelApps/ProductKD/Libraries/VGC/Debug/ && cp ~/Public/libVGDrm.7.4.iOS.all.Debug.a "$_"
#mkdir -p ./WhitelabelApps/ProductKD/Libraries/VGC/Debug && cp ./WhitelabelApps/ProductKD/Libraries/VGC/Release/libVGDrm.7.4.iOS.all.NonDebug.a "$_/libVGDrm.7.4.iOS.all.Debug.a"

#buildNum=$(ectool getProperty "/projects/VE_iOS/curBuildNumber")
buildNum=$(ectool getProperty "buildNumber")
echo changing debug settings
cd $workspaceDir/WhitelabelApps/ProductKD/SupportingFiles/DebugSettings/Settings.bundle
#change the params
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppVersionNumber' $buildNum
echo change date
now=$(date)
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppBuildDate' "$now"
echo change bundle identifier
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppBuildNumber' $(ectool getProperty "version")

echo changing production settings
cd $workspaceDir/WhitelabelApps/ProductKD/SupportingFiles/ProductionSettings/Settings.bundle
#change the params
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppVersionNumber' $buildNum
echo change date
now=$(date)
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppBuildDate' "$now"
echo change bundle identifier
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppBuildNumber' $(ectool getProperty "version")
echo changing info.plist

cd $workspaceDir/WhitelabelApps/ProductKD/SupportingFiles
plutil -replace CFBundleDisplayName -string ProductKD Info.plist
plutil -replace CFBundleVersion -string $buildNum Info.plist
now=$(date)
plutil -replace CFBundleBuildDate -string "$now" Info.plist
plutil -replace CFBundleShortVersionString -string $buildNum Info.plist
plutil -replace CiscoVersion -string $(ectool getProperty "version") Info.plist
