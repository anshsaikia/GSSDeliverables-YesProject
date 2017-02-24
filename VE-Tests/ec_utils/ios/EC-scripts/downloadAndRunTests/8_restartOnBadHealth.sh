#!/usr/bin/env bash
if [ $(ectool getProperty "health_check") = "BAD" ]; then
    echo "restarting device..."
    export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
    #idevicepair pair -u $(ectool getProperty "/myParent/DEVICE_SERIAL")
    idevicediagnostics restart -u $(ectool getProperty "/myParent/DEVICE_SERIAL")
    sleep 40

    pushd $(ectool getProperty "/myParent/tests_dir")/
    source venv/bin/activate

    cd tests
    if [[ "$(ectool getProperty "PROJECT")" == "KD" ]]; then
        py.test KD/test_healthcheck.py -rfx -m 'healthcheck_device' -sv -v
    else
        py.test K/test_healthcheck.py -rfx -m 'healthcheck_device' -sv -v
    fi
    if [ $? == 0 ]; then
    health_check="OK"
    else
    health_check="BAD"
    fi
    ectool setProperty "summary" --value $health_check
    ectool setProperty "/myParent/health_check" --value $health_check
fi

