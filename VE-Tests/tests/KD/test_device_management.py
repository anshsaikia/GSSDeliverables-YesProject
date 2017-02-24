__author__ = 'srevg'

import pytest
import random
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

class CompareDeviceInfo(object):
    device_details_milestones = None
    device_details_upm = None
    device_preferences_upm = None
    ve_test = None

def compare_device_detail(compareInfo, fromEntry, toEntry):
    fromString = str(compareInfo.device_details_milestones[fromEntry])
    toString = str(compareInfo.device_details_upm[toEntry])
    compareInfo.ve_test.log_assert(fromString == toString, "failed detail compare - " + fromEntry + ": '" + fromString + "', " + toString + ": '" + toEntry + "'")

def compare_device_preference(compareInfo, fromEntry, toEntry):
    fromString = str(compareInfo.device_details_milestones[fromEntry])
    toString = str(compareInfo.device_preferences_upm[toEntry])
    compareInfo.ve_test.log_assert(fromString == toString, "failed preference compare - " + fromEntry + ": '" + fromString + "', " + toString + ": '" + toEntry + "'")

def compare_device_details(compareInfo):
    compare_device_detail(compareInfo, 'app-version-name', 'clientApplicationVersion')
    compare_device_detail(compareInfo, 'os-full-version', 'osVersion')
    compare_device_detail(compareInfo, 'os-type', 'osName')
    compare_device_detail(compareInfo, 'device-manufacturer', 'manufacturer')
    compare_device_detail(compareInfo, 'device-model', 'modelName')
    compare_device_preference(compareInfo, 'device-name', 'friendlyName')

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2477
@pytest.mark.MF2477_regulations_and_legals
def test_settings_legals():
    ve_test = VeTestApi("settings:test_settings_legal")
    ve_test.begin()

    #Navigating to Settings and Choosing Legal Menu
    ve_test.screens.settings.open_legal()

    ve_test.wait(6)

    milestones = ve_test.milestones
    elements = milestones.getElements()

    scroller1 = [milestones.get_dic_value_by_key("DIC_HELP_SETTINGS_DATA_SECURITY_INFO"),
                 milestones.get_dic_value_by_key("DIC_LEGAL_SETTINGS_TERMS_AND_CONDITIONS"),
                 milestones.get_dic_value_by_key("DIC_LEGAL_SETTINGS_CANCELLATION_RIGHTS"),
                 milestones.get_dic_value_by_key("DIC_LEGAL_SETTINGS_OSS_LICENSE")]

    for link_value in scroller1:
        ve_test.log_assert(milestones.getElementContains(elements, link_value), \
                           "link_value is not present")

    #firstElement = ve_test.milestones.getElement([("title_text", milestones.get_dic_value_by_key("DIC_LEGAL_SETTINGS_TERMS_AND_CONDITIONS"), "==")], elements)
    #distanceEl = ve_test.milestones.getElement([("name", "events_scroller", "==")], elements)
    #distance = distanceEl["width"]
    #direction = ScreenActions.LEFT
    #ve_test.appium.scroll_from_element(firstElement, distance, direction, 0)

    oss_value = milestones.get_dic_value_by_key("DIC_LEGAL_SETTINGS_OSS_LICENSE")
    oss_button = ve_test.milestones.getElement([("title_text", oss_value, "==")])
    ve_test.appium.tap_element(oss_button)

    ve_test.wait(4)
    milestones = ve_test.milestones
    elements = milestones.getElements()
    ve_test.log_assert(ve_test.milestones.getElement([("is_oss_imprint", True, "==")], elements),
                         "imprint oss view did not appear.")
    back_element = ve_test.milestones.getElement([("title_text", "BACK", "==")], elements)
    ve_test.appium.tap_element(back_element)

    scroller2 = [milestones.get_dic_value_by_key("DIC_LEGAL_SETTINGS_CONTACT_INFORMATION"),
                 milestones.get_dic_value_by_key("DIC_LEGAL_SETTINGS_IMPRINT_INFORMATION")]

    milestones = ve_test.milestones
    elements = milestones.getElements()

    for link_value in scroller2:
        ve_test.log_assert(milestones.getElementContains(elements, link_value), \
                        "link_value is not present")


    ve_test.screens.settings.open_data_privacy()

    ve_test.wait(3)
    ve_test.appium.send_app_to_foreground()
    ve_test.wait(3)

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF381
@pytest.mark.MF381_device_management
#@IHmark.LV_L2 # remove from level2 since it's stuck without timeout
# #@pytest.mark.level2
def test_device_quota():
    ve_test = VeTestApi("device_management:test_device_quota")
    ve_test.log("Create a household and changing its maximum deviceQuota to 2")
    hhId, login = ve_test.he_utils.createTestHouseHold(withSTB=False, withPVR=False)
    ve_test.he_utils.set_households_device_quota(hhId, 2)
    deviceIds = []
    ve_test.log("Adding 2 devices to the household")
    for i in range(0, 2):
        deviceIds.append(str(random.randint(100, 10000)))
        ve_test.he_utils.addHouseHoldDevices(hhId, [deviceIds[i]], deviceFullType="Android-Phone", drmDeviceType=None)
        ve_test.log("device id %s" % deviceIds[i])
    '''Signing in'''
    ve_test.begin(login=None)
    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123', verify_startup_screen=False)
    ve_test.wait(10)

    '''Verify the error string and the string in the button'''
    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_SIGN_IN_MAX_DEVICES_EXCEEDED")
    notification.tap_notification_button("DIC_HELP_SETTINGS_CUSTOMER_SELF_CARE")
    ve_test.wait(3)
    ve_test.appium.send_app_to_foreground()
    ve_test.wait(3)
    notification.tap_notification_button("DIC_LOGIN_TRY_AGAIN")
    ve_test.wait(3)
    ve_test.screens.login_screen.verify_active()


    '''Delete one device'''
    ve_test.log("Deleting a device id %s" % deviceIds[0])
    returnCode = ve_test.he_utils.deleteDevicefromHouseholdRestricted(hhId,deviceIds[0])
    ve_test.log("rv from delete is " + str(returnCode))
    '''try to sign in again'''
    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123')
    '''delete one more device and see if it is allowed'''
    ve_test.log("Trying to Delete  device id %s and verifying the Boa device deletion restriction" % deviceIds[1])
    returnCode = ve_test.he_utils.deleteDevicefromHouseholdRestricted(hhId,deviceIds[1])
    ve_test.log_assert(returnCode==403, "The second device deletion is not restricted rv = %d" %returnCode)

    '''delete the additional  device by unrestricted delete and verify it is allowed'''

    ve_test.log("Trying to Delete  device id %s and verifying the unrestricted Boa device deletion" % deviceIds[1])
    returnCode = ve_test.he_utils.deleteDevicefromHousehold(hhId,deviceIds[1])
    ve_test.log_assert(returnCode==200, "The second device deletion is restricted rv = %d" %returnCode)

    '''Get the device details from milestones and upm, compare'''
    ve_test.log("Comparing the device details")
    compareInfo = CompareDeviceInfo()
    compareInfo.device_details_milestones = ve_test.milestones.getDeviceDetails()
    deviceId = compareInfo.device_details_milestones['drm-device-id'].upper()
    compareInfo.device_details_upm = ve_test.he_utils.getDeviceInfofromUpm(hhId, deviceId)
    compareInfo.device_preferences_upm = ve_test.he_utils.getDevicePreferencefromUpm(hhId,deviceId)
    compareInfo.ve_test = ve_test
    compare_device_details(compareInfo)

    ve_test.end()

