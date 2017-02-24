__author__ = 'Oceane Team'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import logging


#########################################################
#                     PRIVATE Functions                 #
#########################################################


def check_grid_screen_back_key(test,press_key):
    """
    private function to check grid screen navigation with BACK key.
    :param test:
    :param press_key:
    :return:
    """
    test.move_towards(press_key)
    test.validate_focused_item(1)
    test.wait(CONSTANTS.GENERIC_WAIT)
    screen_name = test.milestones.get_current_screen()
    test.log_assert(screen_name == 'guide',
                    "GRID:ACCESS_EXIT: The Guide screen should be displayed (%s)" % screen_name)
    # Press Back to leave the GRID screen
    test.appium.key_event("KEYCODE_BACK")
    test.wait(CONSTANTS.GENERIC_WAIT)
    screen_name = test.milestones.get_current_screen()
    test.log_assert(screen_name != 'guide',
                    "GRID:ACCESS_EXIT: When pressing on BACK, The Guide screen is left (%s)" % screen_name)


def check_grid_current_focus_state(test):
    """
    private function to check different focus state in grid.
    :param test:
    :return:
    """

    #
    # Check NOW state
    all_elements = test.milestones.getElements()
    focus_state = test.milestones.get_value_by_key(all_elements,"focus_state")
    test.log_assert(focus_state == 1, "GRID:NAVIGATION:NOW: Current state is %s and NOW is expected."
                    % CONSTANTS.GRID_STATE[focus_state])
    logging.info("GRID:NAVIGATION:NOW: Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    # Check NEXT state
    test.move_towards(direction='right', wait_few_seconds=2)
    all_elements = test.milestones.getElements()
    focus_state = test.milestones.get_value_by_key(all_elements,"focus_state")
    test.log_assert(focus_state == 2, "GRID:NAVIGATION:NEXT: Current state is %s and NEXT is expected."
                    % CONSTANTS.GRID_STATE[focus_state])
    logging.info("GRID:NAVIGATION:NEXT: Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])

    # Check TONIGHT state
    test.move_towards(direction='right', wait_few_seconds=2)
    all_elements = test.milestones.getElements()
    focus_state = test.milestones.get_value_by_key(all_elements,"focus_state")
    test.log_assert(focus_state == 3, "GRID:NAVIGATION:TONIGHT: Current state is %s and TONIGHT is expected."
                    % CONSTANTS.GRID_STATE[focus_state])
    logging.info("GRID:NAVIGATION:TONIGHT: Current state is: %s" % CONSTANTS.GRID_STATE[focus_state])


#########################################################
#                     DOCUMENTATION FUNCTIONS           #
#########################################################
# Functions below are here for documentation pupose only.
# The goal of this is to centralize documentation of QA tests
# using tests from other testLevels (L1/L2/L3).
# Documentation is automatically generated here :
# http://ubu-iptv01.cisco.com/dropbox/Android_sf_k_stb_QA_Tests_doc

def doc_test_qa_grid_current_programme_info():
    """
    TEST: test GRID information for current program

     Step : we are in  full screen
        Action
        - focus on an event (TODAY event)
        - focus on NOW
        - press on "OK" key to launch Action Menu
        Checkup
        - check the programme title and channel logo of the current event in the grid screen
          with those founded in the action menu

    executes test from :
    e2e_tests/test_unitary_actionmenu_ltv.py:test_actionmenu_in_guide_current_event_current_channel()

    markers:
    @pytest.mark.QA
    @pytest.mark.QA_grid
    """

def doc_test_qa_grid_future_programme_info():
    """
    TEST: test GRID information for future program

     Step : we are in  full screen
        Action
        - focus on an event (TODAY event)
        - focus on NEXT
        - press on "OK" key to launch Action Menu
        Checkup
        - check the programme title and channel logo of the future event in the grid screen
          with those found in the action menu

    executes test from :
    e2e_tests/test_unitary_actionmenu_ltv.py:test_actionmenu_in_guide_future_event_current_channel

    markers:
    @pytest.mark.QA
    @pytest.mark.QA_grid
    """

#########################################################
#                     TESTS FUNCTIONS                   #
#########################################################


@pytest.mark.QA
@pytest.mark.QA_grid
def test_qa_grid():
    """
    TEST: test navigation into GRID

     1st step : we are in HUB Screen and the "GRID" is focused
        Action
        - go to "yesterday" option, then validate it
        Checkup
        - check that the GRID screen is displayed.
        - check it is possible to leave the GRID screen by pressing the BACK key

     2nd step : we are in HUB Screen and the "GRID" is focused
        Action
        - go to "today" option, then validate it
        Checkup
        - check that the GRID screen is displayed.
        - check it is possible to leave the GRID screen by pressing the BACK key

     3rd step : we are in HUB Screen and the "GRID" is focused
        Action
        - go to "tomorrow" option, then validate it
        Checkup
        - check that the GRID screen is displayed.
        - check it is possible to leave the GRID screen by pressing the BACK key

     4th step : we are in HUB Screen and the "GRID" item is focused
        Action
        - go to GRID screen
        Checkup
        - check different focus state(NOW, NEXT and TONIGHT)
        - check it is possible to navigate horizontally in the GRID

     5th step : we are in HUB Screen and the "GRID" item is focused
        Action
        - go to GRID screen
        Checkup
        - check it is possible to navigate vertically  in the GRID

     6th step : we are in HUB Screen and the "GRID" item is focused
        Action
        - go to GRID screen
        Checkup
        - check it is possible to navigate in the GRID and reach limits horizontally and vertically (long key press)

     7th step : we are in  "GRID" screen
        Action
        - focus on an event (TODAY event)
        - press on "OK" key to launch Action Menu
        - select "PLAY" item
        Checkup
        - check it is possible to play video of the current channel via the PLAY action from the GRID screen
     """

    logging.info("Begin test_qa_grid")
    # Initialization of test
    test = VeTestApi(title="test_qa_grid")
    test.begin(screen=test.screens.main_hub)
    status = test.screens.main_hub.focus_item_in_hub(item_title='GRID')
    test.log_assert(status, "GRID:ACCESS_EXIT: Failed to focus Grid in HUB Screen")

    # yesterday
    ############
    ''' 1st step : we are in HUB Screen and the "GRID" is focused
        Action
        - go to "yesterday" option, then validate it
        Checkup
        - check that the GRID screen is displayed.
        - check it is possible to leave the GRID screen by pressing the BACK key
    '''
    check_grid_screen_back_key(test,'left')

    # today
    ############
    ''' 2nd step : we are in HUB Screen and the "GRID" is focused
        Action
        - go to "today" option, then validate it
        Checkup
        - check that the GRID screen is displayed.
        - check it is possible to leave the GRID screen by pressing the BACK key
    '''
    check_grid_screen_back_key(test, 'right')

    # tomorrow
    ############
    ''' 3rd step : we are in HUB Screen and the "GRID" is focused
        Action
        - go to "tomorrow" option, then validate it
        Checkup
        - check that the GRID screen is displayed.
        - check it is possible to leave the GRID screen by pressing the BACK key
    '''
    check_grid_screen_back_key(test, 'right')

    # Move focus on TODAY
    test.move_towards('left')

    # Navigation horizontally in the GRID screen
    ############
    ''' 4th step : we are in HUB Screen and the "GRID" item is focused
        Action
        - go to GRID screen
        Checkup
        - check different focus state(NOW, NEXT and TONIGHT)
        - check it is possible to navigate horizontally in the GRID
    '''
    # Going into guide
    logging.info("GRID:NAVIGATION:HORIZONTAL: Going into guide")
    status = test.screens.guide.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.log_assert(status, "GRID:NAVIGATION:HORIZONTAL: guide to hub failed")
    # Check different focus state
    check_grid_current_focus_state(test)

    for _i in range(1, 10):
        status = test.screens.guide.to_nextevent_in_guide()
        test.log_assert(status,
                        "GRID:NAVIGATION:RIGHT: Focus should be changed after pressing a key.")

    # Navigation vertically  in the GRID screen
    ############
    ''' 5th step : we are in HUB Screen and the "GRID" item is focused
        Action
        - go to GRID screen
        Checkup
        - check it is possible to navigate vertically  in the GRID
    '''
    # Going into guide
    logging.info("GRID:NAVIGATION:VERTICAL:Going into guide")
    for _i in range(1, 10):
        status = test.screens.guide.to_nextevent_in_guide()
        test.log_assert(status,
                        "GRID:NAVIGATION:DOWN: Focus should be changed after pressing a key.")

    # Press Back to leave the GRID screen
    test.appium.key_event("KEYCODE_BACK")
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Navigation horizontal long press key in the GRID screen: TO IMPLEMENT
    ############
    ''' 6th step : we are in HUB Screen and the "GRID" item is focused
        Action
        - go to GRID screen
        Checkup
        - check it is possible to navigate in the GRID and reach limits horizontally and vertically (long key press)
    '''

    # GRID Play option
    ############
    ''' 7th step : we are in  "GRID" screen
        Action
        - focus on an event (TODAY event)
        - press on "OK" key to launch Action Menu
        - select "PLAY" item
        Checkup
        - check it is possible to play video of the current channel via the PLAY action from the GRID screen
    '''
    # Going into guide
    logging.info("GRID:ACTION: Launch Action Menu and validate PLAY action")
    status = test.screens.guide.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.log_assert(status, "GRID:ACTION:PLAY: to guide from hub failed")
    test.move_towards(direction='down', wait_few_seconds=CONSTANTS.GENERIC_WAIT)
    all_elements = test.milestones.getElements()
    new_focused_channel_number = test.milestones.get_value_by_key(all_elements,"focused_channel_number")
    test.screens.action_menu.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.action_menu.navigate_to_action('PLAY')
    test.validate_focused_item(1)
    logging.info("GRID:ACTION:PLAY: Check the streaming and the channel")
    playing_status = test.screens.playback.verify_streaming_playing()
    test.log_assert(playing_status, "GRID:ACTION:PLAY: zapping from grid failed")
    test.wait(CONSTANTS.WAIT_TIMEOUT)
    all_elements = test.milestones.getElements()
    current_channel = test.milestones.get_value_by_key(all_elements,"current_channel")
    test.log_assert(current_channel == new_focused_channel_number,
                    "GRID:ACTION:PLAY: Channel number should be different. Live channel: %s   Guide channel:  %s"
                    % (current_channel, new_focused_channel_number))
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("##### End test_qa_grid #####")
    test.end()
