__author__ = 'Oceane Team'

import pytest
import logging

from tests_framework.ve_tests.ve_test import VeTestApi
from tests.KSTB.android.e2e_tests.test_unitary_settings_ux import settings_preferences

from tests_framework.ve_tests.assert_mgr import AssertMgr
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

#############
# DEBUG
local_debug = True   # to get more traces with infos on states of the tests
#############

#########################################################
#                     PRIVATES Functions                #
#########################################################

def check_settings_logout_option_menu(test,test_title, assertmgr, logout_option_item_to_test):
    """
    private function to check settings logout menu.
    :param test:
    :param test_title:
    :param assertmgr:
    :param logout_option_item_to_test:
    :return:
    """
    # Which logout option item do you want to test?
    if logout_option_item_to_test == 'no':
        all_elements = test.milestones.getElements()
        focused_asset = test.milestones.get_value_by_key(all_elements,"focused_asset")
        if focused_asset.lower() not in ['no', 'nein']:
            assertmgr.addCheckPoint(test_title, 1, focused_asset.lower() in ['no', 'nein'],
                                    "SETTINGS:SYSINFO:LOGOUT:NO: KO default selected option is not 'no' (%s)"
                                    % focused_asset)
            if local_debug:
                logging.info("SETTINGS:SYSINFO:LOGOUT:NO: KO the default selected option is not 'no' (%s)"
                             % focused_asset)
        else:
            if local_debug:
                logging.info("SETTINGS:SYSINFO:LOGOUT:NO: OK the default selected option is  'no'")
            # Press "OK" on this option 'no'
            test.validate_focused_item(2)
            # check the hub screen is displayed
            screen_name = test.milestones.get_current_screen()
            if screen_name != 'main_hub':
                assertmgr.addCheckPoint(test_title, 2, screen_name == 'main_hub',
                                        "SETTINGS:SYSINFO:LOGOUT:NO: KO Failed to displaye the hub screen (%s)"
                                        % screen_name)
                if local_debug:
                    logging.info("SETTINGS:SYSINFO:LOGOUT:NO: KO Failed to displaye the hub screen (%s)" % screen_name)
            elif local_debug:
                logging.info("SETTINGS:SYSINFO:LOGOUT:NO: OK The hub screen is displayed correctly as expected")

    else:  # logout_option_item_to_test == 'yes'
        # go to main hub in order to test another option 'yes' without leaving application
        if test.milestones.get_current_screen() != 'main_hub':
            test.screens.main_hub.navigate()
        # Go to SETTINGS item
        # Go to the 'System Information' item
        if test.screens.main_hub.navigate_to_settings_sub_menu("SYSTEM_INFORMATION"):
            # press "ok" on SYSTEM INFORMATION
            test.validate_focused_item(1)
            # Go to LOGOUT item
            if test.screens.main_hub.focus_settings_sub_sub_menu("LOG OUT"):
                # Go to "Yes" option
                test.move_towards('right')
                # Press "OK" on this option
                test.validate_focused_item(2)
                # Wait 7s
                test.wait(7)
                # Check that the login screen is displayed
                screen_name = test.milestones.get_current_screen()
                if screen_name != 'login':
                    assertmgr.addCheckPoint(test_title, 3, screen_name == 'login',
                                            "SETTINGS:SYSINFO:LOGOUT:YES: KO Failed to display the login screen")
                    if local_debug:
                        logging.info(
                            "SETTINGS:SYSINFO:LOGOUT:YES: KO Failed to display the login screen(%s)" % screen_name)
                elif local_debug:
                    logging.info("SETTINGS:SYSINFO:LOGOUT:YES: OK The login screen is displayed as expected")
            else:
                assertmgr.addCheckPoint(test_title, 5, False,"SETTINGS:SYSINFO:LOGOUT:can't go on LOG OUT item")
        else:
            assertmgr.addCheckPoint(test_title, 4, False,"SETTINGS:SYSINFO:LOGOUT:can't go on SYSTEM INFORMATION item")



def check_qa_settings_sysinfo(test, test_title, assertmgr, sysinfo_option_item_to_test):
    """
    private function to check system information in settings.
    :param test:
    :param test_title:
    :param assertmgr:
    :param sysinfo_option_item_to_test:
    :return:
    """
    dict_sysInfo = {}
    if sysinfo_option_item_to_test.lower() in ['connectivity', 'system information']:
        all_elements = test.milestones.getElements()
        nb_text = int(test.milestones.get_value_by_key(all_elements,"list_size"))
        nb_pairs = int(test.milestones.get_value_by_key(all_elements,"pair_size"))
        logging.info("SETTINGS:SYSINFO: nb_text: %d  nb_pairs:%d" % (nb_text, nb_pairs))
        for i in range(0, nb_text):
            for j in range(0, nb_pairs):
                key = test.milestones.get_value_by_key(all_elements,"pair_key_%s_%s" % (i, j))
                value = test.milestones.get_value_by_key(all_elements,"pair_value_%s_%s" % (i, j))
                if local_debug:
                    logging.info("SETTINGS:SYSINFO: key: %s  value:%s" % (key, value))
                    dict_sysInfo[key] = value
        # Get device information
        device_details = test.milestones.getDeviceDetails()

        if sysinfo_option_item_to_test.lower() == 'connectivity':
            # Check that the text WI-FI is displayed Ethernet  Not connected  Connected
            IP_ADDR_WIFI_NOT_CONNECTED = '0.0.0.0'
            if not dict_sysInfo.has_key("Wi-Fi"):
                assertmgr.addCheckPoint(test_title, 2, not dict_sysInfo.has_key("Wi-Fi"),
                                        "SETTINGS:SYSINFO: WI-FI is NOT displayed")
                if local_debug:
                    logging.info("SETTINGS:SYSINFO:CONNECTIVITY: WI-FI is NOT displayed")
            else:
                # Get the IP adress of WI-FI
                ip_addr_wifi = device_details["network-wifi-ip"]
                if ip_addr_wifi == IP_ADDR_WIFI_NOT_CONNECTED:
                    wifi_status = 'Not connected'
                else:
                    wifi_status = 'Connected'
                # check that WI-FI status is correct
                if wifi_status != dict_sysInfo.get("Wi-Fi"):
                    assertmgr.addCheckPoint(test_title, 3, wifi_status == dict_sysInfo.get("Wi-Fi"),
                                            "SETTINGS:SYSINFO:CONNECTIVITY: Wi-FI status is NOT correct: %s"
                                            % dict_sysInfo.get("Wi-Fi"))
                    if local_debug:
                        logging.info("SETTINGS:SYSINFO:CONNECTIVITY: WI-FI status is NOT correct: %s (%s)" % (
                            dict_sysInfo.get("Wi-Fi"), wifi_status))
                elif local_debug:
                    logging.info("SETTINGS:SYSINFO:CONNECTIVITY: WI-FI status is correct as expected")
    
            # Check that the text ETHERNET is displayed Ethernet  Not connected  Connected
            if not dict_sysInfo.has_key("Ethernet"):
                assertmgr.addCheckPoint(test_title, 2, not dict_sysInfo.has_key("Ethernet"),
                                        "SETTINGS:SYSINFO:CONNECTIVITY: ETHERNET is NOT displayed")
                if local_debug:
                    logging.info("SETTINGS:SYSINFO:CONNECTIVITY: ETHERNETis NOT displayed")
            else:
                # Get ETHERNET status
                if wifi_status == 'Not connected':
                    ethernet_status = 'Connected'
                else:
                    ethernet_status = 'Not connected'
                # check that ETHERNET status is correct
                if ethernet_status != dict_sysInfo.get("Ethernet"):
                    assertmgr.addCheckPoint(test_title, 3, wifi_status == dict_sysInfo.get("Ethernet"),
                                            "SETTINGS:SYSINFO:CONNECTIVITY: ETHERNET status is NOT correct: %s"
                                            % dict_sysInfo.get("Ethernet"))
                    if local_debug:
                        logging.info("SETTINGS:SYSINFO:CONNECTIVITY: WI-FI status is NOT correct: %s (%s)" % (
                            dict_sysInfo.get("Ethernet"), ethernet_status))
                elif local_debug:
                    logging.info("SETTINGS:SYSINFO:CONNECTIVITY: ETHERNET status is correct as expected")
    
        elif sysinfo_option_item_to_test.lower() == 'system information':
            # Check that the "IPTV APP VERSION" text is displayed
            if not dict_sysInfo.has_key("IPTV App Version"):
                assertmgr.addCheckPoint(test_title, 2, not dict_sysInfo.has_key("IPTV App Version"),
                                        "SETTINGS:SYSINFO:SYSTEM INFO: IPTV APP VERSION is NOT displayed")
                if local_debug:
                    logging.info("SETTINGS:SYSINFO:SYSTEM INFO: IPTV APP VERSION is NOT displayed")
            else:
                # Get the version from the app'
                current_app_version = device_details["app-version-name"]
                # check that IIPTV App Version value is correct
                if current_app_version != dict_sysInfo.get("IPTV App Version"):
                    assertmgr.addCheckPoint(test_title, 3, current_app_version == dict_sysInfo.get("IPTV App Version"),
                                            "SETTINGS:SYSINFO:SYSTEM INFO: IPTV App Version value is NOT correct: %s"
                                            % dict_sysInfo.get("IPTV App Version"))
                    if local_debug:
                        logging.info("SETTINGS:SYSINFO:SYSTEM INFO: IIPTV APP VERSION value is NOT correct: %s (%s)" % (
                            dict_sysInfo.get("IPTV App Version"), current_app_version))
                elif local_debug:
                    logging.info("SETTINGS:SYSINFO:SYSTEM INFO: IIPTV App Version value is correct as expected")
    
            # Check that the "ANDROID VERSION" text is displayed
            if not dict_sysInfo.has_key("Android Version"):
                assertmgr.addCheckPoint(test_title, 2, not dict_sysInfo.has_key("Android Version"),
                                        "SETTINGS:SYSINFO:SYSTEM INFO: Android Version is NOT displayed")
                if local_debug:
                    logging.info("SETTINGS:SYSINFO:SYSTEM INFO: Android Version is NOT displayed")
            else:
                # Get OS full version: android version
                os_android_version = device_details["os-full-version"]
                # check that ANDROID VERSION value is correct
                if os_android_version != dict_sysInfo.get("Android Version"):
                    assertmgr.addCheckPoint(test_title, 3, os_android_version == dict_sysInfo.get("Android Version"),
                                            "SETTINGS:SYSINFO:SYSTEM INFO: Android Version value is NOT correct: %s"
                                            % dict_sysInfo.get("Android Version"))
                    if local_debug:
                        logging.info("SETTINGS:SYSINFO:SYSTEM INFO: Android Version value is NOT correct: %s (%s)" % (
                            dict_sysInfo.get("Android Version"), os_android_version))
    
                elif local_debug:
                    logging.info("SETTINGS:SYSINFO:SYSTEM INFO: Android Version value is correct as expected")
    
            # Check that the "SDK VERSION" text is displayed
            if not dict_sysInfo.has_key("SDK Version"):
                    assertmgr.addCheckPoint(test_title, 2, not dict_sysInfo.has_key("SDK Version"),
                                            "SETTINGS:SYSINFO:SYSTEM INFO: SDK VERSION is NOT displayed")
                    if local_debug:
                        logging.info("SETTINGS:SYSINFO:SYSTEM INFO: SDK VERSION is NOT displayed")
            else:
                # Get SDK version
                os_sdk_version = device_details["os-version-sdk"]
                # check that SDK VERSION value is correct
                if os_sdk_version != int(dict_sysInfo.get("SDK Version")):
                    assertmgr.addCheckPoint(test_title, 3,
                                            os_sdk_version == int(dict_sysInfo.get("SDK Version")),
                                            "SETTINGS:SYSINFO:SYSTEM INFO: SDK VERSION value is NOT correct: %s"
                                            % dict_sysInfo.get("SDK Version"))
                    if local_debug:
                        logging.info("SETTINGS:SYSINFO:SYSTEM INFO: SDK VERSION value is NOT correct: %s (%s)" % (
                                     dict_sysInfo.get("SDK Version"), os_sdk_version))
                elif local_debug:
                    logging.info("SETTINGS:SYSINFO:SYSTEM INFO: SDK VERSION value is correct as expected")

    elif sysinfo_option_item_to_test.lower() in ['log out', 'ausloggen']:
        '''
        1. go to logout menu : SETTINGS/SYSTEM INFORMATION/LOGOUT
        2. check that the default selected focus is on 'NO'
        4. press "OK" to validate "No" option
        3. check that the HUB screen is displayed
        '''
        # Check logout option menu "no"
        check_settings_logout_option_menu(test, test_title, assertmgr, 'no')

        '''
        1. go to logout menu : SETTINGS/SYSTEM INFORMATION/LOGOUT
        2. select "Yes" option
        4. press "OK" to validate "Yes" option
        3. check that the login screen is displayed
        '''
        # Check logout option menu "yes"
        check_settings_logout_option_menu(test, test_title, assertmgr, 'yes')


#########################################################
#                     DOCUMENTATION FUNCTIONS           #
#########################################################
# Functions below are here for docuementation pupose only.
# The goal of this is to centralize documention of QA tests
# using tests from other testLevels (L1/L2/L3).
# Documentation is automatically generated here :
# http://ubu-iptv01.cisco.com/dropbox/Android_sf_k_stb_QA_Tests_doc


def doc_test_qa_settings_close_caption():
    """
    TEST: check close caption settings in settings menu

     step : check close caption menu in settings menu
        Action
        - navigate to close caption menu
        Checkup
        - check items in cc menu
    """


def doc_test_qa_settings_audio():
    """
    TEST: check audio preference in settings menu

     step : go to menu: settings/preferences/audio
        Action
        - select another audio language
        - zap to another channel
        - go back to menu: settings/preferences/audio
        Checkup
        - check that the selected audio language is still underlined and the preference
          audio language defined in UPM is updated to the selected audio language.
        - check that the default audio language is underlined and it is the one defined in UPM
    """


#########################################################
#                       TESTS Functions                 #
#########################################################


@pytest.mark.QA
@pytest.mark.QA_settings
@pytest.mark.QA_sysinfo
def test_qa_settings_sysinfo():
    """
    TEST: check system information ins settings menu

     1st step : boot the STB (System information - Navigation)
        Action
        - go to menu settings/system information
        Checkup
        - check it is possible to navigate in the proposed options of SYSTEM INFORMATION item

     2nd step : go to menu settings/system information (System information - Connectivity)
        Action
        - select connectivity in menu settings/system information
        Checkup
        - check the information provided by the option Connectivity are correct and correctly displayed:
          Connected on the WI-FI or ETHERNET and Not Connected on the other one depending on the internet connection

     3rd step : go to menu settings/system information (System information - System information)
        Action
        - select System information in menu settings/system information
        Checkup
        - check it is possible to access the system information related on the Android Device: IPTV APP version ,
          Android version and SDK version are correct and correctly displayed.

     4th step : go to menu settings/system information (System information - log out)
        Action
        - select log out in menu settings/system information
        Checkup
        - check that the default selected focus is on 'NO'
        - check that when validating 'NO' option by pressing on "OK", the HUB screen is displayed

     5th step : go to menu settings/system information (System information - log out)
        Action
        - select log out in menu settings/system information
        - validate 'YES' option by pressing on "OK"
        Checkup
        - check that the login screen is displayed
    """
    logging.info("BEGIN test_qa_settings_sysinfo")
    # Test data
    test_name = "test_qa_settings_sysinfo"
    # Initialization of test
    test = VeTestApi(title=test_name)
    assertmgr = AssertMgr(test)
    # Test starting
    test.begin(screen=test.screens.fullscreen)
    # Go to SETTINGS item
    status = test.screens.main_hub.navigate()
    test.log_assert(status,"fail1 to go to main hub")
    # Go to the 'System Information' item
    status = test.screens.main_hub.navigate_to_settings_sub_menu("SYSTEM_INFORMATION")
    test.log_assert(status,"fail to go to SYSTEM INFORMATION")
    # press "ok" on SYSTEM INFORMATION
    test.validate_focused_item(1)

    ############
    ''' 1st step : boot the STB (System information - Navigation)
        Action
        - go to menu settings/system information
        Checkup
        - check it is possible to navigate in the proposed options of SYSTEM INFORMATION item
    '''
    nb_items =len(CONSTANTS.list_sysinfo_eng)
    for _nb in range(1, nb_items):
        all_elements = test.milestones.getElements()
        before_focus_changed = test.milestones.get_value_by_key(all_elements,"focused_item")
        test.move_towards("up")
        all_elements = test.milestones.getElements()
        after_focus_changed = test.milestones.get_value_by_key(all_elements,"focused_item")
        test.log_assert(before_focus_changed != after_focus_changed,
                        "SETTINGS:NAVIGATION: Focus should be changed after pressing a key. before_focus_changed: %s   "
                        "after_focus_changed:  %s"
                        % (before_focus_changed, after_focus_changed))

    for _nb in range(1, nb_items):
        all_elements = test.milestones.getElements()
        before_focus_changed = test.milestones.get_value_by_key(all_elements,"focused_item")
        test.move_towards("down")
        all_elements = test.milestones.getElements()
        after_focus_changed = test.milestones.get_value_by_key(all_elements,"focused_item")
        test.log_assert(before_focus_changed != after_focus_changed,
                        "SETTINGS:NAVIGATION: Focus should be changed after pressing a key. before_focus_changed: %s   "
                        "after_focus_changed:  %s"
                        % (before_focus_changed, after_focus_changed))
    ############
    ''' 2nd step : go to menu settings/system information (System information - Connectivity)
        Action
        - select connectivity in menu settings/system information
        Checkup
        - check the information provided by the option Connectivity are correct and correctly displayed:
          Connected on the WI-FI or ETHERNET and Not Connected on the other one depending on the internet connection
    '''
    logging.info(" Check option CONNECTIVITY")   
    if test.screens.main_hub.focus_settings_sub_sub_menu("CONNECTIVITY") :
        # Check option "CONNECTIVITY"
        check_qa_settings_sysinfo(test, test_name, assertmgr, CONSTANTS.list_sysinfo_eng[0])
    else:
        test.log_assert(False,"fail to go to CONNECTIVITY")
    ############
    ''' 3rd step : go to menu settings/system information (System information - System information)
        Action
        - select System information in menu settings/system information
        Checkup
        - check it is possible to access the system information related on the Android Device: IPTV APP version ,
          Android version and SDK version are correct and correctly displayed.
    '''
    logging.info(" Check option SYSTEM INFORMATION")
    if test.screens.main_hub.focus_settings_sub_sub_menu("SYSTEM INFORMATION") :
        # Check option "SYSTEM INFORMATION"
        check_qa_settings_sysinfo(test, test_name, assertmgr, CONSTANTS.list_sysinfo_eng[1])
    else:
        test.log_assert(False,"fail to go to SYSTEM INFORMATION")

    # Check option menu of item "LOGOUT"
    ############
    ''' 4th step : go to menu settings/system information (System information - log out)
        Action
        - select log out in menu settings/system information
        Checkup
        - check that the default selected focus is on 'NO'
        - check that when validating 'NO' option by pressing on "OK", the HUB screen is displayed
    '''

    ############
    ''' 5th step : go to menu settings/system information (System information - log out)
        Action
        - select log out in menu settings/system information
        - validate 'YES' option by pressing on "OK"
        Checkup
        - check that the login screen is displayed
    '''
    logging.info(" Check option LOG OUT")
    if test.screens.main_hub.focus_settings_sub_sub_menu("LOG OUT") == True:
        check_qa_settings_sysinfo(test, test_name, assertmgr, CONSTANTS.list_sysinfo_eng[2])
    else:
        test.log_assert(False,"fail to go to LOG OUT")

    assertmgr.verifyAllCheckPoints()
    logging.info("##### End test_qa_settings_sysinfo #####")
    test.end()
