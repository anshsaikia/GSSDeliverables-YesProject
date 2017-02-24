#!/usr/bin/env bash
echo "#####################################################"
echo "${COMMANDER_WORKSPACE}"
echo "$(ectool getProperty "/myJob/jobName")"
echo "$(ectool getProperty "/myJobStep/assignedResourceName")"
echo "Build Version: $(ectool getProperty "build_version")"

job_dir="${COMMANDER_WORKSPACE}"
report_dir="${COMMANDER_WORKSPACE}/report_dir"
api_key="6tqkv4rbthooc0ks4sc04gskk4g0cw4"

ectool setProperty "/myParent/Jobdir" --value $job_dir
ectool setProperty "/myParent/reportdir" --value $report_dir
ectool setProperty "/myParent/apiKey" --value $api_key

machine_name=$(ectool getProperty "/myResource/hostName")
ectool setProperty "/myParent/machine_name" --value $machine_name

all_files="http://"$machine_name"/$(ectool getProperty "/myJob/jobName")"
echo "All files URL = "$all_files
ectool setProperty "/myParent/report-urls/All Files" --value $all_files

echo "#####################################################"