__author__ = 'gmaman'

import pytest

''' Constants '''
LAUNCH_TIMEOUT = 8
REMAIN_IN_BACKGROUND_TIMEOUT = 5

BAD_TOKEN_ACCOUNT_ID = "HH-Btoken"
INVALID_SAML_ACCOUNT_ID = 'HH-BSAML'

from tests_framework.ve_tests.ve_test import VeTestApi

def login_error(test, user_name, password, error_key):
    test.screens.login_screen.enter_credentials(user_name, password)
    test.wait(8)
    notification = test.screens.notification
    notification.verify_notification_message_by_key(error_key)


@pytest.mark.MF358_Device_activation
@pytest.mark.export_regression_MF358_Device_activation
@pytest.mark.regression
@pytest.mark.MF1109_Device_activation
def test_login_reboot():
    ve_test = VeTestApi("activation:test_login")
    #device activatrion is done in sighn in process, which called in begin
    ve_test.begin()

    for x in range(1):
        #print "We're on time %d" % (x)
        #cold reboot (restart). no sign in screen should be displayed. go directly to main hub
        ve_test.appium.restart_app()
        ve_test.wait(LAUNCH_TIMEOUT)
        ve_test.screens.main_hub.verify_active(ignoreNotification=True)

        #warm reboot (background). no sign in screen should be displayed. should remain in main hub
        ve_test.appium.send_app_to_background()
        ve_test.wait(REMAIN_IN_BACKGROUND_TIMEOUT)
        ve_test.appium.send_app_to_foreground()
        ve_test.screens.main_hub.verify_active(ignoreNotification=True)

    ve_test.end()

@pytest.mark.MF358_Device_activation
@pytest.mark.export_regression_MF358_Device_activation
@pytest.mark.regression
@pytest.mark.MF1109_Device_activation
@pytest.mark.commit
@pytest.mark.ios_regression
@pytest.mark.reg_MF1382_infra_error_message
def test_login_non_existent_account():
    ve_test = VeTestApi("activation:test_login_non_existent_account")
    ve_test.begin(login=ve_test.login_types.none)

    login_error(ve_test, user_name="dummy_account", password='123', error_key='DIC_ERROR_SIGN_IN_FAILED_CREDENTIALS')

    ve_test.end()

@pytest.mark.MF358_Device_activation
@pytest.mark.MF1109_Device_activation
def test_login_drm_activation_failed():
    ve_test = VeTestApi("activation:test_login_drm_activation_failed")
    ve_test.begin(login=ve_test.login_types.none)

    login_error(ve_test, user_name=BAD_TOKEN_ACCOUNT_ID, password='123', error_key='DIC_ERROR_SIGN_IN_FAILED_ACTIVATION')

    ve_test.end()

@pytest.mark.MF358_Device_activation
@pytest.mark.MF1109_Device_activation
def test_login_invalid_saml():
    ve_test = VeTestApi("activation:test_login_invalid_saml")
    ve_test.begin(login=ve_test.login_types.none)

    login_error(ve_test, user_name=INVALID_SAML_ACCOUNT_ID, password='123', error_key='DIC_ERROR_SIGN_IN_FAILED_CREDENTIALS')

    ve_test.end()

