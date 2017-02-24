__author__ = 'srevg'

import json
import random
from tests_framework.ve_tests.ve_test import VeTestApi


def compare_device_details(ve_test, device_details_milestones, device_details_upm, device_preference_upm):
    ve_test.log_assert(str(device_details_milestones['app-version-code']) == device_details_upm['clientApplicationVersion'])
    ve_test.log_assert(device_details_milestones['os-version-release'] == device_details_upm['osVersion'])
    ve_test.log_assert(device_details_milestones['os-type'] == device_details_upm['osName'])
    ve_test.log_assert(device_details_milestones['device-manufacturer'] == device_details_upm['manufacturer'])
    ve_test.log_assert(device_details_milestones['device-model'] == device_details_upm['modelName'])
    ve_test.log_assert(device_details_milestones['device-model'] == device_preference_upm['friendlyName'])

def test_device_quota():
    ve_test = VeTestApi("device_management:test_verify_household_properties")

    #creating a dummy household and changing its Maximum deviceQuota to 2
    hhId, login = ve_test.he_utils.createTestHouseHold(withPVR=False)
    ve_test.he_utils.set_households_device_quota(hhId, 2)

    #Adding 2 devices to the household
    for i in range(0, 2):
        deviceId = str(random.randint(100, 10000))
        ve_test.he_utils.addHouseHoldDevices(hhId, [deviceId], deviceFullType="Android-Phone", drmDeviceType=None)

    #Signing in
    ve_test.appium.launch_app()
    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123', verify_startup_screen = False)
    ve_test.wait(10)

    #Verify the error string and the string in the button.
    notification = ve_test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_SIGN_IN_MAX_DEVICES_EXCEEDED")
    notification.tap_notification_button("DIC_HELP_SETTINGS_CUSTOMER_SELF_CARE")

    ve_test.wait(3)
    ve_test.appium.send_app_to_foreground()
    notification.tap_notification_button("DIC_LOGIN_TRY_AGAIN")
    ve_test.wait(3)
    ve_test.screens.login_screen.verify_active()

    #Change the household Maxdevice Quota to 5 and sign in
    ve_test.he_utils.set_households_device_quota(hhId, 5)

    #ve_test.he_utils.setHHoffers(hhId)
    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123')


    #Get the device details from milestones and upm, compare
    device_details_milestones = ve_test.milestones.getDeviceDetails()
    deviceId = device_details_milestones['drm-device-id']
    device_details_upm = ve_test.he_utils.getDeviceInfofromUpm(hhId, deviceId)
    device_preferences_upm = ve_test.he_utils.getDevicePreferencefromUpm(hhId,deviceId)
    compare_device_details(ve_test, device_details_milestones, device_details_upm, device_preferences_upm)

