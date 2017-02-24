#!/usr/bin/env bash
set -x
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:/opt/X11/bin
workspaceDir=$(ectool getProperty "/myParent/parent/workspace_dir")

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
git checkout $(ectool getProperty "A_commitId")
git status

#workaround!! copy drm lib to correct place
#echo workaround. copying DRM lib
#mkdir -p ./WhitelabelApps/ProductK/Libraries/VGC/Debug/ && cp ~/Public/libVGDrm.7.4.iOS.all.Debug.a "$_"

buildNum=$(ectool getProperty "A_buildNumber")
echo changing debug settings
#todo: check if this is the correct settings to change
echo is this really needed?
cd $workspaceDir/WhitelabelApps/ProductK/SupportingFiles/Settings.bundle
#change the params
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppVersionNumber' $buildNum
echo change date
now=$(date)
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppBuildDate' "$now"
echo change bundle identifier
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceAppSettings.sh Root.plist 'AppBuildNumber' $(ectool getProperty "A_version")

#change plist for all targets
#infoPlistFiles="Happy-Info.plist Etisalat-Info.plist Apollo-Info.plist AEG-Info.plist VTRON-Info.plist Solaris-Info.plist ZTV-Info.plist ZTVProd-Info.plist Proximus-Info.plist TME-Info.plist Yes-Info.plist NET-Info.plist VSScloud-Info.plist Voo-Info.plist Telus-Info.plist NET_Prod_SD-Info.plist"
infoPlistFiles="CiscoVE-Info.plist"
for plist in $infoPlistFiles; do
    if ! [ -s $workspaceDir/WhitelabelApps/ProductK/SupportingFiles/$plist ]; then
        continue;
    fi
    cd $workspaceDir/WhitelabelApps/ProductK/SupportingFiles
    plutil -replace CFBundleVersion -string $buildNum $plist
    now=$(date)
    plutil -replace CFBundleBuildDate -string "$now" $plist
    plutil -replace CFBundleShortVersionString -string $buildNum $plist
    plutil -replace CiscoVersion -string $(ectool getProperty "A_version") $plist
done