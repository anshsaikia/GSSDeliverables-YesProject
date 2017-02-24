import pytest
from tests_framework.ve_tests.ve_test import VeTestApi

' Global constants '
PARENTAL_PIN = '0000'
INITIAL_PARENTAL_RATING_THRESHOLD = 30


@pytest.mark.MF2057_modify_parental_control
def test_modify_parental_controls_category():
    ve_test = VeTestApi("test_modify_parental_controls_category")
    ve_test.begin()
    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')
    #set default values for parentalRatingPin; Client uses 18 as the default theshold when not available in UPM
    ve_test.he_utils.setParentalRatingPin(hhId, PARENTAL_PIN)
    ve_test.screens.settings.navigate()

    elements = ve_test.milestones.getElements()
    parental_control_label = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROL").upper()
    parental_control_label = ve_test.milestones.getElement([("title_text", parental_control_label, "==")], elements)
    ve_test.log_assert(parental_control_label, "No parental control milestone in current screen")

    #check that selected_threshold is 30
    parental_control_seek_bar = ve_test.milestones.getElement([("name","parental_control_seek_bar", "==")], elements)
    ve_test.log_assert(parental_control_seek_bar['selected-threshold'] == INITIAL_PARENTAL_RATING_THRESHOLD,
                           "UI is not showing the INITIAL_PARENTAL_RATING_THRESHOLD ")

    lock_button = ve_test.milestones.getElement([("name", "parental_control_lock_unlock_button", "==")], elements)
    ve_test.log_assert(lock_button, "No Lock button in milestone of current screen")

    ve_test.log_assert(ve_test.screens.settings.verify_parental_control_state_locked() == True, "Parental control state is not correct")
    ve_test.appium.tap_element(lock_button)

    ve_test.wait(3)

    pin = ve_test.he_utils.getParentalRatingPin(hhId)
    ve_test.screens.pincode.verify_active()

    #enter correct pin in the custom keypad
    ve_test.log("entering correct pin")
    ve_test.screens.pincode.enter_pin(pin)

    ve_test.wait(5)
    #verify state is UNLOCKED after correct pin entry
    ve_test.log_assert(ve_test.screens.settings.verify_parental_control_state_locked() == False, "Parental control state is not correct")

    # get the CTAP API to check the threshold values to choose from.
    threshold_categories_from_ctap = ve_test.he_utils.getParentalPolicies(hhId)

    #verify categories show up on the UI
    for threshold in threshold_categories_from_ctap:
        value = str(threshold['category'])
        if value == "YOUNG_ADULTS":
            value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_YOUNG_ADULTS")

        elif value == "TEENS":
            value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_TEENS")

        elif value == "CHILDRENS":
            value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_CHILDRENS")
            category_to_choose = value

        elif value == "OFF":
            value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_OFF")

        test_label = ve_test.milestones.getElement([("title_text", value, "==")], elements)
        ve_test.log_assert(test_label, "No button %s control in milestone of current screen" % value)

    #choose a new parentalRating category - for CHILDRENS
    category_label_to_choose = ve_test.milestones.getElement([("title_text", category_to_choose, "==")], elements)
    ve_test.log_assert(category_label_to_choose, "No LABEL in milestone of category")

    ve_test.appium.tap_element(category_label_to_choose)
    ve_test.wait(3)

    elements = ve_test.milestones.getElements()
    description = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_DESCRIPTION_CHILDRENS")
    category_description_label = ve_test.milestones.getElement([("title_text", description.upper(), "==")], elements)
    ve_test.log_assert(category_description_label, "No LABEL in milestone of category")

    # verify state is LOCKED after 30s timeout
    ve_test.wait(30)
    ve_test.log_assert(ve_test.screens.settings.verify_parental_control_state_locked() == True,
                       "Parental control state is not correct")

    #verify UPM value for parentalRatingThreshold is updated
    ve_test.log("verifying if parentalRatingThreshold value was updated in UPM")
    new_parental_threshold = ve_test.he_utils.getParentalRatingThreshold(hhId)

    elements = ve_test.milestones.getElements()
    parental_control_seek_bar = ve_test.milestones.getElement([("name", "parental_control_seek_bar", "==")], elements)
    ve_test.log_assert(parental_control_seek_bar['selected-threshold'] == int(new_parental_threshold),
                           "ParentalRatingThreshold did not update on UPM")

    ve_test.end()
