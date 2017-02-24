import pytest


from tests_framework.ve_tests.ve_test import VeTestApi

def validate_device_info(ve_test):
    #Obtain Screen handle
    screenhandle = ve_test.milestones

    ve_test.log_assert (ve_test.he_utils.houseHolds, "Failed to get a valid household")
    hhId = ve_test.he_utils.houseHolds[0]

    #Retrieve device settings
    deviceSettings = ve_test.he_utils.getDeviceSettings(ve_test,hhId)
    accountID =  deviceSettings['accountId']
    auxHouseholdID =  deviceSettings['auxHouseholdId']
    endDeviceId = deviceSettings['devices'][0]['deviceId']
    hhId = deviceSettings['householdId']
    if auxHouseholdID == "":
        auxHouseholdID = '-'
    if accountID == "":
        accountID = '-'

    #Validate Account ID title
    account_id_text = screenhandle.get_dic_value_by_key('DIC_DEVICE_SETTINGS_ACCOUNT_ID')
    account_id_element = screenhandle.getElement([("title_text",account_id_text, "==")])
    ve_test.log_assert (account_id_element,"Account ID title is not displayed")
    #Check if Account Id value is present in milestone
    element = ve_test.milestones.getElement([("title_text",accountID, "==")])
    ve_test.log_assert (element, "Account ID value is not displayed")

    #Validate Household ID title
    hh_id_text = screenhandle.get_dic_value_by_key('DIC_DEVICE_SETTINGS_HOUSEHOLD')
    hh_id_element = screenhandle.getElement([("title_text",hh_id_text, "==")])
    ve_test.log_assert (hh_id_element, "Household ID title is not displayed")
    #Check if Household ID value is present in milestone
    element = ve_test.milestones.getElement([("title_text",hhId, "==")])
    ve_test.log_assert (element, "Household ID value is not displayed")

    ve_test.screens.settings.scroll(hh_id_element, account_id_element)
    ve_test.wait(2)
    hh_id_element = screenhandle.getElement([("title_text",hh_id_text, "==")])

    #Validate Device ID title
    device_id_text = screenhandle.get_dic_value_by_key('DIC_DEVICE_SETTINGS_DEVICE_ID')
    device_id_element = screenhandle.getElement([("title_text",device_id_text, "==")])
    ve_test.log_assert (device_id_element,"Device ID title is not displayed")
    #Check if Device ID value is present in milestone
    element = ve_test.milestones.getElement([("title_text",endDeviceId.lower(), "==")])
    ve_test.log_assert (element, "Device ID value is not displayed")

    ve_test.screens.settings.scroll(device_id_element, hh_id_element)
    ve_test.wait(2)

    #Validate Aux Household ID title
    aux_hh_text = screenhandle.get_dic_value_by_key('DIC_DEVICE_SETTINGS_AUX_HOUSEHOLD')
    aux_hh_element = screenhandle.getElement([("title_text",aux_hh_text, "==")])
    ve_test.log_assert (aux_hh_element, "Aux Household ID title is not displayed")
    #check if Aux Household id value is present in milestone
    element = ve_test.milestones.getElement([("title_text",auxHouseholdID, "==")])
    ve_test.log_assert (element, "Aux HH ID value is not displayed")


@pytest.mark.MF1252_client_logging
def test_device_info():
    ve_test = VeTestApi("test_device_info")
    ve_test.begin()
    # Navigate to Settings Page
    ve_test.screens.settings.navigate()
    # Validate Device Info Settings
    validate_device_info(ve_test)
    ve_test.end()


