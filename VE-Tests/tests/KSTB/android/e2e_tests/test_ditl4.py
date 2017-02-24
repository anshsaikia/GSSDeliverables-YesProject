# -*- coding: utf-8 -*-
__author__ = 'oceane_team'
from tests_framework.ve_tests.assert_mgr import AssertMgr
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.ve_tests.ve_test import VeTestApi
from datetime import datetime
import logging
import pytest
import sys

' Global constants '
channel_number = 5

# Actions for current event on current channel and asset in the Store
actionlist_video_live_current_event = ['SUMMARY', 'RECORD', 'WATCH LIST', 'RELATED', 'LIKE', 'ADD TO FAVORITES']
actionlist_video_live_current_event2 = ['INHALT', 'AUFNEHMEN', 'WATCH LIST', 'ÄHNLICHE', 'LIKE', 'ZU FAVORITEN HINZUFÜGEN']
actionlist_store_asset = ['SUMMARY', 'PLAY', 'WATCH LIST', 'LIKE']

def check_action_menu_logo_title(test, expected_channel_logo, expected_event_title) :
    return test.screens.action_menu.check_action_menu_logo_title(expected_channel_logo, expected_event_title)

def check_screen_on_back(test, screen):
    logging.info("Check that '%s' is displayed on Back" % screen)
    test.go_to_previous_screen()
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, screen)
    test.log_assert(status, "Fail to go back to %s. Current screen: %s" % (screen, test.milestones.get_current_screen()))
    return status

def check_navigate_grid(test):
    for i in range(1, 3):
        test.move_towards(direction='down')
    for i in range(1, 3):
        test.move_towards(direction='right')
    test.screens.action_menu.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
    test.log_assert(status, "Failed to go to action_menu. Current screen: %s" % (test.milestones.get_current_screen()))

def check_actionmenu_list(test,assertmgr):
    # Check all action list items
    for nb in range(0, len(actionlist_video_live_current_event)):
        selected_item = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_item") #which item is focused ?
        logging.info("selected_item: %s" % selected_item)
        if selected_item not in actionlist_video_live_current_event and selected_item not in actionlist_video_live_current_event2:
            assertmgr.addCheckPoint("test_ditl4_scenario_search", 1, False, "%s is displayed but not in the lists:\n   %s\n    (%s)" % (selected_item, actionlist_video_live_current_event,actionlist_video_live_current_event2))
        test.move_towards('up')

def check_play_in_actionmenu_list(test,assertmgr):
    # Check all action list items
    for nb in range(0, len(actionlist_store_asset)):
        selected_item = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_item") #which item is focused ?
        logging.info("selected_item: %s" % selected_item)
        if selected_item == "PLAY":
            # lopp is done
            break
        test.move_towards('up')

def check_position(vod_manager, test, assertmgr):
    """
    Allow to check if the position is correct
    :param vod_manager: the vod manager instance
    :param test_vod: the current test
    """
    current_position_prev = test.screens.playback.vod_manager.get_current_position(CONSTANTS.GENERIC_WAIT)
    test.wait(5)
    current_position = test.screens.playback.vod_manager.get_current_position(CONSTANTS.GENERIC_WAIT)
    if not (current_position > current_position_prev):
        assertmgr.addCheckPoint("Test_ditl4_vod", 2, False, "The current position is not valid : " + str(current_position) + " , expected to be more than : " + str(current_position_prev))

def check_search_scenarios_and_update_clock(test, assertmgr):

    # Check that default focus is on 'A'
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    assertmgr.addCheckPoint("Test_ditl4_search", 4, selected_char == 'A' , "Default focus is NOT on first letter of alphabetical characters but: %s" % selected_char)

    # Select letter and check suggestions
    #####################################
    letter = 'C'
    logging.info("Select letter %s" % letter)
    status = test.screens.search.search_select_char(letter, True)
    assertmgr.addCheckPoint("Test_ditl4_search", 5, status , "Fail to selected character: %s" % letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    assertmgr.addCheckPoint("Test_ditl4_search", 6, status , "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # validate the first suggestion to go to the search result screen
    if suggestions_nb == 1 and suggestions_list[0] == CONSTANTS.g_no_suggestions_msg_text:
        assertmgr.addCheckPoint("Test_ditl4_search", 7, False, "No suggestion available")

    asset = suggestions_list[0]
    test.screens.search.scroll_to_suggestion(asset)
    test.validate_focused_item()
    status = test.screens.fullcontent.is_in_full_content()
    assertmgr.addCheckPoint("Test_ditl4_search", 8,status, "Fail to go in search result screen (%s) for asset: %s" % (test.milestones.get_current_screen(), asset))

    clock_time = test.get_clock_time()
    if not clock_time:
        assertmgr.addCheckPoint("Test_ditl4_search", 9, False, "The Clock is not displayed in Search fullcontent")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    ######################################
    status = test.check_clock_time_update(clock_time)
    if not status :
      assertmgr.addCheckPoint("Test_ditl4_search", 10, False, "Clock is not more displayed after 1min OR clock time has not changed. Current screen: %s" % test.milestones.get_current_screen())

    test.go_to_previous_screen(wait_few_seconds=5)
    test.wait(CONSTANTS.GENERIC_WAIT)

     # Press <
    status = test.screens.search.search_select_char('<', True)
    assertmgr.addCheckPoint("Test_ditl4_search", 11, status , "Fail to selected character: <")
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    assertmgr.addCheckPoint("Test_ditl4_search", 12, input_text == '_' , "Fail to erase C")

    #check "no suggestion available" scneario
    #########################################
    status = test.screens.search.search_select_char('A', True)
    assertmgr.addCheckPoint("Test_ditl4_search", 13, status, "Fail to selected character: A")
    status = test.screens.search.search_select_char('B', True)
    assertmgr.addCheckPoint("Test_ditl4_search", 14, status, "Fail to selected character: B")
    status = test.screens.search.search_select_char('C', True)
    assertmgr.addCheckPoint("Test_ditl4_search", 15, status, "Fail to selected character: C")
    milestone = test.milestones.getElements()
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list', milestone)
    logging.info("%s" % suggestions_list)
    if not (suggestions_list == [u'No suggestion available.']) :
      assertmgr.addCheckPoint("Test_ditl4_search", 16, False, "There is a suggestion available in the list!")
    test.go_to_previous_screen()



##### All the scenario : Zapping, Timeline, Search, Grid, and VOD

def scenario_ditl4_zapping(test, assertmgr):
    """
    Check the FullScreen is correctly launched from Hub
    Press DOWN  keys for zapping
    Stock the Channel Number as Initial Channel Number
    Press DOWN several times
    Press RIGHT or LEFT keys from Live TV to access the Timeline
    Press UP keys and return to the initial channel
    Press OK to go to FullScreen
    Check if we have returned to the Initial Channel Number
    :param test:
    :param assertmgr:
    """

    ############
    ''' First step : Zapping by UP/Down
        Action
        - zapping via the zapplist UP/Down
        - zapping by DCA
        Checkup
        - check before zapping is the fullscreen is launched
    '''

 	# Press DOWN Key press to Zapp
    for n in range(1, 4):
       test.move_towards(direction='down')
       test.wait(CONSTANTS.GENERIC_WAIT)

	# Zapping by entering a channel number
    test.wait(5)
    test.screens.playback.dca(channel_number)
    test.wait(CONSTANTS.LONG_WAIT)

	# Stock channel number as first channel
    first_channel = int(test.milestones.get_value_by_key(test.milestones.getElements(), "focused_channel_number"))
    logging.info("First channel: %s" % first_channel)

    # Press DOWN several times via Zapplist
    for n in range(1, 5):
        test.move_towards("down")
        test.wait(CONSTANTS.GENERIC_WAIT)

    ''' Second step : Zapping via Timeline
         Action
         - Launch and Scrolling in the Timeline
         - Trying to come back to the first channel
         Checkup
         - Check if the timeline is launched
         - Retrieve the current position, and check the expected channel
    '''
	# Launch and Scrolling in the Timeline
    test.wait(CONSTANTS.GENERIC_WAIT)
    logging.info("Verify that Timeline can be launch by Left long key press")
    status = test.screens.timeline.navigate("left")
    test.log_assert(status, "Fail to launch the timeline by long Left key press. Current screen: %s" % test.milestones.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    #Trying to come back to the first channel
    logging.info("Scrolling in the timeline")
    for n in range(1, 5):
        test.move_towards("up")
        current_channel = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_channel_number")
        # check if we have returned to the first channel
        if current_channel == first_channel:
            logging.info("The number of channel scrolled is %s" %n)
            break
    else:
        assertmgr.addCheckPoint("Test_ditl4_zapping", 3, False, "Not able to find to come-back on the first channel")

    logging.info("Verify that Timeline can be exit by OK key press")
    status = test.screens.fullscreen.navigate("ok")
    test.log_assert(status, "Fail to dismiss the timeline by OK on different channel than the launch one. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.WAIT_TIMEOUT)

def scenario_ditl4_timeline(test, assertmgr):
    """
    Navigate horizontally via LEFT or RIGHT keys
    Select one item (channel/event) then press OK to launch the Action Menu
    check information related on the selected item: channel logo and event title
    Come-back to Timeline screen with the BACK key
    Come-back to Live TV(Full screen) with the BACK key
    Access to Main Hub via BACK key
    :param test:
    :param assertmgr:
    """
    ''' First step : go to timeline
        Action
        - Launch and scroll in the timeline
        - go from timeline to fullscreen
        Checkup
        - check that the timeline can be launched
        - Check video playing when come back on fullscreen
    '''

    # check that the timeline can be launched
    logging.info("Verify that Timeline can be launch by right long key press")
    status = test.screens.timeline.navigate("right")
    test.log_assert(status, "Fail to launch the timeline by long Right key press. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Scroll in the timeline")
    test.screens.timeline.to_nextchannel('up')

    logging.info("Go in Initials Conditions: fullscreen with video playing")
    status = test.screens.fullscreen.navigate("ok")
    test.log_assert(status,
                    "Initials Conditions: Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.WAIT_TIMEOUT)

    playback_state = test.screens.playback.verify_streaming_playing()
    playback_status = playback_state["playbackState"]
    test.log_assert(playback_status == "PLAYING",
                    "Initials Conditions: Fail to playback in fullscreen. Current screen: %s  playback_status: %s" % (test.milestones.get_current_screen(), playback_status))

    ''' Second step : Select an item in the timeline
        Action
        - Launch and naviguate in the timeline
        - select an item from the timeline
        Checkup
        - check that the timeline can be launched
        - check the action menu of the selected item
    '''

    logging.info("From Live TV, launch Timeline by pressing on Right long key press")
    status = test.screens.timeline.navigate("right")
    logging.info("Verify that Timeline can be launch by Right long key press")
    test.log_assert(status, "Fail to launch the timeline. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

	# Navigate horizontally via RIGHT
	# Select an item (channel/event) then launch the Action Menu
    logging.info("Select an item (channel/event) then launch the Action Menu")
    for n in range(0, 3):
        test.move_towards('right', 0.2)

	# Memorize the selected item (channel/event)
    milestone = test.milestones.getElements()
    timeline_channelLogo = test.milestones.get_value_by_key(milestone, "focused_channel_logo")
    timeline_eventTitle  = test.milestones.get_value_by_key(milestone, "focused_event_title")

	# launch the Action Menu
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.action_menu.navigate()
    test.log_assert(status, "Fail to open the Action Menu. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    ''' Third step : Check logo in the timeline
        Action
        - retrieve logo url in action menu
        - return to timeline and then fullscreen
        Checkup
        - check that Timeline is displayed on Back
        - check go back on fullscreen
    '''
	# Do not perform the comparison in Dummy
    if not test.is_dummy:
        status = check_action_menu_logo_title(test, timeline_channelLogo,timeline_eventTitle)
        test.log_assert(status, "Action menu logo url or event title not valid. See log error messages")

        # Return to the time line screen
        logging.info("Check that Timeline is displayed on Back")
        check_screen_on_back(test,"timeline")
        # Come-back to fullscreen with the back key
        test.wait(CONSTANTS.GENERIC_WAIT)
        status = test.to_fullscreen_from_timeline('back')
        test.log_assert(status, "Fail to go back on fullscreen after Timeline->ActionMenu->Back->Back. Current screen: %s" % test.milestones.get_current_screen())
    else:
        logging.info("Dummy mode. Check only that Fullscreen is displayed on Back")
        check_screen_on_back(test,"timeline")
        check_screen_on_back(test,"fullscreen")

	logging.info("Press on Back in fullscreen")
	test.go_to_previous_screen()
	test.wait(CONSTANTS.GENERIC_WAIT)
	logging.info("Check that on Back in fullscreen, Main Hub screen is displayed")
    status = test.wait_for_screen(CONSTANTS.GENERIC_WAIT, "fullscreen" )
    test.log_assert(status, "Failed because we are not in main_hub screen")

def scenario_ditl4_search(test, assertmgr):
    """
    From Hub select search option
    Search for a valid string
    Count the number of suggestions
    Select the first one
    Wait 1min and check if time updated
    Go to the previous screen and delete the previous Search
    Search for an new invalid string
    Check that "No suggetions available"
    Access to Hub via BACK key
    Access to Fullscreen from Hub
    Repeat all the above actions for GENRE & TIME in Search
    :param test:
    :param assertmgr:
    """
    # Access to Hub from Fullscreen
    status = test.screens.main_hub.navigate()
    test.log_assert(status, "Fail to go to Hub from Fullscreen. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    ''' First step : Search from hub for a valid items
        Action
        - access to search from hub
        - select a valid caracter
        - wait under suggestions are available
        - select the first proposed one
        - wait 1 min and check time if updated
        - try to delete the entered character
        Checkup
        - check search if correctly launched from hub
        - check if suggestions field is empty
        - check time if updated after 1min of waiting
        - check keyborad after deleting the entered character
    '''

    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    check_search_scenarios_and_update_clock(test, assertmgr)
    ''' Second step : Search from hub for unvalid item
        Action
        - select unvalid item
        - check if any suggestion is available
        - come back to hub then fullscreen
        Checkup
        - check that 'No suggestion available'
        - check if suggestions field is empty
        - check if fullscreen is well launched
    '''
    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Fullscreen could not be accessed")
    test.wait(CONSTANTS.GENERIC_WAIT)

    ''' Third step : Search from Genres for a valid items
        Action
        - access to search from genres
        - select a valid caracter
        - wait under suggestions are available
        - select the first proposed one
        - wait 1 min and check time if updated
        - try to delete the entered character
        Checkup
        - check search if correctly launched from hub
        - check if suggestions field is empty
        - check time if updated after 1min of waiting
        - check keyborad after deleting the entered character
    '''
    status = test.screens.main_hub.navigate()
    test.log_assert(status, "Fail to go to Hub from Fullscreen . Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.store.navigate()
    test.log_assert(status, "Fail to go to Store. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    assertmgr.addCheckPoint("Test_ditl4_search", 17, status , "Fail to go to Search. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    check_search_scenarios_and_update_clock(test, assertmgr)

    ''' 4th step : Search from genres for unvalid item
        Action
        - select unvalid item
        - check if any suggestion is available
        - come back to hub then fullscreen
        Checkup
        - check that 'No suggestion available'
        - check if suggestions field is empty
        - check if screen is well launched
    '''
    # Come-back to Main-hub
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.main_hub.navigate()
    test.log_assert(status, "Fullscreen could not be accessed")
    test.wait(CONSTANTS.GENERIC_WAIT)

def scenario_ditl4_grid(test, assertmgr):
    """
    Navigation in the Grid From TODAY
    Select one program and press OK
    Navigate in all the proposed options
    Access back to the GRID menu via BACK key twice
    Repeat all the above actions for the Grid from Yesterday and Tomorrow
    :param test:
    :param assertmgr:
    """
    # Access to Hub from Fullscreen
    now = datetime.utcnow()
    status = test.screens.main_hub.navigate()
    test.log_assert(status, "Failed to be in Hub")

    status = test.screens.main_hub.focus_item_in_hub(item='GRID')
    test.log_assert(status, "Failed to focus Guide in Hub")

    ''' First step : Go to grid
        Action
        - access to search from hub
        - Going into guide of today
        - navigate in the grid
        - select an event
        - navigate in the action menu list
        Checkup
        - check the day is today
        - check focus state "Now is expected"
        - check action menu list
    '''

    # move the focus to "GRID"
    if test.is_dummy:
        status = test.screens.filter.focus_menu_item_by_id_in_filter("TELEVISION", "GRID")

    # check the day is today (does not work in dummy mode)
    if not test.is_dummy:
        logging.info("Checking calendar day is today")
        assertmgr.addCheckPoint("Test_ditl4_grid", 18, int(test.screens.main_hub.get_day_in_main_hub()) == int(now.day),
                        ("Calendar day is not today : %s is not %s", str(test.screens.main_hub.get_day_in_main_hub()), str(now.day)))
        assertmgr.addCheckPoint("Test_ditl4_grid", 19, (test.get_month_in_main_hub()).upper() == (now.strftime("%b")).upper(),
                        ("Calendar month is not today : %s is not %s", str(test.get_month_in_main_hub()), str(now.day)))
        logging.info("Calendar day is today")

    # Going into guide
    logging.info("Going into guide")

    status = test.screens.guide.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.log_assert(status, "to_guide_from_hub failed")

    # check the current day offset is 0
    assertmgr.addCheckPoint("Test_ditl4_grid", 20, test.screens.guide.get_dayOffset_in_guide() == 0, "dayOffset_now is not 0")

    # check different focus state
    focus_state = test.milestones.get_value_by_key(test.milestones.getElements(), "focus_state")
    assertmgr.addCheckPoint("Test_ditl4_grid", 21, focus_state == 1, "Current state is %s and NOW is expected." % CONSTANTS.GRID_STATE[focus_state])

    logging.info("Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    check_navigate_grid(test)
    check_actionmenu_list(test, assertmgr)

    # Going back on hub
    logging.info("Going back on hub")
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)

    ''' Second step : Go to grid
        Action
        - access to search from hub
        - Going into guide of yesterday
        - navigate in the grid
        - select an event
        - navigate in the action menu list
        Checkup
        - check the day is today
        - check focus state "Now is expected"
        - check action menu list
    '''

    test.move_towards('left')
    status = test.screens.guide.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.log_assert(status, "to_guide_from_hub failed")
    check_navigate_grid(test)
    check_actionmenu_list(test, assertmgr)

    # Going back on hub
    logging.info("Going back on hub")
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)

    ''' Third step : Go to grid
        Action
        - access to search from hub
        - Going into guide of tomorrow
        - navigate in the grid
        - select an event
        - navigate in the action menu list
        Checkup
        - check the day is today
        - check focus state "Now is expected"
        - check action menu list
    '''

    test.move_towards('right')
    test.move_towards('right')
    status = test.screens.guide.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.log_assert(status, "to_guide_from_hub failed")
    check_navigate_grid(test)
    check_actionmenu_list(test, assertmgr)

    # Going back on hub
    logging.info("Going back on hub")
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)

def scenario_ditl4_vod(test,assertmgr):
    """
    Start a VOD playback
    Check if the playback screen is displayed, with error detection
    Check the stream is playing
    Get the current stream position
    Wait for 9 seconds to complete the seek operation
    Navigate in actionmenu to STOP
    STOP the video and check Fullscreen
    :param test:
    :param assertmgr:
    """

    ''' First step : Going to Store
        Action
        - access to store from hub
        - select an asset vod
        - playback the selected one
        - wait for 9min
        - stop the playback via the action menu
        Checkup
        - check going to Store
        - verify streaming playing
        - check current position
        - check fullscreen
    '''

    #vod_manager = VODManager()
    status = test.to_store_from_hub()
    test.log_assert(status, "Fail to go to Store. Current screen: %s" % test.milestones.get_current_screen())
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)

    for i in range(1, 2):
     #check the VOD List
     test.move_towards('right')

    test.validate_focused_item(2)
    check_play_in_actionmenu_list(test,assertmgr)
    # Play the video
    test.validate_focused_item(2)
    start_status = test.screens.playback.verify_streaming_playing(test,test.milestones)
    check_position(test.screens.playback.vod_manager,test, assertmgr)
    current_position = test.screens.playback.vod_manager.get_current_position()
    test.wait(9)
    test.screens.action_menu.navigate()
    test.screens.action_menu.navigate_to_action('STOP')
    test.repeat_key_press("KEYCODE_DPAD_CENTER", 1, 5)
    test.wait(CONSTANTS.GENERIC_WAIT)
    stop_status = test.screens.playbacak.verify_streaming_playing(test,test.milestones)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.log_assert(start_status["playbackType"] != stop_status["playbackType"] , "Playback shoul be different %s - %s"%(start_status["playbackType"],stop_status["playbackType"]))


@pytest.mark.non_regression
@pytest.mark.LV_L4
def test_ditl4():
    '''
    - In ditl4, we navigate in all the principales features:
      PHASE 1 – ZAPPING
      PHASE 2 – TIMELINE
      PHASE 3 – GRID
      PHASE 4 – SEARCH
      PHASE 5 – VOD
    '''
    test = VeTestApi("Test_ditl4")
    assertmgr = AssertMgr(test)

    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    #status = test.to_fullscreen_from_hub()
    #test.wait(CONSTANTS.GENERIC_WAIT)

    # Zapping scenario
	# --------------------------------------
    scenario_ditl4_zapping(test, assertmgr)

	# Timeline scenario
	# --------------------------------------
    scenario_ditl4_timeline(test, assertmgr)

    # Search scenario
	# --------------------------------------
    scenario_ditl4_search(test, assertmgr)

    # Grid scenario
	# --------------------------------------
    scenario_ditl4_grid(test, assertmgr)

    # Vod scenario
	# --------------------------------------
    scenario_ditl4_vod(test,assertmgr)

    assertmgr.verifyAllCheckPoints()
    logging.info("##### End test_ditl4 #####")
    test.end()
