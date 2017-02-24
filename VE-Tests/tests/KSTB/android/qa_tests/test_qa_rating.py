__author__ = 'Oceane Team'

import pytest
import logging

from tests_framework.ve_tests.ve_test import VeTestApi
from tests.KSTB.android.e2e_tests.test_light_sanity import display_pretty_current_screen
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

@pytest.mark.QA
@pytest.mark.QA_rating
def test_qa_rating_set_parental_and_unlock_program():
    """
    TEST: check user ability to unlock protected content after changing PIN code and threshold values from settings menu

     init step : init Parental Limits on UPM & go to PIN code setting screen
        Action
        - set PIN code to 1111 and ThresHold to OFF on UPM
        - enter in PIN code setting menu
        Checkup
        - check PIN code to 1111 and ThresHold to OFF on UPM
        - check PIN code screen is displayed

     1st step : modify PIN Code from setting menu
        Action
        - enter current PIN code (1111)
        - update current PIN code with new PIN code (1234)
        Checkup
        - check PIN code value on UPM matches with changed value from setting

     2nd step : modify parental Threshold from setting menu
        Action
        - enter in Parental threshold screen
        - update current threshold from OFF to 7
        Checkup
        - check threshold value on UPM matches with changed value from setting

     3rd step : select a channel with rated program and unlock current event
        Action
        - go back to fullscreen from PC screen
        - validate "locked program" popup
        - enter valid PIN code to unlock program
        Checkup
        - check current program is locked (no audio/video)
        - check audio/video after PIN code entry

     4th step : modify again PIN Code from setting menu
        Action
        - enter current PIN code (1234)
        - update current PIN code with new PIN code (1233)
        Checkup
        - check PIN code value on UPM matches with changed value from setting

     5th step : check PIN code grace period is active by going back to live TV and by zapping on another channel having rated program
        Action
        - back to fullscreen
        - zapp on next channel (shall be rated program)
        Checkup
        - check no PIN code requested
        - video/audio playback

     6th step : modify again parental Threshold from setting menu to reset PIN code grace period
        Action
        - enter in Parental threshold screen
        - update current threshold from 7 to OFF
        - update current threshold from OFF to 7
        Checkup
        - check threshold value on UPM matches with changed value from setting

     7th step : go back to live TV channel with rated program ; PIN code shall be requested
        Action
        - go back to fullscreen
        Checkup
        - check current program is locked
        - check no audio/video

     8th step : enter PIN code and check live video/audio playback
        Action
        - validate "locked program" popup
        - enter valid PIN code to unlock program
        Checkup
        - check audio/video

     9th step : enter PIN code and check live video/audio playback
        Action
        - wait end of grace periode (10 minutes)
        - then zap on rated program
        Checkup
        - check pincode is request
        - no audio/video
    """

    logging.info("##### BEGIN test_qa_rating_set_parental_and_unlock_program #####")

    ############
    # init test data
    test_qa_rating = VeTestApi("test_qa_rating_set_parental_and_unlock_program")
    #test_qa_rating = KSTBBuildingBlocks(ve_test=ve_test)
    test_qa_rating.begin(screen=test_qa_rating.screens.fullscreen)

    INITIAL_PIN = "1111"
    INITIAL_PIN_SEQUENCE = ["KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_CENTER"]
    NEW_PIN = "1234"
    NEW_PIN_SEQUENCE = ["KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_RIGHT", "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_RIGHT",
                        "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_RIGHT", "KEYCODE_DPAD_CENTER"]
    YA_NEW_PIN = "1233"
    YA_NEW_PIN_SEQUENCE = ["KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_RIGHT", "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_RIGHT",
                        "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_CENTER"]
    INITIAL_THRESHOLD = CONSTANTS.MAX_THRESHOLD
    INITIAL_THRESHOLD_UPM = CONSTANTS.MAX_THRESHOLD_UPM
    NEW_THRESHOLD = CONSTANTS.MIN_THRESHOLD
    NEW_THRESHOLD_UPM = CONSTANTS.MIN_THRESHOLD_UPM
    THRESHOLD_ITEM_COUNTER = 4

    hhid = test_qa_rating.he_utils.get_default_credentials()[0]
    logging.info("current hhid is : " + hhid)

    ############

    """ init step : init Parental Limits on UPM
        Action
        - set PIN code to 1111 and ThresHold to OFF on UPM
        Checkup
        - check PIN code to 1111 and ThresHold to OFF on UPM
    """
    # init PIN code to 1111
    logging.info("set PIN code to " + INITIAL_PIN)
    test_qa_rating.he_utils.setParentalPin(hhid, INITIAL_PIN)

    # init parental ThresHold to OFF
    logging.info("set parental ThresHold to " + INITIAL_THRESHOLD)
    test_qa_rating.he_utils.setParentalRatingThreshold(hhid, INITIAL_THRESHOLD_UPM)

    # control PIN value on UPM
    currentParentalpincode = str(test_qa_rating.he_utils.getParentalpincode())
    errorMessage = "UPM PIN code init with value " + INITIAL_PIN + " failed ! current PIN is : " + currentParentalpincode
    test_qa_rating.log_assert(currentParentalpincode == INITIAL_PIN, errorMessage)
    logging.info("controlled PIN code on UPM " + currentParentalpincode)

    # control THRESHOLD value on UPM
    currentParentalThreshold = str(test_qa_rating.he_utils.getHouseHoldPrentalThreshold())
    errorMessage = "UPM THRESHOLD init with value " + INITIAL_THRESHOLD_UPM + " failed ! current THRESHOLD is : " + currentParentalThreshold
    test_qa_rating.log_assert(currentParentalThreshold == INITIAL_THRESHOLD_UPM, errorMessage)
    logging.info("controlled THRESHOLD on UPM " + currentParentalThreshold)

    ############
    ''' init step : go to PIN code setting screen
        Action
        - enter in PIN code setting menu
        Checkup
        - check PIN code screen is displayed
    '''
    # enter in setting menu to change PIN code
    logging.info("navigate_to_settings_screen")
    status = test_qa_rating.screens.main_hub.navigate()
    errorMessage = "RATING/SETTINGS : Navigation to Hub failed, current screen = " + str(display_pretty_current_screen(test_qa_rating))
    test_qa_rating.log_assert(status, errorMessage)

    logging.info("navigate_to_parental_control_screen")
    status = test_qa_rating.screens.main_hub.navigate_to_settings_sub_menu("PARENTAL")
    
    errorMessage = "RATING/SETTINGS : Navigation from Hub to Settings, current screen = " + str(display_pretty_current_screen(test_qa_rating))
    test_qa_rating.log_assert(status, errorMessage)

    ############
    ''' 1st step : modify PIN Code from setting menu
        Action
        - enter current PIN code (1111)
        - update current PIN code with new PIN code (1234)
        Checkup
        - check PIN code value on UPM matches with changed value from setting
    '''
    # modify PIN Code
    logging.info("select modify PIN Code in setting menu")
    test_qa_rating.validate_focused_item()

    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:SETTINGS : check PIN code entry screen is displayed failed, current text is " + textToVerify
    test_qa_rating.log_assert("current Parental PINCODE" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)
    logging.info("enter current PIN Code " + INITIAL_PIN)
    test_qa_rating.screens.pincode.enter_pincode( INITIAL_PIN_SEQUENCE)

    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:SETTINGS : check new PIN code entry screen is displayed failed, current text is " + textToVerify
    test_qa_rating.log_assert("enter your new PINCODE" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)
    logging.info("enter new PIN Code " + NEW_PIN)
    test_qa_rating.screens.pincode.enter_pincode( NEW_PIN_SEQUENCE)

    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:SETTINGS : check new PIN code entry screen is displayed failed, current text is " + textToVerify
    test_qa_rating.log_assert("confirm your new PINCODE" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)
    logging.info("confirm new PIN Code " + NEW_PIN)
    test_qa_rating.screens.pincode.enter_pincode( NEW_PIN_SEQUENCE)

    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:SETTINGS : check PIN code change successs is displayed failed, current text is " + textToVerify.replace("\n","")
    test_qa_rating.log_assert("successfully" in textToVerify, errorMessage)
    logging.info("PINCODE update message " + textToVerify.replace("\n",""))

    # check new PIN code value on UPM
    currentParentalpincode = str(test_qa_rating.he_utils.getParentalpincode())
    errorMessage = "RATING:SETTINGS : UPM PIN code update with value " + NEW_PIN + " failed ! current PIN is : " + currentParentalpincode
    test_qa_rating.log_assert(currentParentalpincode == NEW_PIN, errorMessage)
    logging.info("UPM PIN code updated with : " + currentParentalpincode)

    ############
    ''' 2nd step : modify parental Threshold from setting menu
        Action
        - enter in Parental threshold screen
        - update current threshold from OFF to 7
        Checkup
        - check threshold value on UPM matches with changed value from setting
    '''
    # modify parental ThresHold
    test_qa_rating.go_to_previous_screen(1)
    test_qa_rating.move_towards('up', 1, False)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_item"))
    errorMessage = "RATING:SETTINGS : check PARENTAL CONTROL screen is displayed failed, current focused_item is " + textToVerify
    test_qa_rating.log_assert("PARENTAL CONTROL" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)

    test_qa_rating.validate_focused_item()
    test_qa_rating.screens.pincode.enter_pincode( NEW_PIN_SEQUENCE)
    test_qa_rating.validate_focused_item()
    currentFocusedItem = str(test_qa_rating.screens.action_menu.get_focused_item())
    errorMessage = "RATING:SETTINGS : focus is not on MODIFY PARENTAL THRESHOLD item !  current focused item is : " + currentFocusedItem
    test_qa_rating.log_assert(currentFocusedItem == "MODIFY PARENTAL THRESHOLD", errorMessage)

    LOCALWORKER = THRESHOLD_ITEM_COUNTER
    while LOCALWORKER > 0:
        elements = test_qa_rating.milestones.getElements()
        focusIsOn = test_qa_rating.milestones.get_value_by_key(elements,"focused_asset")
        if focusIsOn == NEW_THRESHOLD:
            logging.info("focus is on " + NEW_THRESHOLD)
            break
            LOCALWORKER -= 1
        test_qa_rating.move_towards('right', 1, False)

    errorMessage = "RATING:SETTINGS : can't focus on THRESHOLD " + NEW_THRESHOLD
    test_qa_rating.log_assert(focusIsOn == NEW_THRESHOLD, errorMessage)

    # control selected THRESHOLD on UPM
    test_qa_rating.validate_focused_item()
    # check THRESHOLD value
    currentParentalThreshold = str(test_qa_rating.he_utils.getHouseHoldPrentalThreshold())
    errorMessage = "RATING/SETTINGS : UPM THRESHOLD update with value " + NEW_THRESHOLD_UPM + " failed ! current THRESHOLD is : " + currentParentalThreshold
    test_qa_rating.log_assert(currentParentalThreshold == NEW_THRESHOLD_UPM, errorMessage)
    logging.info("UPM THRESHOLD updated with : " + currentParentalThreshold)

    ############
    ''' 3rd step : select a channel with rated program and unlock current event
        Action
        - go back to fullscreen from PC screen
        - validate "locked program" popup
        - enter valid PIN code to unlock program
        Checkup
        - check current program is locked (no audio/video)
        - check audio/video after PIN code entry
    '''
    # go back to fullscreen
    logging.info("navigate back to fullscreen from " + display_pretty_current_screen(test_qa_rating))
    test_qa_rating.go_to_previous_screen(CONSTANTS.GENERIC_WAIT)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_item"))
    errorMessage = "RATING:SETTINGS : check MODIFY THRESHOLD screen is displayed failed, current focused_item is " + textToVerify
    test_qa_rating.log_assert("PIN MANAGEMENT" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)

    test_qa_rating.go_to_previous_screen(CONSTANTS.GENERIC_WAIT)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_item"))
    errorMessage = "RATING:SETTINGS : check PIN MANAGEMENT screen is displayed failed, current focused_item is " + textToVerify
    test_qa_rating.log_assert("SETTINGS" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)

    ##### must be improved: Can't check here if current screen is fullscreen or locked screen
    test_qa_rating.go_to_previous_screen(1)
    # status = test_qa_rating.is_infolayer_shown()
    # if not status:
    #    test_parental_control.go_to_previous_screen(1)
    #######

    # video/audio well Mute ?
    playback_status = test_qa_rating.milestones.getPlaybackStatus()
    logging.info(
        "video locked=" + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
    errorMessage = "RATING:LIVE-LOCK : video and audio not locked."
    test_qa_rating.log_assert(playback_status["hiddenVideo"] and playback_status["muted"], errorMessage)
    # current PROGRAM LOCKED ?
    # to be improved ; actually, no easy rules to guaranty current program is well locked
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_event_title"))
    errorMessage = "RATING:LIVE-LOCK : current event is not LOCKED, current focused_item is " + textToVerify
    test_qa_rating.log_assert("LOCKED PROGRAM" in textToVerify, errorMessage)
    logging.info("current focused item is " + textToVerify)

    # valid current LOCKED PROGRAM and enter PINCODE
    test_qa_rating.validate_focused_item(1)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:LIVE-LOCK : PINCODE not displayed on LOCKED event, current focused_item is " + textToVerify
    test_qa_rating.log_assert("enter your PINCODE" in textToVerify, errorMessage)
    logging.info("current focused item is " + textToVerify)

    logging.info("typing PINCODE " + NEW_PIN)
    test_qa_rating.screens.pincode.enter_pincode( NEW_PIN_SEQUENCE)

    # video/audio unMute ?
    playback_status = test_qa_rating.milestones.getPlaybackStatus()
    logging.info("video locked=" + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
    errorMessage = "RATING:LIVE-UNLOCK : video and audio still locked."
    test_qa_rating.log_assert(not playback_status["hiddenVideo"] and not playback_status["muted"], errorMessage)

    ############
    ''' 4th step : modify again PIN Code from setting menu
        Action
        - enter current PIN code (1234)
        - update current PIN code with new PIN code (1233)
        Checkup
        - check PIN code value on UPM matches with changed value from setting
    '''

    # enter in setting menu to change PIN code
    logging.info("navigate_to_settings_screen")
    status = test_qa_rating.screens.main_hub.navigate()
    errorMessage = "RATING:SETTINGS : Navigation to Hub failed, current screen = " + str(display_pretty_current_screen(test_qa_rating))
    test_qa_rating.log_assert(status, errorMessage)

    logging.info("navigate_to_parental_control_screen")
    status = test_qa_rating.screens.main_hub.navigate_to_settings_sub_menu("PARENTAL")
    errorMessage = "RATING:SETTINGS : Navigation from Hub to Settings failed, current screen = " + str(display_pretty_current_screen(test_qa_rating))
    test_qa_rating.log_assert(status, errorMessage)

    # go to PIN code menu
    logging.info("select modify PIN Code in setting menu")
    test_qa_rating.validate_focused_item()
    test_qa_rating.wait(CONSTANTS.GENERIC_WAIT)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:SETTINGS : check PIN code entry screen is displayed failed, current text is " + textToVerify
    test_qa_rating.log_assert("current Parental PINCODE" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)
    logging.info("enter current PIN Code " + NEW_PIN)
    test_qa_rating.screens.pincode.enter_pincode( NEW_PIN_SEQUENCE)
    test_qa_rating.wait(CONSTANTS.GENERIC_WAIT)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:SETTINGS : check new PIN code entry screen is displayed failed, current text is " + textToVerify
    test_qa_rating.log_assert("enter your new PINCODE" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)
    logging.info("enter new PIN Code " + YA_NEW_PIN)
    test_qa_rating.screens.pincode.enter_pincode( YA_NEW_PIN_SEQUENCE)
    test_qa_rating.wait(CONSTANTS.GENERIC_WAIT)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:SETTINGS : check new PIN code entry screen is displayed failed, current text is " + textToVerify
    test_qa_rating.log_assert("confirm your new PINCODE" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)
    logging.info("confirm new PIN Code " + YA_NEW_PIN)
    test_qa_rating.screens.pincode.enter_pincode( YA_NEW_PIN_SEQUENCE)
    test_qa_rating.wait(CONSTANTS.GENERIC_WAIT)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:SETTINGS : check PIN code change successs is displayed failed, current text is " + textToVerify.replace("\n",
                                                                                                                 "")
    test_qa_rating.log_assert("successfully" in textToVerify, errorMessage)
    logging.info("PINCODE update message " + textToVerify.replace("\n", ""))

    # check new PIN code value on UPM
    currentParentalpincode = str(test_qa_rating.he_utils.getParentalpincode())
    errorMessage = "RATING:SETTINGS : UPM PIN code update with value " + YA_NEW_PIN + " failed ! current PIN is : " + currentParentalpincode
    test_qa_rating.log_assert(currentParentalpincode == YA_NEW_PIN, errorMessage)
    logging.info("UPM PIN code updated with : " + currentParentalpincode)

    ############
    ''' 5th step : check PIN code grace period is active by going back to live TV and by zapping on another channel having rated program
        Action
        - back to fullscreen
        - zapp on next channel (shall be rated program)
        Checkup
        - check no PIN code requested
        - video/audio playback
    '''
    # go back to fullscreen
    logging.info("navigate back to fullscreen from " + display_pretty_current_screen(test_qa_rating))
    test_qa_rating.go_to_previous_screen(1)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_item"))
    errorMessage = "RATING:SETTINGS : check MODIFY THRESHOLD screen is displayed failed, current focused_item is " + textToVerify
    test_qa_rating.log_assert("PIN MANAGEMENT" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)

    test_qa_rating.go_to_previous_screen(2)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_item"))
    errorMessage = "RATING:SETTINGS : check PIN MANAGEMENT screen is displayed failed, current focused_item is " + textToVerify
    test_qa_rating.log_assert("SETTINGS" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)

    ##### must be improved: Can't check here if current screen is fullscreen or locked screen
    test_qa_rating.go_to_previous_screen(1)
    #######

    # video/audio well unlocked ?
    playback_status = test_qa_rating.milestones.getPlaybackStatus()
    logging.info(
        "video locked=" + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
    errorMessage = "RATING:LIVE-UNLOCK/GRACE-PERIOD : video and audio still locked."
    test_qa_rating.log_assert(not playback_status["hiddenVideo"] and not playback_status["muted"], errorMessage)

    # zap to next channel
    test_qa_rating.move_towards('down', 5)

    # video/audio well unlocked ?
    playback_status = test_qa_rating.milestones.getPlaybackStatus()
    logging.info(
        "video locked=" + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
    errorMessage = "RATING:GRACE-PERIOD : video and audio still locked."
    test_qa_rating.log_assert(not playback_status["hiddenVideo"] and not playback_status["muted"], errorMessage)


    ############
    ''' 6th step : modify again parental Threshold from setting menu to reset PIN code grace period
        Action
        - enter in Parental threshold screen
        - update current threshold from 7 to OFF
        - update current threshold from OFF to 7
        Checkup
        - check threshold value on UPM matches with changed value from setting
    '''
    # enter in setting menu to change parental ThresHold
    logging.info("navigate_to_settings_screen")
    status = test_qa_rating.screens.main_hub.navigate()
    errorMessage = "RATING:SETTINGS : Navigation to Hub failed, current screen = " + str(display_pretty_current_screen(test_qa_rating))
    test_qa_rating.log_assert(status, errorMessage)

    logging.info("navigate_to_parental_control_screen")
    status = test_qa_rating.screens.main_hub.navigate_to_settings_sub_menu("PARENTAL")
    errorMessage = "RATING:SETTINGS : Navigation from Hub to Settings failed, current screen = " + str(display_pretty_current_screen(test_qa_rating))
    test_qa_rating.log_assert(status, errorMessage)

    # modify parental ThresHold
    test_qa_rating.move_towards('up', 1, False)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_item"))
    errorMessage = "RATING:SETTINGS : check PARENTAL CONTROL screen is displayed failed, current focused_item is " + textToVerify
    test_qa_rating.log_assert("PARENTAL CONTROL" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)

    test_qa_rating.validate_focused_item()
    test_qa_rating.screens.pincode.enter_pincode( YA_NEW_PIN_SEQUENCE)
    test_qa_rating.validate_focused_item()
    currentFocusedItem = str(test_qa_rating.screens.action_menu.get_focused_item())
    errorMessage = "RATING:SETTINGS : focus is not on MODIFY PARENTAL THRESHOLD item !  current focused item is : " + currentFocusedItem
    test_qa_rating.log_assert(currentFocusedItem == "MODIFY PARENTAL THRESHOLD", errorMessage)

    # select OFF
    LOCALWORKER = THRESHOLD_ITEM_COUNTER
    while LOCALWORKER > 0:
        elements = test_qa_rating.milestones.getElements()
        focusIsOn = test_qa_rating.milestones.get_value_by_key(elements,"focused_asset")
        if focusIsOn == INITIAL_THRESHOLD:
            logging.info("focus is on " + INITIAL_THRESHOLD)
            break
            LOCALWORKER -= 1
        test_qa_rating.move_towards('right', 1, False)

    test_qa_rating.wait(CONSTANTS.GENERIC_WAIT)
    LOCALWORKER = THRESHOLD_ITEM_COUNTER
    while LOCALWORKER > 0:
        elements = test_qa_rating.milestones.getElements()
        focusIsOn = test_qa_rating.milestones.get_value_by_key(elements,"focused_asset")
        if focusIsOn == NEW_THRESHOLD:
            logging.info("focus is on " + NEW_THRESHOLD)
            break
            LOCALWORKER -= 1
        test_qa_rating.move_towards('right', 1, False)

    errorMessage = "RATING:SETTINGS : can't focus on THRESHOLD " + NEW_THRESHOLD
    test_qa_rating.log_assert(focusIsOn == NEW_THRESHOLD, errorMessage)

    # control selected THRESHOLD on UPM
    test_qa_rating.validate_focused_item()
    # check THRESHOLD value
    currentParentalThreshold = str(test_qa_rating.he_utils.getHouseHoldPrentalThreshold())
    errorMessage = "RATING:SETTINGS : UPM THRESHOLD update with value " + NEW_THRESHOLD_UPM + " failed ! current THRESHOLD is : " + currentParentalThreshold
    test_qa_rating.log_assert(currentParentalThreshold == NEW_THRESHOLD_UPM, errorMessage)
    logging.info("UPM THRESHOLD updated with : " + currentParentalThreshold)


    ############
    ''' 7th step : go back to live TV channel with rated program ; PIN code shall be requested
        Action
        - go back to fullscreen
        Checkup
        - check current program is locked
        - check no audio/video
    '''
    # go back to fullscreen
    logging.info("navigate back to fullscreen from " + display_pretty_current_screen(test_qa_rating))
    test_qa_rating.go_to_previous_screen(1)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_item"))
    errorMessage = "RATING:SETTINGS : check MODIFY THRESHOLD screen is displayed failed, current focused_item is " + textToVerify
    test_qa_rating.log_assert("PIN MANAGEMENT" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)

    test_qa_rating.go_to_previous_screen(2)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_item"))
    errorMessage = "RATING:SETTINGS : check PIN MANAGEMENT screen is displayed failed, current focused_item is " + textToVerify
    test_qa_rating.log_assert("SETTINGS" in textToVerify, errorMessage)
    logging.info("current Screen is " + textToVerify)

    ##### must be improved: Can't check here if current screen is fullscreen or locked screen
    test_qa_rating.go_to_previous_screen(1)
    # status = test_qa_rating.is_infolayer_shown()
    # if not status:
    #    test_parental_control.go_to_previous_screen(1)
    #######

    # video/audio Mute ?
    playback_status = test_qa_rating.milestones.getPlaybackStatus()
    logging.info(
        "video locked=" + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
    errorMessage = "RATING:LIVE-LOCK/GRACE-PERIOD : video and audio not locked."
    test_qa_rating.log_assert(playback_status["hiddenVideo"] and playback_status["muted"], errorMessage)
    # current PROGRAM LOCKED ?
    # to be improved ; actually, no easy rules to guaranty current program is well locked
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "focused_event_title"))
    errorMessage = "RATING:LIVE-LOCK/GRACE-PERIOD : current event is not LOCKED, current focused_item is " + textToVerify
    test_qa_rating.log_assert("LOCKED PROGRAM" in textToVerify, errorMessage)
    logging.info("current 1efocused item is " + textToVerify)

    ############
    ''' 8th step : enter PIN code and check live video/audio playback
        Action
        - validate "locked program" popup
        - enter valid PIN code to unlock program
        Checkup
        - check audio/video
    '''
    # valid current LOCKED PROGRAM and enter PINCODE
    test_qa_rating.validate_focused_item(1)
    elements = test_qa_rating.milestones.getElements()
    textToVerify = str(test_qa_rating.milestones.get_value_by_key(elements, "pincode_message"))
    errorMessage = "RATING:LIVE-LOCK : PINCODE not displayed on LOCKED event, current focused_item is " + textToVerify
    test_qa_rating.log_assert("enter your PINCODE" in textToVerify, errorMessage)
    logging.info("current focused item is " + textToVerify)

    logging.info("typing PINCODE " + YA_NEW_PIN)
    test_qa_rating.screens.pincode.enter_pincode(YA_NEW_PIN_SEQUENCE)

    # video/audio Mute ?
    playback_status = test_qa_rating.milestones.getPlaybackStatus()
    logging.info(
        "video locked=" + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
    errorMessage = "RATING:LIVE-UNLOCK : video and audio still locked."
    test_qa_rating.log_assert(not playback_status["hiddenVideo"] and not playback_status["muted"], errorMessage)

    ############
    ''' 9th step : enter PIN code and check live video/audio playback
        Action
        - wait end of grace periode (10 minutes)
        - then zap on rated program
        Checkup
        - check pincode is request
        - no audio/video
    '''
    # wait 10 minutes
    test_qa_rating.wait(CONSTANTS.TEN_MINUTES_WAIT)

    # zap to next channel
    test_qa_rating.move_towards('down', 5)
    # video/audio well locked ?
    playback_status = test_qa_rating.milestones.getPlaybackStatus()
    logging.info(
        "video locked=" + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
    errorMessage = "RATING:LIVE-UNLOCK/GRACE-PERIOD : video and audio still unlocked."
    test_qa_rating.log_assert(playback_status["hiddenVideo"] and playback_status["muted"], errorMessage)

    logging.info("##### BEGIN test_qa_rating_set_parental_and_unlock_program #####")

    test_qa_rating.end()
