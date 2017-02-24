
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.ve_tests.ve_test import VeTestApi

import pytest
import logging

# ====================
# UTILITIES FUNCTIONS
# ====================



def zaplist_scroll_channellineup(test, direction='down'):
    test.move_towards(direction)
    test.wait(0.5)
    current_channel = test.milestones.get_value_by_key_retry("focused_channel_number")
    return current_channel


def get_live_event(test):
    event = test.milestones.get_value_by_key_retry("current_event_title")
    return event


def get_live_channel(test):
    event = test.milestones.get_value_by_key_retry("current_event_title")
    return event


def get_focused_event(test):
    event = test.milestones.get_value_by_key_retry("focused_event_title")
    if not event:
        logging.info("get_focused_event milestone: %s" % test.milestones.getElements())
    return event


def get_focused_channel_number(test):
    channel_number = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_channel_number")
    return channel_number


def check_playback_state_playing(test):
    playback_status = test.screens.playback.verify_streaming_playing()
    test.log_assert(playback_status, "Failure to retrieve valid playback status: {0}".format(playback_status))

    playback_state = playback_status["playbackState"]
    test.log_assert(playback_state == "PLAYING",
                    "Playback is NOT in PLAYING state. Current screen: {0}  playback_state:  {1}\n"
                    "getPlaybackStatus: {2}"
                    .format(test.milestones.get_current_screen(), playback_state, test.milestones.getPlaybackStatus()))


def check_channel_playing(test, expected_lcn):
    elements = test.milestones.getElements()
    new_lcn = test.milestones.get_value_by_key(elements, 'current_channel')
    test.log_assert(new_lcn, "Fail to retrieve the fullscreen channel number."
                    "Milestone: {0}".format(test.milestones.getElements()))

    test.log_assert(new_lcn == expected_lcn,
                    "Fail to zap by Zaplist. Differents channel are playing before and after Zaplist zapping\n"
                    "previous_lcn: {0}   new_lcn: {1}\nMilestone: {2}"
                    .format(expected_lcn, new_lcn, test.milestones.getElements()))


# ====================
# TESTS
# ====================

@pytest.mark.non_regression
@pytest.mark.FS_Zaplist
@pytest.mark.LV_L2
def test_zaplist_launch_exit():
    """
    Verify that the Channel List can be launch and exit on fullscreen
      - launch by a Up and Down long key press
      - exit by Back or OK key press
    :return:
    """
    test = VeTestApi("test_zaplist_launch_exit")
    test.begin(screen=test.screens.fullscreen) 

    # Go to Initial Conditions: afullscreen
    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())

    logging.info("Verify that Zaplist can be launch by DOWN long key press")
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT+CONSTANTS.GENERIC_WAIT)

    check_playback_state_playing(test)
    fullscreen_lcn = test.screens.fullscreen.get_current_channel()

    logging.info("Verify that Zaplist can be launch by DOWN long key press")
    status = test.screens.zaplist.navigate('down')
    test.log_assert(status, "Fail to launch the zaplist. Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Verify that Zaplist can be exit by Back key press")
    status = test.screens.fullscreen.navigate(direction="back")
    test.log_assert(status, "Fail to exit the zaplist by Back key press. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    check_playback_state_playing(test)
    check_channel_playing(test, fullscreen_lcn)

    fullscreen_lcn = test.screens.fullscreen.get_current_channel()

    logging.info("Verify that Zaplist can be launch by UP long key press")
    status = test.screens.zaplist.navigate("up")
    test.log_assert(status, "Fail to launch the Zaplist. Current screen: %s" % test.milestones.get_current_screen())

    logging.info("Verify that Zaplist can be exit by OK key press")
    status = test.screens.fullscreen.navigate(direction="ok")
    test.log_assert(status, "Fail to exit the zaplist by OK key press. Current screen: {0}".format(test.milestones.get_current_screen()))

    check_playback_state_playing(test)
    check_channel_playing(test, fullscreen_lcn)

    test.wait(CONSTANTS.GENERIC_WAIT)

    test.end()
    logging.info("##### End test_zaplist_launch_exit #####")


@pytest.mark.non_regression
@pytest.mark.FS_Zaplist
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_zaplist_timeout():
    """
    Verify that the Zaplist is no longer display after timeout from last user interaction.
    Check with Up, Down, Left and Right
    """
    test = VeTestApi("test_zaplist_timeout")
    test.begin(screen=test.screens.fullscreen) 

    # Go to Initial Conditions: fullscreen
    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT+CONSTANTS.GENERIC_WAIT)

    logging.info("Check timeout after launch")
    status = test.screens.zaplist.navigate('down')
    test.log_assert(status, "Fail to launch the zaplist. Current screen: %s" % test.milestones.get_current_screen())
    status = test.check_timeout("zap_list_tv", CONSTANTS.INFOLAYER_TIMEOUT)
    test.log_assert(status, "Failure on timeout test at launch")
    test.wait(CONSTANTS.GENERIC_WAIT)

    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())

    logging.info("Check timeout after user interaction (Down)")
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT+CONSTANTS.GENERIC_WAIT)
    status = test.screens.zaplist.navigate('down')
    test.log_assert(status, "Fail to launch the zaplist. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    test.move_towards(direction='down')
    status = test.check_timeout("zap_list_tv", CONSTANTS.INFOLAYER_TIMEOUT)
    test.log_assert(status, "Failure on timeout from last user interaction (down)")
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Check timeout after user interaction (Up)")
    status = test.screens.zaplist.navigate('down')
    test.log_assert(status, "Fail to launch the zaplist. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.move_towards(direction='up')
    status = test.check_timeout("zap_list_tv", CONSTANTS.INFOLAYER_TIMEOUT)
    test.log_assert(status, "Failure on timeout from last user interaction (Up)")
    test.wait(CONSTANTS.GENERIC_WAIT)

    test.end()
    logging.info("##### End test_zaplist_timeout #####")

@pytest.mark.non_regression
@pytest.mark.FS_Zaplist
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_zapping
def test_zaplist_cyclic():
    """
    Verify that the Channel List is cyclic
    """
    test = VeTestApi(title="test_zaplist_cyclic")
    test.begin(screen=test.screens.fullscreen) 

    # Go to Initial Conditions: fullscreen
    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT+CONSTANTS.GENERIC_WAIT)

    logging.info("Verify that Zaplist can be launch by UP/Down long key press")
    status = test.screens.zaplist.navigate('down')
    test.log_assert(status, "Fail to launch the zaplist. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(1)

    logging.info("Navigate through all the channels lineup")
    first_channel = get_focused_channel_number(test)
    logging.info("First channel: %s" % first_channel)

    for n in range(1, 1000):
        current_channel = zaplist_scroll_channellineup(test, 'down')
        if current_channel == first_channel:
            logging.info("The number of channel scrolled is %s" % n)
            break
    else:
        test.log_assert(False, "Not able to find to come-back on the first channel")

    for n in range(1, 1000):
        current_channel = zaplist_scroll_channellineup(test, 'up')
        if current_channel == first_channel:
            logging.info("The number of channel scrolled is %s" % n)
            break
    else:
        test.log_assert(False, "Not able to find to come-back on the first channel")

    test.end()
    logging.info("##### End test_zaplist_cyclic #####")


@pytest.mark.non_regression
@pytest.mark.FS_Zaplist
@pytest.mark.dummy
@pytest.mark.LV_L2
def test_zaplist_services_order():
    """
    Verify that the services are displayed in ascending order
    """
    test = VeTestApi(title="test_zaplist_services_order")
    test.begin(screen=test.screens.fullscreen) 

    # Go to Initial Conditions: fullscreen
    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())
    channel_number = CONSTANTS.channel_number_classic_1
    test.screens.playback.dca(channel_number)
    logging.info("Zap to channel n {0}".format(channel_number))    
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT+CONSTANTS.GENERIC_WAIT)

    # Launch the Zaplist
    status = test.screens.zaplist.navigate('down')
    test.log_assert(status, "Fail to launch the zaplist. Current screen: %s" % test.milestones.get_current_screen())

    first_channel_number = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_channel_number")
    logging.info("Navigate through all the channels lineup and check the channel number order")
    logging.info("First channel: %s" % first_channel_number)

    previous_channel_number = first_channel_number
    for n in range(1, 1000):
        current_channel_number = zaplist_scroll_channellineup(test, 'down')
        if str(current_channel_number) == "False":      # the timing to zap can be a false problem
            logging.info("current_channel_number == False")
            continue
        # logging.info("---> new: %s   previous: %s" % (current_channel_number, previous_channel_number))
        if current_channel_number == first_channel_number:
            logging.info("The number of channel scrolled is %s" % n)
            break
        if current_channel_number < previous_channel_number:
            test.log_assert(False, "After %d zapping, next channel number (%s) is < previous number (%s)" % (n, current_channel_number, previous_channel_number))
            break
        previous_channel_number = current_channel_number
    else:
        test.log_assert(False, "Not able to find to come-back on the first channel")

    test.end()
    logging.info("##### End test_zaplist_services_order #####")


@pytest.mark.non_regression
@pytest.mark.FS_Zaplist
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_zapping
def test_zaplist_tuning():
    """
    Verify that the user is able to tune to another channel than the current one by the Channel List
    :return:
    """
    test = VeTestApi(title="test_zaplist_tuning")
    test.begin(screen=test.screens.fullscreen) 

    # Go to Initial Conditions: fullscreen
    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())
    channel_number = CONSTANTS.channel_number_classic_1
    test.screens.playback.dca(channel_number)
    logging.info("Zap to channel n {0}".format(channel_number))
    test.wait_for_screen(CONSTANTS.INFOLAYER_TIMEOUT, "fullscreen")
    check_playback_state_playing(test)

    # Launch the Zaplist
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.zaplist.navigate("down")
    test.log_assert(status, "Failed to launch the Zaplist. Current screen: %s" % test.milestones.get_current_screen())

    # Check the tuning on another service than the current one
    test.move_towards('down')
    test.move_towards('down')

    zaplist_channel = False
    elements = test.milestones.getElements()
    if test.screens.zaplist.verify_zaplist_showing(elements):
        zaplist_channel = get_focused_channel_number(test)
    else:
        test.log_assert(False, "Failure to keep in Zaplist, no able to retrieve channel and event. {0}".format(elements))

    # Wait a few to check that the automatic zapping occurs
    status = test.wait_for_screen(CONSTANTS.INFOLAYER_TIMEOUT + CONSTANTS.SCREEN_TIMEOUT, "fullscreen")
    test.log_assert(status, "Failure to automatically go in Fullscreen. {0}".format(status))

    check_playback_state_playing(test)
    check_channel_playing(test, zaplist_channel)

    test.end()
    logging.info("##### End test_zaplist_tuning #####")


@pytest.mark.non_regression
@pytest.mark.FS_Zaplist
@pytest.mark.LV_L3
def test_zaplist_services_list():
    """
    Verify that the Channel List display all the services
    :return:
    """
    test = VeTestApi("test_zaplist_services_list")
    test.begin(screen=test.screens.fullscreen) 

    # Retrieve the services list from the sched
    logical_channel_number_list = test.he_utils.get_channel_number_list_from_cmdc(serviceDeliveryType="ABR")
    cmdc_logical_channel_number_list = sorted(list(set(logical_channel_number_list)))

    # Go to Initial Conditions: fullscreen
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Failed to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # Launch the Zaplist
    status = test.screens.zaplist.navigate('up')
    test.log_assert(status, "Failed to launch the Zaplist. Current screen: %s" % test.milestones.get_current_screen())
    zaplist_channel_number = int(test.milestones.get_value_by_key_retry("focused_channel_number", 3))
    first_zaplist_channel_number = zaplist_channel_number
    # logging.info("zaplist_channel_number: %s" % zaplist_channel_number)

    # Browse the Zaplist and build the Zaplist Channel number list
    total_number_of_services = len(cmdc_logical_channel_number_list)
    logging.info("cmdc totalNumberOfServices: %s" % total_number_of_services)
    zaplist_services_number_list = []
    for n in range(0, 1000):
        if zaplist_channel_number not in zaplist_services_number_list:
            zaplist_services_number_list.append(zaplist_channel_number)
        else:
            test.log_assert(False, "Channel number %s is already present" % zaplist_channel_number)
        test.move_towards('down')
        zaplist_channel_number = int(test.milestones.get_value_by_key(test.milestones.getElements(), "focused_channel_number"))
        if zaplist_channel_number == first_zaplist_channel_number:
            break
    zaplist_services_number_list.sort()
    logging.info("zaplist totalNumberOfServices: %s" % len(zaplist_services_number_list))

    test.log_assert(cmdc_logical_channel_number_list == zaplist_services_number_list, "Service List is not the same:\n  Zaplist: %s  \n cmdc: %s" % (zaplist_services_number_list, cmdc_logical_channel_number_list))

    test.end()
    logging.info("##### End test_zaplist_services_list #####")


@pytest.mark.non_regression
@pytest.mark.FS_Zaplist
@pytest.mark.LV_L3
def test_zaplist_missing_channel_logo():
    """
    Check that the channel is displayed in case of no channel logo is available
    :return:
    """
    test = VeTestApi(title="test_zaplist_missing_channel_logo")

    test.begin(screen=test.screens.fullscreen) 

    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Hub timeout to fullscreen failed")
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # Check that Channel name is displayed as no logo is available
    status = test.screens.zaplist.navigate('down')
    test.log_assert(status, "Failed to be in Zaplist")

    # Zap to a channel without logo
    channel_number = CONSTANTS.channel_number_without_logo
    logging.info("Zap to channel n %s" % channel_number)
    test.screens.playback.dca(channel_number)
    test.wait(CONSTANTS.GENERIC_WAIT)
    status, logo = test.get_channel_logo_display('focused_channel_info')
    logging.info("status get_channel_logo_display: %s " % status)
    test.log_assert(not status, "Channel logo is displayed and is not expected on this channel (%s)" % test.milestones.get_value_by_key(test.milestones.getElements(), 'focused_channel_info'))
    status, channel_name = test.get_channel_name_display('focused_channel_info')
    logging.info("status get_channel_name_display: %s " % status)
    test.log_assert(status, "Channel name is not displayed and is expected on this channel (%s)." % test.milestones.get_value_by_key(test.milestones.getElements(), 'focused_channel_info'))

    # Zap to a channel with logo
    channel_number = CONSTANTS.channel_number_classic_1
    test.screens.playback.dca(channel_number)
    logging.info("Zap to channel n %s" % channel_number)
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that Channel name is displayed as no logo is available
    status, logo = test.get_channel_logo_display('focused_channel_info')
    test.log_assert(status, "Channel logo is NOT displayed and is expected on this channel (%s)" % test.milestones.get_value_by_key(test.milestones.getElements(), 'focused_channel_info'))
    test.wait(CONSTANTS.GENERIC_WAIT)

    test.end()
