__author__ = 'srikrive'

from tests_framework.ve_tests.ve_test import VeTestApi

PARENTAL_PIN = '1111'
THRESHOLD = 7
WRONG_PIN = '0110'

def test_parental_control():
    ve_test = VeTestApi("test_parental_control")
    ve_test.begin()

    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')
    ve_test.he_utils.setParentalRatingPin(hhId, PARENTAL_PIN)

    preferences = ve_test.he_utils.getUserprofilePreferences(hhId)
    preferences['parentalRatingThreshold']= THRESHOLD
    ve_test.he_utils.updateUserprofilePreferences(hhId, preferences)
    ve_test.wait(5)

    ve_test.appium.restart_app()
    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123', verify_startup_screen=False)
    ve_test.wait(30)

    ve_test.screens.main_hub.navigate()
    ve_test.screens.settings.navigate()

    elements = ve_test.milestones.getElements()
    parental_control_label = ve_test.milestones.getElement([("title_text", "PARENTAL CONTROL", "==")], elements)
    ve_test.log_assert(parental_control_label, "No button parental control in milestone of current screen")
    ve_test.appium.tap_element(parental_control_label)
    ve_test.wait(3)

    ve_test.screens.pincode.verify_active()
    ve_test.log("entering wrong pin")
    ve_test.screens.pincode.enter_pin(WRONG_PIN)

    mismatch_pin_label = ve_test.milestones.get_dic_value_by_key("DIC_PIN_CODE_INVALID_RETRY")
    elements = ve_test.milestones.getElements()
    mismatch_pin_label = str(mismatch_pin_label).replace("%s", "2")
    mismatch_pin_label = ve_test.milestones.getElement([("title_text", mismatch_pin_label, "==")], elements)
    ve_test.log_assert(mismatch_pin_label, "No label named PIN DOES NOT MATCH")

    ve_test.log("entering correct pin")
    ve_test.screens.pincode.enter_pin(PARENTAL_PIN)
    elements = ve_test.milestones.getElements()

    thresholdDict= ve_test.he_utils.getParentalPolicies(hhId)
    for i in thresholdDict:
        value=str(i['category'])
        if(value == "YOUNG_ADULTS"):
            value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_YOUNG_ADULTS")
        elif (value == "TEENS"):
            value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_TEENS")
        elif (value == "CHILDRENS"):
            value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_CHILDRENS")
        elif (value == "OFF"):
            value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_OFF")

        test_label=ve_test.milestones.getElement([("title_text", value, "==")], elements)
        ve_test.log_assert(test_label, "No button %s control in milestone of current screen"% value )

    # Get selectedThreshold from MileStones
    parentalControlSeekBar = ve_test.milestones.getElement([("name", "parental_control_seek_bar", "==")], elements)
    uiSelectedThreshold=parentalControlSeekBar['selected_threshold']
    ve_test.log_assert(uiSelectedThreshold == THRESHOLD,"Mismatch of Parental Threshold")

    #Tap to New Threshold from UI
    yaTapElement = ve_test.milestones.getElement([("title_text","YA17+", "==")], elements)
    ve_test.log_assert(yaTapElement, "No button YA17+ control in milestone of current screen")
    ve_test.appium.tap_element(yaTapElement)

    ve_test.wait(10)

    #Get From UPM
    preferences = ve_test.he_utils.getUserprofilePreferences(hhId)
    latestThreshold=preferences['parentalRatingThreshold']

    elements = ve_test.milestones.getElements()

    # Get selectedThreshold from MileStones
    parentalControlSeekBar = ve_test.milestones.getElement([("name","parental_control_seek_bar", "==")], elements)
    uiSelectedThreshold = parentalControlSeekBar['selected_threshold']
    ve_test.log_assert(uiSelectedThreshold == latestThreshold, "Mismatch of Parental Threshold")

    ve_test.end()