#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
ideviceinstaller -u $(ectool getProperty "/myParent/DEVICE_SERIAL") -U $(ectool getProperty "/myParent/APP_BUNDLE_NAME")