#!/bin/sh
#syntax: ./test_level.sh <platform Android/iOS> <level 0/1/2> <folder K/KD>
#usage: ./test_level.sh Android 1 K

TEST_RESULT_DIR=./results/$1_LV_L$2_$3
if [ ! -d "${TEST_RESULT_DIR}" ]; then
mkdir -p "${TEST_RESULT_DIR}"
fi
if [ $1 == 'Android' ]; then
if [ $2 == '1' ]; then
py.test --junitxml=$TEST_RESULT_DIR/test_result.xml -sv -rfx --platform Android -m 'LV_L1 and O_Android' $3
elif [ $2 == '2' ]; then
py.test --junitxml=$TEST_RESULT_DIR/test_result.xml -sv -rfx --platform Android -m 'LV_L2 and O_Android' $3
else
py.test --junitxml=$TEST_RESULT_DIR/test_result.xml -sv -rfx --platform Android -m '(LV_L1 and O_Android) or (LV_L2 and O_Android)' $3
fi
else
if [ $2 == '1' ]; then
py.test --junitxml=$TEST_RESULT_DIR/test_result.xml -sv -rfx --platform iOS -m 'LV_L1 and O_iOS' $3
elif [ $2 == '2' ]; then
py.test --junitxml=$TEST_RESULT_DIR/test_result.xml -sv -rfx --platform iOS -m 'LV_L2 and O_iOS' $3
else
py.test --junitxml=$TEST_RESULT_DIR/test_result.xml -sv -rfx --platform Android -m '(LV_L1 and O_iOS) or (LV_L2 and O_iOS)' $3
fi
fi
cd ${TEST_RESULT_DIR}
wget -O "./build_junit_report.xml" "https://stash-eng-rtp1.cisco.com/stash/projects/CAMPNOU/repos/ci_utilities/browse/junit_reports/build_junit_report.xml?at=4ab8a05eb489e82b2f8d5303a7c11e905ad2067c&raw"
wget -O "./junit-frames.xsl" "https://stash-eng-rtp1.cisco.com/stash/projects/CAMPNOU/repos/ci_utilities/browse/junit_reports/junit-frames.xsl?at=0a682a2018536d72b8c7b3a0a6deeb323a41a69a&raw"
sed -i -- 's/frameset cols="20%/frameset cols="0%/g' junit-frames.xsl
ant -f build_junit_report.xml -Darg0=test_result.xml -Darg1=.
