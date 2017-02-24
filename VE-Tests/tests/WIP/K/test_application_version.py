import pytest
import logging
import httplib
import re
import os
from time import sleep
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.mandatory_update_mock.mandatory_update_mock_ios import *
from vgw_test_utils.IHmarks import IHmark

#from tests_framework.mandatory_update_mock.mandatory_update_mock import *


' Constants '
API = '/minAllowedVersion/?platform=iOS'
TIMEOUT = 3
HIGHER_VESION = "99"
LOWER_VESION = "1"

level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=level,
                    format="^%(asctime)s !%(levelname)s <t:%(threadName)s T:%(name)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s",
                    datefmt="%y/%m/%d %H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARNING)


"Get minimum version of app required from server"
def get_min_required_version(ve_test):
    "Retrieve sever IP, port from appium.ini"
    #Url = 'https://' + ve_test.configuration["he"]["versionServerIp"] + API
    device_details = ve_test.milestones.getDeviceDetails()
    version_server = device_details["server_minimum_allowed"]
    Url = version_server + API
    print Url
    r = ve_test.requests.get(Url,verify=False)
    logging.info(' response: %s' % r.text)
    ve_test.log_assert(r.status_code == httplib.OK, 'Failed to get minimum version of app required')
    responseDict = json.loads(r.text)
    min_version = responseDict['MinAllowedVersion']
    return normalizeVersionFromVersion(min_version)

def normalizeVersionFromVersion(version):
    print version
    version = re.sub("[^0-9.]", "",version)
    components=version.split('.')
    #should be 1.2.3
    numOfComponents=len(components)
    while numOfComponents<3:
        components.append("0")
        numOfComponents += 1
    print components
    numericVersion=0
    i=0
    for component in components:
        numericVersion *= 2^16
        numericVersion += long(component)
        i += 1
    print numericVersion
    return numericVersion

def run_mock_server():
    mock_server = MandatoryUpdateSimulator()
    mock_server.start()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1254
@pytest.mark.MF1254_mandatory_upgrade
@pytest.mark.commit
@pytest.mark.level2
@pytest.mark.ios_regression
# MF1254 - Mandatory Upgrade [iOS]
def test_device_upgrade_required():
    "Launch app"
    ve_test = VeTestApi("test_device_upgrade_required")
    ve_test.begin(login="custom")
    ve_test.milestones.changeSettings(json.dumps([{"mandatoryUpgradeCheck": True}]))
    ve_test.wait(2)
    ve_test.appium.restart_app()
    ve_test.wait(7)

    "Get the version from the app"
    device_details = ve_test.milestones.getDeviceDetails()
    current_app_version = normalizeVersionFromVersion(device_details["app-version-code"])
    print "app version is %s",current_app_version

    "Get minimum version of app required from server"
    min_required_version = get_min_required_version(ve_test)
    print "Min Version set is:%s",min_required_version

    "Check if version of app is less than minimum required version"
    if current_app_version < min_required_version:
        "Check for Unsupported App Version Notification"
        ve_test.screens.notification.verify_notification()
        sleep(0.5)

    else:
        "Check if login screen appears"
        sleep(TIMEOUT)
        ve_test.screens.login_screen.verify_active()

    logging.info('End test_device_upgrade_required')
    #ve_test.milestones.changeSettings(json.dumps([{"mandatoryUpgradeCheck":False}]))
    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1254
@pytest.mark.MF1254_mandatory_upgrade
# MF1254 - Mandatory Upgrade [iOS]
def test_server_down():
    ve_test = VeTestApi("test_server_down")

    "Server is not started"
    mock_server = MandatoryUpdateSimulator()

    "Launch app"
    ve_test.begin(login="custom")
    app_config_file = ve_test.milestones.getConfigFile()
    version_server = app_config_file["server_minimum_allowed"]
    ve_test.milestones.changeSettings(json.dumps([{"mandatoryUpgradeCheck":True},{"ytvVersionServer":"http://"+ MandatoryUpdateSimulator.ip[0:-5]}]))
    ve_test.wait(2)
    ve_test.appium.restart_app()
    ve_test.wait(7)

    "Check network connection Notification "
    notificationText = ve_test.milestones.get_dic_value_by_key('DIC_ERROR_VERSION_CHECK_FAILED_VERIFY_APPLICATION_VERSION')
    ve_test.screens.notification.verify_notification_message(notificationText)
    ve_test.screens.notification.verify_dismiss(True)

    ve_test.milestones.changeSettings(json.dumps([{"ytvVersionServer":version_server}]))
    logging.info('End test_server_down')
    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1254
@pytest.mark.MF1254_mandatory_upgrade
# MF1254 - Mandatory Upgrade [iOS]
def test_mock_device_upgrade_required():
    ve_test = VeTestApi("test_mock_device_upgrade_required")

    "start the mock server"
    serverThread = threading.Thread(target=run_mock_server)
    serverThread.daemon = True
    serverThread.start()
    ve_test.wait(3)

    "Post to the mock with a higher version"
    post_url = "http://"+ MandatoryUpdateSimulator.ip +"/minAllowedVersion?platform=iOS"
    print post_url
    res = ve_test.requests.post(post_url, data=HIGHER_VESION)

    "Get the version from the mock"
    get_url = 'http://' + MandatoryUpdateSimulator.ip + API
    print get_url
    r = requests.get(get_url)
    logging.info(' response: %s' % r.text)
    responseDict = json.loads(r.text)
    min_version = normalizeVersionFromVersion(responseDict['MinAllowedVersion'])

    "Launch app"
    ve_test.begin(login="custom")
    app_config_file = ve_test.milestones.getConfigFile()
    version_server = app_config_file["server_minimum_allowed"]
    ve_test.milestones.changeSettings(json.dumps([{"ytvVersionServer":"http://"+ MandatoryUpdateSimulator.ip}]))
    ve_test.wait(2)
    ve_test.appium.restart_app()
    ve_test.wait(7)

    "get the version from the app"
    device_details = ve_test.milestones.getDeviceDetails()
    current_app_version = normalizeVersionFromVersion(device_details["app-version-code"])

    if current_app_version < min_version:
        "Check for Unsupported App Version Notification "
        message_text = ve_test.milestones.get_dic_value_by_key('DIC_ERROR_VERSION_CHECK_VERSION_TOO_OLD')
        ve_test.screens.notification.verify_notification_message(message_text)
        ve_test.screens.notification.verify_dismiss(True)

    ve_test.milestones.changeSettings(json.dumps([{"ytvVersionServer":version_server}]))
    print "after checks"
    logging.info('End mock_test_device_upgrade_required')
    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1254
@pytest.mark.MF1254_mandatory_upgrade
# MF1254 - Mandatory Upgrade [iOS]
def test_mock_device_upgrade_not_required():
    ve_test = VeTestApi("test_mock_device_upgrade_not_required")

    "assuming mock server already up"
    serverThread = threading.Thread(target=run_mock_server)
    serverThread.daemon = True
    serverThread.start()
    ve_test.wait(3)

    "Post to the mock with a lower version"
    post_url = "http://"+ MandatoryUpdateSimulator.ip +"/minAllowedVersion?platform=iOS"
    res = ve_test.requests.post(post_url, data=LOWER_VESION)

    "Get the version from the mock"
    get_url = 'http://' + MandatoryUpdateSimulator.ip + API
    r = ve_test.requests.get(get_url)
    logging.info(' response: %s' % r.text)
    responseDict = json.loads(r.text)
    min_version = normalizeVersionFromVersion(responseDict['MinAllowedVersion'])

    "Launch app"
    ve_test.begin(login="custom")
    app_config_file = ve_test.milestones.getConfigFile()
    version_server = app_config_file["server_minimum_allowed"]
    ve_test.milestones.changeSettings(json.dumps([{"ytvVersionServer":"http://"+ MandatoryUpdateSimulator.ip}]))
    ve_test.wait(2)
    ve_test.appium.restart_app()
    ve_test.wait(7)

    "get the version from the app"
    device_details = ve_test.milestones.getDeviceDetails()
    current_app_version = normalizeVersionFromVersion(device_details["app-version-code"])

    if min_version <= current_app_version :
        "Check if login screen appears"
        sleep(TIMEOUT)
        ve_test.screens.login_screen.verify_active()

    ve_test.milestones.changeSettings(json.dumps([{"ytvVersionServer":version_server}]))
    logging.info('End mock_test_device_upgrade_not_required')
    ve_test.end()
