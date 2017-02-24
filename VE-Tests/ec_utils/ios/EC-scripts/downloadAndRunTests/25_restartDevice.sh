#!/usr/bin/env bash
if [ $(ectool getProperty "device_pool") == "CICD_iOS_Devices" ]; then
    echo "Device is part of the CICD_iOS_Devices pool, restating it"
    export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
    #idevicepair pair -u $(ectool getProperty "/myParent/DEVICE_SERIAL")
    idevicediagnostics restart -u $(ectool getProperty "/myParent/DEVICE_SERIAL")
    sleep 30
fi

