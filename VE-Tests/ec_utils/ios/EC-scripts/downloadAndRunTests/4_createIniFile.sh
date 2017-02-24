#!/usr/bin/env bash
proj=$(ectool getProperty "PROJECT")

BASE_INI_PATH=$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/CI_Environment_KD.ini
if [[ "$(ectool getProperty "PROJECT")" == "K" ]]; then
    proj="HAPPY"
    BASE_INI_PATH=$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/CI_Environment_K.ini
fi

python $(ectool getProperty "/myParent/tests_dir")/ec_utils/android/create_ini_file.py $(ectool getProperty "/myParent/DEVICE_SERIAL") $BASE_INI_PATH $(ectool getProperty "/myParent/tests_dir")/tests/ 0 0 $(ectool getProperty "HE_address") $proj $(ectool getProperty "/myParent/jobdir")/screenshots