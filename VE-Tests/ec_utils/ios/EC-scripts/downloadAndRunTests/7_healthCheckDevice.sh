#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
set -x

health_check="BAD"
ectool createProperty "/myParent/health_check" --value $health_check

#For notification when a problem occur
ectool createProperty "/myParent/health_check_first" --value $health_check

#put in project property for simple dashboard
ectool setProperty "/myProject/device_$(ectool getProperty "/myParent/resource_short") " "BAD"

pushd $(ectool getProperty "/myParent/tests_dir")/
source venv/bin/activate

cd tests

if [[ "$(ectool getProperty "PROJECT")" == "KD" ]]; then
    py.test KD/test_healthcheck.py -rfx -m 'healthcheck_device' -sv -v --report-to-elk=True
else
    py.test K/test_healthcheck.py -rfx -m 'healthcheck_device' -sv -v --report-to-elk=True
fi
if [ $? == 0 ]; then
health_check="OK"
ectool setProperty "/myProject/device_$(ectool getProperty "/myParent/resource_short") " "OK"
else
health_check="BAD"
fi
ectool setProperty "summary" --value $health_check
ectool setProperty "/myParent/health_check" --value $health_check
ectool setProperty "/myParent/health_check_first" --value $health_check
