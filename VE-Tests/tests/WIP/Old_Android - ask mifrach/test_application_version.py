import os
import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ve_tests.ve_test import VeTestLoginType
from tests_framework.mandatory_update_mock.mandatory_update_mock import *


' Constants '
API = '/minAllowedVersion/?platform=Android'
TIMEOUT = 3
HIGHER_VESION = "99"
LOWER_VESION = "1"

level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=level,
                    format="^%(asctime)s !%(levelname)s <t:%(threadName)s T:%(name)s M:%(filename)s F:%(funcName)s L:%(lineno)d > %(message)s",
                    datefmt="%y/%m/%d %H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARNING)

# MF360 - Device Upgrade [Android]
@pytest.mark.MF360_device_upgrade
@pytest.mark.MF360_device_upgrade_regression
def test_mock_device_upgrade_required():
    ve_test = VeTestApi("test_mock_device_upgrade_required")

    "start the mock server"
    mock_server = MandatoryUpdateSimulator()
    mock_server.start()

    ve_test.appium.push_data_to_settings("version_check_url", "http://"+ MandatoryUpdateSimulator.ip +":8080")

    "Post to the mock with a higher version"
    post_url = "http://"+MandatoryUpdateSimulator.ip +':8080'+"/?minAllowedVersion="+HIGHER_VESION
    res = ve_test.requests.post(post_url)

    "Get the version from the mock"
    get_url = 'http://' + MandatoryUpdateSimulator.ip +':8080'+ API
    r = ve_test.requests.get(get_url)
    logging.info(' response: %s' % r.text)
    responseDict = json.loads(r.text)
    min_version = int(responseDict['MinAllowedVersion'])

    "Launch app"
    ve_test.begin(login=VeTestLoginType.none)

    "get the version from the app"
    device_details = ve_test.milestones.getDeviceDetails()
    current_app_version = int(device_details["app-version-code"])

    if current_app_version < min_version:
        "Check for Unsupported App Version Notification "
        notification = ve_test.screens.notification
        notification.verify_notification_message_by_key('DIC_ERROR_VERSION_CHECK_VERSION_TOO_OLD')

    mock_server.stop()
    logging.info('End mock_test_device_upgrade_required')
    ve_test.end()


# MF360 - Device Upgrade [Android]
@pytest.mark.MF360_device_upgrade
def test_server_down():
    ve_test = VeTestApi("test_server_down")

    "Server is not started"
    mock_server = MandatoryUpdateSimulator()

    ve_test.appium.push_data_to_settings("version_check_url", "http://"+ MandatoryUpdateSimulator.ip +":8080")

    "Launch app"
    ve_test.begin(login=VeTestLoginType.none)

    "Check network connection Notification "
    notification = ve_test.screens.notification
    notification.verify_active()
    notification.verify_notification_message_by_key('DIC_ERROR_VERSION_CHECK_FAILED_VERIFY_APPLICATION_VERSION')

    logging.info('End test_server_down')
    ve_test.end()

"Test version check, without mock server"
def test_version_check():
    ve_test = VeTestApi("test_version_check")
    ve_test.begin(login=VeTestLoginType.none)

    device_details = ve_test.milestones.getDeviceDetails()
    version_check_enabled = device_details['preferences']["pref_app_use_version_check"]
    if version_check_enabled:
        logging.info("Version check enabled.")
        "Get the version from version server"
        version_check_url = device_details['preferences']["pref_version_check_server_base_url"] + API
        r = ve_test.requests.get(version_check_url)
        responseDict = r.json()
        min_version = int(responseDict['MinAllowedVersion'])

        current_app_version = int(device_details["app-version-code"])

        if current_app_version < min_version:
            "Check for Unsupported App Version Notification "
            notification = ve_test.screens.notification
            notification.verify_notification_message_by_key('DIC_ERROR_VERSION_CHECK_VERSION_TOO_OLD')
            logging.info("App has older version and https://static.xx.fbcdn.net/rsrc.php/v2/y4/r/-PAXP-deijE.gifnotification shows up")
        else:
            ve_test.log_assert(ve_test.screens.login_screen.is_active(), "Login screen did not show up")

    else:
        ve_test.log_assert(ve_test.screens.login_screen.is_active(), "Login screen did not show up")
        logging.info("Version check is disabled")
    logging.info('End test_version_check')
    ve_test.end()
