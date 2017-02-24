import os
import pytest
import requests
import logging
from time import time
from tests_framework.ve_tests.ve_test import VeTestApi, VeTestLoginType
from tests_framework.mandatory_update_mock.mandatory_update_mock import *


' Constants '
API = '/minAllowedVersion/?platform=androidTV'
TIMEOUT = 3
HIGHER_VESION = "99"
LOWER_VESION = "1"

level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=level,
                    format="^%(asctime)s !%(levelname)s <t:%(threadName)s T:%(name)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s",
                    datefmt="%y/%m/%d %H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARNING)


"Get minimum version of app required from server"
def get_min_required_version(configuration):
    "Retrieve sever IP, port from appium.ini"
    Url = 'https://' + configuration["he"]["versionServerIp"] + '/' + API
    logging.info(' Url: %s' % Url)
    r = requests.get(Url,verify=False)
    logging.info(' response: %s' % r.text)
    assert r.status_code == httplib.OK, 'Failed to get minimum version of app required'
    responseDict = json.loads(r.text)
    min_version = int(responseDict['MinAllowedVersion'])
    return min_version

@pytest.mark.ethernet
@pytest.mark.boot
@pytest.mark.sanity
def test_device_upgrade_required():
    ve_test = VeTestApi("test_device_upgrade_required")

    ve_test.appium.turn_on_device()
    ve_test.appium.reset_app()
    ve_test.appium.launch_app()
    ve_test.start_time = time()
    ve_test.login=VeTestLoginType.login

    "Get the version from the app"
    device_details = ve_test.milestones.getDeviceDetails()
    current_app_version = int(device_details["app-version-code"])

    "Get minimum version of app required from server"
    configuration = ve_test.configuration
    min_required_version = get_min_required_version(configuration)

    "Check if version of app is less than minimum required version"
    if current_app_version < min_required_version:
        "Check for Unsupported App Version Error "
        element = ve_test.milestones.getElement([("msg_title", "Error", "==")])
        #logging.info('dump msg_title == Error: %s ' % json.dumps(element))
        ve_test.log_assert(element, "error msg not found on screen")
        dic_value_msg = ve_test.milestones.get_dic_value_by_key('DIC_ERROR_APP_VERSION_TOO_OLD', type="error")
        # Remove "Error code " from msg_error >> element["msg_error"][11:]
        msg_text=element["msg_text"]+"("+element["msg_error"][11:]+")"
        ve_test.log_assert(msg_text == dic_value_msg or msg_text == dic_value_msg.upper, "error msg %s is not equal to %s " % (msg_text, dic_value_msg))
    else:
        "Check if login screen appears"
        ve_test.wait(TIMEOUT)
        element = ve_test.milestones.getElement([("name", "login", "==")])
        ve_test.log_assert(element, "login not found on screen")

    logging.info('End test_device_upgrade_required')
    ve_test.end()

@pytest.mark.ethernet
@pytest.mark.boot
@pytest.mark.sanity
def test_mock_device_upgrade_required():
    ve_test = VeTestApi("test_mock_device_upgrade_required")

    "start the mock server"
    mock_server = MandatoryUpdateSimulator()
    mock_server.start()

    ve_test.appium.push_data_to_settings("version_check_url", "http://"+ MandatoryUpdateSimulator.ip +":5055")
    logging.info('version_check_url: http://%s:5055' % MandatoryUpdateSimulator.ip)

    "Post to the mock with a higher version"
    post_url = "http://"+ MandatoryUpdateSimulator.ip +":5055/?minAllowedVersion="+HIGHER_VESION
    res = requests.post(post_url)

    "Get the version from the mock"
    get_url = "http://" + MandatoryUpdateSimulator.ip +":5055/" + API
    r = requests.get(get_url)
    logging.info(' response: %s' % r.text)
    responseDict = json.loads(r.text)
    min_version = int(responseDict['MinAllowedVersion'])

    "Launch app"
    ve_test.appium.turn_on_device()
    # Do not reset app to keep previous "version_check_url" setting
    ve_test.appium.launch_app()
    ve_test.start_time = time()
    ve_test.login=VeTestLoginType.login

    "get the version from the app"
    device_details = ve_test.milestones.getDeviceDetails()
    current_app_version = int(device_details["app-version-code"])

    if current_app_version < min_version:
        "Check for Unsupported App Version Error "
        element = ve_test.milestones.getElement([("msg_title", "Error", "==")])
        #logging.info('dump msg_title == Error: %s ' % json.dumps(element))
        ve_test.log_assert(element, "error msg not found on screen")
        dic_value_msg = ve_test.milestones.get_dic_value_by_key('DIC_ERROR_APP_VERSION_TOO_OLD', type="error")
        # Remove "Error code " from msg_error >> element["msg_error"][11:]
        msg_text=element["msg_text"]+"("+element["msg_error"][11:]+")"
        ve_test.log_assert(msg_text == dic_value_msg or msg_text == dic_value_msg.upper, "error msg %s is not equal to %s " % (msg_text, dic_value_msg))

    mock_server.stop()
    logging.info('End mock_test_device_upgrade_required')
    ve_test.end()

@pytest.mark.ethernet
@pytest.mark.boot
@pytest.mark.sanity
def test_mock_device_upgrade_not_required():
    ve_test = VeTestApi("test_mock_device_upgrade_not_required")

    "start the mock server"
    mock_server = MandatoryUpdateSimulator()
    mock_server.start()

    ve_test.appium.push_data_to_settings("version_check_url", "http://"+ MandatoryUpdateSimulator.ip +":5055")

    "Post to the mock with a lower version"
    post_url = "http://"+ MandatoryUpdateSimulator.ip +":5055/?minAllowedVersion="+LOWER_VESION
    res = requests.post(post_url)

    "Get the version from the mock"
    get_url = "http://" + MandatoryUpdateSimulator.ip +":5055/" + API
    r = requests.get(get_url)
    logging.info(' response: %s' % r.text)
    responseDict = json.loads(r.text)
    min_version = int(responseDict['MinAllowedVersion'])

    "Launch app"
    ve_test.appium.turn_on_device()
    # Do not reset app to keep previous "version_check_url" setting
    ve_test.appium.launch_app()
    ve_test.start_time = time()
    ve_test.login=VeTestLoginType.login

    "get the version from the app"
    device_details = ve_test.milestones.getDeviceDetails()
    current_app_version = int(device_details["app-version-code"])

    if min_version <= current_app_version :
        "Check if login screen appears"
        ve_test.wait(TIMEOUT)
        element = ve_test.milestones.getElement([("name", "login", "==")])
        ve_test.log_assert(element, "login not found on screen")

    mock_server.stop()
    logging.info('End mock_test_device_upgrade_not_required')
    ve_test.end()

@pytest.mark.ethernet
@pytest.mark.boot
@pytest.mark.sanity
def test_server_down():
    ve_test = VeTestApi("test_server_down")

    "Server is not started"
    mock_server = MandatoryUpdateSimulator()

    ve_test.appium.push_data_to_settings("version_check_url", "http://"+ MandatoryUpdateSimulator.ip +":5055")

    "Launch app"
    ve_test.appium.turn_on_device()
    # Do not reset app to keep previous "version_check_url" setting
    ve_test.appium.launch_app()
    ve_test.start_time = time()
    ve_test.login=VeTestLoginType.login

    "Check network connection Error "
    element = ve_test.milestones.getElement([("msg_title", "Error", "==")])
    #logging.info('dump msg_title == Error: %s ' % json.dumps(element))
    ve_test.log_assert(element, "error msg not found on screen")
    dic_value_msg = ve_test.milestones.get_dic_value_by_key('DIC_ERROR_UNABLE_TO_VERIFY_APP_VERSION', type="error")
    # Remove "Error code " from msg_error >> element["msg_error"][11:]
    msg_text=element["msg_text"]+"("+element["msg_error"][11:]+")"
    ve_test.log_assert(msg_text == dic_value_msg or msg_text == dic_value_msg.upper, "error msg %s is not equal to %s " % (msg_text, dic_value_msg))

    logging.info('End test_server_down')
    ve_test.end()