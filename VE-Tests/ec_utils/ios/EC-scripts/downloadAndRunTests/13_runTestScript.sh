#!/usr/bin/env bash
set -x
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
pwd=$(pwd)

cd $pwd

DEVICE_SERIAL=$(ectool getProperty "/myParent/DEVICE_SERIAL")
echo $DEVICE_SERIAL
REPORT_DIR="$(ectool getProperty "/myCall/reportDir")"
SCRRENSHOT_DIR="screenshots"

# create dir
if [ ! -d "${SCRRENSHOT_DIR}" ]; then
mkdir "${SCRRENSHOT_DIR}"
fi

if [ ! -d "${REPORT_DIR}" ]; then
mkdir "${REPORT_DIR}"
fi

#create the markers from the params
markers_buf="\"(("
stability=""
params=" -sv -rfx -v -m "
xmlStr=--junitxml=\"$REPORT_DIR/$(ectool getProperty "/myParent/DEVICE_SERIAL").xml\"

if [[ $(ectool getProperty "markers_stability") != "true" ]]; then
stability="stress or stability or"
fi

# custom , level , list
if [[ ! -z "$(ectool getProperty "marker_custom")" ]]; then

markers_buf="${markers_buf}$(ectool getProperty "marker_custom")"

elif [[ ! -z "$(ectool getProperty "level_of_tests")" ]]; then

if [[ "$(ectool getProperty "level_of_tests")" == "level_1_tests" ]]; then
markers_buf="${markers_buf} LV_L1"
fi
if [[ "$(ectool getProperty "level_of_tests")" == "level_2_tests" ]]; then
markers_buf="${markers_buf} LV_L2"
fi
if [[ "$(ectool getProperty "level_of_tests")" == "level_3_tests" ]]; then
markers_buf="${markers_buf} LV_L3"
fi


else

markers_buf="$markers_buf $(ectool getProperty "markers_list")"
fi

if [[ ! -z "$(ectool getProperty "Owner")" ]]; then
    if [[ "${#markers_buf}" -lt 5 ]]; then
        markers_buf="${markers_buf} $(ectool getProperty "Owner")"
    else
        markers_buf="${markers_buf} and $(ectool getProperty "Owner")"
    fi

fi

if [[ "$(ectool getProperty "PROJECT")" == "KD" ]]; then
    test_path="KD"
else
    test_path="K"
fi

#if custom test path
if [[ ! -z "$(ectool getProperty "markers_tests_path")" ]]; then
test_path="$(ectool getProperty "markers_tests_path")"
fi

#ELK
#if [[ $(ectool getProperty "ELK") == "true" ]]; then
report_to_elk="--report-to-elk=True"
#fi

#LOOP
loop_times="--count="$(ectool getProperty "/myParent/loop_on_test")

combined_markers="$xmlStr $loop_times $params $marker_custom $markers_buf ) and (not ($stability unsupported)))\" $test_path $report_to_elk"

cd $(ectool getProperty "/myParent/tests_dir")/
source venv/bin/activate

cd $(ectool getProperty "/myParent/tests_dir")/tests

pwd
echo "Markers = py.test "$combined_markers


#py.test  $combined_markers
printf "py.test ">p.sh
printf " $xmlStr ">>p.sh
printf " $loop_times ">>p.sh
printf " $params ">>p.sh
printf " $marker_custom ">>p.sh
printf " $markers_buf ">>p.sh
printf " ) and (not ($stability unsupported)))\" ">>p.sh
printf " $test_path">>p.sh
echo " $report_to_elk">>p.sh
echo ============
cat p.sh
echo ==========
cat p.sh | bash


if [ $? == 0 ]; then
    ectool setProperty "/myParent/failure" --value false
fi
