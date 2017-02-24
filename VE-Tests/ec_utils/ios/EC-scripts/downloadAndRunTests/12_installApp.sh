#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt

#ideviceinstaller -u $(ectool getProperty "/myParent/DEVICE_SERIAL") -i $(ectool getProperty "/myParent/APP_FULL_NAME").app
ios-deploy --id $(ectool getProperty "/myParent/DEVICE_SERIAL") --bundle $(ectool getProperty "/myParent/APP_FULL_NAME").app
