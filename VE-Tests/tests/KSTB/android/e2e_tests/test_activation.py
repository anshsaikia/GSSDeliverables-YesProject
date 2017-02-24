__author__ = 'eleduc'

import pytest
import random
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.login_screen import SIGN_IN_TIMEOUT
from tests_framework.ui_building_blocks.KSTB.error import *

''' Constants '''
LAUNCH_TIMEOUT = 8
REMAIN_IN_BACKGROUND_TIMEOUT = 5
BAD_TOKEN_ACCOUNT_ID = "HH-Btoken"
INVALID_SAML_ACCOUNT_ID = 'HH-BSAML'
RETRY_ACTION = "RETRY"
HOME_ACTION = "EXIT"

def login_error(test, user_name, password, error_title, error_msg, error_code, error_actions, focused_action):
    """
    Check the activation error message
    :param test: The test instance
    :param user_name: The login user name
    :param password: The login password
    :param error_title: The expected title on the error message screen
    :param error_msg: The expected error message
    :param error_code: The expected error code
    :param error_actions: The expected buttons displayed (array of titles)
    :return: Raise assert error if the expected values are not displayed
    """
    test.screens.login_screen.enter_credentials(user_name, password)
    test.wait(SIGN_IN_TIMEOUT)
    test.check_notification_screen(shown=True, msg_title=error_title, msg_text=error_msg, msg_code=error_code, msg_buttons=error_actions, focused_action=focused_action)

@pytest.mark.sanity
@pytest.mark.FS_Drmdummy
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_login():
    """
    Start the application
    Once correctly started and logged, restart the application
    Check no login screen displayed again, and hub screen active
    Put the application in background
    Restore it and check the hub is still active
    :return: Raise assert error if any
    """
    ve_test = VeTestApi("activation:test_login")
    #device activation is done in sign in process, which called in begin
    ve_test.begin()

    # Cold reboot (restart).
    # No sign in screen should be displayed.
    # Go directly to main hub
    ve_test.appium.restart_app()
    ve_test.wait(LAUNCH_TIMEOUT)
    ve_test.screens.main_hub.verify_active()

    # Warm reboot (background).
    # No sign in screen should be displayed.
    # Should remain in main hub
    ve_test.appium.send_app_to_background()
    ve_test.wait(REMAIN_IN_BACKGROUND_TIMEOUT)
    ve_test.appium.send_app_to_foreground()
    ve_test.screens.main_hub.verify_active()

    ve_test.end()

@pytest.mark.FS_Drm
@pytest.mark.sanity
@pytest.mark.LV_L2
def test_login_non_existent_account():
    """
    Check error message LOGIN_FAILED_ERROR_MSG on dummy_account user name
    :return: Raise assert error if any
    """
    ve_test = VeTestApi("activation:test_login_non_existent_account")
    ve_test.begin(login=ve_test.login_types.none)

    buttons = [RETRY_ACTION, HOME_ACTION]
    login_error(ve_test, user_name="dummy_account", password='123', error_title=ERROR_TITLE, error_msg=E_LOGIN_FAILED_ERROR_MSG, error_code=E_LOGIN_FAILED_ERROR_CODE, error_actions=buttons, focused_action=RETRY_ACTION)

    ve_test.end()

@pytest.mark.FS_Drm
@pytest.mark.sanity
@pytest.mark.LV_L2
def test_login_drm_activation_failed():
    """
    Check error message ACTIVATION_FAILED_ERROR_MSG when DRM activation
    failed with the credential BAD_TOKEN_ACCOUNT_ID
    :return: Raise assert error if any
    """
    ve_test = VeTestApi("activation:test_login_drm_activation_failed")
    ve_test.begin(login=ve_test.login_types.none)

    buttons = [RETRY_ACTION, HOME_ACTION]
    login_error(ve_test, user_name=BAD_TOKEN_ACCOUNT_ID, password='123', error_title=ERROR_TITLE, error_msg=E_ACTIVATION_FAILED_ERROR_MSG, error_code=E_ACTIVATION_FAILED_ERROR_CODE, error_actions=buttons, focused_action=RETRY_ACTION)

    ve_test.end()

@pytest.mark.FS_Drm
@pytest.mark.sanity
@pytest.mark.LV_L3
def test_login_invalid_saml():
    """
    Check the error message LOGIN_FAILED_ERROR_MSG with the credential user name INVALID_SAML_ACCOUNT_ID
    :return: Raise assert error if any
    """
    ve_test = VeTestApi("activation:test_login_invalid_saml")
    ve_test.begin(login=ve_test.login_types.none)

    buttons = [RETRY_ACTION, HOME_ACTION]
    login_error(ve_test, user_name=INVALID_SAML_ACCOUNT_ID, password='123', error_title=ERROR_TITLE, error_msg=E_LOGIN_FAILED_ERROR_MSG, error_code=E_LOGIN_FAILED_ERROR_CODE, error_actions=buttons, focused_action=RETRY_ACTION)

    ve_test.end()

@pytest.mark.FS_Drm
@pytest.mark.sanity
@pytest.mark.LV_L3
def test_login_fail_recover():
    """
    This test allow to exercise the retry mechanism on BACK key pressed
    Check the ACTIVATION_FAILED_ERROR_MSG with the credential BAD_TOKEN_ACCOUNT_ID
    On BACK key, check the default credential is accepted
    :return: Raise assert error if any
    """
    ve_test = VeTestApi("activation:test_login_fail_recover")
    ve_test.begin(login=ve_test.login_types.none)

    buttons = [RETRY_ACTION, HOME_ACTION]
    login_error(ve_test, user_name=BAD_TOKEN_ACCOUNT_ID, password='123', error_title=ERROR_TITLE, error_msg=E_ACTIVATION_FAILED_ERROR_MSG, error_code=E_ACTIVATION_FAILED_ERROR_CODE, error_actions=buttons, focused_action=RETRY_ACTION)
    ve_test.wait(1)
    ve_test.appium.key_event("KEYCODE_BACK")
    ve_test.wait(5)
    (hh_id, user_name) = ve_test.he_utils.get_default_credentials()
    ve_test.screens.login_screen.enter_credentials(user_name, '123')
    ve_test.wait_for_screen_assert(SIGN_IN_TIMEOUT, "main_hub", msg = "Failed to verify MainHub screen when completing signIn")

    ve_test.end()


def concurrency(numDevices, maxDevices):
    """
    Allow to check if added a new device is accepted or not depending of the input values.
    :param numDevices: Number of devices to activate
    :param maxDevices: Maximum of devices allowed
    :return: Raise an assert error if the expected error message is not displayed (numDevices = maxDevices)
    or if a new devices cannot be activated (numDevices < maxDevices)
    """
    ve_test = VeTestApi("test_login_max_devices")

    he_utils = ve_test.he_utils
    hhid,login = he_utils.createTestHouseHold("test_login_max_devices", maxDevices = maxDevices)

    ve_test.wait(10)

    try:
        for i in range(0, numDevices):
            deviceId = str(random.randint(100, 10000))
            he_utils.addHouseHoldDevices(hhid, [deviceId], deviceFullType = "Android-Phone", drmDeviceType = None)
    except:
        pass

    ve_test.begin(login=ve_test.login_types.custom)
    if ve_test.platform == "Android":
        if numDevices == maxDevices:
            buttons = [RETRY_ACTION, HOME_ACTION]
            login_error(ve_test, user_name=login, password='123', error_title=ERROR_TITLE, error_msg=E_MAX_DEVICES_EXCEEDED_ERROR_MSG, error_code=E_MAX_DEVICES_EXCEEDED_ERROR_CODE, error_actions=buttons, focused_action=RETRY_ACTION)
        else:
            ve_test.screens.login_screen.sign_in(hh_id=hhid,user_name=login)
            ve_test.screens.main_hub.verify_active()

    ve_test.end()

@pytest.mark.FS_Drm
@pytest.mark.sanity
@pytest.mark.LV_L3
def test_login_max_device_4_5():
    """
    Check activation is correct for an other device with same household identifier
    when the maximum allowed is not yet reached.
    :return: A new added device shall be correctly activated
    """
    concurrency(4, 5)
    pass

@pytest.mark.FS_Drm
@pytest.mark.sanity
@pytest.mark.LV_L3
def test_login_max_device_10():
    """
    Check it is not allowed to activate one more device with same household identifier
    when the maximum allowed is already activated
    :return: Raise an error if the expected error message is not displayed.
    """
    concurrency(10, 10)
    pass

