__author__ = 'abarilan'

import sys, os
from commands import getstatusoutput


def usage(reason):
    print
    if(reason):
        print reason
    print "Usage: publish_file_to_delivery_artifactory.py <file path> <path>\n"
    assert 0


if not os.path.exists(sys.argv[1]):
        usage("File not found")
ARTIFACTORY_USERNAME = "spvss-vci-service-deployer"
ARTIFACTORY_PASSWORD = "spvss-vci-service-deployer"
BUNDLE_PATH = sys.argv[1]
ARTIFACTORY_PATH = sys.argv[2]
APP_NAME = BUNDLE_PATH.split("/")[-1]


print getstatusoutput("curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/"+ARTIFACTORY_PATH+"/"+APP_NAME + " -T "+ BUNDLE_PATH)