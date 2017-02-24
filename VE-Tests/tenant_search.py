from subprocess import call
from subprocess import check_output
import time
import requests
import json
import os
from os.path import expanduser
import sys

isScramble = False
isSTB = True


def create_HH(fullPath, HH, tenantName):
    project_dir = os.getcwd()
    os.chdir(fullPath)
    # example : os.chdir("/cygdrive/c/Users/rzawrbac/vgw-test-utils")

    # VE region is always 16384~16385
    call("export CMDC_REGION=16384~16385", shell=True)

    tenantName = tenantName.replace("_", "-")

    call(
        "STB_PLATFORM=vgw10-bcm7444Se0 fab -f fabfile/__init__.py reset_household:subnet=openstack-%s,device_id=%s,household_id=%s_HH" % (
        tenantName, HH, HH), shell=True)

    os.chdir(project_dir)


def launch_app(tenant):
    print "run config.sh"
    os.system("./config.sh %s" % (tenant))

    print "build and install app on " + tenant
    os.system("./gradlew install%sDebug" % (tenant))

    print "launch application"
    os.system(
        "adb shell am start -S -W -a android.intent.action.VIEW -c android.intent.category.DEFAULT -n com.vodafone.pearlandroid/com.cisco.veop.client.MainActivity")


def login_app(HH, isSTB):
    adb_ouput = check_output(["adb", "devices"])
    devicelist = adb_ouput.split("\n")
    deviceId = devicelist[1].split("\t")
    deviceId = deviceId[0]

    print "login app"

    if (isSTB):
        os.system("adb -s %s -d shell input text %s_HH" % (deviceId, HH))
    else:
        os.system("adb -s %s -d shell input text %s" % (deviceId, HH))
    os.system("adb -s %s shell input keyevent 61" % (deviceId))
    os.system("adb -s %s -d shell input text 123" % (deviceId))
    os.system("adb -s %s shell input keyevent 66" % (deviceId))


def check_streaming_state():
    print "Check if stream exist"
    # wait till stream should arrive
    time.sleep(7)

    device_ip = check_output(
        ["adb shell ip route | grep wlan0 | grep -o 'src [^ ]*' | cut -b5- | uniq | tr -d \"\n\" "], shell=True)

    payload = {'jsonrpc': '2.0', 'method': 'getPlaybackStatus', 'id': 1}
    # KD works on port 5050
    r = requests.post("http://%s:5050/milestones" % (device_ip), data=json.dumps(payload))

    jsonResponse = r.json()
    return json.loads(jsonResponse["result"])["playbackState"]


def read_cfg():
    global fullPath
    global HH
    path = os.getcwd() + "/user_cfg.txt"
    if (os.path.isfile(path)):
        fullPath = None
        HH = None
        f = open(path, 'r')
        for line in f:
            if "vgw_test_utils_path" in line:
                fullPath = line.split("= ")
                fullPath = fullPath[1]
                print "reut: ful path is!!!!!"+fullPath

            elif "HH" in line:
                HH = line.split("= ")
                HH = HH[1].rstrip()
                print "reut: HH is !!!!"+HH
    else:
        # create a file and ask for input
        f = open('user_cfg.txt', 'w')
        HH = raw_input("please enter your HH(no_HH at the end): ")
        if (HH != ""):
            f.write('HH = %s\n' % HH)
        else:
            print "Script can not run without HH. Exit(0)"
            os.remove('user_cfg.txt')
            sys.exit(0)
        if (isSTB):
            fullPath = raw_input("please enter full path for vgw-test-utils OR run reset_household by yourself: ")
            if (fullPath):
                f.write('vgw_test_utils_path = %s' % fullPath)


def main(argv):
    isScramble = False
    isSTB = True

    for args in sys.argv:
        if args == "scramble":
            isScramble = True
        elif args == "notSTB":
            isSTB = False

    if isScramble:
        TENANT_LIST = ['jer_lion', 'jer_cicd', 'jer_tiger', 'jer_popcorn', 'jer_amstel']
    else:
        TENANT_LIST = ['jer_batman', 'jer_cicd', 'jer_amstel', 'jer_doritos']

    read_cfg()

    for tenant in TENANT_LIST:
        print "Trying to run againt " + tenant

        # check if we have lab_settings for this tenant and continue otherwise
        if (not os.path.exists(os.getcwd() + "/lab_settings/" + tenant)):
            continue

        if (isSTB):
            if (fullPath):
                create_HH(fullPath, HH, tenant)
            else:
                print "********You have not entered vgw-test-utils path. You may not be authorized to watch streaming***********"
        else:
            print "make sure to run creat HH script on your own"

        call("adb -d uninstall com.vodafone.pearlandroid", shell=True)

        launch_app(tenant)
        # wait till app is installed
        time.sleep(10)
        login_app(HH, isSTB)

        playbackState = check_streaming_state()

        if playbackState == "PLAYING":
            print tenant + " has streaming"
            break
        else:
            call("adb shell am force-stop com.vodafone.pearlandroid", shell=True)
            continue


        # print "No tenant with streaming has been found."


if __name__ == "__main__": main(sys.argv[1:])
