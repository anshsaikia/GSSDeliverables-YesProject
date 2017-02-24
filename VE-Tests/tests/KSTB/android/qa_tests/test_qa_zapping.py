__author__ = 'Oceane Team'

from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

import pytest
import logging

#########################################################
#                     PRIVATE Functions                 #
#########################################################


def check_qa_zapping_get_live_channel(qa_test):
    """
    private function to get current channel number
    :param qa_test:
    :return: channel_number
    """
    elements = qa_test.milestones.getElements()
    channel_number = qa_test.milestones.get_value_by_key(elements, "current_channel")
    return channel_number


def check_qa_zapping_action_play(test):
    """
    private function to zap down (P-) and check video playback
    :param test:
    :return:
    """

    test.move_towards(direction='down', wait_few_seconds=CONSTANTS.GENERIC_WAIT)
    elements = test.milestones.getElements()
    new_focused_channel_number = test.milestones.get_value_by_key(elements, "focused_channel_number")
    logging.info("ZAPPING:ACTION: Launch Action Menu and validate PLAY action")
    test.screens.action_menu.navigate()
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.action_menu.navigate_to_action('PLAY')
    test.validate_focused_item(1)
    logging.info("ZAPPING:ACTION:PLAY: Check the streaming and the channel")
    playing_status = test.screens.playback.verify_streaming_playing()
    test.log_assert(playing_status, "ZAPPING:ACTION:PLAY: zapping from grid failed")
    test.wait(CONSTANTS.WAIT_TIMEOUT)
    elements = test.milestones.getElements()
    current_channel = test.milestones.get_value_by_key(elements, "current_channel")
    test.log_assert(current_channel == new_focused_channel_number,
                    "ZAPPING:ACTION:PLAY: Channel number should be different. Live channel: %s   Guide channel:  %s"
                    % (current_channel, new_focused_channel_number))
    test.wait(CONSTANTS.GENERIC_WAIT)


#########################################################
# DOCUMENTATION FUNCTIONS           #
#########################################################
# Functions below are here for documentation pupose only.
# The goal of this is to centralize documentation of QA tests
# using tests from other testLevels (L1/L2/L3).
# Documentation is automatically generated here :
# http://ubu-iptv01.cisco.com/dropbox/Android_sf_k_stb_QA_Tests_doc

def doc_test_qa_zapping_zap_via_zaplist():
    """
    TEST: check zapping feature via zaplisst

    step : go to full screen
       Action
       - press "DOWN" Key to display zaplist screen
       Checkup
       - check that the user is able to change a channel to an another channel by
         selecting one in the Channel List in zap list: zap via the ZAP list

   executes test from :
   e2e_tests/test_unitary_zaplist.py:test_zaplist_tuning()

   markers :
   @pytest.mark.QA
   @pytest.mark.QA_zapping
   """

def doc_test_qa_zapping_zap_via_timeline():
   """
   TEST: check zapping features via timeline

   step : go to full screen
      Action
      - press "LEFT" Key, then press "DOWN" Key
      Checkup
      - check that the user is able to change a channel to an another channel by
        selecting one in timeline by pressing OK: zap via timeline

   executes test from :
   e2e_tests/test_unitary_zaplist.py:test_timeline_launch_exit()

   markers :
   @pytest.mark.QA
   @pytest.mark.QA_zapping
   """

def doc_test_qa_zapping_zap_via_up_down():
    """
    TEST: check zapping features via up/down key (P+/P-)

    step : go to full screen
       Action
       - press "UP/DOWN" Key
       Checkup
       - check that the user is able to change a channel to another channel by
         pressing on UP/DOWN Key : zap via UP/DOWN Key

    executes test from :
    e2e_tests/test_zapping.py:test_unitary_zapping_to_next_channel_ethernet()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_zapping
    """

def doc_test_qa_zapping_loop_via_zaplist():
    """
    TEST: check zapping loop feature in zaplist

    step : go to full screen
       Action
       - press on "UP/DOWN" Key to display the zaplist
       Checkup
       - check that the user is able to zap and loop to the initial channel via the zaplist

    executes test from :
    e2e_tests/test_unitary_zaplist.py:test_zaplist_cyclic()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_zapping
    """

def doc_test_qa_zapping_loop_via_timeline():
    """
    TEST: check zapping loop feature in timeline

    step : go to full screen
       Action
       - press "LEFT/RIGHT" Key  to display the timeline screen
       Checkup
       - check that the user is able to zap and loop to the initial channel via the timeline

    executes test from :
    e2e_tests/test_unitary_timeline.py:test_timeline_cyclic()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_zapping
    """


def doc_test_qa_dca_fullscreen():
    """
    TEST: check DCA behavior on fullscreen

    Steps : Check DCA behavior on fullscreen
       Action
         - zapping on existing channel
         - zapping on non-existing channel (hole in the channel list)
         - zapping on non-existing channel (out of bound)

       Checkup
         - check dca with correction in keypress
         - check if DCA Error message

    executes test from :
    e2e_tests/test_unitary_dca.py:test_dca_fullscreen()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_dca
    """

def doc_test_qa_dca_grid():
    """
    TEST: Check DCA behavior on grid

    Steps : Check DCA behavior on grid
       Action
         - zapping on existing channel
         - zapping on non-existing channel (hole in the channel list)
         - zapping on non-existing channel (out of bound)

       Checkup
         - check dca with correction in keypress
         - check if DCA Error message

   executes test from :
   e2e_tests/test_unitary_dca.py:test_dca_grid()

   markers :
   @pytest.mark.QA
   @pytest.mark.QA_dca
   """

#########################################################
# TESTS FUNCTIONS                   #
#########################################################
@pytest.mark.QA
@pytest.mark.QA_zapping
def test_qa_zapping_zap_via_grid():
    """
    TEST: check zapping features via the grid

     step : go to grid screen
        Action
        - press "OK" Key, then select "Play" item
        Checkup
        - check that the user is able to change a channel to an another channel by
          selecting one in grid by Action Menu "PLAY" item: zap via the grid
    """
    logging.info("##### Begin of test_qa_zapping_zap_via_grid #####")
    ############
    ''' step : go to grid screen
        Action
        - press "OK" Key, then select "Play" item
        Checkup
        - check that the user is able to change a channel to an another channel by
          selecting one in grid by Action Menu "PLAY" item: zap via the grid
    '''
    # Initialization of test
    test = VeTestApi(title="test_qa_zapping_zap_via_grid")
    test.begin(screen=test.screens.fullscreen)
    status = test.screens.main_hub.navigate()
    test.log_assert(status, "ZAPPING:ACTION:PLAY: Failed to go to HUB Screen")
    status = test.screens.main_hub.focus_item_in_hub(item_title='GRID')
    test.log_assert(status, "ZAPPING:ACTION:PLAY: Failed to focus Grid in HUB Screen")
    test.validate_focused_item(1)
    test.wait(CONSTANTS.GENERIC_WAIT)
    screen_name = test.milestones.get_current_screen()
    test.log_assert(screen_name == 'guide',
                    "ZAPPING:ACTION:PLAY: The Guide screen should be displayed (%s)" % screen_name)
    # Check it is possible to to change a channel to an another channel by selecting one in grid
    # by Action Menu "PLAY" item
    check_qa_zapping_action_play(test)
    logging.info("##### End of test_qa_zapping_zap_via_grid #####")
    test.end()


@pytest.mark.QA
@pytest.mark.QA_zapping
def test_qa_zapping_zap_after_booting():
    """
    TEST: check zapping features after boot

     step : go to full screen
        Action
        - press go to next channel by pressing on "UP/DOWN" Key
        - press on HOME button to exit appli
        - re-start appli
        Checkup
        - check that after booting, the default channel A/V is displayed

    """
    logging.info("##### Begin of test_qa_zapping_zap_after_booting #####")

    # Initialization
    qa_test = VeTestApi("test_qa_zapping_zap_after_booting")
    # Go to full screen
    qa_test.begin(screen=qa_test.screens.fullscreen)
    # Zap to another channel
    print ("ZAPPING: test_qa_zapping_zap_after_booting : Zap to next channel")
    qa_test.screens.playback.zap_to_next_channel(CONSTANTS.WAIT_TIMEOUT)
    # Get the number of current channel before booting
    number_of_channel_before_booting = check_qa_zapping_get_live_channel(qa_test)
    # restart app
    print ("ZAPPING: test_qa_zapping_zap_after_booting : Restart app")
    qa_test.appium.restart_app()
    qa_test.wait(15)
    # Press Back to go to fullscreen from Hub
    qa_test.appium.key_event("KEYCODE_BACK")
    qa_test.wait(CONSTANTS.LONG_WAIT)
    logging.info("ZAPPING: test_qa_zapping_zap_after_booting : We should be on full screen ")
    screen_name = qa_test.milestones.get_current_screen()
    qa_test.log_assert(screen_name == 'fullscreen' , "fail to go back on fullscreen , we are on: " + screen_name)
    # Get the number of current channel after booting
    number_of_channel_after_booting = check_qa_zapping_get_live_channel(qa_test)
    # Check if after booting, the default channel A/V is displayed
    qa_test.log_assert(number_of_channel_before_booting == number_of_channel_after_booting,
                    "ZAPPING: Failure " + '\n' + "number_of_channel_before_booting= %s number_of_channel_after_booting= %s" % (
                           number_of_channel_before_booting, number_of_channel_after_booting))
    # End test
    qa_test.end()
    logging.info("##### End of test_qa_zapping_zap_after_booting #####")
