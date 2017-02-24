#!/usr/bin/env bash
set -x
pwd
if [[ -z "$(ectool getProperty "HE_address")" ]]; then
echo using HE address from config
exit 0
fi
addressToUse=$(ectool getProperty "HE_address")
echo $addressToUse
addressToUse=`echo $addressToUse | cut -f2- -d"-" | tr "-" "_"`
echo $addressToUse
$(ectool getProperty "/myParent/tests_dir")/ec_utils/ios/replaceHeAddressInSettings.sh $addressToUse $(ectool getProperty "/myParent/APP_FULL_NAME")
touch app_ready.flag
