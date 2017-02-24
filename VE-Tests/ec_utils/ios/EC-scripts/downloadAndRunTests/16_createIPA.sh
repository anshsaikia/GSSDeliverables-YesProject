#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:/opt/X11/bin
testsFailed=$(ectool getProperty "/myParent/failure")
if [ -e $(ectool getProperty "/myParent/APP_BINARY_PATH")/$(ectool getProperty "/myParent/APP_FULL_NAME").ipa ]; then
        rm -f $(ectool getProperty "/myParent/APP_BINARY_PATH")/$(ectool getProperty "/myParent/APP_FULL_NAME").ipa
fi
    zip -r $(ectool getProperty "/myParent/APP_FULL_NAME").app.zip $(ectool getProperty "/myParent/APP_FULL_NAME").app
    MY_APP_ZIP=$(ectool getProperty "/myParent/APP_FULL_NAME").app.zip
    PROVISIONING_PROFILE=~/ci/Cisco_Generic_App_IL.mobileprovision
    MY_EMAIL=""
    MY_NOTES=""
    IPA_URL=$(curl http://macserver-29568.il.nds.com/CodeSign -F upload=@$MY_APP_ZIP -F profile=@$PROVISIONING_PROFILE -F email="$MY_EMAIL" -F notes="$MY_NOTES" -F appspot=false)
    echo $IPA_URL
    curl $IPA_URL > $(ectool getProperty "/myParent/APP_BINARY_PATH")/$(ectool getProperty "/myParent/APP_FULL_NAME").ipa
    #enable for debug only - because only debug has symbols
    #zip -r $(ectool getProperty "/myParent/APP_BINARY_PATH")/$(ectool getProperty "/myParent/APP_FULL_NAME").dSYM.zip $(ectool getProperty "/myParent/BUILD_OUTPUT_DIR")/Build/Products/$(ectool getProperty "build_cfg")-$(ectool getProperty "build_sdk")/$(ectool getProperty "/myParent/APP_FULL_NAME").app.dSYM
