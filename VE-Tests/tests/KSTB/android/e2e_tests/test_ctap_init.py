__author__ = 'pculembo'

import pytest
import logging
import requests
import json
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.error import *

'''
Boot application, change the app server url
Check that the application still works as changing settings after ctap init is not taken into account
'''
@pytest.mark.FS_Reboot
@pytest.mark.sanity
def test_server_unreachable():
    ve_test = VeTestApi("test_server_unreachable")
    ve_test.begin(ve_test.login_types.login)
    # Modify the server name to make it unreachable
    ve_test.milestones.changeSettings(json.dumps(["pref_app_server_base_url","https://sesguard.veop.phx.cisco99.com"]));
    ve_test.wait(5)
    ve_test.appium.restart_app()
    ve_test.wait(10)
    ve_test.check_notification_screen(shown=False, msg_title=ERROR_TITLE, msg_text=E_DIC_ERROR_SERVER_UNREACHABLE, msg_code=E_DIC_ERROR_SERVER_UNREACHABLE_CODE)
    ve_test.end()

	
'''
Boot application and verify the boot component list

@pytest.mark.FS_Reboot
@pytest.mark.sanity
def test_server_error():
    ve_test = VeTestApiKSTB("test_server_error")
    #ve_test.begin(ve_test.login_types.login)
    #ve_test.wait(5)
    #wifi_disconnect(ve_test)
    logging.info("wifi_connect(False) 1")
    #ve_test.appium.wifi_connect(False)
    #ve_test.wait(20)
    ve_test.begin(ve_test.login_types.login) #ve_test.appium.restart_app()
    ve_test.milestones.changeSettings(json.dumps(["pref_app_boot_components","LogoBootComponent,SignInBootComponent,SessionsCleanupBootComponent,DataCachingBootComponent,CtapInitBootComponent,SelectTunedChannelBootComponent"]));
    ve_test.wait(5)
    ve_test.milestones.changeSettings(json.dumps(["pref_app_boot_components_timeout","10000,0,10000,10000,10000"]));
    ve_test.wait(5)
    logging.info("wifi_connect(False) 2")
    ve_test.appium.wifi_connect(False)
    ve_test.wait(20)
    ve_test.appium.restart_app()
    ve_test.wait(5)
    element = ve_test.milestones.getElement([("name", "NotificationView", "==")])
    logging.info("element"+ str(element))
    ve_test.log_assert(element["text_0"] == "Network Issues. Please check your network connection and try again.", "NotificationView not found on screen")
    ve_test.wait(5)

    ve_test.end()	
'''


