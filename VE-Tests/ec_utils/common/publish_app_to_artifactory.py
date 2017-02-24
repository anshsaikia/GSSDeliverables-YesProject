__author__ = 'bwarshaw'

import sys, os
from commands import getstatusoutput


def usage(reason):
    print
    if(reason):
        print reason
    print "Usage: publish_app_to_artifactory.py <ios/android> <app/apk path> <dummy/realHE> <version>\n"
    assert 0


def check_arguments():
    if len(sys.argv) < 5:
        usage("Wrong arguments" + sys.argv)

    if sys.argv[1] not in ["ios", "android"]:
        usage("Supported platforms are ios or android")
    if not os.path.exists(sys.argv[2]):
        usage("File not found: " + sys.argv[2])
    if sys.argv[1] == "android" and not sys.argv[2].endswith(".apk") and not sys.argv[2].endswith(".txt"):
        usage("Wrong apk")
    if sys.argv[1] == "ios" and not sys.argv[2].endswith(".app") and not sys.argv[2].endswith(".zip") and not sys.argv[2].endswith(".ipa"):
        usage("Wrong app")

    if sys.argv[3] not in ["dummy", "realHE"]:
        usage("Please specify whether the bundle is against dummy or realHE")

check_arguments()

ARTIFACTORY_USERNAME = "spvss-vci-service-deployer"
ARTIFACTORY_PASSWORD = "spvss-vci-service-deployer"
PLATFORM = sys.argv[1]
BUNDLE_PATH = sys.argv[2]
ENV = sys.argv[3]
APP_NAME = BUNDLE_PATH.split("/")[-1]
VERSION = sys.argv[4]
if len(sys.argv)>5:
	REPO_NAME=sys.argv[5]
else:
	REPO_NAME="release"

print getstatusoutput("curl -v --user "+ARTIFACTORY_USERNAME+":"+ARTIFACTORY_PASSWORD+" --data-binary @"+BUNDLE_PATH+" -X PUT http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-"+REPO_NAME+"-repo/VEoP/ci/"+PLATFORM+"/"+VERSION+"/"+ENV+"/"+APP_NAME)