__author__ = 'srevg'

from tests_framework.ve_tests.ve_test import VeTestApi

def test_log_out():
    ve_test = VeTestApi("log_out_feature")
    ve_test.begin()

    device_details_milestones = ve_test.milestones.getDeviceDetails()
    deviceId_1 = device_details_milestones['drm-device-id']
    hh_id = ve_test.configuration["he"]["generated_household"]
    user_name = ve_test.configuration["he"]["generated_username"]
    ve_test.wait(7)
    ve_test.screens.settings.log_out()

    # Re Sign In with Same User Name and verify if the device id which is used is same:
    login_screen = ve_test.screens.login_screen
    login_screen.sign_in(hh_id,user_name)
    device_details_milestones = ve_test.milestones.getDeviceDetails()
    deviceId_2 = device_details_milestones['drm-device-id']
    ve_test.log_assert(deviceId_1 == deviceId_2, "Device ids are different")
    ve_test.wait(7)
    ve_test.screens.settings.log_out()

    #Query from upm and see if the device id is still present in the household
    d = ve_test.he_utils.getDeviceIdFromDeviceAndHH(deviceId_2, hh_id)
    ve_test.log_assert(deviceId_2 == d, "device id deleted in upm")

    #Re Sign In with different User Name and verify if the device id which is used is different:
    hhId, login = ve_test.he_utils.createTestHouseHold()
    ve_test.he_utils.setHHoffers(hhId)

    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123')

    device_details_milestones = ve_test.milestones.getDeviceDetails()
    deviceId_3 = device_details_milestones['drm-device-id']
    ve_test.log_assert(deviceId_3 is not deviceId_2,"Device ids are same")
    ve_test.wait(7)
    ve_test.screens.settings.log_out()
