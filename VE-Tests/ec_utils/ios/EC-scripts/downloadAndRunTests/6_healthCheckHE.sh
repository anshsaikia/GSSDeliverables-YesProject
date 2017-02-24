#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
set -x

ectool setProperty "summary" --value $(ectool getProperty "HE_address")

pushd $(ectool getProperty "/myParent/tests_dir")/
source venv/bin/activate

cd tests

health_check="BAD"

ectool setProperty "/projects/VE_iOS/server_$(ectool getProperty "HE_address") " "BAD"

ectool createProperty "/myParent/health_check_he" --value $health_check
if [[ "$(ectool getProperty "PROJECT")" == "KD" ]]; then
    py.test KD/test_healthcheck.py -rfx -m 'healthcheck_network' -sv -v
else
    py.test K/test_healthcheck.py -rfx -m 'healthcheck_network' -sv -v
fi
if [ $? == 0 ]; then
health_check="OK"
ectool setProperty "/projects/VE_iOS/server_$(ectool getProperty "HE_address") " "OK"
fi

ectool setProperty "/myParent/health_check_he" --value $health_check




