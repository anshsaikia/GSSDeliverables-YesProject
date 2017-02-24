__author__ = 'baradel'

import pytest
import logging
from collections import Iterable
import json
from StringIO import StringIO

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.milestones.milestones_kpi_request_parser import KpiRequestParserAPI
from tests_framework.milestones.milestones_kpi_client import CC_TRACKS

from tests.KSTB.android.e2e_tests.lib import verify_streaming_playing, verify_streaming_paused
from tests_framework.ve_tests.assert_mgr import AssertMgr
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.he_utils.he_utils import HeUtilsPreloadTypes

# CONSTANTS
###########
TIME_ETHERNET_ZAPPING = 10
TIME_WIFI_ZAPPING = 15
TIME_INTER_SCREEN = 5

''' For Action Menu - Action List test '''
list_live_current = ['SUMMARY', 'AUDIO', 'SUBTITLES', 'RECORD', 'RELATED']
list_live_otherchannel = ['SUMMARY', 'PLAY', 'RECORD', 'RELATED']
list_live_future = ['SUMMARY', 'RECORD', 'RELATED']

# Classic channel
CHANNEL_WITH_VIDEO_A = 4


def internal_boot_with_drm(ve_test):
    check = ve_test.assertmgr.addCheckPointLight
    ve_test.begin(preload={HeUtilsPreloadTypes.abr.value}, screen=ve_test.screens.fullscreen),
    check(ve_test.milestones.get_current_screen() == "fullscreen",
          "After the boot, we should be on fullscreen (current= %s)" % (str(ve_test.milestones.get_current_screen())))



def check_notification(ve_test, elements):
    screen = ve_test.milestones.get_value_by_key(elements, "screen_name")
    if screen == "notification":
        return True
    else:
        return False


def internal_zapping_video(ve_test, zapp_time):
    ve_test.assertmgr.setup("test_zapping_video")
    check = ve_test.assertmgr.addCheckPointLight

    ve_test.screens.fullscreen.navigate()
    # Wait a zapping time in order to be sure that the previous zapping has finished
    ve_test.wait(zapp_time)
    parserApiBeforeZapping = KpiRequestParserAPI(ve_test.milestones.getLiveKpiMeasurement())

    urlBeforeZapping = ve_test.screens.playback.retrieve_session_playback_url()
    check(urlBeforeZapping is not False,
           "Failure to retrieve a valid playbackUrl: {0}\n".format(ve_test.milestones.getPlaybackStatus()))

    for i in range(1, 6):
        playback_status = ve_test.milestones.getPlaybackStatus()
        if 'playbackState' in playback_status and playback_status["playbackState"] != "PLAYING":
            ve_test.wait(10)
            delay = zapp_time + (i*10)
            check((ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
                    "[Delay=%d] The video before the 1st zapping is not playing (url = %s - current screen=%s)" %(delay, urlBeforeZapping, ve_test.milestones.get_current_screen()))

    check((ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
            "The video before the 1st zapping is not playing (url = %s - current screen=%s)" %(urlBeforeZapping, ve_test.milestones.get_current_screen()))
    check((parserApiBeforeZapping.getFailedPlaybackNb() == 0),
            "A failed playback occurs before the 1st zapping")

    elements = ve_test.milestones.getElements()
    check(check_notification(ve_test, elements) == False,
            "A notification is shown with msg_error=%s, msg_text=%s" %(str(ve_test.milestones.get_value_by_key(elements, "msg_error")), str(ve_test.milestones.get_value_by_key(elements, "msg_text"))))

    ve_test.screens.playback.zap_to_next_channel(zapp_time)
    parserApiAfterOneZapping = KpiRequestParserAPI(ve_test.milestones.getLiveKpiMeasurement())
    number_profile_1 = parserApiAfterOneZapping.getProfilesIds().__len__()

    check(ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING",
          "The video is not playing")
    check(parserApiAfterOneZapping.getFailedPlaybackNb() == 0,
          "A zapping has failed")
    check(parserApiAfterOneZapping.getSuccessPlaybackNb() == (parserApiBeforeZapping.getSuccessPlaybackNb() + 1),
          "A zapping has failed")
    check(parserApiAfterOneZapping.getMaxPlaybackStartSequenceDuration() < (zapp_time * 1000),
          "A zapping took more than " + str(zapp_time) + " s")
    ve_test.screens.playback.zap_to_previous_channel(zapp_time)

    new_url = ve_test.screens.playback.retrieve_session_playback_url()
    check(new_url is not False,
          "Failure to retrieve a valid playbackUrl: {0}\n".format(ve_test.milestones.getPlaybackStatus()))

    check(urlBeforeZapping == new_url,
          "The url is not the expected one.\nBefore: {0}\n After:  {1}".format(urlBeforeZapping, new_url))

TIME_VOD_STARTING = 10  # s
TIME_AFTER_PLAY_PAUSE = 5  # s
TIME_PLAYING_CHECK_TWO_POSITIONS = 5  # s
TIME_VOD_STOPPING = 10  # s


def internal_test_parental_control(ve_test):

    ve_test.screens.fullscreen.navigate()

    ############
    # init
    INITIAL_PIN = "1111"
    INITIAL_PIN_SEQUENCE = ["KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_CENTER"]
    NEW_PIN = "1234"
    NEW_PIN_SEQUENCE = ["KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_RIGHT", "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_RIGHT", "KEYCODE_DPAD_CENTER", "KEYCODE_DPAD_RIGHT", "KEYCODE_DPAD_CENTER"]
    INITIAL_THRESHOLD = "30"
    NEW_THRESHOLD = "C7+"
    NEW_THRESHOLD_UPM = "7"
    THRESHOLD_ITEM_COUNTER = 4

    hhid = ve_test.he_utils.get_default_credentials()[0]
    logging.info("current hhid is : " + hhid)

    ############
    ''' First step : init Parental Limits on UPM
        Action
        - set PIN code to 1111 and ThresHold to OFF on UPM
        Checkup
        - check PIN code to 1111 and ThresHold to OFF on UPM
    '''

    # init PIN code to 1111
    logging.info("set PIN code to " + INITIAL_PIN)
    ve_test.he_utils.setParentalPin(hhid, INITIAL_PIN)

    # init parental ThresHold to OFF
    logging.info("set parental ThresHold to " + INITIAL_THRESHOLD)
    ve_test.he_utils.setParentalRatingThreshold(hhid, INITIAL_THRESHOLD)

    # control PIN value on UPM
    current_parental_pincode = str(ve_test.he_utils.getParentalpincode())
    error_message = "UPM PIN code init with value " + INITIAL_PIN + " failed ! current PIN is : " + current_parental_pincode
    ve_test.assertmgr.addCheckPoint("test_parental_control", 1, current_parental_pincode == INITIAL_PIN, error_message)
    logging.info("controlled PIN code on UPM " + current_parental_pincode)

    # control THRESHOLD value on UPM
    current_parental_threshold = str(ve_test.he_utils.getHouseHoldPrentalThreshold())
    error_message = "UPM THRESHOLD init with value " + INITIAL_THRESHOLD + " failed ! current THRESHOLD is : " + current_parental_threshold
    ve_test.assertmgr.addCheckPoint("test_parental_control", 2, current_parental_threshold == INITIAL_THRESHOLD, error_message)
    logging.info("controlled THRESHOLD on UPM " + current_parental_threshold)

    ############
    ''' Second step : go to PIN code setting screen
        Action
        - enter in PIN code setting menu
        Checkup
        - check PIN code screen is displayed
    '''

    # enter in setting menu to change PIN code
    logging.info("navigate_to_settings_screen")
    status = ve_test.screens.main_hub.navigate()
    error_message = "Navigation to Hub failed : current screen = " + str(display_pretty_current_screen(ve_test))
    ve_test.assertmgr.addCheckPoint("test_parental_control", 3, status, error_message)

    logging.info("navigate_to_parental_control_screen")
    status = ve_test.screens.main_hub.navigate_to_settings_sub_menu("PARENTAL")
    error_message = "Navigation : Hub --> Settings  : current screen = " + str(display_pretty_current_screen(ve_test))
    ve_test.assertmgr.addCheckPoint("test_parental_control", 4, status, error_message)

    ############
    ''' 3rd step : change Parental PIN code from settings
        Action
        - enter current PIN code (1111)
        - update current PIN code with new PIN code (1234)
        Checkup
        - check PIN code value on UPM matches with changed value from setting
    '''
    logging.info("select modify PIN Code in setting menu")
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    text_to_verify = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "pincode_message"))
    error_message = "check PIN code entry screen is displayed failed, current text is " + text_to_verify
    ve_test.assertmgr.addCheckPoint("test_parental_control", 5, "current Parental PINCODE" in text_to_verify, error_message)
    logging.info("current Screen is " + text_to_verify)
    logging.info("enter current PIN Code " + INITIAL_PIN)
    ve_test.screens.pincode.enter_pincode(INITIAL_PIN_SEQUENCE)

    text_to_verify = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "pincode_message"))
    error_message = "check new PIN code entry screen is displayed failed, current text is " + text_to_verify
    ve_test.assertmgr.addCheckPoint("test_parental_control", 6, "enter your new PINCODE" in text_to_verify, error_message)
    logging.info("current Screen is " + text_to_verify)
    logging.info("enter new PIN Code " + NEW_PIN)
    ve_test.screens.pincode.enter_pincode(NEW_PIN_SEQUENCE)

    text_to_verify = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "pincode_message"))
    error_message = "check new PIN code entry screen is displayed failed, current text is " + text_to_verify
    ve_test.assertmgr.addCheckPoint("test_parental_control", 7, "confirm your new PINCODE" in text_to_verify, error_message)
    logging.info("current Screen is " + text_to_verify)
    logging.info("confirm new PIN Code " + NEW_PIN)
    ve_test.screens.pincode.enter_pincode(NEW_PIN_SEQUENCE)

    text_to_verify = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "pincode_message"))
    error_message = "check PIN code change successs is displayed failed, current text is " + text_to_verify.replace("\n","")
    ve_test.assertmgr.addCheckPoint("test_parental_control", 8, "successfully" in text_to_verify, error_message)
    logging.info("PINCODE update message " + text_to_verify.replace("\n",""))

    # check new PIN code value on UPM
    current_parental_pincode = str(ve_test.he_utils.getParentalpincode())
    error_message = "UPM PIN code update with value " + NEW_PIN + " failed ! current PIN is : " + current_parental_pincode
    ve_test.assertmgr.addCheckPoint("test_parental_control", 9, current_parental_pincode == NEW_PIN,error_message)
    logging.info("UPM PIN code updated with : " + current_parental_pincode)

    ############
    ''' 4th step : change Parental threshold from settings
        Action
        - enter in Parental threshold screen
        - update current threshold from OFF to 7
        Checkup
        - check threshold value on UPM matches with changed value from setting
    '''

    # modify parental ThresHold
    # Go Back to the previous screen
    ve_test.appium.key_event("KEYCODE_BACK")
    ve_test.wait(2*CONSTANTS.SMALL_WAIT)

    ve_test.move_towards('up', 2*CONSTANTS.SMALL_WAIT, False)
    text_to_verify = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item"))
    error_message = "check PARENTAL CONTROL screen is displayed failed, current focused_item is " + text_to_verify
    ve_test.assertmgr.addCheckPoint("test_parental_control", 10, "PARENTAL CONTROL" in text_to_verify, error_message)
    logging.info("current Screen is " + text_to_verify)

    ve_test.validate_focused_item()
    ve_test.screens.pincode.enter_pincode(NEW_PIN_SEQUENCE)
    ve_test.validate_focused_item()
    current_focused_item = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_item"))
    error_message = "focus is not on MODIFY PARENTAL THRESHOLD item !  current focused item is : " + current_focused_item
    ve_test.assertmgr.addCheckPoint("test_parental_control", 11, current_focused_item == "MODIFY PARENTAL THRESHOLD", error_message)

    while THRESHOLD_ITEM_COUNTER > 0:
        focus_is_on = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_asset")
        if focus_is_on == NEW_THRESHOLD:
            logging.info("focus is on " + NEW_THRESHOLD)
            break
        THRESHOLD_ITEM_COUNTER -= 1
        ve_test.move_towards('right', 2*CONSTANTS.SMALL_WAIT, False)

    error_message = "can't focus on THRESHOLD " + NEW_THRESHOLD
    ve_test.assertmgr.addCheckPoint("test_parental_control", 12, focus_is_on == NEW_THRESHOLD, error_message)

    # control selected THRESHOLD on UPM
    ve_test.validate_focused_item()
    # check THRESHOLD value
    current_parental_threshold = str(ve_test.he_utils.getHouseHoldPrentalThreshold())
    error_message = "UPM THRESHOLD update with value " + NEW_THRESHOLD_UPM + " failed ! current THRESHOLD is : " + current_parental_threshold
    ve_test.assertmgr.addCheckPoint("test_parental_control", 13, current_parental_threshold == NEW_THRESHOLD_UPM, error_message)
    logging.info("UPM THRESHOLD updated with : " + current_parental_threshold)

    ############
    ''' 5th step : go to fullscreen (on locked program)
        Action
        - go back to fullscreen from PC screen
        Checkup
        - check current program is locked
        - check no audio/video
    '''
    # go back to fullscreen
    logging.info("navigate back to fullscreen from " + str(display_pretty_current_screen(ve_test)))
    ve_test.go_to_previous_screen(CONSTANTS.GENERIC_WAIT)
    text_to_verify = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item"))
    error_message = "check MODIFY THRESHOLD screen is displayed failed, current focused_item is " + text_to_verify
    ve_test.assertmgr.addCheckPoint("test_parental_control", 14, "PIN MANAGEMENT" in text_to_verify, error_message)
    logging.info("current Screen is " + text_to_verify)

    ve_test.go_to_previous_screen(CONSTANTS.GENERIC_WAIT)
    text_to_verify = str(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item"))
    error_message = "check PIN MANAGEMENT screen is displayed failed, current focused_item is " + text_to_verify
    ve_test.assertmgr.addCheckPoint("test_parental_control", 15, "SETTINGS" in text_to_verify, error_message)
    logging.info("current Focused item is " + text_to_verify)

    ve_test.go_to_previous_screen(2*CONSTANTS.SMALL_WAIT)
    current_screen = ve_test.milestones.get_current_screen(ve_test.milestones.getElements())
    info_layer_is_shown = ve_test.screens.fullscreen.is_infolayer_shown()
    error_message = "current screen is {0} instead of infolayer and info layer is shown status is {1} instead of true ".format(current_screen, info_layer_is_shown)
    ve_test.assertmgr.addCheckPoint("test_parental_control", 16, info_layer_is_shown and current_screen is not "infolayer",
                            error_message)

    # video/audio Mute ?
    playback_status = ve_test.milestones.getPlaybackStatus()
    logging.info(
        "video locked=" + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
    error_message = "video and audio not locked."
    ve_test.assertmgr.addCheckPoint("test_parental_control", 17, playback_status["hiddenVideo"] and playback_status["muted"],
                            error_message)
    text_to_verify = "{}".format(ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_event_title"))
    error_message = "current event is not LOCKED PROGRAM, current event title is " + text_to_verify
    ve_test.assertmgr.addCheckPoint("test_parental_control", 18, "LOCKED PROGRAM" == text_to_verify, error_message)
    logging.info("current event title is " + text_to_verify)

    ############
    ''' 6th step : unlock current locked program
        Action
        - validate "locked program" popup
        - enter valid PIN code to unlock program
        Checkup
        - check audio/video
    '''
    # valid current LOCKED PROGRAM and enter PINCODE
    ve_test.validate_focused_item(2*CONSTANTS.SMALL_WAIT)
    elements = ve_test.milestones.getElements()
    text_to_verify = str(ve_test.milestones.get_value_by_key(elements, "pincode_message"))
    error_message = "PINCODE not displayed on LOCKED event, current screen is {0} \n milestones = {1}" \
                   .format( ve_test.milestones.get_current_screen(elements),json.dumps(elements,indent=2))
    ve_test.assertmgr.addCheckPoint("test_parental_control", 19, "enter your PINCODE" in text_to_verify, error_message)
    logging.info("current focused item is " + text_to_verify)

    logging.info("typing PINCODE " + NEW_PIN)
    ve_test.screens.pincode.enter_pincode(NEW_PIN_SEQUENCE)

    # video/audio Mute ?
    playback_status = ve_test.milestones.getPlaybackStatus()
    logging.info("video locked= {0}  audio locked= {1}".format(playback_status["hiddenVideo"],playback_status["muted"]))
    error_message = "video and audio still locked. \n playback_status ={0}".format(json.dumps(playback_status,indent=2))
    ve_test.assertmgr.addCheckPoint("test_parental_control",
                            20, not playback_status["hiddenVideo"] and not playback_status["muted"], error_message)

    ############
    ''' 7th step : end of test, parental threshold back to OFF
        Action
        - set parental threshold back to OFF
        Checkup
        - none
    '''
    # set Threshold OFF on UPM
    logging.info("set parental ThresHold to " + INITIAL_THRESHOLD)
    ve_test.he_utils.setParentalRatingThreshold(hhid, INITIAL_THRESHOLD)

    print "<ul>"
    print "<li> 'Parental Control' performed </li>"
    print "</ul>"


def internal_test_vod(ve_test):
    # Not yet impemented
    vod_manager = ve_test.screens.playback.vod_manager

    ve_test.repeat_key_press("KEYCODE_BACK",2,3)
    #status = test_vod.navigate_to_main_hub()

    screen_name = ve_test.milestones.get_current_screen()
    if screen_name != "main_hub":
        ve_test.repeat_key_press("KEYCODE_BACK",1,0)

    live_status = ve_test.milestones.getPlaybackStatus()
    live_url = ve_test.screens.playback.retrieve_session_playback_url()
    ve_test.assertmgr.addCheckPoint("sanity_vod", 0, live_url is not False, "Failure to retrieve a valid playbackUrl: {0}\n"
                            .format(ve_test.milestones.getPlaybackStatus()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    ''' First step : Play vod
        Action
        - launch a VOD asset
        Checkup
        - Check the playback status
        - Retrieve the current position, wait 10s, and check again the expected position
    '''
    status = vod_manager.start_free_playback(TIME_VOD_STARTING)
    ve_test.assertmgr.addCheckPoint("sanity_vod", "Play vod 0", status, "Sanity VOD - Can't select the VOD Asset ")

    if status:
        milestone = ve_test.milestones.getElements()
        screen_name = ve_test.milestones.get_value_by_key(milestone,"screen_name")
        status = screen_name != "notification"
        error_text = ""
        if not status:
            error_text = "{0} {1}".format(ve_test.milestones.get_value_by_key(milestone,"msg_error"),ve_test.milestones.get_value_by_key(milestone,"msg_text"))
            logging.error("{0} {1}".format(status, error_text))

        ve_test.assertmgr.addCheckPoint("sanity_vod", "Play vod 1", status, "Sanity VOD - 1st step: The VOD playback has fails, {0} ".format(error_text))

    if status:
        playback_status = ve_test.milestones.getPlaybackStatus()
        ve_test.assertmgr.addCheckPoint("sanity_vod", "Play vod 2", playback_status['playbackState'] == "PLAYING", "Sanity VOD - 1st step: The current status should be PLAYING, it is " + playback_status['playbackState']  )
        ve_test.assertmgr.addCheckPoint("sanity_vod", "Play vod 3", playback_status['playbackType'] == "VOD", "Sanity VOD - 1st step: The playback type should be vod, it is "+playback_status['playbackType'])

        # check if the video is not too short for more steps
        total_duration = vod_manager.get_total_duration()
        logging.info("VOD duration " + str(total_duration))
        if total_duration >= 60000:
            current_pos = vod_manager.get_current_position(TIME_PLAYING_CHECK_TWO_POSITIONS,True)
            new_current_pos = vod_manager.get_current_position(0,True)
            ve_test.assertmgr.addCheckPoint("sanity_vod", "Play vod 4", ((new_current_pos >= (((TIME_PLAYING_CHECK_TWO_POSITIONS - 1) * 1000) + current_pos))
                                                              and (new_current_pos <= current_pos + (TIME_PLAYING_CHECK_TWO_POSITIONS + 3)*1000) ),
                                                              ("Sanity VOD - 1st step: Position has not correclty changed during normal playback  : old=" + str(current_pos) + " --> new = "+str(new_current_pos)))

            logging.info("sanity_vod  Play vod 4 "+  " [new_current_pos = " + str(new_current_pos)  + "] [current_pos= " + str(current_pos) + "]")

            ''' Second step : Pause the asset
            Action :
            - Press Pause
            Checkup :
            - Check Playback Status (=Paused)
            - Get Current Position, wait 3s, check that the current position has not changed
            '''
            vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
            ve_test.assertmgr.addCheckPoint("sanity_vod", "Pause 1", ve_test.milestones.getPlaybackStatus()['playbackState'] == "PAUSED", "Sanity VOD - 2nd step: The current status should be PAUSED"  )
            current_pos = vod_manager.get_current_position(TIME_PLAYING_CHECK_TWO_POSITIONS)
            new_current_pos = vod_manager.get_current_position()
            ve_test.assertmgr.addCheckPoint("sanity_vod", "Pause 2", (new_current_pos == current_pos), "Sanity VOD - 2nd step: The position should not change in pause")

            ''' Third step : Resume the asset
            Action :
            - Press resume
            Checkup :
            - Check playback status (= Playing)
            - Check the current position will change
            '''
            vod_manager.process_play_or_pause(3)
            ve_test.assertmgr.addCheckPoint("sanity_vod", "Resume 1", ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING", "Sanity VOD - 3rd step: The current status should be PLAYING"  )
            current_pos = vod_manager.get_current_position(TIME_PLAYING_CHECK_TWO_POSITIONS, True)
            new_current_pos = vod_manager.get_current_position(0,True)
            ve_test.assertmgr.addCheckPoint("sanity_vod", "Resume 2",((new_current_pos >= (((TIME_PLAYING_CHECK_TWO_POSITIONS -1) * 1000) + current_pos))
                                                              and (new_current_pos <= current_pos + (TIME_PLAYING_CHECK_TWO_POSITIONS + 3)*1000) ),
                                                              "Sanity VOD - 3rd step:Position has not correclty changed : old=" + str(current_pos) + " --> new = "+str(new_current_pos))

            # wait for trick mode to disappear
            ve_test.wait(10)

        else:
            logging.info("VOD duration is too short for more steps")

    ''' 6th step : Stop the playback
    Action :
    - Press stop
    '''
    if status:
        vod_manager.process_stop(TIME_VOD_STOPPING)
        ve_test.wait(CONSTANTS.GENERIC_WAIT)

        new_live_status = ve_test.milestones.getPlaybackStatus()
        new_live_url = ve_test.screens.playback.retrieve_session_playback_url()
        ve_test.assertmgr.addCheckPoint("sanity_vod", 0, new_live_url is not False, "Failure to retrieve a valid playbackUrl: {0}\n"
                            .format(ve_test.milestones.getPlaybackStatus()))

        ve_test.assertmgr.addCheckPoint("sanity_vod", "Stop 1", live_url == new_live_url, "After stopping the vod playback we should play the live")
        ve_test.assertmgr.addCheckPoint("sanity_vod", "Stop 2", ve_test.milestones.get_current_screen() in ["filter", "full_content"], "After stopping the vod playback we should come back to filter or full_content, not "+str(ve_test.milestones.get_current_screen()))
        ve_test.assertmgr.addCheckPoint("sanity_vod", "Stop 3", new_live_status['playbackState'] == "PLAYING", "After stopping the vod playback, we should be in PLAYING state, not "+str(new_live_status['playbackState']))

    # should go back to the hub at the end of the test
    status = ve_test.screens.main_hub.navigate()
    ve_test.assertmgr.addCheckPoint("sanity_vod", "End", status, "Cannot go back to main Hub: current_screen = {}".format(ve_test.milestones.get_current_screen()))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    print "<ul>"
    print "<li> 'test vod' performed </li>"
    print "</ul>" 
     

def display_pretty_current_screen(ve_test):
    current = ve_test.milestones.get_current_screen()
    if current == "notification":
        elements = ve_test.milestones.getElements()
        title = ve_test.milestones.get_value_by_key(elements, "msg_title")
        text = ve_test.milestones.get_value_by_key(elements, "msg_text")
        error = ve_test.milestones.get_value_by_key(elements, "msg_error")
        return "Notification(" + title + ","+error+")"
    else :
        return current


def internal_test_hub_navigation(ve_test):
    ve_test.assertmgr.setup("test_hub_navigation")
    check = ve_test.assertmgr.addCheckPointLight

    logging.info("test_navigation : current screen = "+ str(display_pretty_current_screen(ve_test)))    
    status = ve_test.screens.main_hub.navigate()
    # navigate_to_main_hub does not work from full_content so you need to double it
    if status is False :
        status = ve_test.screens.main_hub.navigate()

    check( ve_test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES"),
            "Navigation : Hub --> Settings  : current screen = " + str(display_pretty_current_screen(ve_test)))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    check(ve_test.screens.main_hub.navigate(),
            "Navigation : Settings --> Hub  : current screen = " + str(display_pretty_current_screen(ve_test)))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    check(ve_test.screens.guide.navigate(directly=False),
            "Navigation : Hub --> Guide  : current screen = " + str(display_pretty_current_screen(ve_test)))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    check(ve_test.screens.main_hub.navigate(),
            "Navigation : Guide --> Hub  : current screen = "+ str(display_pretty_current_screen(ve_test)))

    check(ve_test.screens.main_hub.navigate_to_store(),
            "Navigation : Hub --> Store  : current screen = "+ str(display_pretty_current_screen(ve_test)))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    check(ve_test.screens.main_hub.navigate(),
            "Navigation : Store --> Hub  : current screen = "+ str(display_pretty_current_screen(ve_test)))



def internal_test_zaplist(ve_test):
    """
    Sanity check of Channel List
      - launch (Left and Right),
      - navigation (Up and down),
      - exit (back, OK)
    :return:
    """
    status = ve_test.screens.fullscreen.navigate()
    ve_test.assertmgr.addCheckPoint("test_zaplist", 1, status,
                            "Initials Conditions: Failed to go to fullscreen. Screen: {0}"
                            .format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT + CONSTANTS.GENERIC_WAIT)

    channel_number = CONSTANTS.channel_number_classic_1
    logging.info("Zap on channel number: {0}".format(channel_number))
    ve_test.screens.playback.dca(channel_number, with_ok=True)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT + CONSTANTS.GENERIC_WAIT)

    playback_status = ve_test.milestones.getPlaybackStatus()
    ve_test.assertmgr.addCheckPoint("test_zaplist", 2, playback_status['playbackState'] == "PLAYING",
                            "Initials Conditions: The video is not playing: {0}".format(playback_status))

    fullscreen_lcn = ve_test.screens.fullscreen.get_current_channel()

    # Launch the Channel List by long key press on Down
    #    Do some navigation
    #    Exit the Channel List by OK key press and check the zapping

    status = ve_test.screens.zaplist.navigate("down")
    ve_test.assertmgr.addCheckPoint("test_zaplist", 3, status, "Failed to go to zaplist. Screen: {0}"
                            .format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Check the navigation and zapping functionality by selected and zap to channel
    status = ve_test.screens.zaplist.tune_to_channel_by_sek(CHANNEL_WITH_VIDEO_A, True, True)
    ve_test.assertmgr.addCheckPoint("test_zaplist", 4, status, "Failed to zap on channel {0}.\n"
                            "getPlaybackStatus: {1}".format(CHANNEL_WITH_VIDEO_A, ve_test.milestones.getPlaybackStatus()))

    ve_test.wait(2*CONSTANTS.INFOLAYER_TIMEOUT)
    status = not ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.assertmgr.addCheckPoint("test_zaplist", 5, status, "info_layer is not dismissed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    new_fullscreen_lcn = ve_test.screens.fullscreen.get_current_channel()

    ve_test.assertmgr.addCheckPoint("test_zaplist", 6, new_fullscreen_lcn != fullscreen_lcn,
                            "New fullscreen channel (lcn: {0}) is the same that before tuning by Zaplist (lcn:{1})"
                            .format(new_fullscreen_lcn, fullscreen_lcn))
    ve_test.assertmgr.addCheckPoint("test_zaplist", 7, new_fullscreen_lcn == CHANNEL_WITH_VIDEO_A,
                            "Wrong channel tuned after Zaplist zapping"
                            "New fullscreen channel (lcn: {0})   Zaplist (lcn:{1})"
                            .format(new_fullscreen_lcn, CHANNEL_WITH_VIDEO_A))

    # Launch the Channel List by long key press on Up
    #    Do some navigation
    #    Exit the Channel List
    status = ve_test.screens.zaplist.navigate("up")
    ve_test.assertmgr.addCheckPoint("test_zaplist", 8, status, "Failed to go to Zaplist. Screen: {0}"
                            .format(ve_test.milestones.get_current_screen()))

    for nb in range(0, 5):
        status = ve_test.screens.zaplist.to_nextchannel('up')
        ve_test.assertmgr.addCheckPoint("test_zaplist", 9, status, "Failed to get the focus to the prev channel.\n"
                                "Milestone: {0}".format(ve_test.milestones.getElements()))

    for nb in range(0, 5):
        status = ve_test.screens.zaplist.to_nextchannel('down')
        ve_test.assertmgr.addCheckPoint("test_zaplist", 10, status, "Failed to get the focus to the next channel.\n"
                                "Milestone: {0}".format(ve_test.milestones.getElements()))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.fullscreen.navigate('ok')
    ve_test.assertmgr.addCheckPoint("test_zaplist", 11, status, "Fail to go back to fullscreen. Screen: {0}"
                            .format(ve_test.milestones.get_current_screen()))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    print "<ul>"
    print "<li> 'zaplist' performed </li>"
    print "</ul>" 
    

def internal_test_timeline(ve_test):
    '''
    Sanity check of Timeline
      - launch (Left and Right),
      - navigation (Up and down),
      - exit (back, OK)
    :return:
    '''
    # Go to Initial Conditions:
    # To fullscreen
    status = ve_test.screens.fullscreen.navigate()
    ve_test.assertmgr.addCheckPoint("test_timeline", 1, status,
                            "Failed to go to fullscreen. Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT + CONSTANTS.GENERIC_WAIT)

    # Zap on channel 1
    logging.info("Zap on channel number %s", CONSTANTS.channel_number_classic_1)
    ve_test.screens.playback.dca(CONSTANTS.channel_number_classic_1, with_ok=True)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT + CONSTANTS.GENERIC_WAIT)
    ve_test.assertmgr.addCheckPoint("test_timeline", 2, ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING",
                            "Initials Conditions: Zapping on channel n 1, the video is not playing.\n"
                            "milestones.getPlaybackStatus: {0}".format(ve_test.milestones.getPlaybackStatus()))

    fullscreen_lcn = ve_test.screens.fullscreen.get_current_channel()

    # Launch the Timeline by Left, do a navigation to the next channel then do a zapping on the selected channel
    status = ve_test.screens.timeline.navigate("left")
    ve_test.assertmgr.addCheckPoint("test_timeline", 3, status, "Failed to go to timeline. "
                                                        "Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    timeline_lcn = ve_test.screens.timeline.get_focused_channel_number()
    # check that the timeline is launch on the fullscreen's channel
    ve_test.assertmgr.addCheckPoint("test_timeline", 4, fullscreen_lcn == timeline_lcn,
                            "Timeline (lcn: {0}) is not launch on the fullscreen channel (lcn:{1})"
                            .format(fullscreen_lcn, timeline_lcn))

    # Check the navigation and zapping functionality by selected and zap to channel
    status = ve_test.screens.timeline.tune_to_channel_by_sek(CHANNEL_WITH_VIDEO_A, False, False)
    ve_test.assertmgr.addCheckPoint("test_timeline", 5, status, "Failed to zap on channel {0}".format(CHANNEL_WITH_VIDEO_A))

    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.assertmgr.addCheckPoint("test_timeline", 6, status, "info_layer is not shown")
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT + CONSTANTS.GENERIC_WAIT)
    elements = ve_test.milestones.getElements()
    ve_test.assertmgr.addCheckPoint("test_timeline", 7, ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING",
                            "The video is not playing\n"
                            "milestones.getPlaybackStatus: {0}\n"
                            "milestones.getElements: {1}".format(ve_test.milestones.getPlaybackStatus(), elements))

    new_fullscreen_lcn = ve_test.milestones.get_value_by_key(elements, 'current_channel')
    ve_test.assertmgr.addCheckPoint("test_timeline", 8, new_fullscreen_lcn != fullscreen_lcn,
                            "New fullscreen channel (lcn: {0}) is the same that before tuning by Timeline (lcn:{1})"
                            .format(new_fullscreen_lcn, fullscreen_lcn))
    ve_test.assertmgr.addCheckPoint("test_timeline", 9, new_fullscreen_lcn == CHANNEL_WITH_VIDEO_A,
                            "Wrong channel tuned after Timeline zapping"
                            "New fullscreen channel (lcn: {0})   Timeline (lcn:{1})"
                            .format(new_fullscreen_lcn, CHANNEL_WITH_VIDEO_A))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Launch the Timeline by Right, do some navigation then dismiss the Timeline by Back key
    fullscreen_lcn = ve_test.screens.fullscreen.get_current_channel()

    #
    # Caution, time out may be too short for launching the timeline.
    #
    status = ve_test.screens.timeline.navigate("right")
    ve_test.assertmgr.addCheckPoint("test_timeline", 10, status, "Failed to go to timeline. "
                                                         "Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    for nb in range(0, 8):
        status = ve_test.screens.timeline.to_nextchannel('up')
        ve_test.assertmgr.addCheckPoint("test_timeline", 11, status, "Failed to get the focus to the next channel")

    status = ve_test.screens.fullscreen.navigate("back")
    ve_test.assertmgr.addCheckPoint("test_timeline", 12, status, "Fail to go back to fullscreen. "
                                                         "Screen: {0}".format(ve_test.milestones.get_current_screen()))
    elements = ve_test.milestones.getElements()
    new_fullscreen_lcn = ve_test.milestones.get_value_by_key(elements, 'current_channel')
    ve_test.assertmgr.addCheckPoint("test_timeline", 13, new_fullscreen_lcn == fullscreen_lcn,
                            "Channels are not the same after pressing Back in Timeline"
                            "New fullscreen channel (lcn: {0})   previous channel(lcn:{1})"
                            .format(new_fullscreen_lcn, fullscreen_lcn))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    print "<ul>"
    print "<li> 'timeline' performed </li>"
    print "</ul>" 

def internal_test_actionmenu_ltv_fullscreen(ve_test):
    '''
    Sanity check of Action Menu on Linear content
      - launch
      - event display
      - action list
    :return:
    '''
    test_tag = "test_actionmenu_ltv_fullscreen"
    status = ve_test.screens.fullscreen.navigate()
    ve_test.assertmgr.addCheckPoint(test_tag, 1, status, "Failed to go to fullscreen. "
                                                 "Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    logging.info("Zap on channel number %s", CONSTANTS.channel_number_classic_1)
    ve_test.screens.playback.dca(CONSTANTS.channel_number_classic_1, with_ok=True)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.assertmgr.addCheckPoint(test_tag, 2, ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING",
                            "Initials Conditions: Zapping on channel n 1, the video is not playing")

    if not ve_test.is_dummy:
        ve_test.screens.fullscreen.wait_for_event_with_minimum_time_until_end()

    # Launch the Channel Action Menu on current channel/event
    status = ve_test.screens.action_menu.navigate()
    ve_test.assertmgr.addCheckPoint(test_tag, 3, status, "Failed to go to Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    first_focused_action = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")

    # Do not perform the comparaison in Dummy
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    if ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "prog_schedule_info") is None:
        ve_test.assertmgr.addCheckPoint(test_tag, 4, False, "No available event")
    else:
        # Check that selected item is the first one (SUMMARY)
        ve_test.assertmgr.addCheckPoint(test_tag, 5, first_focused_action == list_live_current[0],
                                "Default item is not SUMMARY but %s" % first_focused_action)

        # Browse the Action list
        ve_test.move_towards('up')
        selected_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")
        if selected_item != first_focused_action:
            for nb in range(1, 10):
                    ve_test.move_towards('up')
                    selected_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")
                    if selected_item == first_focused_action:
                        # loop is done
                        break
            else:
                ve_test.assertmgr.addCheckPoint(test_tag, 6, False, "no loop on first item")

        # Access to the SUMMARY
        # Not available in Dummy
        if not ve_test.is_dummy:
            status = ve_test.screens.action_menu.get_summary()
            ve_test.assertmgr.addCheckPoint(test_tag, 7, status, "Summary is not displayed")

    # Check Action Menu exit (Back key)
    status = ve_test.screens.fullscreen.navigate()
    ve_test.assertmgr.addCheckPoint(test_tag, 8, status, "Unable to exit from Action Menu (fullscreen) by Back key. "
                                                 "Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    print "<ul>"
    print "<li> 'action menu ltv fullscreen' performed </li>"
    print "</ul>"


def internal_test_actionmenu_ltv_timeline(ve_test):
    '''
    Sanity check of Action Menu on Linear content
      - launch
      - event display
      - action list
    :return:
    '''
    status = ve_test.screens.fullscreen.navigate()
    ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 1, status,
                            "Failed to go to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    if not ve_test.is_dummy:
        ve_test.screens.fullscreen.wait_for_event_with_minimum_time_until_end()

    # Check Action Menu on future event with Timeline
    status = ve_test.screens.timeline.navigate()
    ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 2, status,
                            "Fail to launch the Timeline. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(3)
    ve_test.move_towards('right', 0.2)
    ve_test.wait(3)

    # Memorize selected channel/event
    timeline_eventTitle = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_event_title")

    # Launch the Action Menu
    status = ve_test.screens.action_menu.navigate()
    ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 3, status,
                            "Fail to open the Action Menu. Current screen: %s" % ve_test.milestones.get_current_screen())

    am_eventTitle = ve_test.screens.action_menu.get_event_title()
    first_focused_action = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")

    # Check channel/event display
    # Do not perform the comparaison in Dummy
    if not ve_test.is_dummy:
        ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 4, am_eventTitle == timeline_eventTitle,
                                "Action Menu is not launch on selected event")

    # Check that selected item is the first one (SUMMARY)
    ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 5, first_focused_action == list_live_current[0],
                            "Default item is not SUMMARY but %s" % first_focused_action)

    # Browse the Action list
    ve_test.move_towards('up')
    selected_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")
    if selected_item != first_focused_action:
        for nb in range(1, 10):
                ve_test.move_towards('up')
                selected_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")
                if selected_item == first_focused_action:
                    # loop is done
                    break
        else:
            ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 5, False, "no loop on first item")

    # Check the come-back to the Timeline
    # No come-back in Dummy
    if not ve_test.is_dummy:
        ve_test.wait(2)
        ve_test.go_to_previous_screen()
        status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "timeline")
        ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 7, status,
                                "Fail to come-back to the Timeline. Current screen: %s" % ve_test.milestones.get_current_screen())
        # go to full screen
        status = ve_test.screens.fullscreen.navigate('back')
        ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 8, status,
                                "Fail to come-back to the Fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())
    else:
        status = ve_test.screens.fullscreen.navigate()
        ve_test.assertmgr.addCheckPoint("test_actionmenu_ltv_timeline", 8, status,
                                "Unable to exit from Action Menu (fullscreen) by Back key. "
                                "Current screen: %s" % ve_test.milestones.get_current_screen())
        ve_test.wait(CONSTANTS.GENERIC_WAIT)
    print "<ul>"
    print "<li> 'actionmenu ltv timeline' performed </li>"
    print "</ul>"


def internal_test_multiAudio(ve_test):
    '''
    Sanity check of multi audio change
      - go to multi audio channel (44 euro news)
      - launch action menu 
      - select audio language and check it
      - change the audio for the next audio on list
      - go to fullscreen and verify that the audio has change and it is the good one -ger-
    :return:
    '''

    check = ve_test.assertmgr.addCheckPointLight

    check(ve_test.screens.main_hub.navigate(),
          "Failed to go to main_hub: Current screen: {}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # go to channel CONSTANTS.channel_number_with_several_audio for multi audio - euronews should be "eng deu ita free"

    logging.info("Zap on channel number {} euronews".format(CONSTANTS.channel_number_with_several_audio))
    ve_test.screens.playback.dca(CONSTANTS.channel_number_with_several_audio, with_ok=True)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT +CONSTANTS.GENERIC_WAIT)

    channel_lcn = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"current_channel")

    check(channel_lcn == CONSTANTS.channel_number_with_several_audio,
          "Initials Conditions: Zapping on channel number {0} fails, Current channel playing number {1}"
                            .format(CONSTANTS.channel_number_with_several_audio,channel_lcn))

    check(ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING",
          "Initials Conditions: Zapping on channel n {}, the video is not playing"
          .format(CONSTANTS.channel_number_with_several_audio))

    logging.info("Verify that ActionMenu can be launch by OK key press on 'fullscreen'")

    check(ve_test.screens.action_menu.navigate(),
          "Fail to launch the ActionMenu. Current screen:{}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    check(ve_test.screens.action_menu.get_menu_nb_audio() > 1, "No audio items in sub-menu")

    check(ve_test.screens.action_menu.navigate_to_action(CONSTANTS.A_LANGUAGE), "Fail to select Languages item")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    elements = ve_test.milestones.getElements()
    first_focused_item = ve_test.milestones.get_value_by_key(elements, "focused_item")
    current_focused_language = ve_test.milestones.get_value_by_key(elements, "focused_asset")
    check(current_focused_language is not None, "No current focused language" )
    logging.info("first_focused_item: {} current_focused_language: {}".format(first_focused_item, current_focused_language))

    # Select a new audio language and check
    ve_test.wait(CONSTANTS.SMALL_WAIT)
    ve_test.move_towards('right')
    ve_test.wait(CONSTANTS.SMALL_WAIT)
    current_focused_language = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_asset")

    logging.info("new selected language: {}".format(current_focused_language))
    # Select next audio language in sub-menu should be GERMAN
    ve_test.validate_focused_item(CONSTANTS.SMALL_WAIT)
    ve_test.wait(5)

    logging.info("--> go back to fullscreen")

    check(ve_test.screens.fullscreen.navigate(),
          "Failed to go to fullscreen. Current screen: {}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    response = ve_test.milestones.getPlaybackStatus()

    check( len(response["playbackStreams"]) > 1,"No available Stream")

    iso_code = [item["language"] for item in response["playbackStreams"] if item["type"] == "AUDIO"]
    lang = ""

    check( len(iso_code) == 1,"No audio stream selected")

    if CONSTANTS.dico_languages.has_key(iso_code[0]):
        logging.info("{}".format(CONSTANTS.dico_languages[iso_code[0]]))
        lang = CONSTANTS.dico_languages[iso_code[0]]

        check( lang == current_focused_language, "Expected language is {} (current is {})".format(current_focused_language,lang))

    ve_test.wait(CONSTANTS.GENERIC_WAIT)


def internal_test_dvbsub(ve_test):
    '''
    Sanity check of dvb subtitles
      - set settings to Subtitles : POR, CC: OFF
      - go to DVB sub channel (45, with portuguese subtitles)
      - launch action menu
      - check that subtitles are present in the stream and displayed
      - launch action menu: check that subtitle entries are correct
      - disable subtitles and check that they are no longer displayed after dismissing the action menu
    :return:
    '''
    check = ve_test.assertmgr.addCheckPointLight

    check(ve_test.screens.main_hub.navigate(),
          "Failed to go to main_hub: Current screen: %s" % ve_test.milestones.get_current_screen())
    check(ve_test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES"),
          "Failed to go to Settings. Milestone: %s" % ve_test.milestones.getElements())

    check(ve_test.screens.main_hub.select_settings_sub_sub_menu("SUBTITLES", "PORTUGUESE"),
          "Failed select PORTUGUESE" % ve_test.milestones.getElements())
    check(ve_test.screens.main_hub.select_settings_sub_sub_menu("CLOSED CAPTION", "NONE"),
          "Failed to go to CLOSED CAPTION -> OFF. Milestone: %s" % ve_test.milestones.getElements())

    check(ve_test.screens.fullscreen.navigate(),
          "Failed to go to fullscreen: Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.screens.playback.dca(CONSTANTS.channel_number_with_dvb_sub, with_ok=True)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT+ CONSTANTS.GENERIC_WAIT)

    check(ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING",
          "Initials Conditions: Zapping on channel n %d, the video is not playing" % CONSTANTS.channel_number_with_dvb_sub)

    check(ve_test.screens.action_menu.navigate(),
          "Failed to go to action_menu: Current screen: %s" % ve_test.milestones.get_current_screen())
    check(ve_test.screens.action_menu.navigate_to_action("SUBTITLES"),
          "Failed to select SUBTITLES")

    selected_subtitles = ve_test.screens.action_menu.get_subtitles_selected()
    check(selected_subtitles, "No Subtitles selected")
    check("PORTUGUESE" in ve_test.screens.action_menu.get_subtitles_selected(),
          "PORTUGUESE not selected")

    s = [ stream for stream in ve_test.milestones.getPlaybackStatus()["playbackStreams"] if (stream["name"] == "por" and stream["type"] == "TEXT_SMPTEE_ID3") ]
    check(len(s) == 1,
           "no DVB sub played")

    check( ve_test.screens.action_menu.select_subtitles("off"), "off subtitles selection failure")
    ve_test.wait(5)
    selected_subtitles = ve_test.screens.action_menu.get_subtitles_selected()
    check("off" in selected_subtitles,
          "off not selected, {} instead".format(selected_subtitles))

    # to be uncommented & checked with milestones
    #s = [ stream for stream in ve_test.milestones.getPlaybackStatus()["playbackStreams"] if (stream["type"] == "TEXT_SMPTEE_ID3") ]
    #check(len(s) == 0,
    #      "sub ")


def internal_test_closedCaption(ve_test):
    '''
    Sanity check closed caption
      - go to multi closed caption (40)
      - launch settings 
      - select closed caption 
      - change for CC1
      - go to fullscreen
      - verify CC1 is on screen
    :return:
    '''
    check = ve_test.assertmgr.addCheckPointLight
    check(ve_test.screens.fullscreen.navigate(),
            "Failed to go to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # go to channel 40 for ClosedCaption
    logging.info("Zap on channel number {}".format(CONSTANTS.channel_number_with_closed_caption))
    ve_test.screens.playback.dca(CONSTANTS.channel_number_with_closed_caption, with_ok=True)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT+ CONSTANTS.GENERIC_WAIT)

    channel_lcn = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"current_channel")

    check(channel_lcn == CONSTANTS.channel_number_with_closed_caption,
          "Initials Conditions: Zapping on channel n {0} fails, Current channel playing n {1}"
           .format(CONSTANTS.channel_number_with_closed_caption,channel_lcn))

    check(ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING",
            "Initials Conditions: Zapping on channel n {}, the video is not playing"
            .format(CONSTANTS.channel_number_with_closed_caption))

    check(ve_test.screens.main_hub.navigate(),
            "Failed to go to Main Hub. Current screen: %s" % ve_test.milestones.get_current_screen())

    check(ve_test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES"),
            "Failed to go to Settings. Milestone: %s" % ve_test.milestones.getElements())

    check(ve_test.screens.main_hub.select_settings_sub_sub_menu("CLOSED CAPTION", "CC1"),
            "Failed to go to CLOSED CAPTION -> CC1. Milestone: %s" % ve_test.milestones.getElements())

    check(ve_test.screens.fullscreen.navigate(),
            "Failed to go to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # checked if CC1 are displayed on screen
    playbackStatus = ve_test.milestones.getClientPlaybackStatus()
    ccTrack = playbackStatus['ccTrack']
    check(ccTrack['trackId'].lower() == CC_TRACKS['cc1'].lower(),
            "closed caption CC1 are not displayed on screen")




def internal_test_search_linear(ve_test):
    """
    Sanity check search
        - go to the search from Hub
        - perform a search for dedicated string
        - access to the search result
        - access to the action menu
        - go back to fullscreen
        :return:
    """
    check = ve_test.assertmgr.addCheckPointLight

    check(ve_test.screens.fullscreen.navigate(),
          "Failed to go to fullscreen. Current screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    channel_number = CONSTANTS.channel_number_classic_1
    logging.info("Zap to channel n %s" % channel_number)
    ve_test.screens.playback.dca(channel_number)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT + CONSTANTS.SCREEN_TIMEOUT)

    check(ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING",
          "Initials Conditions: Zapping on channel n %d, the video is not playing" % CONSTANTS.channel_number_classic_1)

    # Check that the search is able to find linear content
    status, error_to_display = ve_test.screens.fullscreen.wait_for_event_with_minimum_time_until_end(min_time_in_seconds=240)
    check(status, "Failed to wait for a correct event : {0}".format(error_to_display))

    event_title = ve_test.screens.fullscreen.get_current_event_title()
    if isinstance(event_title, bool):
        check(event_title,"Fail to retrieve the current event title: {0}".format(event_title))

    event_title_start = event_title.split(':')
    logging.info("Current event title: {0}".format(event_title))

    # Access to Search
    check(ve_test.screens.main_hub.navigate(),"Fail to go to Main Hub. Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    check(ve_test.screens.search.navigate(),
          "Fail to go to Search from Main Hub. Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    check(ve_test.screens.search.find_suggestion_contains(suggestion_string=str(event_title_start[0])),
            "Fail to have suggestion for: {0}".format(event_title_start))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    check(ve_test.screens.fullcontent.is_in_full_content(),
            "Failure to be in fullcontent. Screen: {0}".format(ve_test.milestones.get_current_screen()))

    logging.info("Access to Action Menu then come-back to search")
    check(ve_test.screens.action_menu.navigate(),
            "Fail to access to Action Menu from Fullcontent. Screen: {0}".format(ve_test.milestones.get_current_screen()))

    check(ve_test.screens.fullcontent.navigate(),
            "Fail to come-back from Action Menu to Fullcontent. Screen: {0}".format(ve_test.milestones.get_current_screen()))

    logging.info("Come-back to fullscreen")
    ve_test.go_to_previous_screen(wait_few_seconds=TIME_INTER_SCREEN)
    check(ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "search"),
            "Fail to go back to Search. Screen: {0}".format(ve_test.milestones.get_current_screen()))

    ve_test.go_to_previous_screen(wait_few_seconds=TIME_INTER_SCREEN)
    check(ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub"),
          "Fail to go back to Main Hub. Screen: {0}".format(ve_test.milestones.get_current_screen()))


    check(ve_test.screens.fullscreen.navigate(), "Fail to go back to Fullscreen. Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)


def internal_test_search_vod(ve_test):
    """
    Sanity check search
        - go to the search from Hub
        - perform a search for dedicated string
        - access to the search result
        - access to the action menu
        - go back to fullscreen
        :return:
    """
    check = ve_test.assertmgr.addCheckPointLight

    check(ve_test.screens.fullscreen.navigate(),
        "Failed to go to fullscreen. Current screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    asset_title = 'AWAKENING'
    logging.info("Asset's title to find: {0}".format(asset_title))
    # Access to Search
    check(ve_test.screens.main_hub.navigate(),
        "Fail to go to Main Hub. Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    check(ve_test.screens.search.navigate(),
        "Fail to go to Search from Main Hub. Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    check(ve_test.screens.search.find_suggestion_contains(suggestion_string=str(asset_title)),
        "Fail to find sugestion for asset Title: {0}".format(asset_title))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    check(ve_test.screens.fullcontent.is_in_full_content(),
        "Failure to be in fullcontent.  Screen: {0}".format(ve_test.milestones.get_current_screen()))

    logging.info("Access to Action Menu then come-back to search")
    check(ve_test.screens.action_menu.navigate(),
        "Fail to access to Action Menu from Fullcontent. Screen: {0}".format(ve_test.milestones.get_current_screen()))

    check(ve_test.screens.fullcontent.navigate(),
        "Fail to come-back from Action Menu to Fullcontent. Screen: {0}".format(ve_test.milestones.get_current_screen()))

    logging.info("Come-back to fullscreen")
    ve_test.go_to_previous_screen(wait_few_seconds=TIME_INTER_SCREEN)
    check(ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "search"),
        "Fail to go back to Search. Screen: {0}".format(ve_test.milestones.get_current_screen()))

    ve_test.go_to_previous_screen(wait_few_seconds=TIME_INTER_SCREEN)
    check(ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub"),
        "Fail to go back to Main Hub. Screen: {0}".format(ve_test.milestones.get_current_screen()))

    check(ve_test.screens.fullscreen.navigate(),
        "Fail to go back to Fullscreen. Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)


def internal_test_store_editorial_assets(ve_test):
    '''
    Sanity logout
      - begin to fullscreen go to the hub
      - launch store menu
      - Verify that the assets displayed in store menu come from editorial-content classification
    :return
    '''
    cmdc_assets_list = []
    store_assets_list = []

    # go to fullscreen
    status = ve_test.screens.fullscreen.navigate()
    ve_test.assertmgr.addCheckPoint("store_editorial_assets", 1, status, "Failed to go to fullscreen. "
                                                      "Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # Access to Search
    status = ve_test.screens.main_hub.navigate()
    ve_test.assertmgr.addCheckPoint("store_editorial_assets", 2, status, "Fail to go to Main Hub. "
                                                     "Screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # navigate to hub store
    status = ve_test.screens.main_hub.focus_store_item_in_hub()
    ve_test.assertmgr.addCheckPoint("store_editorial_assets", 3, status, "Failed to go to store. "
                                                      "Current screen: %s" % ve_test.milestones.get_current_screen())

    # Retrieve editorial contents from CMDC request:
    #Get CatalogId
    catId = ve_test.he_utils.getCatalogueId(ve_test.he_utils.platform)
    logging.info("CatalogueId : %s" % catId)
    ve_test.assertmgr.addCheckPoint("store_editorial_assets", 4, status, "No Catalogue ID found by CMDC")

    #Get Root ClassificationId from CatalogId
    rootclassId = ve_test.he_utils.get_rootClassificationID_from_catalogId(catId)
    logging.info("rootclassId : %s" % rootclassId)
    ve_test.assertmgr.addCheckPoint("store_editorial_assets", 5, status, "No root classification ID Found by CMDC")

    #Get Classification Type 41 in root classification from CatalogID and Root CatalogId
    #editorial classification type is 41
    classType41List = ve_test.he_utils.get_classification_from_catId_rootclassId_typeId(catId,rootclassId,41)
    ve_test.assertmgr.addCheckPoint("store_editorial_assets", 6, status, "No Classification type 41 in catalogue")

    #Get all assets ID & InstanceID of all 41 type classificationId from Classification List
    diccmdcassetsids,cmdc_assets_list = ve_test.he_utils.get_assetIds_from_classif_list(catId, classType41List)

    # Retrieve assets displayed to Store Menu
    #TECHNICAL DEBT: currently we cannot get contentId and contentInstanceId from UI. So we are going to use title instead
    assetName = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_asset")
    while assetName not in store_assets_list:  # loop to count assets
        logging.info("assetName: %s" % assetName)
        store_assets_list.append(assetName)
        ve_test.move_towards('right',1)        # next asset
        assetName = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_asset")   # next asset

    #Hub Store should contain editorial assets, but if not any, we also use toplist assets
    #So if cmdc assets list is bigger than the one displayed, it means that all assets displayed should belong to cmdc assets list
    #in the opposite, all items from cmdc assets list should be displayed on store
    nb=7 #count for assertManager checkpoint
    if len(cmdc_assets_list) > len(store_assets_list):
        for asset in store_assets_list:
            status = asset in cmdc_assets_list
            ve_test.assertmgr.addCheckPoint("store_editorial_assets", nb, status, "%s does not belong to cmdc editorial assets list" % asset)
            nb += 1
    else:
        for asset in cmdc_assets_list:
            status = asset in store_assets_list
            ve_test.assertmgr.addCheckPoint("store_editorial_assets", nb, status, "%s does not belong to Hub Store assets list" % asset)
            nb += 1

    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    print "<ul>"
    print "<li> 'store editorial assets' performed </li>"
    print "</ul>"


def internal_test_logout(ve_test):
    '''
    Sanity logout
      - begin to fullscreen go to the hub
      - launch settings 
      - select system and then log out
      - change for yes
      - wait
      - verify authentification screen
    :return
    '''

    # go to fullscreen
    status = ve_test.screens.fullscreen.navigate()
    ve_test.assertmgr.addCheckPoint("test_logout", 1, status, "Failed to go to fullscreen. "
                                                      "Current screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # navigate to settings and to logout
    #
    ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_settings_sub_menu("SYSTEM_INFORMATION")
    ve_test.assertmgr.addCheckPoint("test_logout", 2, status, "Failed to go to SYSTEM INFORMATION. Current screen: {0}"
                                    .format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    # Select the No choice of Log out. We should go back to Hub.
    status = ve_test.screens.main_hub.select_settings_sub_sub_menu("LOG OUT", "No", check_selected_asset=False)
    ve_test.assertmgr.addCheckPoint("test_logout", 3, status, "Failed to go to LOG OUT. "
                                                      "Current screen: {0}".format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    current_screen =  ve_test.milestones.get_current_screen()
    ve_test.assertmgr.addCheckPoint("test_logout", 4, current_screen == "main_hub",
                                    "Failed to go to hub screen. Current screen: {0}".format(current_screen))

    # Select the Yes choice of Log out. We should go back to Hub.
    status = ve_test.screens.main_hub.navigate_to_settings_sub_menu("SYSTEM_INFORMATION")
    ve_test.assertmgr.addCheckPoint("test_logout", 5, status, "Failed to go to SYSTEM INFORMATION. Current screen: {0}"
                                    .format(ve_test.milestones.get_current_screen()))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    status = ve_test.screens.main_hub.select_settings_sub_sub_menu("LOG OUT", "Yes", check_selected_asset=False)
    ve_test.assertmgr.addCheckPoint("test_logout", 6, status, "Failed to select yes for LOG OUT. ")

    # check login  screen is displayed
    ve_test.wait(5*CONSTANTS.GENERIC_WAIT)
    current_screen =  ve_test.milestones.get_current_screen()
    ve_test.assertmgr.addCheckPoint("test_logout", 7, current_screen == "login",
                                    "Failed to go to login screen. Current screen: {0}".format(current_screen))
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    
    print "<ul>"
    print "<li> 'logout' performed </li>"
    print "</ul>"


def launch_test(ve_test, test_function, param, test_name, pretty_performed_test):
    ve_test.assertmgr.setup(test_name)
    try:
        if param is None:
            test_function(ve_test)
        else:
            test_function(ve_test, param)
    except AssertMgr.Failure:
        ve_test.log("aborting %s" % test_name)
    finally:
        ve_test.screens.fullscreen.navigate()
        ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    print "<ul>"
    print "<li> '%s' performed </li>" % pretty_performed_test
    print "</ul>"


@pytest.mark.light_sanity
@pytest.mark.ethernet
@pytest.mark.LV_L1
def test_sanity_ethernet():
    ve_test = VeTestApi("Sanity", useAssertMgr=True)
    launch_test(ve_test, internal_boot_with_drm, None, 'test_boot_with_drm', 'boot with drm')
    launch_test(ve_test, internal_zapping_video, TIME_ETHERNET_ZAPPING, 'test_zapping_video', 'zapping video')
    internal_test_vod(ve_test)
    launch_test(ve_test, internal_test_hub_navigation, None, 'test_hub_navigation', 'hub navigation')
    internal_test_parental_control(ve_test)
    internal_test_zaplist(ve_test)
    internal_test_timeline(ve_test)
    internal_test_actionmenu_ltv_fullscreen(ve_test)
    internal_test_actionmenu_ltv_timeline(ve_test)
    launch_test(ve_test, internal_test_multiAudio, None, 'test_multiAudio', 'multi Audio')
    launch_test(ve_test, internal_test_closedCaption, None, 'test_closeCaption', 'closed caption')
    launch_test(ve_test, internal_test_dvbsub, None, 'test_dvbsub', 'dvbsub')
    launch_test(ve_test, internal_test_search_linear, None, 'search_linear', 'linear search')
    launch_test(ve_test, internal_test_search_vod, None, 'search_vod', 'vod search')
    internal_test_store_editorial_assets(ve_test)
    internal_test_logout(ve_test)
    ve_test.assertmgr.verifyAllCheckPoints()
    ve_test.end()


@pytest.mark.light_sanity
@pytest.mark.wifi
@pytest.mark.LV_L1
def test_sanity_wifi():
    ve_test = VeTestApi("Sanity", useAssertMgr=True)
    launch_test(ve_test, internal_boot_with_drm, None, 'test_boot_with_drm', 'boot with drm')
    launch_test(ve_test, internal_zapping_video, TIME_WIFI_ZAPPING, 'test_zapping_video', 'zapping video')
    internal_test_vod(ve_test)
    launch_test(ve_test, internal_test_hub_navigation, None, 'test_hub_navigation', 'hub navigation')
    internal_test_parental_control(ve_test)
    internal_test_zaplist(ve_test)
    internal_test_timeline(ve_test)
    internal_test_actionmenu_ltv_fullscreen(ve_test)
    internal_test_actionmenu_ltv_timeline(ve_test)
    launch_test(ve_test, internal_test_multiAudio, None, 'test_multiAudio', 'multi Audio')
    launch_test(ve_test, internal_test_closedCaption, None, 'test_closeCaption', 'closed caption')
    launch_test(ve_test, internal_test_dvbsub, None, 'test_dvbsub', 'dvbsub')
    launch_test(ve_test, internal_test_search_linear, None, 'search_linear', 'linear search')
    launch_test(ve_test, internal_test_search_vod, None, 'search_vod', 'vod search')
    internal_test_store_editorial_assets(ve_test)
    internal_test_logout(ve_test)
    ve_test.assertmgr.verifyAllCheckPoints()
    ve_test.end()


@pytest.mark.ethernet
@pytest.mark.LV_PRTests
def test_PRtests_ethernet():
    ve_test = VeTestApi("PRTests", useAssertMgr=True)
    launch_test(ve_test, internal_boot_with_drm, None, 'test_boot_with_drm', 'boot with drm')
    launch_test(ve_test, internal_zapping_video, TIME_ETHERNET_ZAPPING, 'test_zapping_video', 'zapping video')
    launch_test(ve_test, internal_test_hub_navigation, None, 'test_hub_navigation', 'hub navigation')
    internal_test_zaplist(ve_test)
    internal_test_timeline(ve_test)
    internal_test_actionmenu_ltv_fullscreen(ve_test)
    internal_test_actionmenu_ltv_timeline(ve_test)
    ve_test.assertmgr.verifyAllCheckPoints()
    ve_test.end()


@pytest.mark.wifi
@pytest.mark.LV_PRTests
def test_PRtests_wifi():
    ve_test = VeTestApi("PRTests", useAssertMgr=True)
    launch_test(ve_test, internal_boot_with_drm, None, 'test_boot_with_drm', 'boot with drm')
    launch_test(ve_test, internal_zapping_video, TIME_WIFI_ZAPPING, 'test_zapping_video', 'zapping video')
    launch_test(ve_test, internal_test_hub_navigation, None, 'test_hub_navigation', 'hub navigation')
    internal_test_zaplist(ve_test)
    internal_test_timeline(ve_test)
    internal_test_actionmenu_ltv_fullscreen(ve_test)
    internal_test_actionmenu_ltv_timeline(ve_test)
    ve_test.assertmgr.verifyAllCheckPoints()
    ve_test.end()
