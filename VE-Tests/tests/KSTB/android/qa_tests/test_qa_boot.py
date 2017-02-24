__author__ = 'Oceane Team'

import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests.KSTB.android.qa_tests.test_qa_settings import check_settings_logout_option_menu
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS


@pytest.mark.QA
@pytest.mark.QA_boot
@pytest.mark.QA_boot_login
def test_qa_boot_login():
    """
    TEST: test login at boot :

     Step : run Cisco Infinite Video Application after installation
        Action
        - launch Cisco Infinite Home Application
        Checkup
        - check it is possible to login and launch after installing this application.
    """

    ve_test = VeTestApi(title="test_qa_boot_login")
    logging.info("##### BEGIN test_qa_boot_login #####")
    ve_test.begin(ve_test.login_types.login)
    logging.info("##### End test_qa_boot_login #####")
    ve_test.end()


@pytest.mark.QA
@pytest.mark.QA_boot
@pytest.mark.QA_boot_login
def test_qa_boot_login_after_logout():
    """
    TEST: test login after logout

     Step : run Cisco Infinite Video Application logout and then login
        Action
        - launch Cisco Infinite Home Application
        - select log out in menu settings/system information
        - validate 'YES' option by pressing on "OK"
        Checkup
        - check that the login screen is displayed
        - check it is possible to login and launch app
    """

    ############
    # Test data
    test_name = "test_qa_boot_login_after_logout"
    # Initialization of test
    test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(test)
    # Test starting
    logging.info("##### BEGIN test_qa_boot_login_after_logout #####")
    test.begin(screen=test.screens.fullscreen)

    # Check logout option menu "yes"
    check_settings_logout_option_menu(test, test_name, assertmgr, 'yes')
    test.wait(CONSTANTS.WAIT_TIMEOUT)
    # Enter the login and password
    test.screens.login_screen.auto_sign_in()
    logging.info("##### End test_qa_boot_login_after_logout #####")
    test.end()


@pytest.mark.QA
@pytest.mark.QA_boot
@pytest.mark.QA_boot_launching
def test_qa_boot_no_login_after_re_run():
    """
    TEST: test login action after exiting from Cisco Infinite Video Application

     Step : check login screen not displayed after re-run Cisco Infinite Video Application
        Action
        - restart Cisco Infinite Home Application
        Checkup
        - check that the login screen is not displayed again
    """
    ############
    # Test data
    test = VeTestApi(title="test_qa_boot_no_login_after_re_run")
    test.begin(screen=test.screens.fullscreen)

    logging.info("##### BEGIN test_qa_boot_no_login_after_re_run #####")

    test.wait(CONSTANTS.GENERIC_WAIT)
    test.appium.restart_app()
    test.wait(CONSTANTS.WAIT_TIMEOUT)
    screen_name = test.milestones.get_current_screen()
    test.log_assert(screen_name != 'login',
                    "Once correctly started and logged, when restarting the appli, login screen should not be displayed again (%s)" % screen_name)

    logging.info("##### End test_qa_boot_login_access_wifi_ethernet #####")
    test.end()
