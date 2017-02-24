__author__ = 'isinitsi'

from tests_framework.ve_tests.tests_conf import set_device_type

FIRST_LAUNCH_TIMEOUT = 10

def set_mock_data_and_begin_test(test, bundle_name, bundle_file):
    test.appium.turn_on_device()
    test.appium.push_data_to_settings(bundle_name, bundle_file)
    test.wait(2)

    test.appium.launch_app()
    test.wait(2)

    test.wait(FIRST_LAUNCH_TIMEOUT)
    test.screens.main_hub.verify_active()

    set_device_type(test)

def set_mock_data_multiple_and_begin_test(test, data_table):
    test.appium.turn_on_device()

    '''TODO: this needs to be done better'''
    for key in data_table:
        test.appium.push_data_to_settings(key, data_table[key])
        test.wait(2)

    test.appium.launch_app()
    test.wait(2)

    test.wait(FIRST_LAUNCH_TIMEOUT)
    test.screens.main_hub.verify_active()

def set_mock_data_open_login(test, bundle_name, bundle_file) :
    test.appium.turn_on_device()
    test.appium.push_data_to_settings(bundle_name, bundle_file)
    test.wait(2)

    test.appium.launch_app()