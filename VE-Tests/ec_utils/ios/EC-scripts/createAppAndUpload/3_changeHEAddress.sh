#!/usr/bin/env bash
if [[ -z $(ectool getProperty "HE_address") ]]; then
echo using HE address from config
exit 0
fi
addressToUse=$(ectool getProperty "HE_address")
echo $addressToUse
cd $(ectool getProperty "/myParent/parent/build_dir")/derived/Build/Products/Release-iphoneos
$(ectool getProperty "/myParent/parent/tests_dir")/ec_utils/ios/replaceHeAddressInSettings.sh $addressToUse $(ectool getProperty "/myParent/parent/APP_FULL_NAME")