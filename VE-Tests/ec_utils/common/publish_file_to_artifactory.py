__author__ = 'abarilan'

import sys, os
from commands import getstatusoutput


def usage(reason):
    print
    if(reason):
        print reason
    print "Usage: publish_file_to_artifactory.py <file path> <path> <snapshots/release>\n"
    assert 0


if not os.path.exists(sys.argv[1]):
        usage("File not found")
ARTIFACTORY_USERNAME = "spvss-vci-service-deployer"
ARTIFACTORY_PASSWORD = "spvss-vci-service-deployer"
BUNDLE_PATH = sys.argv[1]
APP_NAME = BUNDLE_PATH.split("/")[-1]
REPO_PATH = sys.argv[2]
REPO_NAME=sys.argv[3]

print getstatusoutput("curl -v --user "+ARTIFACTORY_USERNAME+":"+ARTIFACTORY_PASSWORD+" --data-binary @"+BUNDLE_PATH+" -X PUT http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-"+REPO_NAME+"-repo/VEoP/ci/"+REPO_PATH+"/"+APP_NAME)