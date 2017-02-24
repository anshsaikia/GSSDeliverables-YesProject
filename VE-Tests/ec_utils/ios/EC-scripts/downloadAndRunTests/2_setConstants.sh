#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_60.jdk/Contents/Home
whoami
hostname

echo "#####################################################"
echo "${COMMANDER_WORKSPACE}"
echo "$(ectool getProperty "/myJob/jobName")"
echo "$(ectool getProperty "/myJobStep/assignedResourceName")"

job_dir="${COMMANDER_WORKSPACE}"
short_report_dir="report_dir-$(ectool getProperty "jobStepId")"
report_dir="${COMMANDER_WORKSPACE}/report_dir-$(ectool getProperty "jobStepId")"
echo "report Dir = "$report_dir
ectool setProperty "/myParent/Jobdir" --value $job_dir
ectool setProperty "/myCall/reportdir" --value $report_dir
ectool setProperty "/myCall/shortReportdir" --value $short_report_dir

machine_name=$(ectool getProperty "/myResource/hostName")
ectool setProperty "/myParent/machine_name" --value $machine_name

all_files="http://"$machine_name"/$(ectool getProperty "/myJob/jobName")"
echo "All files URL = "$all_files
ectool setProperty "/myParent/report-urls/All Files" --value $all_files

echo "#####################################################"

#====================================
#     APPLICATION NAME
#====================================
APP_NAME="ProductKD"
#PKD_REL|PKD_DBG|--------|PK_DBG|PAPPOLO_REL|PSOLARIS_REL|PTME_REL|PVTRON_REL|PYES_REL|PZTV_REL|PZTV_REL
neededFlavors=""
targetNames=()
i=0
if [[ "$(ectool getProperty "PROJECT")" == "KD" ]]; then
    APP_NAME="ProductKD"
    BUNDLE="com.vodafone.pearlios"
fi
if [[ "$(ectool getProperty "PROJECT")" == "K" ]]; then
    APP_NAME="HAPPY"
    BUNDLE="com.cisco.cloudtv.ios.xcode.Happy"
fi
if [[ "$(ectool getProperty "PROJECT")" == "APOLLO" ]]; then
    APP_NAME="Apollo"
    BUNDLE="com.cisco.cloudtv.ios.xcode.Apollo"
fi
if [[ "$(ectool getProperty "PROJECT")" == "SOLARIS" ]]; then
    APP_NAME="Solaris"
    BUNDLE="com.cisco.cloudtv.ios.xcode.Mitchell"
fi
if [[ "$(ectool getProperty "PROJECT")" == "TME" ]]; then
    APP_NAME="TME"
    BUNDLE="com.cisco.cloudtv.ios.xcode.TME"
fi
if [[ "$(ectool getProperty "PROJECT")" == "VTRON" ]]; then
    APP_NAME="VTRON"
    BUNDLE="com.cisco.cloudtv.ios.xcode.Videotron"
fi
if [[ "$(ectool getProperty "PROJECT")" == "ZTV" ]]; then
    APP_NAME="ZTV"
    BUNDLE="com.cisco.il.ZTV"
fi

APP_FULL_NAME=$APP_NAME

echo "Application name: "$APP_NAME
echo "App full name: "$APP_FULL_NAME
echo "App bundle name: "$BUNDLE

#====================================

echo "$(ectool getProperty "HE_address")"
ectool setProperty "/myParent/HE_ADDRESS" --value $(ectool getProperty "HE_address")
ectool setProperty "/myParent/failure" --value true
ectool setProperty "/myParent/APP_FULL_NAME" --value $APP_FULL_NAME
ectool setProperty "/myParent/APP_BUNDLE_NAME" --value $BUNDLE


ectool setProperty "/myParent/DEVICE_SERIAL" --value "$(ectool getProperty "/myResource/SERIAL_NUMBER")"


ectool setProperty "/myParent/APPIUM_SERVER_IP" --value "127.0.0.1"
ectool setProperty "/myParent/APPIUM_LISTENING_PORT" --value "$(ectool getProperty "/myResource/UNIQUE_PORT")"

ectool setProperty "/myParent/HOCKEYAPP_API_TOKEN" --value "9773aac4343f4bb2bf96f62764575d0c"
ectool setProperty "/myParent/APP_BINARY_PATH" --value "~"
ectool setProperty "/myParent/REPOSITORY_ROOT" --value "~/Public/ytv-kd-ios-app"
ectool setProperty "/myParent/WORKSPACE_PATH_RELATIVE" --value "WhitelabelApps/ProductKD"
ectool setProperty "/myParent/BUILD_OUTPUT_DIR" --value "~/Library/Developer/Xcode/DerivedData/ProductKD-cxaagiieoyjnyihimxhaaxurqhcr"
ectool setProperty "/myParent/UNIQUE_PORT" --value "$(ectool getProperty "/myResource/UNIQUE_PORT")"

ipAddr=$(ipconfig getifaddr en0):9000
echo $ipAddr
ectool setProperty "myParent/LOCALHOST_SERVER_ADDRESS" --value $ipAddr

LOG_DIR="$(pwd)/logs-$(ectool getProperty "jobStepId")"
echo $LOG_DIR
ectool createProperty "/myCall/logDir" --value $LOG_DIR
echo "---> LOG_DIR=$LOG_DIR"
if [ ! -d $LOG_DIR ]; then
	mkdir $LOG_DIR
fi

#====================================
#     PATH
#====================================
set -x
resource_name=$(ectool getProperty "/myJobStep/assignedResourceName")
resource_short_name=`echo $resource_name | grep -o '..$' `

testsDir=$(ectool getProperty "/myParent/tests_dir")


workspaceDir=~/Public/ytv-kd-ios-app
buildDir=~/Public
buildDirName=derived
buildDirFullPath=$buildDir/derived
ectool createProperty "/myParent/workspace_dir" --value $workspaceDir
ectool createProperty "/myParent/build_dir" --value $buildDir
ectool createProperty "/myParent/build_dir_full_Path" --value $buildDirFullPath
#ectool createProperty "/myParent/tests_dir" --value $testsDir


# Set last user mail
last_code_commit_user_mail=`git -C ~/Public/ytv-kd-ios-app log --format="<%aE>" -n 3 | tr '\n' ',' | sed -e 's/<//g; s/@cisco.com>//g' | sed -e 's/,$//'`
ectool createProperty "/myParent/last_code_commit_user_mail" --value $last_code_commit_user_mail
last_tests_commit_user_mail=`git -C $testsDir log --format="<%aE>" -n 3 | tr '\n' ',' | sed -e 's/<//g; s/@cisco.com>//g' | sed -e 's/,$//'`
ectool createProperty "/myParent/last_tests_commit_user_mail" --value $last_tests_commit_user_mail

#Notifications
html_body="<h3>Device health check failed</h3>"
echo $html_body
ectool setProperty "/myParent/html_body" --value "$html_body"

#resource short name
ectool createProperty "/myParent/resource_short" --value $resource_short_name