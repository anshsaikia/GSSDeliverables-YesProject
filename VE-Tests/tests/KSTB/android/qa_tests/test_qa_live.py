__author__ = 'Oceane Team'

import pytest
import logging

from datetime import datetime
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.milestones.milestones_kpi_client import CC_TRACKS
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests.KSTB.android.e2e_tests.test_unitary_search_results import check_alphanumerical_sorting
from tests.KSTB.android.e2e_tests.test_ui_program_schedule_format import check_format,is_today_format
from tests.KSTB.android.e2e_tests.test_unitary_timeline import check_playback_state_playing


MAX_INTERVAL_TIME = 12  # max event duration 


#########################################################
#                     PRIVATES Functions                #
#########################################################
def zapping_by_dca(test,channel_id,check_playback=False):
    """
    private function, zapping by dca
    :param test: the current test instance
    :param channel_id: channel id
    :param check_playback: to check if playback is playing
    :return : None
    """

    test.screens.playback.dca(channel_id, with_ok=True)
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT)  # wait a few for the zap to exit fullscreen to go to infolayer
    test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, "fullscreen")  # wait for the end of infolayer
    cur_chan = test.screens.fullscreen.get_current_channel()  # must be on the good channel
    test.log_assert((cur_chan == channel_id),"Fail to zap by dca on service id %s" % str(channel_id))

    if check_playback :
        check_playback_state_playing(test)

def get_playback_audios(test):
    """
    private function, get audios available on service
    :param test: the current test instance
    :return: audios available on service
    """

    audios_playback = test.screens.action_menu.retrieve_audio_languages()
    audio_string = test.screens.action_menu.convert_languages_to_id_isocode_string(audios_playback)
    available_audios = test.screens.action_menu.get_languages(audios_playback)
    logging.info("LIVE-TV:AUDIO : available audios  %s" % audio_string )

    return available_audios

def get_playback_audio(test):
    """
    private function, get current audio playback
    :param test: the current test instance
    :return: current audio playback
    """

    audio=None
    request = test.milestones.getPlaybackStatus()
    if 'playbackStreams' in request:
        # current audio on stream
        audio_key=request['playbackStreams'][1]['language']
        if audio_key is not None and audio_key in CONSTANTS.dico_languages :
            audio=CONSTANTS.dico_languages[audio_key]

    return audio

def get_audio_select(test,audios_available):
    """
    private function, get selected audio
    :param test: the current test instance
    :param audios_available: audios available on service
    :return: selected audio
    """

    audio_select=None
    for _i in range(len(audios_available)):
        all_elements = test.milestones.getElements()
        focused_audio = test.screens.action_menu.get_focused_asset()
        if focused_audio and test.milestones.get_value_by_key(all_elements,"isSelected") == "true":
            audio_select = focused_audio
            break
        else:
            test.move_towards("right")

    return audio_select

def check_audio_display_list(test, audios_available):
    """
    private function, check audios on ui matches with audio list
    :param test: the current test instance
    :param audios_available: audios available on service
    :return: None
    """

    test.log_assert((len(audios_available) == test.screens.action_menu.get_menu_nb_audio()),"LIVE-TV:AUDIO audio available : "+str(audios_available)+" audio display in action menu: " +str(test.screens.action_menu.get_menu_audio_items()))
    check_audio_name_list = list(set(test.screens.action_menu.get_menu_audio_items()) - set(audios_available))
    test.log_assert(( len(check_audio_name_list) == 0 ),"LIVE-TV:AUDIO audio available :" + str(audios_available) + " audio display : " + str(test.screens.action_menu.get_menu_audio_items()))

def check_audio_selected(test,audios_available,expected_audio):
    """
    private function, check audio selected match with audio expected and audio playback
    :param test: the current test instance
    :param audios_available: audios available on service
    :param expected_audio: audio expected
    :return: None
    """

    # audio_select from action menu
    audio_select = get_audio_select(test, audios_available)
    if audio_select is None:
        test.log_assert(False, "LIVE-TV:AUDIO No audio selected")

    # audio playback
    audio_playback = get_playback_audio(test)
    if audio_playback is None:
        test.log_assert(False, "LIVE-TV:AUDIO audio playback is None")

    logging.info("LIVE-TV:AUDIO   expected audio %s select audio %s playback audio %s " % (expected_audio, audio_select, audio_playback))

    # check coherence
    if expected_audio is None and audio_select != audio_playback:
        test.log_assert(False,"LIVE-TV:AUDIO : audio_select: " + audio_select + " audio_playback: " + audio_playback)

    if expected_audio is not None and audio_select != expected_audio or  audio_select != audio_playback:
        test.log_assert(False,"LIVE-TV:AUDIO : audio_select: "+audio_select+" audio_playback: "+audio_playback+" audio expected: "+expected_audio)


def action_menu_audio_display(test,audios_available,expected_audio):
    """
    private function, checks audio list and audio selected in action menu
    :param test: the current test instance
    :param audios_available: audios available on service
    :param expected_audio: audio expected
    :return: None
    """

    status = test.screens.action_menu.navigate()
    test.log_assert(status,"LIVE-TV:AUDIO fullscreen ---> ActionMenu. Current screen: "+str(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    status = test.screens.action_menu.navigate_to_action(CONSTANTS.A_LANGUAGE)
    test.log_assert(status,"LIVE-TV:AUDIO ActionMenu ---> languages. Current screen: "+str(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    check_audio_display_list(test,audios_available)
    check_audio_selected(test,audios_available,expected_audio)

    status = test.go_to_previous_screen()
    test.log_assert(status,"LIVE-TV:AUDIO ActionMenu language ---> fullscreen. Current screen: "+str(test.milestones.get_current_screen()))

    test.wait(CONSTANTS.GENERIC_WAIT)

def setting_select_audio_display(test,audio_select):
    """
    private function, select audio on setting
    :param test: the current test instance
    :param audio_select: audio selected
    :return: None
    """

    status = test.screens.main_hub.navigate() #.screens.main_hub.navigate()
    if not status:
        test.log_assert( False, "can not find main_hub menu")
    status = test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES")
    if not status:
        test.log_assert( False, "can not find settings menu")
    status = test.screens.main_hub.select_settings_sub_sub_menu("AUDIO",audio_select)
    if not status:
        test.log_assert( False, "can not find AUDIO menu")

    test.log_assert(status, "LIVE-TV:AUDIO fullscreen ---> setting audio. Current screen: " + str(test.milestones.get_current_screen()) + " audio to select: " + audio_select )
    test.screens.fullscreen.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)

def get_time_event_from_action_menu(test):
    """
    private function, get time event and check time event format from action menu
    :param test: the current test instance
    :return: True if duration could be calculate
    """

    start_time = ""
    end_time = ""
    duration = -1

    status, schedule_string = check_format(test, is_today_format)
    if status:
        itv = schedule_string.split(' ')        # ex: 2.20 PM 4.50 PM
        if len(itv) == 4:
            if 12 <= float(itv[0]) <= 12.59 :   # ex: 12.50 
                itv[0] = str (int(itv[0]) - 12)
                itv[1] = " PM"                  # now 0.50 PM
            if 12 <= float(itv[2]) <= 12.59 :   # ex: 12.25 
                itv[2] = str (int(itv[2]) - 12)
                itv[3] = " PM"                  # now 0.25 PM
            
            if itv[1] == "":
                if itv[2] > itv[0]:             # ex: 1.20  1.30 PM
                    itv[1] = itv[3]             # now 1.20 PM 1.30 PM
                else: 
                    if itv[3] == "PM":          # ex: 11.15  1.30 PM
                        itv[1] = "AM"
                    else:                       # ex: 11.20 PM 1.30 AM
                        itv[3] = "PM"
                        itv[1] = "AM"           # now 11.20 AM 1.30 PM

            
            start_time = itv[0] + " " + itv[1]
            end_time = itv[2] + " " + itv[3]

            tdelta = datetime.strptime(end_time, '%H.%M %p') - datetime.strptime(start_time, '%H.%M %p')
            if int(tdelta.total_seconds() / 3600) > MAX_INTERVAL_TIME:
                logging.error("check interval time event seems too long duration %d !!! ",int(tdelta.total_seconds() / 3600))
            duration = int(tdelta.total_seconds() / 60)
        else:
            status=False

    logging.info("- Action Menu: startTime %s endTime %s duration %s", start_time, end_time, duration)

    return status, duration

def to_focusnow_in_timeline(test, max_event_display=5, wait_few_seconds=1):
    """
    private function, navigate to focus now in time line
    :param test: the current test instance
    :param max_event_display: number of event time display
    :param wait_few_seconds: delay for move previous item in time line
    :return: True when focused is on event now
    """

    focus_now = False
    if test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "timeline"):
        cpt = 0
        focus_now = test.screens.timeline.is_focused_on_current_event()

        while (focus_now == False and cpt < max_event_display):
                test.move_towards(direction="left", wait_few_seconds=wait_few_seconds)
                focus_now = test.screens.timeline.is_focused_on_current_event()
                cpt += 1

    else:
        logging.info("failed to move focus on now : wait for timeline timed out")

    return focus_now

def to_timeline_from_actionmenu(test,check_data=False,expected_logo=None, expected_title=None):
    """
    private function, dismisses the action menu with Back key, check data logo and title
    :param test:
    :param check_data:
    :param expected_logo:
    :param expected_title:
    :return:
    """
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")

    if not status:
        logging.error("wait for action_menu timed out")
        return False

    logging.info("In action_menu")

    data_match = not check_data
    #logging.info("to_timeline_from_actionmenu data_match %s check_data %s " % (str(data_match), str(check_data)))
    if check_data :
        if expected_logo is not None and expected_title is not None:
            logging.info("check expected_logo %s expected_title %s " % (expected_logo,expected_title))
            data_match = test.screens.action_menu.check_action_menu_logo_title(expected_logo,expected_title)
        #logging.info(" check data to time line event and action menu status: %s " % str(data_match))

    test.go_to_previous_screen()
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "timeline")
    #logging.info(" Go Back to time line from action menu status: %s " % str(status))

    if not status or not data_match :
        logging.error("wait for timeline timed out")
        return False
    logging.info("In timeline")

    return status

def check_navigate_event_in_timeline(test, max_event_display=5, check_data=False):
    """
    private function, navigate to next event in time line
    :param test: the current test instance
    :param max_event_display: max event display in time line
    :param check_data: flag to check or not logo and title of event
    :return: True when focused on next event and all time line event are visited
    """
    move_event_status = True
    action_menu_status=True
    cpt = 0

    while (move_event_status and action_menu_status and cpt < max_event_display):

            move_event_status = test.screens.timeline.to_nextevent()

            all_elements = test.milestones.getElements()
            focused_event_name = test.milestones.get_value_by_key(all_elements,"focused_event_id")
            expected_channel_logo = test.milestones.get_value_by_key(all_elements,"focused_channel_logo")
            expected_event_title  = test.milestones.get_value_by_key(all_elements,"focused_event_title")

            if move_event_status :
                all_elements = test.milestones.getElements()
                focused_event = test.milestones.get_value_by_key(all_elements, "focused_event_id")
                expected_channel_logo = test.milestones.get_value_by_key(all_elements, "focused_channel_logo")
                expected_event_title = test.milestones.get_value_by_key(all_elements, "focused_event_title")
                
                test.log_assert((expected_channel_logo is not None and expected_event_title is not None),"LIVE-TV:TIMELINE no logo or title on time line")

                logging.info("- navigate event time line: move %d logo %s title %s on time line",cpt , expected_channel_logo, expected_event_title )

                test.validate_focused_item(CONSTANTS.SMALL_WAIT)
                status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
                test.log_assert(status, "LIVE-TV:TIMELINE Fail to go in action menu ")

                status = test.screens.action_menu.check_action_menu_logo_title(expected_channel_logo, expected_event_title)
                test.log_assert(status, "LIVE-TV:TIMELINE  logo and title from time line doesn't match with logo and title in action menu")

                status, duration = get_time_event_from_action_menu(test)

                test.log_assert(status,"LIVE-TV:TIMELINE fail check format time event ")
                if  cpt > 0 :
                    test.log_assert((status and duration >= 0),"LIVE-TV:TIMELINE fail check format time event or the events do not follow in time")

                test.go_to_previous_screen()

                status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "timeline")
                test.log_assert(status, "LIVE-TV:TIMELINE Fail to go back on timeline screen")

                back_focus_event = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_event_id")

                if (back_focus_event is not None and focused_event is not None) and (back_focus_event == focused_event) :
                    logging.info("success action menu from time line focus event %s " % focused_event)
                else:
                    action_menu_status = False
                    logging.error("fail back to focus event ")

            cpt += 1

    return (cpt == max_event_display and move_event_status and action_menu_status )


def check_duration_display(test,expected_duration):
    """
    private function, check event duration
    :param test: the current test instance
    :param expected_duration : expected duration.  string containing time in minutes
    :return: True if duration from milestones infolines is equal to expected duration
    """
    elements = test.milestones.getElements()
    title_items = test.milestones.get_value_by_key(elements, "infolines")
    title_array = title_items[1:-1].split(",")
    
    logging.info("check_duration_display {}: title_array= {}".format(expected_duration,title_array))
    
    #status = [item == expected_duration for item in title_array if " MIN" in item and item.split(' ')[1] == "MIN"]
    infolin_time = ""
    for item in title_array:
        logging.info("check  item '%s' in title:"%item)
        if " MIN" in item:
            l_parts = item.strip().split(' ')
            if l_parts[1] == "MIN" and len(l_parts)==2:
                infolin_time = item.strip()
                logging.info("add time:" + infolin_time)
    
    status = ( infolin_time == expected_duration )
    return status

#########################################################
#                     DOCUMENTATION FUNCTIONS           #
#########################################################
# Functions below are here for documentation pupose only.
# The goal of this is to centralize documentation of QA tests
# using tests from other testLevels (L1/L2/L3).
# Documentation is automatically generated here :
# http://ubu-iptv01.cisco.com/dropbox/Android_sf_k_stb_QA_Tests_doc

def doc_test_qa_live_timeline_timeout():
    """ TEST : Verify that the Timeline is no longer display after timeout from last user interaction

    executes test from :
    e2e_tests/test_unitary_timeline.py:test_timeline_timeout()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_live

    """


#########################################################
#                       TESTS Functions                 #
#########################################################

@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_close_caption
def test_qa_live_close_caption():
    """
    TEST: test close caption activation on current program

     1st step : select live channel with close caption tracks
        Action
        - got to live channel with close caption
        Checkup
        - check no cc is active by default

     2nd step : change cc from None to CC1
        Action
        - got to close caption setting menu and activate CC1
        Checkup
        - check CC1 track is selected on live channel

     3rd step : change cc from CC1 to None
        Action
        - got to close caption setting menu and de-activate CC1 (None)
        Checkup
        - check no cc is active
    """
    logging.info("##### BEGIN test_qa_live_close_caption #####")

    ############
    # init test data
    test_close_caption = VeTestApi("test_qa_live_close_caption")
    test_close_caption.begin(screen=test_close_caption.screens.fullscreen)

    hhid = test_close_caption.he_utils.get_default_credentials()[0]
    logging.info("current hhid is : " + hhid)

    ############
    ''' 1st step : select live channel with close caption tracks
        Action
        - got to live channel with close caption
        Checkup
        - check no cc is active by default
    '''
    test_close_caption.screens.playback.dca(CONSTANTS.channel_number_with_closed_caption, with_ok=True)
    test_close_caption.wait(CONSTANTS.INFOLAYER_TIMEOUT)
    test_close_caption.wait(CONSTANTS.GENERIC_WAIT)

    playbackStatus = test_close_caption.milestones.getClientPlaybackStatus()
    
    logging.info("playbackStatus: %s"%(str(playbackStatus))) # debug 
    
    ccTrack = playbackStatus['ccTrack']
    errorMessage = "LIVE_TV/Close Caption - step 1: current close caption track is " + str(ccTrack['trackId']) + " but None is expected."
    test_close_caption.log_assert(ccTrack['trackId'] == CC_TRACKS['off'], errorMessage)
    if str(ccTrack['trackId']) == "":
        logText = "None"
    else:
        logText = str(ccTrack['trackId'])
    logging.info("step 1: current close caption track is " + logText)

    ############
    ''' 2nd step : change cc from None to CC1
        Action
        - got to close caption setting menu and activate CC1
        Checkup
        - check CC1 track is selected on live channel
    '''

    test_close_caption.screens.main_hub.navigate() #.screens.main_hub.navigate()
    test_close_caption.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES")
    status = test_close_caption.screens.main_hub.select_settings_sub_sub_menu("CLOSED CAPTION", "CC1")
    test_close_caption.log_assert(status, "fail to select CC1")

    ## go back to fullscreen
    status = test_close_caption.screens.fullscreen.navigate()
    errorMessage = "navigation from CC setting to live failed"
    test_close_caption.log_assert(status, errorMessage)
    logging.info(errorMessage)

    test_close_caption.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # checked if CC1 are displayed on screen
    playbackStatus = test_close_caption.milestones.getClientPlaybackStatus()
    
    logging.info("playbackStatus: %s"%(str(playbackStatus))) # debug 
    ccTrack = playbackStatus['ccTrack']
    errorMessage = "LIVE_TV/Close Caption - step 2 : current close caption track is " + str(ccTrack['trackId']) + " but cc1 is expected."
    test_close_caption.log_assert(ccTrack['trackId'].lower() == CC_TRACKS['cc1'], errorMessage)
    if str(ccTrack['trackId']) == "":
        logText = "None"
    else:
        logText = str(ccTrack['trackId'])
    logging.info("step 1: current close caption track is " + logText)

    ############
    ''' 3rd step : change cc from CC1 to None
        Action
        - got to close caption setting menu and de-activate CC1 (None)
        Checkup
        - check no cc is active
    '''

    test_close_caption.screens.main_hub.navigate() #.screens.main_hub.navigate()
    test_close_caption.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES")
    test_close_caption.screens.main_hub.select_settings_sub_sub_menu("CLOSED CAPTION", "None")

    ## go back to fullscreen
    status = test_close_caption.screens.fullscreen.navigate()
    errorMessage = "Step 3 : navigation from CC setting to live failed"
    test_close_caption.log_assert(status, errorMessage)
    logging.info(errorMessage)

    test_close_caption.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # checked no CC active
    playbackStatus = test_close_caption.milestones.getClientPlaybackStatus()
    ccTrack = playbackStatus['ccTrack']
    playbackStatus = test_close_caption.milestones.getClientPlaybackStatus()
    errorMessage = "LIVE_TV/Close Caption - step 4: current close caption track is " + str(ccTrack['trackId']) + " but None is expected."
    test_close_caption.log_assert(ccTrack['trackId'] == CC_TRACKS['off'], errorMessage)
    if str(ccTrack['trackId']) == "":
        logText = "None"
    else:
        logText = str(ccTrack['trackId'])
    logging.info("current close caption track is " + logText)

    logging.info("##### End test_qa_live_close_caption #####")
    test_close_caption.end()

    ############

@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_live_audio
def test_qa_live_audio():
    """
    TEST: check audio selection on current program
    TEST NOT ACTIVATED : reason to be specified here (defect ?)

     1st step : go to action menu language
        Action
        - select audio
        Checkup
        - check audio selected is audio playback
        - check all audio has been selected

     2st step : go to action menu language
        Action
        - change default language
        Checkup
        - check default language is recovered after a zapping

    """
    logging.info("##### BEGIN test_qa_live_audio #####")

    test_title = "test_qa_live_audio"
    test = VeTestApi(title=test_title)

    test.begin(screen=test.screens.fullscreen)

    test.he_utils.setParentalRatingThreshold(test.he_utils.getHhId(), CONSTANTS.MAX_THRESHOLD_UPM)
    zapping_by_dca(test, channel_id=CONSTANTS.channel_number_with_several_audio)

    """ 1st step : go to action menu language
        Action
        - select audio
        Checkup
        - check audio selected is audio playback
        - check all audio has been selected
    """

    audios_available= get_playback_audios(test)
    test.log_assert(len(audios_available) > 1,"LIVE-TV:AUDIO : No multi audio language available on service %s " % CONSTANTS.channel_number_with_several_audio )

    previous_audio_playback = get_playback_audio(test)
    if previous_audio_playback is None:
        test.log_assert(False,"LIVE-TV:AUDIO audio playback is None ")

    #
    list_languages=['English']
    translate_languages=['LANGUAGES']
    translate_langue=['LANGUAGE']

    for idl in range(len(list_languages)):
            test.screens.main_hub.navigate()
            test.log_assert(test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES"),"LIVE-TV:AUDIO Failed to go to Settings. Milestone: %s" % test.milestones.getElements())
            test.log_assert(test.screens.main_hub.select_settings_sub_sub_menu(translate_langue[idl],list_languages[idl]), "Failed to go to LANGUAGE -> English. Milestone: %s " % test.milestones.getElements())
            test.log_assert(test.screens.fullscreen.navigate(), "LIVE-TV:AUDIO Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())
            test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

            test.log_assert(test.screens.action_menu.navigate(), "LIVE-TV:AUDIO fullscreen ---> ActionMenu. Current screen: " + test.milestones.get_current_screen())
            test.wait(CONSTANTS.GENERIC_WAIT)
            test.log_assert(test.screens.action_menu.navigate_to_action(translate_languages[idl]),"LIVE-TV:AUDIO ActionMenu ---> languages. Current screen: " + test.milestones.get_current_screen())
            test.wait(CONSTANTS.GENERIC_WAIT)

            check_audio_display_list(test, audios_available)

            logging.info("LIVE-TV:AUDIO --- > check all audio language in action menu ")

            audios_available_check=[]

            for ida in range(len(audios_available)):
                elements = test.milestones.getElements()
                current_focused_audio_language = test.screens.action_menu.get_focused_asset()
                audio_playback = get_playback_audio(test)
                logging.info("- loop current item %s current screen %s", test.screens.action_menu.get_focused_asset(), str(test.milestones.get_current_screen()))
                if audio_playback is not None :
                    logging.info("- loop indice %d audio playback %s audio focus %s selected %s ", ida, audio_playback,current_focused_audio_language, test.milestones.get_value_by_key(elements,"isSelected"))
                    if ( current_focused_audio_language == audio_playback ) and (test.milestones.get_value_by_key(elements,"isSelected") == "true" ):
                        audios_available_check.append(current_focused_audio_language)
                        test.move_towards("right")
                        test.validate_focused_item(CONSTANTS.SMALL_WAIT)
                    elif test.milestones.get_value_by_key(elements,"isSelected") != "true" :
                        test.validate_focused_item(CONSTANTS.SMALL_WAIT)
                else :
                    test.log_assert(False, "LIVE-TV:AUDIO audios playback is None during move and select audio in action menu "+str(audios_available[ida]))

            audio_not_check = list(set(audios_available) - set(audios_available_check))
            test.log_assert((len(audio_not_check) == 0),"LIVE-TV:AUDIO audios language available not check "+str(audio_not_check))
            logging.info("LIVE-TV:AUDIO : audio check : %s " % audios_available_check)
            test.go_to_previous_screen()


    """ 2st step : go to action menu language
            Action
            - change default language
            Checkup
            - check default language is recovered after a zapping
    """

    test.log_assert(test.screens.action_menu.navigate(),"LIVE-TV:AUDIO fullscreen ---> ActionMenu. Current screen: "+str(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    test.log_assert(test.screens.action_menu.navigate_to_action(translate_languages[idl]), "LIVE-TV:AUDIO ActionMenu ---> languages. Current screen: " + str(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("LIVE-TV:AUDIO : - check local language is lost after zapping")
    current_focused_audio_language = test.screens.action_menu.get_focused_asset()
    logging.info("LIVE-TV:AUDIO : previous_audio_playback %s current_focused_audio_language %s isSelected %s " % (previous_audio_playback,current_focused_audio_language,str(test.milestones.get_value_by_key(test.milestones.getElements(),"isSelected"))))
    if (previous_audio_playback == current_focused_audio_language) and (test.milestones.get_value_by_key(test.milestones.getElements(),"isSelected") == "true" ):
        test.move_towards("right")
        test.validate_focused_item(CONSTANTS.SMALL_WAIT)
        if current_focused_audio_language != test.screens.action_menu.get_focused_asset() and test.milestones.get_value_by_key(test.milestones.getElements(),"isSelected") == "true" :
            test.go_to_previous_screen(wait_few_seconds=1)
            test.log_assert(test.screens.fullscreen.to_previouschannel_in_fullscreen(CONSTANTS.WAIT_TIMEOUT),"LIVE-TV:AUDIO Failed to zap on previous channel  ")
            test.log_assert(test.screens.fullscreen.to_nextchannel_in_fullscreen(CONSTANTS.WAIT_TIMEOUT), "LIVE-TV:AUDIO Failed to zap on next channel " )
            test.wait(CONSTANTS.GENERIC_WAIT)
            action_menu_audio_display(test, audios_available, previous_audio_playback)
        else:
            test.go_to_previous_screen(wait_few_seconds=1)
            test.log_assert(False,"LIVE-TV:AUDIO validate next audio from :" +previous_audio_playback+" failed " )
    else:
        test.go_to_previous_screen(wait_few_seconds=1)
        test.log_assert(False,"LIVE-TV:AUDIO audio "+ previous_audio_playback+" should be selected " )


    logging.info("##### End test_qa_live_audio #####")
    test.end()


@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_live_audio
def test_qa_live_audio_preferred():
    """
    TESTS: check prefered audio selection on current program

     1st step : go to multi service audio
        Action
        - zapping on multi service
        Checkup
        - check multi audio are available on service

     2st step : go to action menu language
        Action
        - display action menu
        Checkup
        - check preferred audio is select and play if audio is available
        - change preferred audio language and check audio is selected and play

     3st step : go to action menu language
        Action
        - select a not valid audio language on setting
        Checkup
        - check first audio on manifest is select and play if audio is available

    """
    logging.info("##### BEGIN QA_live_audio_preferred #####")

    check_messages = []

    test_title = "test_qa_live_audio_preferred"
    test = VeTestApi(title=test_title)
    assertmgr = AssertMgr(test)
    logging.info("================ Live TV : start test live audio preferred ===============")
    test.begin(screen=test.screens.fullscreen)
    test.he_utils.setParentalRatingThreshold(test.he_utils.getHhId(), CONSTANTS.MAX_THRESHOLD_UPM)

    zapping_by_dca(test, channel_id=CONSTANTS.channel_number_with_several_audio)

    ''' 1st step : go to multi service audio
        Action
        - zapping on multi service
        Checkup
        - check multi audio are available on service
    '''
    audios_available = get_playback_audios(test)
    logging.info(" -- audios available %s %d" % (audios_available,len(audios_available)))
    test.log_assert( (len(audios_available) > 1) , "LIVE-TV:AUDIO No multi audio language available on service " +str(CONSTANTS.channel_number_with_several_audio))

    ''' 2st step : go to action menu language
        Action
        - display action menu
        Checkup
        - check preferred audio is select and play if audio is available
        - change preferred audio language and check audio is selected and play
    '''
    p_audio_key = test.he_utils.getAudioLanguage()
    p_audio = []
    if p_audio_key is not None:
        p_audio.append(CONSTANTS.dico_languages[p_audio_key])

    # we check preferred on enter channel number
    if len(list(set(audios_available) & set(p_audio))) :
        logging.info("LIVE-TV:AUDIO --- > Check Preferred Audio ( audio selected on display should be audio preferred %s ) "% p_audio)
        action_menu_audio_display(test,audios_available, p_audio[0])
        check_messages.append( "- check preferred is currently selected when we go on multi language service \n")
    else:
        logging.info("LIVE-TV:AUDIO on your tenant we should not pass here")

    # we check another preferred
    p_other_audio = audios_available[1]
    if len(p_audio) and audios_available[1] == p_audio[0] :
        p_other_audio = audios_available[0]

    logging.info( "LIVE-TV:AUDIO --- > Check change preferred audio on setting ( audio selected on display should be audio preferred %s ) " % p_other_audio)

    setting_select_audio_display(test,p_other_audio)
    action_menu_audio_display(test, audios_available,p_other_audio)
    check_messages.append("- check change preferred on setting corectly done \n")

    ''' 3st step : go to action menu language
        Action
        - select a not valid audio language on setting
        Checkup
        - check first audio on manifest is select and play if audio is available
    '''

    # check first audio on manifest is selected and play list_audio_languages
    audios_not_available = list(set([x.upper() for x in CONSTANTS.list_audio_language_eng]) ^ set(audios_available))

    if audios_not_available > 0:
        logging.info("LIVE-TV:AUDIO ---> check with preferred selected not available %s (first audio available %s should be selected) " % (audios_not_available[0],audios_available[0]) )
        setting_select_audio_display(test,audios_not_available[0])
        status = test.screens.fullscreen.to_previouschannel_in_fullscreen(CONSTANTS.WAIT_TIMEOUT)
        status = test.screens.fullscreen.to_nextchannel_in_fullscreen(CONSTANTS.WAIT_TIMEOUT)
        test.log_assert(status, "LIVE-TV:AUDIO Zapping Error on go back to channel multi audio " + str(CONSTANTS.channel_number_with_several_audio))
        action_menu_audio_display(test,audios_available,audios_available[0])
        check_messages.append("LIVE-TV:AUDIO  check first audio available is selected when preferred is not available \n")

    assertmgr.addCheckPoint(test_title, 1,(len(check_messages) == 3) ,"check is not complete, audio validate : %s " % check_messages )
    logging.info("LIVE-TV:AUDIO audio validate : %s " % check_messages )

    assertmgr.verifyAllCheckPoints()
    logging.info("##### End test_qa_live_audio_preferred #####")
    test.end()

@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_live_timeline
def test_qa_live_timeline_navigation():
    """
    TEST: test timeline navigation

     1st step : go to channel
        Action
        - zap on channel number
        Checkup
        - check playback status PLAYING

     2nd step : go to time line
        Action
        - display time line
        Checkup
        - check  time line screen is launch
        - check current focus on channel number playing

     3rd step : time line is display
        Action
        - move focus vertically
        Checkup
        - check focus title and logo is same compare to zap list
        - check timeout is respect to get focus on channel number

     4th step : time line is display
        Action
        - move focus horizontally
        Checkup
        - check navigation on future event can be done
        - check title and logo is same in action menu

     5th step : time line exit
        Action
        - back key
        Checkup
        - check exit time line with back key
    """

    """
     -- Prerequisite
            service with playing video

     -- Timeline launch
            check launch timeline by right key and exit with back key
            check focus is on current channel/current event

     -- Move focus vertically
            check focus timeout is respect and focus is really move
            check focus logo and title is those of info layer on current channel

     -- Move focus horizontally
            check that the number of event in the future corresponds to that expected

     -- Action Menu launch by validate on future event and go back to time line with back key
            check title and logo on future event match with those of previous screen
            check focus is set on same event when we go back from action menu to timeline
            todo check coherency on time line interval of future event ...
    """

    logging.info("##### BEGIN QA_live_timeline_navigation#####")

    test_title = "test_qa_live_timeline"
    test = VeTestApi(title=test_title)
    test.begin(screen=test.screens.fullscreen)

    test.he_utils.setParentalRatingThreshold(test.he_utils.getHhId(), CONSTANTS.MAX_THRESHOLD_UPM)

    zapping_by_dca(test, channel_id=CONSTANTS.channel_number_classic_1,check_playback=True)

    current_event_remaining_time = test.screens.fullscreen.current_event_remaining_time()
    if not isinstance(current_event_remaining_time, bool) and current_event_remaining_time.total_seconds() < 120:
        test.wait(current_event_remaining_time.seconds + 30)

    ''' step : go to time line
        Action
        - display time line
        Checkup
        - check  time line screen is launch
        - check current focus on channel number playing
    '''
    # check launch timeline screen
    logging.info("- check Launch timeline screen")
    status = test.screens.timeline.navigate("right")
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to launch the timeline. Current screen {0} ".format(test.milestones.get_current_screen()))

    # check current focus on channel number
    logging.info("- check current focus channel ")
    focus_channel_number = test.screens.timeline.get_focused_channel_number(test.milestones.getElements())
    test.log_assert(focus_channel_number == CONSTANTS.channel_number_classic_1,"LIVE-TV:TIMELINE focus not set on current event ")

    ''' step : time line is display
        Action
        - move focus vertically
        Checkup
        - check focus title and logo is same compare to zap list
        - check timeout is respect to get focus on channel number
    '''
    # check focus channel number change and timeout
    logging.info("- check move up and down ")
    test.screens.timeline.to_nextchannel(direction="up")
    test.screens.timeline.to_nextchannel(direction="down")
    test.screens.timeline.to_nextchannel(direction="down")
    test.screens.timeline.to_nextchannel(direction="up")

    ''' step : time line is display
        Action
        - move focus horizontally
        Checkup
        - check navigation on future event can be done
        - check title and logo is same in action menu
    '''

    logging.info("- check focus on next event in timeline ")

    status = check_navigate_event_in_timeline(test, max_event_display=5,check_data=True)
    test.log_assert(status,"LIVE-TV:TIMELINE Fail to move focus on future event ")

    status = to_focusnow_in_timeline(test, max_event_display=5, wait_few_seconds=1)
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to move focus on event now ")

    ''' step : time line exit
        Action
        - back key
        Checkup
        - check exit time line with back key
    '''
    logging.info("- check exit timeline with back key ")
    test.screens.fullscreen.navigate("back")
    test.log_assert(status, "LIVE-TV:TIMELINE  Fail to go back to fullscreen with back key")

    logging.info("##### End test_qa_live_timeline #####")
    test.end()


@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_live_timeline
def test_qa_live_timeline_zapping():
    """
    TEST : Verify zapping from timeline

     1st step : time line
        Action
        - enter time line with left key
        - exit with validate key
        Checkup
        - check focus title in time line match with current title service

     2nd step : time line
        Action
        - enter time line with left
        - move vertically [ toward top and bottom and validate selected channel ]
        Checkup
        - check channel number has been found and that the focus is on
        - check  info layer is display on validate service channel
        - check video is playing

     3rd step : time line
        Action
        - enter time line with right key
        Checkup
        - check timeout to go back to fullscreen
    """

    """
    -- Prerequisite
            two service with playing video
    -- TimeLine is launch
            check enter by [ right and left key ]
            check exit by  [ back key, timeout, ok on current focus ]
    -- Move vertically [ toward top and bottom and validate selected channel ]
            check channel number has been found and that the focus is on
            check  info layer is display on validate service channel
            check video is playing
            check focus title in time line match with current title service
    """

    logging.info("##### BEGIN QA_live_timeline_zapping#####")

    test_title = "test_qa_live_timeline"
    test = VeTestApi(title=test_title)
    test.begin(screen=test.screens.fullscreen)

    test.he_utils.setParentalRatingThreshold(test.he_utils.getHhId(), CONSTANTS.MAX_THRESHOLD_UPM)

    logging.info("- Prerequisite video playing on channel %s " % str(CONSTANTS.channel_number_classic_2) )
    zapping_by_dca(test, channel_id=CONSTANTS.channel_number_classic_2,check_playback=True)

    current_event_remaining_time = test.screens.fullscreen.current_event_remaining_time()
    if not isinstance(current_event_remaining_time, bool) and current_event_remaining_time.total_seconds() < 120:
        test.wait(current_event_remaining_time.seconds + 30)

    ''' step : time line
        Action
            - enter time line with left key
            - exit with validate key
        Checkup
            - check focus title in time line match with current title service
    '''

    # check enter time line by left key go back to full screen by validate key
    logging.info("Verify that Timeline can be launch by left long key press and full screen by key ok")

    current_focus_title = test.screens.fullscreen.get_current_event_title()
    test.log_assert((current_focus_title is not None), "LIVE-TV:TIMELINE No Title on channel service % s" % str(CONSTANTS.channel_number_classic_2) )

    current_channel_number = test.milestones.get_value_by_key(test.milestones.getElements(),"current_channel")
    current_time   = test.screens.fullscreen.get_current_event_broadcasting_time()

    status = test.screens.timeline.navigate("left")
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to launch the Timeline by long Left key press. Current screen: {0}".format(test.milestones.get_current_screen()))

    elements = test.milestones.getElements()
    focus_channel_number = test.milestones.get_value_by_key(elements,"focused_channel_number")
    focus_event_title = test.milestones.get_value_by_key(elements,"focused_event_title")
    focus_event_logo = test.milestones.get_value_by_key(elements, "focused_channel_logo")

    test.log_assert((focus_channel_number == current_channel_number),"LIVE-TV:TIMELINE Fail focus on timeline ")
    status = test.screens.fullscreen.navigate("ok")
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to dismiss the Timeline by OK on same channel than the launch one. Current screen: {0}".format(test.milestones.get_current_screen()))
    if current_time == test.screens.fullscreen.get_current_event_broadcasting_time() :
        test.log_assert(( focus_event_title == current_focus_title ),"LIVE-TV:TIMELINE Fail focus title no match with current title")
        test.log_assert(not isinstance(focus_event_logo, bool), "LIVE-TV:TIMELINE Fail  no logo exist ")

    logging.info("- Prerequisite video playing on channel %s " % str(CONSTANTS.channel_number_classic_1))
    zapping_by_dca(test, channel_id=CONSTANTS.channel_number_classic_1, check_playback=True)

    ''' step : time line
        Action
            - enter time line with left
            - move vertically [ toward top and bottom and validate selected channel ]
        Checkup
            - check channel number has been found and that the focus is on
            - check  info layer is display on validate service channel
            - check video is playing
    '''

    status = test.screens.timeline.navigate("left")
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to launch the timeline. Current screen {0} ".format(test.milestones.get_current_screen()))

    status = test.screens.timeline.tune_to_channel_by_sek(channel_id=str(CONSTANTS.channel_number_classic_2),verify_infolayer=True)
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to zap from timeline to channel number %s" % str(CONSTANTS.channel_number_classic_2))

    # check enter time line by right zap to service channel selected
    status = test.screens.timeline.navigate("right")
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to launch the timeline. Current screen {0} ".format(test.milestones.get_current_screen()))

    status = test.screens.timeline.tune_to_channel_by_sek(channel_id=str(CONSTANTS.channel_number_classic_1),direction="KEYCODE_DPAD_UP",verify_infolayer=True)
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to zap from timeline to channel number %s" % str(CONSTANTS.channel_number_classic_1))

    ''' step : time line
        Action
            - enter time line with right key
        Checkup
            - check timeout to go back to fullscreen
    '''
    logging.info("Verify Timeline timeout ")
    status = test.screens.timeline.navigate("left")
    test.log_assert(status, "LIVE-TV:TIMELINE Fail to launch the Timeline. Current screen: {0}".format(test.milestones.get_current_screen()))

    status = test.check_timeout('timeline', CONSTANTS.SCREEN_TIMEOUT)
    test.log_assert(status, "LIVE-TV:TIMELINE Failure on timeout test after last user interaction")

    logging.info("##### End test_qa_live_timeline_zapping #####")
    test.end()


@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_live_summary
def test_qa_live_summary():
    """
    TEST: Verify display summary, Title,Duration in Action Menu

     1st step : select live channel with close caption tracks
        Action
        - go to live channel
        - go to action menu
        Checkup
        - check time event format of action menu screen.
        - check duration of event match with info lines [ time event is get from full screen and action menu ]
        - check compare Title event get from full screen with and title event from action menu
        - check summary action menu not empty

    """
    logging.info("##### BEGIN QA_live_summary#####")

    test_title = "test_qa_live_timeline"
    test = VeTestApi(title=test_title)
    test.begin(screen=test.screens.fullscreen)


    ''' step : live tv summary
        Action
            - display action menu
        Checkup
            - check event title
            - check display time event in action menu
            - check summary
    '''
    logging.info("- Prerequisite min time event of 80 s ")
    zapping_by_dca(test, CONSTANTS.channel_number_classic_1)
    test.screens.fullscreen.wait_for_event_with_minimum_time_until_end(min_time_in_seconds=80)

    expected_event_title = test.screens.fullscreen.get_current_event_title()
    test.log_assert(not isinstance(expected_event_title,bool),"LIVE-TV:QA_live_summary Failure to get event title of current service %s" % expected_event_title)

    dict_evt = test.screens.fullscreen.get_current_event_broadcasting_time()
    test.log_assert(not isinstance(dict_evt,bool),"LIVE-TV:QA_live_summary Failure to get time event of current service")
    delta_duration = dict_evt["event_end_time"] - dict_evt["event_start_time"]

    expected_duration= str( int(delta_duration.total_seconds() / 60)) + " MIN"

    # - action menu .
    status = test.screens.action_menu.navigate()
    test.log_assert(status, "LIVE-TV:QA_live_summary Failed to go to Action Menu")

    # - check event title
    milestone = test.milestones.getElements()
    am_event_title = test.milestones.get_value_by_key(milestone,"prog_title")
    test.log_assert(not isinstance(am_event_title,bool),"LIVE-TV:QA_live_summary Failure to get event title from action menu")
    test.log_assert((am_event_title == expected_event_title),"LIVE-TV:QA_live_summary compare event title failed current %s action menu %s" % (expected_event_title,am_event_title))

    # - check event duration
    logging.info("- Compare duration (%s) of event from current service with info lines ",expected_duration)
    status = check_duration_display(test,expected_duration)
    test.log_assert(status, "LIVE-TV:QA_live_summary event duration in guide doesn't match with duration between start and end time of action menu")

    status, expected_duration = get_time_event_from_action_menu(test)
    logging.info("- Compare duration (%s%s) of event from action menu with info lines",str(expected_duration)," MIN")
    status = check_duration_display(test,str(expected_duration)+" MIN")
    test.log_assert(status, "LIVE-TV:QA_live_summary event duration in info lines doesn't match with duration between start and end time of action menu")

    # - check  summary
    summary= test.screens.action_menu.get_summary()
    test.log_assert(not isinstance(summary,bool) and len(summary) > 0,"LIVE-TV:QA_live_summary Failure to get summary")

    logging.info("##### End test_qa_live_summary #####")
    test.end()

@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_live_genres_and_time
def test_qa_live_genres_and_time():
    """
    TEST:  Check Genres & Time sorting.

     Steps : Genres & Time
        Action
          - From Live TV, Go to Genres & Time
          - Navigate in all proposed categories
          - Select Alphabetical sorting for each one
        Checkup
          - Check Genres & Time screen
          - Check alphabetical sorting if succeed
    """

    logging.info("##### BEGIN test_qa_live_genres_and_time #####")

    test_title = "test_qa_live_genres_and_time"
    test = VeTestApi(title=test_title)
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)

    test.screens.main_hub.navigate()
    status = test.screens.main_hub.focus_item_in_hub(item_title=CONSTANTS.HUB_TV)
    test.log_assert(status, "LIVE-TV:GENRES&TIME Failed to focus LIVE TV in Hub")
    test.move_towards('left')
    test.validate_focused_item(3)
    all_elements = test.milestones.getElements()
    list_GenresAndTime = test.milestones.get_value_by_key(all_elements,"sub_items")
    
    for _i in range(0, len(list_GenresAndTime)):                     #CONSTANTS.list_GenresAndTime)):
        test.validate_focused_item()
        all_elements = test.milestones.getElements()
        selected_category = test.milestones.get_value_by_key(all_elements,"focused_item") #which item is focused ?
        #if selected_category not in CONSTANTS.list_GenresAndTime:
        assertmgr.addCheckPoint("LIVE-TV:GENRES&TIME test_qa_live_genres_and_time", 1, selected_category=='TIME', "We are not in the good screen:  %s\n  " % (selected_category))
        test.validate_focused_item()
        all_elements = test.milestones.getElements()
        asset_list = test.milestones.get_value_by_key(all_elements, 'asset_list')
        test.log_assert(asset_list is not False, "LIVE-TV:GENRES&TIME Any asset displayed in FullContent")

        # Go on sorting menu
        test.appium.key_event("KEYCODE_DPAD_UP")

        # Select Alphabetical sorting
        status = test.screens.fullcontent.fullcontent_select_alphabetical_order()
        test.log_assert(status, "LIVE-TV:GENRES&TIME Fail to select Alphabetical order")
        test.wait(2*CONSTANTS.GENERIC_WAIT)

        # Retrieve the asset list displayed
        milestone = test.milestones.getElements()
        asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
        test.log_assert(asset_list is not False, "LIVE-TV:GENRES&TIME Any asset displayed in FullContent")

        # Check if the asset list is well sorted
        status = check_alphanumerical_sorting(asset_list)
        test.log_assert(status, "LIVE-TV:GENRES&TIME Sorting is NOT the expected one.")

        test.go_to_previous_screen()
        test.wait(CONSTANTS.GENERIC_WAIT)
        all_elements = test.milestones.getElements()
        selected_category = test.milestones.get_value_by_key(all_elements,"focused_item") #which item is focused ?
        #if selected_category not in CONSTANTS.list_GenresAndTime:
        assertmgr.addCheckPoint("LIVE-TV:GENRES&TIME test_qa_live_genres_and_time", 2, selected_category=='TIME', "We are not in the good screen:  %s\n  " % (selected_category))

        test.go_to_previous_screen()
        all_elements = test.milestones.getElements()
        selected_category = test.milestones.get_value_by_key(all_elements,"focused_item") #which item is focused ?
        #if selected_category not in CONSTANTS.list_GenresAndTime:
        assertmgr.addCheckPoint("LIVE-TV:GENRES&TIME test_qa_live_genres_and_time", 3, selected_category=='GENRE & TIME', "We are not in the good screen:  %s\n  " % (selected_category))

        test.move_towards('right')

    assertmgr.verifyAllCheckPoints()
    logging.info("##### End of test_qa_live_genres_and_time #####")
    test.end()

@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_live_playback
def test_qa_live_playback():
    """
    TEST:  LIVE TV Playback.

     Steps : Playback on live TV
        Action
          - Launch app and go to fullscreen
          - Zapping and save the number of current channel
          - Press on Home button to resume app
          - Restart app and wait for fullscreen
          - Zapping again to come back on the cuurent channel
        Checkup
          - Check fullscreen
          - Check video playing on the current channel
          - Check fullscreen again after restarting app          -
          - Check the number of the expected channel
    """
    logging.info("##### BEGIN test_qa_live_playback #####")

    test = VeTestApi(title="test_qa_live_playback")
    
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.move_towards('up')
    test.wait(CONSTANTS.GENERIC_WAIT)
    all_elements = test.milestones.getElements()
    current_channel = test.milestones.get_value_by_key(all_elements,"focused_channel_number")
    test.wait(CONSTANTS.LONG_WAIT)
    logging.info("LIVE-TV:PLAYBACK current channel is : %s" % current_channel)
    test.move_towards('up')
    test.wait(CONSTANTS.LONG_WAIT)

    # check playback is playing on current channel
    logging.info("LIVE-TV:PLAYBACK check playback is playing on current channel ")
    playback_state = test.screens.playback.verify_streaming_playing()
    playback_status = playback_state["playbackState"]
    test.log_assert(playback_status == "PLAYING","LIVE-TV:PLAYBACK Fail Initials Conditions playback in fullscreen. Current screen: %s  playback_status: %s" % (test.milestones.get_current_screen(), playback_status))
    test.wait(CONSTANTS.LONG_WAIT)
    #Press on Home button to resume app
    test.repeat_key_press("KEYCODE_DPAD_HOME", 1, 5)
    test.wait(CONSTANTS.LONG_WAIT)
    # Restart app
    test.appium.restart_app()
    test.wait(CONSTANTS.LONG_WAIT)

    # check playback again after restarting app
    logging.info("LIVE-TV:PLAYBACK check playback is playing after restarting app ")
    playback_state = test.screens.playback.verify_streaming_playing()
    playback_status = playback_state["playbackState"]
    test.log_assert(playback_status == "PLAYING","LIVE-TV:PLAYBACK Fail Initials Conditions playback in fullscreen. Current screen: %s  playback_status: %s" % (test.milestones.get_current_screen(), playback_status))
    test.wait(CONSTANTS.LONG_WAIT)
    status = test.screens.fullscreen.navigate()
    test.wait(CONSTANTS.LONG_WAIT)
    test.log_assert(status, "LIVE-TV:PLAYBACK Fullscreen could not be accessed")
    test.wait(CONSTANTS.LONG_WAIT)
    test.move_towards('down')
    test.wait(CONSTANTS.GENERIC_WAIT)
    all_elements = test.milestones.getElements()
    expected_channel = test.milestones.get_value_by_key(all_elements,"focused_channel_number")
    test.wait(CONSTANTS.LONG_WAIT)
    logging.info("LIVE-TV:PLAYBACK expected channel is : %s" % expected_channel)
    test.log_assert(current_channel==expected_channel, " LIVE-TV:PLAYBACK Expected channel is (%s), but current channel is (%s) " % (expected_channel, current_channel))

    logging.info("##### End of test_qa_live_playback #####")
    test.end()
    
    
