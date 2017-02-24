#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:/opt/X11/bin
set -x
#clone of tests
echo " -- pulling Tests Repo --"
testsDir=$(ectool getProperty "/myParent/tests_dir")
cd $testsDir
#git pull


#git fetch
#git checkout origin/master || git checkout master # Branches will get checked out using the first; commits or tags using the second
#git pull origin master

resource_name=$(ectool getProperty "/myJobStep/assignedResourceName")
if [[ $resource_name == lwr-cilab-* ]]; then
   #Checking internet connectivity. Set proxy if no access
    if [[ `curl --connect-timeout 10 -s -I https://www.google.com | grep HTTP/1.1 | awk {'print $3'}` != OK ]]
    then
        export no_proxy="127.0.0.1,localhost,.cisco.com,10.0.0.0/8"
        export HTTPS_PROXY=https://proxy.esl.cisco.com:80
    fi
fi

pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install --trusted-host engci-maven-master.cisco.com -r requirements-vgw-test-utils.txt