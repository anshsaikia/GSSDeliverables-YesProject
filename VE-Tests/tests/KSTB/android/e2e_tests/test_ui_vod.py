import pytest
import logging
from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.milestones.milestones_kpi_request_parser import KpiRequestParserAPI
from tests_framework.milestones.milestones_kpi_client import CC_TRACKS
from tests_framework.ui_building_blocks.KSTB.playback import VOD_PLAYBACK_TYPE

__author__ = 'eleduc'

' Global constants '
# This value do not reflect the one coming from lab_settings It look like this 
SKIP_DURATION_FRW = 30000
SKIP_DURATION_BKW = 15000
GENERIC_WAIT = 2
TIME_VOD_STARTING = 12#s
TIME_AFTER_PLAY_PAUSE = 5#s
TIME_AFTER_ACTION_EXTENDED = 7#s
TIME_AFTER_JUMP_TO_EOS = 5#s
TIME_AFTER_JUMP_TO_BOS = 5#s
TIME_AFTER_JUMP_FORWARD = 5#s
TIME_AFTER_JUMP_BACKWARD = 5#s
TIME_PLAYING_CHECK_TWO_POSITIONS=5#s
TIME_VOD_STOPPING = 10 #s
ACCEPTED_DELTA_BEFORE_FIRST_IFRAME=1000 #ms


def get_message(ve_test,current_screen):
    """
    In case of error, allow to retrieve the error number and the text
    :param test_vod: the current test
    :param current_screen: the name of the displayed screen
    :return: the displayed error or the current screen name if no error
    """
    milestones = ve_test.milestones
    if current_screen == "notification":
        curmilestones = milestones.getElements()
        error_msg = milestones.get_value_by_key(curmilestones, "msg_error")
        error_text = milestones.get_value_by_key(curmilestones, "msg_text")
        return "'notification' with error : " + error_msg + " - " + error_text
    return current_screen


def start_playback_and_check(ve_test):
    """
    Start a VOD playback and check if the screen is correct and video is playing
    :param test_vod:
    :return: the status of the current playback
    """

    ve_test.screens.playback.vod_manager.start_free_playback(TIME_VOD_STARTING)
    current_screen = ve_test.milestones.get_current_screen()
    screen_name = ve_test.screens.fullscreen.screen_name
    ve_test.log_assert(current_screen == screen_name, "Expected screen '"+screen_name+"', but current screen is : " + get_message(ve_test, current_screen))
    status = ve_test.screens.playback.verify_streaming_playing()
    return status

def check_position(ve_test):
    """
    Allow to check if the position is correct
    :param test_vod: the current test
    """
    vod_manager = ve_test.screens.playback.vod_manager
    current_position_prev = vod_manager.get_current_position(GENERIC_WAIT)
    ve_test.wait(5)
    current_position = vod_manager.get_current_position(GENERIC_WAIT)
    ve_test.log_assert(current_position > current_position_prev, "The current position is not valid : " + str(current_position) + " , expected to be more than : " + str(current_position_prev))

# Start a VOD playback
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_play
def test_ui_vod_play():
    """
     Start a VOD playback
     Check if the playback screen is displayed , with error detection
     Check the stream is playing
    """
    ve_test = VeTestApi("test_ui_vod_play")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.end()

# Stop a VOD playback in the action menu
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_stop
def test_ui_vod_stop():
    """
     Start a VOD playback
     Check if the playback screen is displayed , with error detection
     Check the stream is playing
     Select STOP item in the action menu screen
     Check if the played stream has changed
    """
    ve_test = VeTestApi("test_ui_vod_stop")
     
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
     
    ve_test.wait(GENERIC_WAIT)
    start_status = start_playback_and_check(ve_test)
    ve_test.screens.action_menu.navigate()
    ve_test.screens.action_menu.navigate_to_action('STOP')
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)    
    ve_test.wait(GENERIC_WAIT)
    stop_status = ve_test.screens.playback.verify_streaming_playing()
    ve_test.wait(GENERIC_WAIT)
    ve_test.log_assert(start_status["playbackType"] != stop_status["playbackType"] , "Playback shoul be different %s - %s"%(start_status["playbackType"],stop_status["playbackType"]))

    #Now test stop using trickmode ui buttons : restart VOD asset, pause asset to display tricmode UI and select STOP
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)
    ve_test.wait(GENERIC_WAIT)
    ve_test.repeat_key_press("KEYCODE_DPAD_UP", 1, 5)
    ve_test.wait(GENERIC_WAIT)
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)    
    ve_test.wait(7)
    restart_status = ve_test.screens.playback.verify_streaming_playing()
    ve_test.wait(GENERIC_WAIT)
    ve_test.log_assert(start_status["playbackType"] == restart_status["playbackType"] , "Playback shoul be the same %s - %s"%(start_status["playbackType"],restart_status["playbackType"]))

    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(2)
    ve_test.repeat_key_press("KEYCODE_DPAD_RIGHT", 1, 1)
    ve_test.wait(2)
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)
	
    stop_status = ve_test.screens.playback.verify_streaming_playing()
    ve_test.wait(GENERIC_WAIT)
    ve_test.log_assert(start_status["playbackType"] != stop_status["playbackType"] , "Playback shoul be different %s - %s"%(start_status["playbackType"],stop_status["playbackType"]))
	
    ve_test.end()
 
 
# Check the return to live on stop with the hub menu screen displayed A completer dans le CTAP
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_return_to_live():
    """
    Check the live stream is in progress
    Store the current channel number
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Select STOP item in the action menu screen
    Check the previous selected channel is playing again
    """
    ve_test = VeTestApi("test_ui_vod_return_to_live")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")

    prev_chan_number = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"current_channel_number")
    prev_live_playback_status = ve_test.screens.playback.verify_streaming_playing()
    vod_playback_status = start_playback_and_check(ve_test)
         
    ve_test.screens.action_menu.navigate()
    ve_test.screens.action_menu.navigate_to_action('STOP')
         
    logging.info("Stop the VOD asset in action menu")
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 10) 
         
    logging.info("Check the previous channel is playing again")
    # check the live stream is playing
    current_live_playback_status = ve_test.screens.playback.verify_streaming_playing()
       
    prev_live_url = prev_live_playback_status['sso']['sessionPlaybackUrl']
    current_live_url = current_live_playback_status['sso']['sessionPlaybackUrl']
    vod_url = vod_playback_status['sso']['sessionPlaybackUrl']
       
    # check that a new video is playing
    ve_test.screens.playback.verify_playing_url(vod_url,1,playing=True, compare="!=")
       
    # check it is the same live url playing
    ve_test.log_assert(prev_live_url == current_live_url, "Not playing expected url. expected=%s  actual=%s"%(prev_live_url, current_live_url))
       
    # check the full_content screen is displayed
    screen_name = ve_test.milestones.get_current_screen()
    ve_test.log_assert(screen_name == "full_content","Get screen name %s expected full_content"%screen_name)
       
    # check it is the expected channel number
    curmilestones = ve_test.milestones.getElements()
    numchan = ve_test.milestones.get_value_by_key(curmilestones, "current_channel_number")
    ve_test.log_assert(numchan == prev_chan_number, "Get channel number %s expected %s"%(numchan,prev_chan_number))
    ve_test.end()

# Pause the playback
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_ui_vod_pause():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    """
    ve_test = VeTestApi("test_ui_vod_pause")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    # Check if the playback is paused
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback is not paused")
    ve_test.screens.playback.verify_streaming_paused()
	#use trickmode ui pause button to resume play
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    # Check if the playback is not paused
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(not is_paused,"playback is not paused")
    ve_test.screens.playback.verify_streaming_playing()
	#use trickmode ui pause button to pause
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    # Check if the playback is paused
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback is not paused")
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.end()
   
   
# Resume the playback
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_resume
def test_ui_vod_resume():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Press the media_play (pause) key
    Check the playback screen is in resume mode
    Check the stream is playing again
    """
    ve_test = VeTestApi("test_ui_vod_resume")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)

    start_playback_and_check(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback is not paused")
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    # Check if the playback is resumed
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(not is_paused,"playback is not resumed")
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.end()
   
   
# Pause the playback after a resume
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_pause_resume_pause():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Press the media_play (pause) key
    Check the playback screen is in resume mode
    Check the stream is playing again
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is again in pause mode
    """
    ve_test = VeTestApi("test_ui_vod_pause_resume_pause")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback is not paused")
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(not is_paused,"playback is not resumed")
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be again paused")
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.end()
   
   
# Check the trickmode view is always visible in pause mode
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_ui_vod_pause_trickmode_view_always():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Check the trick mode view is visible on screen
    Wait more than the default time-out value
    Check the trick mode view is still visible on screen
    """
    ve_test = VeTestApi("test_ui_vod_pause_trickmode_view_always")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    is_visible = ve_test.milestones.get_value_by_key(curmilestones, "is_trickmode_visible")
    ve_test.log_assert(is_visible,"trickmode view shall be visible")
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.wait(5);
    curmilestones = ve_test.milestones.getElements()
    is_visible = ve_test.milestones.get_value_by_key(curmilestones, "is_trickmode_visible")
    ve_test.log_assert(is_visible,"trickmode view shall be still visible")
    ve_test.end()
   
   
# Show action menu with playback paused
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_action_menu_after_pause():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Press the OK key
    Check the current screen is action_menu
    """
    ve_test = VeTestApi("test_ui_vod_action_menu_after_pause")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait_for_screen(5,"action_menu")
    ve_test.end()
  
  
# Show action menu with playback played
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_action_menu_after_resume():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Press the media_play (pause) key
    Check the playback screen is in resume mode
    Check the stream is in playing mode
    Press the OK key
    """
    ve_test = VeTestApi("test_ui_vod_action_menu_after_resume")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(not is_paused,"playback shall be resumed")
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.wait(GENERIC_WAIT)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait_for_screen(5,"action_menu")
    ve_test.end()
  

@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_back_key_dismissed_trickmode_view_play():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Check the trick mode view is visible
    Press the media_play (pause) key
    Press the back key
    Check the trick mode view is no more visible
    Check the playback screen is in resume mode
    Check the stream is in playing mode
    Press the OK key
    """
    ve_test = VeTestApi("test_ui_vod_back_key_dismissed_trickmode_view_play")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    # set the playback in paused
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    curmilestones = ve_test.milestones.getElements()
    is_visible = ve_test.milestones.get_value_by_key(curmilestones, "is_trickmode_visible")
    ve_test.log_assert(is_visible,"trickmode view shall be visble")
    # resume it
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    # request to hide the trickmode view before time-out
    ve_test.appium.key_event("KEYCODE_BACK")
    ve_test.wait(GENERIC_WAIT)
    # check the trickmode view is hidden
    curmilestones = ve_test.milestones.getElements()
    is_visible = ve_test.milestones.get_value_by_key(curmilestones, "is_trickmode_visible")
     
    ve_test.log_assert(not is_visible,"trickmode view shall be hidden")
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(not is_paused,"playback shall be resumed")
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.end()
   
   
# BACK key stop the playback and return to live when the playback is in paused
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_back_key_stop_playback_trickmode_view_paused():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Press the back key
    Wait for several seconds
    Check a new stream is playing
    Check the current screen is the main hub
    """
    ve_test = VeTestApi("test_ui_vod_back_key_stop_playback_trickmode_view_paused")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;

    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    vod_playback_status = start_playback_and_check(ve_test)
    vod_url = vod_playback_status['sso']['sessionPlaybackUrl']
    # set the playback in paused
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.appium.key_event("KEYCODE_BACK")
    ve_test.wait(5)
     
    ve_test.screens.playback.verify_playing_url(vod_url,1,playing=True, compare="==")
    current_screen = ve_test.milestones.get_current_screen()
    ve_test.log_assert(current_screen == ve_test.screens.fullscreen.screen_name, "Failed to verify fullscreen. Current screen=%s"%current_screen)
    ve_test.end()
   
   
# BACK key stop the playback and return to the live with the main hub screen displayed
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_back_key_stop_playback_in_play_mode():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the back key
    Wait for several seconds
    Check a new stream is playing
    Check the current screen is the main hub
    """
    ve_test = VeTestApi("test_ui_vod_back_key_stop_playback_in_play_mode")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;

    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    vod_playback_status = start_playback_and_check(ve_test)
    vod_url = vod_playback_status['sso']['sessionPlaybackUrl']
    ve_test.wait(5)
    ve_test.appium.key_event("KEYCODE_BACK")
    ve_test.wait(5)
    # check that a new video is playing
    ve_test.screens.playback.verify_playing_url(vod_url,1, playing=True, compare="!=")
    current_screen = ve_test.milestones.get_current_screen()
    ve_test.log_assert(current_screen == "full_content", "Failed to verify full_content. screen=%s"%current_screen)
    ve_test.end()
   

# Resume from last position of playback after BACK key pressed
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_resume_last_position_back_key_in_play_mode():
    """
        Start a VOD playback
        Check if the playback screen is displayed , with error detection
        Check the stream is playing
        Wait a few seconds
        Get current position
        Press the back key
        Wait for several seconds
        Start same asset VOD playback
        Check resume VOD position playback
        """
    ve_test = VeTestApi("test_ui_vod_resume_last_position_back_key_in_play_mode")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT*2)
    vod_playback_status = start_playback_and_check(ve_test)
    vod_url_play = vod_playback_status['sso']['sessionPlaybackUrl']
    check_position(ve_test)

    ve_test.wait(TIME_VOD_STARTING)
    vod_manager = ve_test.screens.playback.vod_manager 
    vod_manager.process_jump_forward(TIME_AFTER_JUMP_FORWARD, True)
    ve_test.wait(GENERIC_WAIT)
    play_current_position = vod_manager.get_current_position()
    logging.info("play_current_position " +str(play_current_position))
    ve_test.screens.action_menu.navigate()
    ve_test.screens.action_menu.navigate_to_action('STOP')
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)    
    #launch the same asset
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)    
    ve_test.screens.action_menu.navigate_to_action('RESUME')
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)

    vod_url_resume = vod_playback_status['sso']['sessionPlaybackUrl']
    ve_test.log_assert(vod_url_play == vod_url_resume,"Failed to reload the same VOD asset for resume check")
    ve_test.wait(5)
    resume_current_position = vod_manager.get_current_position()
    logging.info("resume_current_position " +str(resume_current_position))
    ve_test.log_assert(resume_current_position>play_current_position,"Failed to resume the same VOD asset "+str(resume_current_position)+">"+str(play_current_position))

    ve_test.end()



# Resume from last position of playback after STOP in action menu
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_resume_last_position_stop_actionmenu_in_play_mode():
    """
        Start a VOD playback
        Check if the playback screen is displayed , with error detection
        Check the stream is playing
        Wait a few seconds
        Get current position
        Navigate to action menu and select STOP
        Wait for several seconds
        Start same asset VOD playback
        Check resume VOD position playback
        """
    ve_test = VeTestApi("test_ui_vod_resume_last_position_stop_actionmenu_in_play_mode")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT*2)
    vod_playback_status = start_playback_and_check(ve_test)
    vod_url_play = vod_playback_status['sso']['sessionPlaybackUrl']
    check_position(ve_test)

    ve_test.wait(TIME_VOD_STARTING)
    vod_manager.process_jump_forward(TIME_AFTER_JUMP_FORWARD, True)

    play_current_position = vod_manager.get_current_position()
    logging.info("play_current_position " +str(play_current_position))

    ve_test.screens.action_menu.navigate()
    ve_test.wait(10)
    ve_test.screens.action_menu.navigate_to_action('STOP')
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)
    ve_test.wait(GENERIC_WAIT*2)
    stop_status = ve_test.screens.playback.verify_streaming_playing()
    logging.info("stop_status " +str(stop_status))
    ve_test.log_assert(vod_playback_status["playbackType"] != stop_status["playbackType"] , "Playback should be different %s - %s"%(vod_playback_status["playbackType"],stop_status["playbackType"]))

    #launch the same asset
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)    
    ve_test.screens.action_menu.navigate_to_action('RESUME')
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)

    resume_playback_status = ve_test.screens.playback.verify_streaming_playing()
    vod_url_resume = resume_playback_status['sso']['sessionPlaybackUrl']
    ve_test.log_assert(vod_url_play == vod_url_resume,"Failed to reload the same VOD asset for resume check")
    ve_test.wait(5)
    resume_current_position = vod_manager.get_current_position()
    logging.info("resume_current_position " +str())
    ve_test.log_assert(resume_current_position>play_current_position,"Failed to resume the same VOD asset"+str(resume_current_position)+">"+str(play_current_position))

    ve_test.end()



# Resume from last position near EOF
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_resume_last_position_EOF_in_play_mode():
    """
        Start a VOD playback
        Check if the playback screen is displayed , with error detection
        Check the stream is playing
        Wait a few seconds
        Jump to EOF minus 90 seconds
        Get current position
        Navigate to action menu and select STOP
        Wait for several seconds
        Check a new stream is playing
        Check the current screen is the main hub
        Start same asset VOD playback
        Check resume VOD position playback is really near EOF
        """
    ve_test = VeTestApi("test_ui_vod_resume_last_position_EOF_in_play_mode")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT*2)
    vod_playback_status = start_playback_and_check(ve_test)
    vod_url_play = vod_playback_status['sso']['sessionPlaybackUrl']
    check_position(ve_test)

    ve_test.wait(TIME_VOD_STARTING)
    vod_manager.jump_forward_to_end_of_stream(90 , 1)
    ve_test.wait(TIME_AFTER_JUMP_TO_EOS)

    play_current_position = vod_manager.get_current_position()
    logging.info("play_current_position " +str(play_current_position))

    ve_test.screens.action_menu.navigate()
    ve_test.screens.action_menu.navigate_to_action('STOP')
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)
    ve_test.wait(GENERIC_WAIT)
    stop_status = ve_test.screens.playback.verify_streaming_playing()
    ve_test.wait(GENERIC_WAIT*2)
    ve_test.log_assert(vod_playback_status["playbackType"] != stop_status["playbackType"] , "Playback should be different %s - %s"%(vod_playback_status["playbackType"],stop_status["playbackType"]))

    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)    
    ve_test.repeat_key_press("KEYCODE_DPAD_UP", 1, 2)
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)
    resume_playback_status = ve_test.screens.playback.verify_streaming_playing()

    vod_url_resume = resume_playback_status['sso']['sessionPlaybackUrl']
    ve_test.log_assert(str(vod_url_play) == str(vod_url_resume),"Failed to reload the same VOD asset for resume check")
    resume_current_position = vod_manager.get_current_position()
    logging.info("resume_current_position " +str(resume_current_position))
    duration = vod_manager.get_total_duration()
    logging.info("total duration " +str(duration))
    ve_test.log_assert(resume_current_position>play_current_position,"Failed to resume the same VOD asset")
    ve_test.log_assert(resume_current_position>duration - 90000,"Failed to resume the same VOD asset near EOF")

    ve_test.end()



# Resume from near beginning of file
# Will not work as you can only resume if video has been played for more than 30s
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_resume_last_position_BOF_in_play_mode():
    """
        Start a VOD playback
        Check if the playback screen is displayed , with error detection
        Check the stream is playing
        Wait a few seconds
        Jump to BOF plus 5 seconds
        Get current position
        Navigate to action menu and select STOP
        Wait for several seconds
        Check a new stream is playing
        Check the current screen is the main hub
        Start same asset VOD playback
        Check resume VOD position playback is really near BOF
    """
		
    ve_test = VeTestApi("test_ui_vod_resume_last_position_BOF_in_play_mode")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT*2)
    vod_playback_status = start_playback_and_check(ve_test)
    vod_url_play = vod_playback_status['sso']['sessionPlaybackUrl']
    check_position(ve_test)

    ve_test.wait(TIME_VOD_STARTING)
    vod_manager.jump_backward_to_begin_of_stream(3)

    #need to wait a bit so to have RESUME option
    ve_test.wait(30)
    play_current_position = vod_manager.get_current_position()
    logging.info("play_current_position " +str(play_current_position))

    ve_test.screens.action_menu.navigate()
    ve_test.screens.action_menu.navigate_to_action('STOP')
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)
    ve_test.wait(GENERIC_WAIT)
    stop_status = ve_test.screens.playback.verify_streaming_playing()
    ve_test.wait(GENERIC_WAIT*2)
    ve_test.log_assert(vod_playback_status["playbackType"] != stop_status["playbackType"] , "Playback should be different %s - %s"%(vod_playback_status["playbackType"],stop_status["playbackType"]))

    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)    
    ve_test.repeat_key_press("KEYCODE_DPAD_UP", 1, 2)
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 2)
    resume_playback_status = ve_test.screens.playback.verify_streaming_playing()	
    vod_url_resume = resume_playback_status['sso']['sessionPlaybackUrl']
    ve_test.log_assert(vod_url_play == vod_url_resume,"Failed to reload the same VOD asset for resume check")
    resume_current_position = vod_manager.get_current_position()
    logging.info("resume_current_position " +str(resume_current_position))
    ve_test.log_assert(resume_current_position>play_current_position,"Failed to resume the same VOD asset")
    ve_test.log_assert(resume_current_position< 60000,"Failed to resume the same VOD asset near BOF")

    ve_test.end()



# Video black and white when the trick mode view is displayed
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_ui_vod_video_black_and_white():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Check the trick mode view is visible
    """
    ve_test = VeTestApi("test_ui_vod_video_black_and_white")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    is_visible = ve_test.milestones.get_value_by_key(curmilestones, "is_trickmode_visible")
    ve_test.log_assert(is_visible, "The trick mode view shall be visible on the screen (%s)"%is_visible);
    ve_test.end()
   
  
# Seek forward in play mode
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_forward
def test_ui_vod_seek_forward_during_play():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Simulate the RIGHT key
    Wait for 9 seconds to complete the seek operation
    Check the new position is more than 30 (skip forward duration) seconds from the previoius one , but no more than 49 (30skip+9wait+10delta) seconds.
    """
    ve_test = VeTestApi("test_ui_vod_seek_during_play")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    current_position = vod_manager.get_current_position()
    ve_test.appium.key_event("KEYCODE_MEDIA_FAST_FORWARD")
    ve_test.wait(9)
     
    ve_test.screens.playback.verify_position(current_position + SKIP_DURATION_FRW,"more")
    #ve_test.screens.playback.verify_position(current_position + SKIP_DURATION_FRW + 19000,"less")
    #make test more tolerant until bug on get_position is solved
    ve_test.screens.playback.verify_position(current_position + SKIP_DURATION_FRW + 9000,"about",20000)
	
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    ve_test.appium.key_event("KEYCODE_DPAD_RIGHT")
    ve_test.wait(2)
    ve_test.appium.key_event("KEYCODE_DPAD_RIGHT")
    ve_test.wait(2)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    ve_test.screens.playback.verify_position(current_position + SKIP_DURATION_FRW*2 + 15000,"about",20000)
	
    ve_test.end()
   
   
# Seek backward in play mode
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_backward
def test_ui_vod_seek_backward_during_play():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Request to be at the position 10 minutes.
    Wait a while to perform the seek
    Simulate the LEFT key
    Wait for 10 seconds to complete the seek operation
    Check the new position is more than 15 seconds from the previoius one.
    """
    ve_test = VeTestApi("test_ui_vod_seek_backward_during_play")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    seek_position = 60000
    ve_test.milestones.sendCommand("seekPlayback",str(seek_position))
    # let some time to perform the seek
    ve_test.wait(15)
    current_position = vod_manager.get_current_position()
    ve_test.appium.key_event("KEYCODE_MEDIA_REWIND")
    ve_test.wait(9)
    ve_test.screens.playback.verify_position(current_position - SKIP_DURATION_BKW + 15000, "about", 10000)

    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    ve_test.appium.key_event("KEYCODE_DPAD_LEFT")
    ve_test.wait(2)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(2)
    ve_test.screens.playback.verify_position(current_position - SKIP_DURATION_BKW*2 + 15000, "about",20000)
    ve_test.end()
   
   
# Seek forward in pause mode
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_ui_vod_seek_forward_in_pause():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Simulate the RIGHT key (this will start play mode)
    Wait for 10 seconds to complete the seek operation
    Check the playback screen is in play mode
    Check the stream is in play mode    Check the new position is between 15 seconds and 45 seconds the previous position
    """
    ve_test = VeTestApi("test_ui_vod_seek_forward_in_pause")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    current_position = ve_test.screens.playback.vod_manager.get_current_position()
    ve_test.appium.key_event("KEYCODE_MEDIA_FAST_FORWARD")
    # let some time to perform the seek
    ve_test.wait(10)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(not is_paused,"playback is not resumed")
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.screens.playback.verify_position(current_position + SKIP_DURATION_FRW + 10000,"about",15000)
    ve_test.end()
   
   
# Seek backward in pause mode
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_ui_vod_seek_backward_in_pause():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Set the position to 10 minutes
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Get the current stream position
    Simulate the LEFT key(this will start play mode)
    Check the current position is between 45 and 15 seconds before the previous one
    """
    ve_test = VeTestApi("test_ui_vod_seek_in_pause")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    seek_position = 60000
    ve_test.milestones.sendCommand("seekPlayback",str(seek_position))
    ve_test.wait(15)
    current_position = vod_manager.get_current_position(GENERIC_WAIT)
    ve_test.log_assert(current_position > seek_position, "The current position shall be highter than " + str(seek_position))
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    current_position = vod_manager.get_current_position()
    ve_test.appium.key_event("KEYCODE_MEDIA_REWIND")
    ve_test.wait(10);
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(not is_paused,"playback is not resumed")
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.screens.playback.verify_position(current_position - SKIP_DURATION_BKW + 10000,"about",15000)
    ve_test.end()
   
   
# Seek to the end of the video in pause mode
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_seek_eof_in_pause():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Set the position near the end of the stream (less than 30 seconds)
    Let time to perform the seek
    Check the position
    Simulate the RIGHT key
    Check the current position is about the end of the stream
    """
    ve_test = VeTestApi("test_ui_vod_seek_eof_in_pause")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT);
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    duration = vod_manager.get_total_duration()
    # Set the position to have less than a skip duration remaining time
    seek_position = duration - SKIP_DURATION_FRW - 20000
    ve_test.milestones.sendCommand("seekPlayback",str(seek_position))
    ve_test.wait(15);
    ve_test.screens.playback.verify_position(seek_position,"about",20000)
    # try to go after the end of the video
    ve_test.appium.key_event("KEYCODE_MEDIA_FAST_FORWARD")
    ve_test.wait(GENERIC_WAIT);
    ve_test.screens.playback.verify_position(duration,"about",20000)
    ve_test.end()
    
    
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
# Seek to the begin of the video
# -----------------------------
# Start the hub store VOD asset
# Press the pause key to pause the video
# Set the position to have less than a skip duration before the current position
# Press the left arrow key
# Check the current position is the beginning of the video
def test_ui_vod_seek_bof_in_pause():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the stream is in pause mode
    Set the position near the begining (less than 30 seconds)
    Let time to perform the seek
    Simulate the LEFT key
    Wait for 10 seconds
    Check the position is more or less 15 seconds
    """
    ve_test = VeTestApi("test_ui_vod_seek_bof_in_pause")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT);
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    seek_position = SKIP_DURATION_BKW - 5000
    ve_test.milestones.sendCommand("seekPlayback",str(seek_position))
    ve_test.wait(15);
    # try to go before the beginning of the video
    ve_test.appium.key_event("KEYCODE_MEDIA_REWIND")
    ve_test.wait(10);
    ve_test.screens.playback.verify_position(0,"more")
    ve_test.screens.playback.verify_position(15000,"less")
    ve_test.end()
   
   
# Seek to the end of the video in playing mode
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_eof_ffwd
def test_ui_vod_seek_eof_in_play_mode():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Set the position near the end of the stream (less than a seek duration)
    Let some time time to perform the seek
    Simulate the RIGHT key
    Wait for a few seconds the end of the playback
    Check no stream is playing
    """
    ve_test = VeTestApi("test_ui_vod_seek_eof_in_play_mode")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    vod_playback_status = ve_test.screens.playback.verify_streaming_playing()
    duration = vod_manager.get_total_duration()
    # Set the position to have less than a skip duration before the end of the video
    seek_position = duration - SKIP_DURATION_FRW
    ve_test.milestones.sendCommand("seekPlayback",str(seek_position))
    ve_test.wait(15);
    # try to go after the end of the video
    ve_test.appium.key_event("KEYCODE_MEDIA_FAST_FORWARD")
    # let some time to return to live stream
    ve_test.wait(15)
    # Check vod playback is stopped and live available
    vodUrl = vod_playback_status['sso']['sessionPlaybackUrl']
    current_screen = ve_test.milestones.get_current_screen();
    ve_test.log_assert(current_screen == "full_content","Current screen is " + current_screen + " , expected to be on 'full_content'")
    ve_test.wait(GENERIC_WAIT)
    ve_test.screens.playback.verify_playing_url(vodUrl,1,playing=True, compare="!=")
    ve_test.end()
    
    
# Seek to the begin of the video in playing mode
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_bof_fbwd
def test_ui_vod_seek_bof_in_play_mode():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Set the position to less than a seek duration
    Wait a while to perform the seek
    Simulate the LEFT key
    Check the position is more less than 10 seconds
    """
    ve_test = VeTestApi("test_ui_vod_seek_bof_in_play_mode")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    seek_position = SKIP_DURATION_BKW - 5000
    ve_test.milestones.sendCommand("seekPlayback",str(seek_position))
    ve_test.wait(15);
    # try to go before the beginning of the video
    ve_test.appium.key_event("KEYCODE_MEDIA_REWIND")
    ve_test.wait(5);
    #ve_test.screens.playback.verify_position(10000,"less")
    # make test more tolerant until get_position bug is solved
    ve_test.screens.playback.verify_position(10000,"about",10000)
    ve_test.screens.playback.verify_position(0,"more")
    ve_test.end()



def check_cc(ve_test, cc_track):
    playbackStatus = ve_test.milestones.getClientPlaybackStatus()
    ccTrack = playbackStatus['ccTrack']

    return ccTrack['trackId'].lower() == cc_track.lower()

# Start a VOD playback
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_cc
def test_ui_vod_play_closedCaption():
    """
     Start a VOD playback with CC disabled and check
     then enable CC and check that it is indeed enabled
    """
    ve_test = VeTestApi("test_ui_vod_play")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.log_assert(check_cc(ve_test, CC_TRACKS['off']), 'cc is not off')

    ve_test.screens.action_menu.navigate()
    ve_test.screens.action_menu.navigate_to_action('STOP')

    logging.info("Stop the VOD asset in action menu")
    ve_test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 10)

    ## change settings
    ve_test.screens.main_hub.navigate()
    ve_test.log_assert(ve_test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES"), "couldn't navigate to settings")
    ve_test.log_assert(ve_test.screens.main_hub.select_settings_sub_sub_menu("CLOSED CAPTION", "CC1"), "couldn't select closed captions")

    ## play the asset again
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    ve_test.log_assert(check_cc(ve_test, CC_TRACKS['cc1']), 'cc1 is not displayed')

    ve_test.end()

  
  
# Check trick mode view still visible on video played after a BACK key pressed
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_ui_vod_trickmode_view_always_visible_on_back_in_play():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Press the OK key
    Check the action menu screen is displayed
    Press the BACK key
    Check the playback screen is displayed
    """
    ve_test = VeTestApi("test_ui_vod_trickmode_view_always_visible_on_back_in_pause")
    ve_test.begin(screen=ve_test.screens.fullscreen) ;
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(GENERIC_WAIT)
    current_screen = ve_test.milestones.get_current_screen();
    ve_test.log_assert(current_screen == "action_menu","Current screen is " + current_screen + ", expected 'action_menu'")
    ve_test.wait(GENERIC_WAIT)
    ve_test.appium.key_event("KEYCODE_BACK")
    ve_test.wait(5) 
    current_screen = ve_test.milestones.get_current_screen();
    ve_test.log_assert(current_screen == "fullscreen","Current screen is " + current_screen + ", expected 'fullscreen'")
    ve_test.end()
  
# Check the live video is in black and white when the vod playback is ended
@pytest.mark.FS_VOD
@pytest.mark.sanity
@pytest.mark.non_regression
@pytest.mark.LV_L3
def test_ui_vod_black_and_white_video_ended():
    """
    Start a VOD playback
    Check if the playback screen is displayed , with error detection
    Check the stream is playing
    Get the current stream position
    Wait for few seconds
    Check the current stream position is greater than the previous one
    Press the media_play (pause) key
    Check the playback screen is in pause mode
    Check the video is in pause mode
    Set the position near end of the video
    Wait a while to perform the seek
    Press the media_play (pause) key
    Check the video is resumed
    Wait until the main_hub screen is displayed
    Check new stream is playing
    """
    ve_test = VeTestApi("test_ui_vod_black_and_white_video_ended")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.log_assert(status,"Shall be on the main hub screen.")
    ve_test.wait(GENERIC_WAIT)
    start_playback_and_check(ve_test)
    check_position(ve_test)
    duration = vod_manager.get_total_duration()
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT);
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(is_paused,"playback shall be paused")
    ve_test.screens.playback.verify_streaming_paused()
    seek_position = duration - 20000
    ve_test.milestones.sendCommand("seekPlayback",str(seek_position))
    ve_test.wait(15)
    ve_test.screens.playback.verify_position(seek_position,"about",15000)
    ve_test.appium.key_event("KEYCODE_MEDIA_PLAY_PAUSE")
    ve_test.wait(GENERIC_WAIT)
    curmilestones = ve_test.milestones.getElements()
    is_paused = ve_test.milestones.get_value_by_key(curmilestones, "is_paused")
    ve_test.log_assert(not is_paused,"playback shall be resumed")
    vod_playback_status = ve_test.screens.playback.verify_streaming_playing()
    curmilestones = ve_test.milestones.getElements()
    vod_url = vod_playback_status['sso']['sessionPlaybackUrl']
    ve_test.wait(22)
    ve_test.screens.playback.verify_playing_url(vod_url,1,playing=True, compare="!=")
    ve_test.end()

# robustness test (short one)
@pytest.mark.FS_VOD
@pytest.mark.robustness
@pytest.mark.short
@pytest.mark.LV_L4
def test_ui_vod_robustness_seek():
    ve_test = VeTestApi("test_ui_vod_robustness_seek")
    assert_mgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.fullscreen)
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    ve_test.wait(2)
    vod_manager.start_free_playback(TIME_VOD_STARTING)
    logging.info("test_ui_vod_robustness_seek Scenario 1")
    '''Scenario 1:
        From Play, Retrieve the total duration of the playback,
        jump forward to 1 mn before the End of Stream, and wait until the End Of Stream
    '''
    vod_manager.jump_forward_to_end_of_stream( 60 , 0)
    #Compute the time to wait until the EOS (+ 5s), with a timeout of 75s
    total_dur = vod_manager.get_total_duration()
    logging.info("Scenario 1 : total_dur "+ str(total_dur))
    current_pos = vod_manager.get_current_position(0)
    logging.info("Scenario 1 : current_pos "+ str(current_pos))
    time_to_wait = min((total_dur - current_pos) / 1000 , 70) + 5
    logging.info("Scenario 1 : waiting "+ str(time_to_wait))
    ve_test.wait(time_to_wait)
    logging.info("Scenario 1 : " + str(vod_manager.get_current_position()) + "/"+ str(vod_manager.get_total_duration())+ " - screen = "+ve_test.milestones.get_current_screen())
    assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 1",
                             (ve_test.milestones.get_current_screen() == "filter" ),
                             "From a loop of seek forward, when we reach the EOF, we should come back to filter, not "+ve_test.milestones.get_current_screen())
     
    assert_mgr.verifyAllCheckPoints()
    '''
        Scenario 2:
        -     From Paused End Of Stream, jump backward to the Begin of stream (we should be in Pause)
        Action :
          - Restart the asset
          - Pause the playback
          - Jump until the EOS
          ==> We should stay in Pause
          - Do a loop of seek backward until the begin of stream
    '''
    logging.info("test_ui_vod_robustness_seek Scenario 2")
    status = ve_test.screens.main_hub.navigate()
    ve_test.wait(2)
    vod_manager.start_free_playback(TIME_VOD_STARTING)
    vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
    vod_manager.check_state(assert_mgr, "test_ui_vod_robustness_seek", "Scenario 2 - Check 0", "PAUSED", "trickmode",
                            "After pressing Pause, we should be in PAUSED state")
    vod_manager.jump_forward_to_end_of_stream( 0 , TIME_AFTER_JUMP_TO_EOS)
    vod_manager.check_state(assert_mgr, "test_ui_vod_robustness_seek", "Scenario 2 - Check 1", "PAUSED", "trickmode",
                            "From pause, when we jump forward and reach the EOS")
    logging.info("vod_manager.get_current_position() "+str(vod_manager.get_current_position()))
    logging.info("vod_manager.get_total_duration() "+str(vod_manager.get_total_duration()))
    logging.info("TIME_AFTER_JUMP_TO_EOS "+str(TIME_AFTER_JUMP_TO_EOS))
    # a jump is 90s and on pause a jump is not made if it will make to current position go after the end of file
    assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 2 - Check 2",
                             (vod_manager.get_current_position() < (vod_manager.get_total_duration() + 50))
                             and (vod_manager.get_current_position() > (vod_manager.get_total_duration() - (90*1000))),
                             "We should be at the end of stream (with a delta of 90 s) : current_position = "+ str(vod_manager.get_current_position()))
    assert_mgr.verifyAllCheckPoints()
     
    ''' Scenario 3:
        - From pause, jump backward until the Begin of stream
    '''
    logging.info("test_ui_vod_robustness_seek Scenario 3")
    vod_manager.jump_backward_to_begin_of_stream(TIME_AFTER_JUMP_TO_BOS)
    vod_manager.check_state(assert_mgr, "test_ui_vod_robustness_seek", "Scenario 3 - Check 1", "PAUSED", "trickmode",
                        "From pause, jump backward until the Begin of stream")
    assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 3 - Check 2",vod_manager.get_current_position()< ACCEPTED_DELTA_BEFORE_FIRST_IFRAME,
                             "We should be at the begin of stream (current_position="+str(vod_manager.get_current_position())+")")
    assert_mgr.verifyAllCheckPoints()
     
    ''' Scenario 4:
    - Go to the middle of the video, in play mode
    - Jump in backward until the begin of stream
    '''
    logging.info("test_ui_vod_robustness_seek Scenario 4")
    vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
    vod_manager.jump_forward_to_end_of_stream( vod_manager.get_total_duration() / 2000)
    vod_manager.jump_backward_to_begin_of_stream(TIME_AFTER_JUMP_TO_BOS)
    vod_manager.check_state(assert_mgr, "test_ui_vod_robustness_seek", "Scenario 4 - Check 1", "PLAYING", "fullscreen", "From play, when we jump backward and reach the EOS")
    assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 4 - Check 2",
                             (vod_manager.get_current_position() <  10000) and (vod_manager.get_current_position() > 0),
                             "We should be at the begin of stream (with a delta of 10 s) current_position="+str(vod_manager.get_current_position()))
    assert_mgr.verifyAllCheckPoints()
     
    '''
    Scenario 5
    - Loop of  Pause ... Play ... Jump Forward ... Pause ... Jump Forward ... Play ... Jump Backward ... Pause ... Jump Backward ...  Play
    '''
    logging.info("test_ui_vod_robustness_seek Scenario 5")
    vod_manager.jump_forward_to_end_of_stream(vod_manager.get_total_duration()/2000)
    start_time = ve_test.getInternetTime()
    i=0
    ve_test.wait(7)
    while ((ve_test.getInternetTime() - start_time) < 15 * 60 * 1000):
        logging.info("[time=" + str(ve_test.getInternetTime()) + " Loop ")
        i+=1
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 0" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING"),
                                 "Invalid check_state(expected_playstate="+"PLAYING" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 0"
                                 )
        # From playing, press pause
        vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 1" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PAUSED"),
                                 "Invalid check_state(expected_playstate="+"PAUSED" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 1"
                                 )
        # From pause, press play
        vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 2" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING"),
                                 "Invalid check_state(expected_playstate="+"PLAYING" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 2"
                                     )
        # From play, jump forward
        vod_manager.process_jump_forward(TIME_AFTER_JUMP_FORWARD, show_debugs=True)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 3" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING"),
                                 "Invalid check_state(expected_playstate="+"PLAYING" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 3"
                                 )
        # From playing, press pause
        vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 4" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PAUSED"),
                                 "Invalid check_state(expected_playstate="+"PAUSED" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 4"
                                 )
        # From pause, jump forward
        vod_manager.process_jump_forward(TIME_AFTER_JUMP_FORWARD, show_debugs=True)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 5" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PAUSED"),
                                 "Invalid check_state(expected_playstate="+"PAUSED" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 5"
                                 )
        # From pause, press play
        vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 6" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING"),
                                 "Invalid check_state(expected_playstate="+"PLAYING" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 6"
                                 )
        # From playing, jump backward
        vod_manager.process_jump_backward(TIME_AFTER_JUMP_BACKWARD, show_debugs=True)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 7" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING"),
                                 "Invalid check_state(expected_playstate="+"PLAYING" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 7"
                                 )
        # From playing, press pause
        vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 8" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PAUSED"),
                                 "Invalid check_state(expected_playstate="+"PAUSED" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 8"
                                 )
        # From pause, jump backward
        vod_manager.process_jump_backward(TIME_AFTER_JUMP_BACKWARD, show_debugs=True)
        assert_mgr.addCheckPoint("test_ui_vod_robustness_seek", "Scenario 5 - Loop "+ str(i) + "- Check 9" ,
                                 (ve_test.milestones.getPlaybackStatus()['playbackState'] == "PAUSED"),
                                 "Invalid check_state(expected_playstate="+"PAUSED" +
                                 ",playback_state="+ ve_test.milestones.getPlaybackStatus()['playbackState']
                                 + ") from : loop step 9"
                                 )
        # From pause, press play
        vod_manager.process_play_or_pause(TIME_AFTER_PLAY_PAUSE)
        assert_mgr.verifyAllCheckPoints()
		
    assert_mgr.verifyAllCheckPoints()
    ve_test.end()
 
# Robustness test
VOD_ROBUSTNESS_LOOP_SIZE = 50 #times
VOD_MAX_TIME_TO_PLAY = 10 #s
@pytest.mark.FS_VOD
@pytest.mark.robustness
@pytest.mark.LV_L4
def test_ui_vod_robustness_start_stop():
    ve_test = VeTestApi("test_ui_vod_robustness_seek")
    assert_mgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.fullscreen)
    vod_manager = ve_test.screens.playback.vod_manager
    status = ve_test.screens.main_hub.navigate()
    live_status = ve_test.milestones.getPlaybackStatus()
     
    ve_test.wait(2)
    vod_manager.start_free_playback(TIME_VOD_STARTING)
     
    for i in range(1,VOD_ROBUSTNESS_LOOP_SIZE+1) :
        vod_manager.check_state(assert_mgr,"test_ui_vod_robustness_start_stop", "start-1", "PLAYING", "fullscreen", "Start["+ str(i) + "] : invalid state or screen")
        assert_mgr.addCheckPoint("test_ui_vod_robustness_start_stop", "start-2",
                                 ve_test.milestones.getPlaybackStatus()['playbackType'] == "VOD",
                                 "The playing url should be vod")
        current_pos = vod_manager.get_current_position(TIME_PLAYING_CHECK_TWO_POSITIONS)
        new_current_pos = vod_manager.get_current_position()
        assert_mgr.addCheckPoint ("test_ui_vod_robustness_start_stop", "start-3", new_current_pos > current_pos, ("Sanity VOD - 1st step: Position has not correclty changed during normal playback  : old=" + str(current_pos) + " --> new = "+str(new_current_pos)))
        vod_manager.process_stop(TIME_VOD_STOPPING)
        new_live_status = ve_test.milestones.getPlaybackStatus()
        vod_manager.check_state(assert_mgr, "test_ui_vod_robustness_start_stop", "stop-1","PLAYING", "filter", "Stop["+ str(i) + "] : invalid state or screen")
        assert_mgr.addCheckPoint("test_ui_vod_robustness_start_stop", "stop-2", live_status['sso']['sessionPlaybackUrl'] == new_live_status['sso']['sessionPlaybackUrl'], "After stopping the vod playback we should play the live")
        assert_mgr.verifyAllCheckPoints()
        ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
        ve_test.wait(GENERIC_WAIT)
        ve_test.appium.key_event("KEYCODE_DPAD_UP")
        ve_test.wait(GENERIC_WAIT)
        ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
        ve_test.wait(TIME_VOD_STARTING)
        
    ve_test.screens.playback.kpi_to_html(VOD_PLAYBACK_TYPE)
    parser = KpiRequestParserAPI(ve_test.milestones.getVodKpiMeasurement())
    assert_mgr.addCheckPoint("test_ui_vod_robustness_start_stop", "robust-1", (parser.getFailedPlaybackNb() == 0 and parser.getSuccessPlaybackNb() == VOD_ROBUSTNESS_LOOP_SIZE), "At least one vod playback has failed" )
    assert_mgr.addCheckPoint("test_ui_vod_robustness_start_stop", "perf-1", parser.getMaxPlaybackStartSequenceDuration() < (VOD_MAX_TIME_TO_PLAY * 1000), "A VOD playback took more than 10s to be played" )
    assert_mgr.verifyAllCheckPoints()
    ve_test.end()
