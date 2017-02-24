#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
set -x
outcome=$(ectool getProperty "/myParent/parent/failure")
echo $outcome
scheme=$(ectool getProperty "/myParent/parent/SCHEME")
pwd=$(pwd)
cd ~/Public/ytv-kd-ios-app/
commitId=$(git log | head -1 | sed s/'commit '//)
cd $pwd
jobName=$(ectool getProperty "/myJob/jobName")
echo uploading to artifactory with commid ID $commitId

if [[ -n $(ectool getProperty "appVersion") ]]; then
        versionToUpload=$(ectool getProperty "appVersion")
else
        versionToUpload=$commitId
fi

APP_DIR=$(ectool getProperty "/myParent/parent/build_dir")/derived/Build/Products/Debug-iphoneos
APP_NAME=$(ectool getProperty "/myParent/parent/APP_FULL_NAME").app
echo "$APP_DIR/$APP_NAME"
cd $APP_DIR
if [ -d CiscoVE.app ]; then
    ls -lad *.app
    mv CiscoVE.app $APP_NAME
fi

zip_filename=$(ectool getProperty "/myParent/parent/APP_FULL_NAME")_$scheme.app.zip

zip -r $zip_filename $APP_NAME
#zip -r $zip_filename $APP_DIR/$APP_NAME
ls -la

cd $pwd
python $(ectool getProperty "/myParent/parent/tests_dir")/ec_utils/common/publish_app_to_artifactory.py ios $APP_DIR/$zip_filename realHE $versionToUpload snapshot
uploadPath=http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-snapshot-repo/VEoP/ci/ios/$versionToUpload/realHE/$zip_filename

#symbols upload
if [[ $(ectool getProperty "project") = "KD" ]]; then

python -u $(ectool getProperty "/myParent/parent/tests_dir")/ec_utils/common/publish_app_to_artifactory.py ios ~/Public/dSYM/Debug/$commitId/ProductKD.app.dSYM.zip realHE $commitId snapshot

fi

echo $uploadPath
ectool setProperty "/myParent/parent/appPath" --value $uploadPath
echo "Updating last build url.."
ectool setProperty "/projects/VE_iOS/last_ios_app_url_$(ectool getProperty "/myParent/parent/APP_FULL_NAME")" --value $uploadPath
