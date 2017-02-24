import pytest
from tests_framework.ve_tests.ve_test import VeTestApi

PARENTAL_PIN = '0000'
INCORRECT_FORMAT_PIN = '2222'
NEW_PIN = '5432'
INCORRECT_PIN = '4231'
TIMEOUT = 3


@pytest.mark.MF1891_Modify_pin
def test_modify_pincode():
    ve_test = VeTestApi("test_modify_pin")
    ve_test.begin()
    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')
    ve_test.he_utils.setParentalRatingPin(hhId, PARENTAL_PIN)
    pin = ve_test.he_utils.getParentalRatingPin(hhId)
    ve_test.log_assert(PARENTAL_PIN == pin, "Pin did not set correctly")

    ve_test.wait(5)
    ve_test.screens.settings.navigate()

    elements = ve_test.milestones.getElements()
    modify_pincode_label = ve_test.milestones.getElement([("title_text", "CHANGE PIN CODE", "==")], elements)
    ve_test.log_assert(modify_pincode_label, "No button to modify pin in milestone of current screen")
    ve_test.appium.tap_element(modify_pincode_label)
    ve_test.screens.pincode.verify_active()

    current_pincode_label = ve_test.milestones.get_dic_value_by_key("DIC_PIN_CODE_ENTER_CURRENT").upper()
    elements = ve_test.milestones.getElements()

    current_pincode_label = ve_test.milestones.getElement([("title_text", current_pincode_label, "==")], elements)
    ve_test.log_assert(current_pincode_label, "No LABEL in milestone of current pin")

    ve_test.log("entering correct pin")
    ve_test.screens.pincode.enter_pin(PARENTAL_PIN)
    ve_test.screens.pincode.verify_active()
    new_pincode_label = ve_test.milestones.get_dic_value_by_key("DIC_PIN_CODE_ENTER_NEW").upper()
    elements = ve_test.milestones.getElements()

    new_pincode_label = ve_test.milestones.getElement([("title_text", new_pincode_label, "==")], elements)
    ve_test.log_assert(new_pincode_label, "No LABEL in milestone of current pin")

    ve_test.log("entering incorrect format pin")
    ve_test.screens.pincode.enter_pin(INCORRECT_FORMAT_PIN)
    ve_test.screens.pincode.verify_active()
    ve_test.wait(10)

    #verifying the error message for incorrect format

    incorrect_format_label = ve_test.milestones.get_dic_value_by_key("DIC_PIN_CODE_INVALID_FORMAT")

    elements = ve_test.milestones.getElements()
    incorrect_format_label = str(incorrect_format_label).replace("%s", "2").upper()
    incorrect_format_label = ve_test.milestones.getElement([("title_text", incorrect_format_label, "==")], elements)
    ve_test.log_assert(incorrect_format_label, "No label named incorrect format")

    ve_test.log("entering correct format pin")
    ve_test.screens.pincode.enter_pin(NEW_PIN)
    ve_test.screens.pincode.verify_active()
    confirm_pin_label = ve_test.milestones.get_dic_value_by_key("DIC_PIN_CODE_CONFIRM_NEW").upper()
    elements = ve_test.milestones.getElements()
    confirm_pin_label = ve_test.milestones.getElement([("title_text", confirm_pin_label, "==")], elements)
    ve_test.log_assert(confirm_pin_label, "No label named confirm pin")

    #Entering mismatched pin
    ve_test.log("entering mismatched pin")
    ve_test.screens.pincode.enter_pin(INCORRECT_PIN)

    ve_test.screens.pincode.verify_active()
    mismatch_pin_label = ve_test.milestones.get_dic_value_by_key("DIC_PIN_CODE_MISMATCH")
    elements = ve_test.milestones.getElements()
    mismatch_pin_label = str(mismatch_pin_label).replace("%s", "2").upper()
    mismatch_pin_label = ve_test.milestones.getElement([("title_text", mismatch_pin_label, "==")], elements)
    ve_test.log_assert(mismatch_pin_label, "No label named PIN DOES NOT MATCH")

    #Entering correctly matched pin
    ve_test.log("entering correct new pin")
    ve_test.screens.pincode.enter_pin(NEW_PIN)
    ve_test.screens.settings.verify_active()

    #verify the new pin set in upm
    ve_test.log("Verify whether the new pin is correctly set in upm")
    pin = ve_test.he_utils.getParentalRatingPin(hhId)
    ve_test.log_assert(NEW_PIN == pin , "Pin did not set correctly")
    ve_test.end()
