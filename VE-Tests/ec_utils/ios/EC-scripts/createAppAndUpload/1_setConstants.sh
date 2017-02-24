#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_60.jdk/Contents/Home

whoami
hostname

echo "#####################################################"
echo "${COMMANDER_WORKSPACE}"
echo ectool getProperty "/myJob/jobName"
echo ectool getProperty "/myJobStep/assignedResourceName"

job_dir="${COMMANDER_WORKSPACE}"
ectool setProperty "/myParent/Jobdir" --value $job_dir

resource_name=$(ectool getProperty "/myJobStep/assignedResourceName")
machine_name=$(ectool getProperty "/myResource/hostName")
echo $machine_name
ectool setProperty "/myParent/machine_name" --value $machine_name

all_files="http://"$machine_name"/"$(ectool getProperty "/myJob/jobName")
echo "All files URL = "$all_files
ectool setProperty "/myParent/report-urls/All Files" --value $all_files

echo "#####################################################"

ectool setProperty "/myParent/parent/failure" --value true

#====================================
#     APPLICATION NAME
#====================================
APP_NAME="ProductKD"
#PKD_REL|PKD_DBG|--------|PK_DBG|PAPOLO_REL|PSOLARIS_REL|PTME_REL|PVTRON_REL|PYES_REL|PZTV_REL|PZTV_REL
#"KD", @"K", @"ZTV", @"TME", @"YES", @"VTRON", @"SOLARIS", @"APOLLO"
neededFlavors=""
targetNames=()
i=0
PROJECT_TYPE="ProductK"
project=$(ectool getProperty "project")
if [[ "$project" == "KD" ]]; then
    neededFlavors=$neededFlavors" YES"
    targetNames[$i]="ProductKD"
    i=($i+1)
    APP_NAME="ProductKD"
    SCHEME="PKD_DBG"
    PROJECT_TYPE="ProductKD"
fi
if [[ "$project" == "ZTV" ]]; then
    neededFlavors=$neededFlavors" ZTV"
    targetNames[$i]="ZTV"
    i=($i+1)
    APP_NAME="ZTV"
    SCHEME="PZTV_DBG"
fi
if [[ "$project" == "K" ]]; then
    neededFlavors=$neededFlavors" K"
    targetNames[$i]="K"
    i=($i+1)
    APP_NAME="Happy"
    SCHEME="PK_DBG"
fi
if [[ "$project" == "APOLLO" ]]; then
    neededFlavors=$neededFlavors" Apollo"
    targetNames[$i]="PAPOLLO_REL"
    i=($i+1)
    APP_NAME="Apollo"
    SCHEME="PAPOLO_REL"
fi
if [[ "$project" == "SOLARIS" ]]; then
    neededFlavors=$neededFlavors" Solaris"
    targetNames[$i]="PSOLARIS_REL"
    i=($i+1)
    APP_NAME="Solaris"
    SCHEME="PSOLARIS_REL"
fi
if [[ "$project" == "YES" ]]; then
    neededFlavors=$neededFlavors" TME"
    targetNames[$i]="PTME_REL"
    i=($i+1)
    APP_NAME="Yes"
    SCHEME="PYES_REL"
fi
if [[ "$project" == "TME" ]]; then
    neededFlavors=$neededFlavors" TME"
    targetNames[$i]="PTME_REL"
    i=($i+1)
    APP_NAME="TME"
    SCHEME="PTME_REL"
fi
if [[ "$project" == "VTRON" ]]; then
    neededFlavors=$neededFlavors" Videotron"
    targetNames[$i]="PVTRON_REL"
    i=($i+1)
    APP_NAME="VTRON"
    SCHEME="PVTRON_REL"
fi
if [[ "$project" == "SOLARIS" ]]; then
    neededFlavors=$neededFlavors" Videotron"
    targetNames[$i]="PSOLARIS_REL"
    i=($i+1)
    APP_NAME="VTRON"
    SCHEME="PSOLARIS_REL"
fi
i=0
#for flavor in $neededFlavors; do
#echo $flavor
#APP_NAME=$flavor
#done

echo "Type: "$PROJECT_TYPE"  Application name: "$APP_NAME" With Scheme: "$SCHEME

echo DRM enabled is $[DRM_enabled]
if [ $[DRM_enabled] == false ]; then
    APP_SUFFIX="withoutDRM"
else
    APP_SUFFIX=""
fi

APP_FULL_NAME=$APP_NAME$APP_SUFFIX
echo $APP_FULL_NAME
ectool setProperty "/myParent/parent/APP_FULL_NAME" --value $APP_NAME$APP_SUFFIX
ectool setProperty "/myParent/parent/SCHEME" --value $SCHEME
ectool setProperty "/myParent/parent/PROJECT_TYPE" --value $PROJECT_TYPE

# Set last user mail
last_commit_user_mail=`git -C ~/Public/ytv-kd-ios-app log --format="<%aE>" -n 1`
ectool createProperty "/myParent/last_commit_user_mail" --value $last_commit_user_mail

workspaceDir=~/Public/ytv-kd-ios-app
testsDir=~/Public/VE-Tests
buildDir=~/Public
buildDirName=derived
buildDirFullPath=$buildDir/derived
ectool createProperty "/myParent/parent/workspace_dir" --value $workspaceDir
ectool createProperty "/myParent/parent/build_dir" --value $buildDir
ectool createProperty "/myParent/parent/build_dir_full_Path" --value $buildDirFullPath
ectool createProperty "/myParent/parent/tests_dir" --value $testsDir