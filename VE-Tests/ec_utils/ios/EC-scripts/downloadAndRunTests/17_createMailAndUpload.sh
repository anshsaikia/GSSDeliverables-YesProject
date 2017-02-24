#!/usr/bin/env bash
outcome=$(ectool getProperty "/myParent/failure")
echo $outcome
pwd=$(pwd)
cd ~/Public/ytv-kd-ios-app/
commitId=$(git log | head -1 | sed s/'commit '//)
cd $pwd
jobName=$(ectool getProperty "/myJob/jobName")
procedureName=$(ectool getProperty "/myParent/procedureName")
subject="Job  '"$jobName"'  from procedure  '"$procedureName"'  COMPLETED  - Commander notification"
ectool setProperty "/myParent/mailSubject" --value "$subject"

echo uploading to HockeyApp
python $(ectool getProperty "/myParent/tests_dir")/ec_utils/common/upload_hockeyapp.py iOS 0 $(ectool getProperty "/myParent/HOCKEYAPP_API_TOKEN") $(ectool getProperty "/myParent/APP_BINARY_PATH")/$(ectool getProperty "/myParent/APP_FULL_NAME").ipa $(ectool getProperty "/myParent/APP_BINARY_PATH")/$(ectool getProperty "/myParent/APP_FULL_NAME").dSYMs.zip "Automatic deployment from EC"

if [ $outcome == true ]; then
    echo preparing failure logs
    ectool setProperty "/myParent/mailBody" --value "PSA failure logs"
else
    echo uploading to artifactory
    if [[ -n "$(ectool getProperty "appVersion")" ]]; then
        versionToUpload=$(ectool getProperty "appVersion")
    else
        versionToUpload=$commitId
    fi
    cd $pwd
        #add to summary text file
        #get AS version
        ASVersion=$ctapVersion
        echo AS version is: $ASVersion
        #get app commit id from the git repo
        AppVersion=$commitId
        echo App commitId is: $AppVersion
        #save to file in ~/ec/Uploaded
        cd ../../Uploaded
        DATE=`date +%Y-%m-%d-%H-%M-%S`
        summary=$DATE" App commitId is: "$AppVersion" and AS version is: "$ASVersion". Uploaded to releases with name "$versionToUpload". See http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/ios/"$versionToUpload
        echo $summary
        echo $summary>>uploaded.txt
        echo "">>uploaded.txt
        ectool setProperty "/myParent/mailBody" --value "$summary"
    fi
cd $pwd
zip -r $(ectool getProperty "/myCall/logDir")/logs.zip ./*.log
