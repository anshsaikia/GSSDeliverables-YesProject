#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_60.jdk/Contents/Home
echo "#####################################################"
echo "${COMMANDER_WORKSPACE}"
echo "$(ectool getProperty "/myJob/jobName")"
echo "$(ectool getProperty "/myJobStep/assignedResourceName")"

job_dir="${COMMANDER_WORKSPACE}"
ectool setProperty "/myParent/Jobdir" --value $job_dir

resource_name=$(ectool getProperty "/myJobStep/assignedResourceName")
machine_name=$(ectool getProperty "/myResource/hostName")
echo $machine_name
ectool setProperty "/myParent/machine_name" --value $machine_name

all_files="http://"$machine_name"/$(ectool getProperty "/myJob/jobName")"
echo "All files URL = "$all_files
ectool setProperty "/myParent/report-urls/All Files" --value $all_files

echo "#####################################################"

APP_NAME="ProductK"
APP_NAMESPACE="com.cisco."
APP_FULL_NAME=$APP_NAME$APP_SUFFIX
echo $APP_FULL_NAME

ectool setProperty "/myParent/APP_FULL_NAME" --value $APP_NAME$APP_SUFFIX
ectool setProperty "/myParent/APP_BUNDLE_NAME" --value $APP_NAMESPACE"pearlios"

ectool setProperty "/myParent/APP_BINARY_PATH" --value "~"
testsDir=~/Public/VE-Tests
ectool createProperty "/myParent/tests_dir" --value $testsDir
ectool createProperty "/myParent/parent/workspace_dir" --value ~/Public/release/ytv-kd-ios-app
