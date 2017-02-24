#!/usr/bin/env bash
set -x
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:/opt/X11/bin
mypwd=$(pwd)
#clone of tests
echo " -- pulling Test --"
testsDir=$(ectool getProperty "/myParent/parent/tests_dir")
cd $testsDir
git pull

#update code repo
workspaceDir=$(ectool getProperty "/myParent/parent/workspace_dir")
buildDir=$(ectool getProperty "/myParent/parent/build_dir")
scheme=$(ectool getProperty "/myParent/parent/SCHEME")
projectType=$(ectool getProperty "/myParent/parent/PROJECT_TYPE")
cd $workspaceDir

echo " -- pulling Code --"
#remove all local changes
git clean  -d  -fx ""
#git rm -f .gitattributes
git add -A
git reset --hard
git status

echo "---------------------|"
echo "Last commit date:    |"
git log -1 --format=%cd --date=local
echo "---------------------|"

commitId1=$(git log | head -1 | sed s/'commit '//)
git checkout master
git pull
if [[ -n $(ectool getProperty "git_commit_id") ]]; then
    git checkout $(ectool getProperty "git_commit_id")
    git status
else
    git status
fi
commitId2=$(git log | head -1 | sed s/'commit '//)

echo old commit id = $commitId1  new = $commitId2

#ItayS: commented out because we need a better testing for Debug/Release, ProductK/KD etc.
#
# if [[ $(ectool getProperty "build") == "false" ]]; then
# if [ $commitId1 == $commitId2 ] && [ -a $(ectool getProperty "/myParent/parent/build_dir")/derived/Build/Products/Release-iphoneos/$(ectool getProperty "/myParent/parent/APP_FULL_NAME").app ]; then #don't build again
#   echo no change in dir, not building again
#   exit 0
# fi
# fi

echo "------  Building  -------"
whoami

#workaround!! copy drm lib to correct place
#echo workaround. copying DRM lib
#mkdir -p ./WhitelabelApps/$projectType/Libraries/VGC/Debug/ && cp ~/Public/libVGDrm.7.4.iOS.all.Debug.a "$_"

#clean and build app
cd WhitelabelApps/$projectType
#agvtool new-version -all $commitId1
#agvtool what-version

#clean
#xcodebuild -project $projectType.xcodeproj -scheme "$scheme" -derivedDataPath $buildDir'/derived' clean ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="iPhone Developer" -configuration Debug

#build
#ls -lad $(ectool getProperty "/myParent/parent/build_dir")/derived/Build/Products/Debug-iphoneos/*
rm -rf $buildDir'/derived'
start=`date +%s`
xcodebuild -project $projectType.xcodeproj -scheme "$scheme" -derivedDataPath $buildDir'/derived' build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="iPhone Developer"
end=`date +%s`
echo "xcodebuild took $((end-start)) seconds" > $mypwd/buildTime.txt
#ls -lad $(ectool getProperty "/myParent/parent/build_dir")/derived/Build/Products/Debug-iphoneos/*
#-configuration Debug
#-sdk iphoneos8.4

#upload symbols only for KD
if [[ $projectType = "ProductKD" ]]; then
  fullName=$(ectool getProperty "/myParent/parent/APP_FULL_NAME")
  ls -la $buildDir/derived/Build/Products/Debug-iphoneos/$fullName.app.dSYM
  rsync -av $buildDir/derived/Build/Products/Debug-iphoneos/$fullName.app.dSYM ~/Public/dSYM/Debug/$commitId2/
  rsync -av $buildDir/derived/Build/Products/Debug-iphoneos/$fullName.app ~/Public/dSYM/Debug/$commitId2/
  cd ~/Public/dSYM/Debug/$commitId2/
  zip -r $fullName.app.dSYM.zip $fullName.app.dSYM
fi
