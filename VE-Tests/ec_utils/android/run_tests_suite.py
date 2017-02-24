__author__ = 'bwarshaw'

import os, sys, subprocess
from commands import getstatusoutput
from time import sleep

APPIUM_SERVER_LAUNCH_TIMEOUT = 5

def usage(reason):
    if reason:
        print reason
    print "Usage: run_tests_suite.py <tests folder> <appium host> <appium port>"
    assert 0

def check_arguments():
    if len(sys.argv) != 4:
        usage("Wrong arguments")

    if not os.path.isdir(sys.argv[1]):
        usage("Second argv must be a folder path to tests")

def start_appium_server():
    global appium_server_process
    appium_server_process = subprocess.Popen(["appium", "-a", appium_host, "-p", appium_port], shell=True)
    sleep(APPIUM_SERVER_LAUNCH_TIMEOUT)

def stop_appium_server():
    appium_server_process.kill()
    appium_server_process.terminate()

check_arguments()
tests_path = sys.argv[1]
appium_host = sys.argv[2]
appium_port = sys.argv[3]

#appium_server_process = None
#start_appium_server()

for test in os.listdir(tests_path):
    if test.startswith("test") and test.endswith(".py"):
        print "Running test: " + tests_path + "/" + test
        print getstatusoutput("py.test " + tests_path + "/" + test)

#stop_appium_server()


