__author__ = 'callix'

from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import pytest
import logging

# ====================
# UTILITIES FUNCTIONS
# ====================

def get_focused_event(test):
#    event = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_event_title", None, 10)
    event = test.milestones.get_value_by_key_retry("focused_event_title")
    if event == False:
        logging.info("get_focused_event milestone: %s" % test.milestones.getElements())
    return event


def get_focused_channel_number(test):
#    channel_number = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_channel_number", None, 10)
    channel_number = test.milestones.get_value_by_key_retry("focused_channel_number")
    return channel_number


def get_live_event(test):
#    event = test.milestones.get_value_by_key(test.milestones.getElements(), "current_event_title", None, 10)
    event = test.milestones.get_value_by_key_retry("current_event_title")
    return event


def get_live_channel(test):
#    channel_number = test.milestones.get_value_by_key(test.milestones.getElements(), "current_channel", None, 10)
    channel_number = test.milestones.get_value_by_key_retry("current_channel")
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
                    "Fail to zap by Timeline. Differents channel are playing before and after Timeline zapping\n"
                    "previous_lcn: {0}   new_lcn: {1}\nMilestone: {2}"
                    .format(expected_lcn, new_lcn, test.milestones.getElements()))

# ====================
# TESTS
# ====================

CHANNEL_WITH_VIDEO_A = 1

@pytest.mark.non_regression
@pytest.mark.FS_Timeline
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_zapping
def test_timeline_launch_exit():
    """
    Verify that the Timeline is launched by Right/Left key and exit with OK/Back key
    """
    test = VeTestApi("test_timeline_launch_exit")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.WAIT_TIMEOUT)

    logging.info("Zap on channel number {0}".format(CHANNEL_WITH_VIDEO_A))
    test.screens.playback.dca(CHANNEL_WITH_VIDEO_A, with_ok=True)
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT)
    test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, "fullscreen")

    check_playback_state_playing(test)
    elements = test.milestones.getElements()
    fullscreen_lcn = test.milestones.get_value_by_key(elements, 'current_channel')

    # Check that the user is able to zap on the same channel by the Timeline
    # ######################################################################
    logging.info("Verify that the user is able to zap on the same channel by the Timeline (OK key press)")
    status = test.screens.timeline.navigate("left")
    test.log_assert(status, "Fail to launch the Timeline by long Left key press. Current screen: {0}"
                    .format(test.milestones.get_current_screen()))
    test.wait(2*CONSTANTS.GENERIC_WAIT)

    status = test.screens.fullscreen.navigate("ok")
    test.log_assert(status, "Fail to dismiss the Timeline by OK on same channel than the launch one. "
                            "Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.WAIT_TIMEOUT)

    # Check the stream is playing and the channel
    check_playback_state_playing(test)
    check_channel_playing(test, fullscreen_lcn)

    # Check that the user is able to zap on another channel by the Timeline
    # ######################################################################
    logging.info("Verify that the user is able to zap on another channel by the Timeline (OK key press)")
    elements = test.milestones.getElements()
    fullscreen_lcn = test.milestones.get_value_by_key(elements, 'current_channel')

    status = test.screens.timeline.navigate("left")
    test.log_assert(status, "Fail to launch the Timeline by long Left key press. "
                            "Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Scroll in the timeline")
    test.screens.timeline.to_nextchannel('down')
    test.screens.timeline.to_nextchannel('down')

    elements = test.milestones.getElements()
    timeline_lcn = test.screens.timeline.get_focused_channel_number(elements)

    test.log_assert(timeline_lcn != fullscreen_lcn, "Unable to select another channel in Timeline"
                            "timeline_lcn: {0}".format(timeline_lcn))

    status = test.screens.fullscreen.navigate("ok")
    test.log_assert(status, "Fail to dismiss the Timeline by OK on different channel than the launch one."
                            "Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.WAIT_TIMEOUT)

    check_playback_state_playing(test)
    check_channel_playing(test, timeline_lcn)

    # Check that the Timeline can be launched with a Right key press and exit by Back
    # ###############################################################################
    logging.info("Verify that Timeline can be launch by Right long key press")
    elements = test.milestones.getElements()
    fullscreen_lcn = test.milestones.get_value_by_key(elements, 'current_channel')
    status = test.screens.timeline.navigate("right")
    test.log_assert(status, "Fail to launch the Timeline. Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Verify that Timeline can be exit by Back key press")
    status = test.screens.fullscreen.navigate("back")
    test.log_assert(status, "Fail to exit from timeline by Back. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.WAIT_TIMEOUT)

    check_playback_state_playing(test)
    check_channel_playing(test, fullscreen_lcn)

    test.end()
    logging.info("##### End test_timeline_launch_exit #####")


@pytest.mark.non_regression
@pytest.mark.FS_Timeline
@pytest.mark.LV_L2
def test_timeline_launch_check_channel_event():
    """
    Verify that the Timeline is launched on current channel/current event
    """
    test = VeTestApi("test_timeline_launch_check_event")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.WAIT_TIMEOUT)

    check_playback_state_playing(test)

    test.screens.fullscreen.wait_for_event_with_minimum_time_until_end()
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT+1)

    check_playback_state_playing(test)

    logging.info("Retrieve the fullscreen current channel/event")
    fullscreen_event_title = get_live_event(test)
    fullscreen_channel = get_live_channel(test)
    logging.info("Fullscreen channel: %s   event: %s" % (fullscreen_channel ,fullscreen_event_title))

    logging.info("Launch the Timeline")
    status = test.screens.timeline.navigate('right')
    test.log_assert(status, "Failed to launch the timeline. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    logging.info("Retrieve the Timeline current channel/event")
    timeline_current_event = get_focused_event(test)
    timeline_current_channel = get_focused_channel_number(test)
    logging.info("Timeline channel: %s   event: %s" % (timeline_current_channel, timeline_current_event))

    test.log_assert(timeline_current_channel == fullscreen_channel,
                    "Failure " + '\n' + "timeline_channel= %s live_channel= %s" % (timeline_current_channel, fullscreen_channel))

    test.log_assert(timeline_current_event == fullscreen_event_title,
                    "Failure " + '\n' + "timeline_event= %s live_event= %s" % (timeline_current_event, fullscreen_event_title))

    # Change of channel and check
    test.wait(CONSTANTS.SCREEN_TIMEOUT+1)
    test.screens.playback.dca(2)
    check_playback_state_playing(test)

    test.screens.fullscreen.wait_for_event_with_minimum_time_until_end()
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT+1)
    check_playback_state_playing(test)

    logging.info("Retrieve the fullscreen current channel/event")
    fullscreen_event_title = get_live_event(test)
    fullscreen_channel = get_live_channel(test)
    logging.info("Fullscreen channel: %s   event: %s" % (fullscreen_channel, fullscreen_event_title))

    logging.info("Launch the Timeline")
    status = test.screens.timeline.navigate('left')
    test.log_assert(status, "Failed to launch the timeline. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    logging.info("Retrieve the Timeline current channel/event")
    timeline_current_event = get_focused_event(test)
    timeline_current_channel = get_focused_channel_number(test)
    logging.info("Timeline channel: %s   event: %s" % (timeline_current_channel, timeline_current_event))

    test.log_assert(timeline_current_channel == fullscreen_channel,
                    "Failure " + '\n' + "timeline_channel= %s live_channel= %s" % (
                    timeline_current_channel, fullscreen_channel))

    test.log_assert(timeline_current_event == fullscreen_event_title,
                    "Failure " + '\n' + "timeline_event= %s live_event= %s" % (
                    timeline_current_event, fullscreen_event_title))

    test.end()
    logging.info("##### End test_timeline_launch_check_event #####")


@pytest.mark.non_regression
@pytest.mark.FS_Timeline
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_live
@pytest.mark.QA_live_timeline
def test_timeline_timeout():
    """
    Verify that the Timeline is no longer display after timeout from last user interaction
    """
    test = VeTestApi("test_timeline_timeout")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.WAIT_TIMEOUT)

    check_playback_state_playing(test)

    logging.info("Verify that Timeline is dimissed after timeout from Timeline access")
    status = test.screens.timeline.navigate()
    test.log_assert(status, "Failed to open the timeline. Current screen: %s" % test.milestones.get_current_screen())
    logging.info("-- Check timeout")
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.check_timeout("timeline", CONSTANTS.SCREEN_TIMEOUT-CONSTANTS.GENERIC_WAIT)
    test.log_assert(status, "Failure on timeout test at launch")
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Verify Timeline dismiss after timeout from last user interaction (Up)")
    status = test.screens.timeline.navigate()
    test.log_assert(status, "Failed to open the timeline. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.SCREEN_TIMEOUT-5)
    test.move_towards('up', 0.5)
    logging.info("-- Check timeout")
    status = test.check_timeout('timeline', CONSTANTS.SCREEN_TIMEOUT)
    test.log_assert(status, "Failure on timeout test after last user interaction")
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Verify Timeline dismiss after timeout from last user interaction (Down)")
    status = test.screens.timeline.navigate()
    test.log_assert(status, "Failed to open the timeline. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.SCREEN_TIMEOUT-10)
    test.move_towards('down', 0.5)
    logging.info("-- Check timeout")
    status = test.check_timeout('timeline', CONSTANTS.SCREEN_TIMEOUT)
    test.log_assert(status, "Failure on timeout test after last user interaction")
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Verify Timeline dismiss after timeout from last user interaction (Left)")
    status = test.screens.timeline.navigate()
    test.log_assert(status, "Failed to open the timeline. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.SCREEN_TIMEOUT-12)
    test.move_towards('right', 0.5)
    logging.info("-- Check timeout")
    status = test.check_timeout('timeline', CONSTANTS.SCREEN_TIMEOUT)
    test.log_assert(status, "Failure on timeout test after last user interaction")
    test.wait(CONSTANTS.GENERIC_WAIT)

    logging.info("Verify Timeline dismiss after timeout from last user interaction (Right)")
    status = test.screens.timeline.navigate()
    test.log_assert(status, "Failed to open the timeline. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.SCREEN_TIMEOUT-12)
    test.move_towards('left', 0.5)
    logging.info("-- Check timeout")
    status = test.check_timeout('timeline', CONSTANTS.SCREEN_TIMEOUT)
    test.log_assert(status, "Failure on timeout test after last user interaction")
    test.wait(CONSTANTS.GENERIC_WAIT)

    test.end()
    logging.info("##### End test_timeline_timeout #####")


@pytest.mark.non_regression
@pytest.mark.FS_Timeline
@pytest.mark.dummy
@pytest.mark.LV_L2
def test_timeline_cyclic():
    """
    Verify that the Timeline is cyclic
    """
    test = VeTestApi(title="test_timeline_cyclic")
    test.begin(screen=test.screens.fullscreen) 

    logging.info("Go in Initials Conditions: fullscreen with video playing")
    status = test.screens.fullscreen.navigate()
    test.log_assert(status,
                    "Initials Conditions: Fail to go to fullscreen. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.WAIT_TIMEOUT)

    check_playback_state_playing(test)

    logging.info("Launch the timeline")
    status = test.screens.timeline.navigate()
    test.log_assert(status, "Fail to open the timeline. Current screen: %s" % test.milestones.get_current_screen())

    logging.info("Navigate through all the channels lineup (by down)")
    first_channel = test.milestones.get_value_by_key(test.milestones.getElements(),  "focused_channel_number")
    test.wait(CONSTANTS.GENERIC_WAIT)
    for n in range(0, 1000):
        test.move_towards('down', 0.5)
        current_channel = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_channel_number")
        if current_channel == first_channel:
            break
        if n > 1000:
            test.log_assert("Fail to get the focus to the next channel in the timeline")
            break
    logging.info("-- The number of channel scrolled is %s" % n)

    logging.info("Navigate through all the channels lineup (by up)")
    test.wait(CONSTANTS.GENERIC_WAIT)
    for n in range(0, 1000):
        test.move_towards('up', 0.5)
        current_channel = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_channel_number")
        if current_channel == first_channel:
            break
        if n > 1000:
            test.log_assert("Fail to get the focus to the next channel in the timeline")
            break

    logging.info("-- The number of channel scrolled is %s"%n)

    test.end()
    logging.info("##### End test_timeline_cyclic #####")


@pytest.mark.non_regression
@pytest.mark.FS_Timeline
@pytest.mark.LV_L3
def test_timeline_missing_channel_logo():
    """
    Check that the channel is displayed in case of no channel logo is available
    :return:
    """
    test = VeTestApi("test_timeline_missing_channel_logo")

    test.begin(screen=test.screens.fullscreen) 

    status = test.screens.fullscreen.navigate()
    test.log_assert(status, "Hub timeout to fullscreen failed")
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    # Check that Channel name is displayed as no logo is available
    status = test.screens.timeline.navigate()
    test.log_assert(status, "Failed to be in Zaplist")

    # Zap to a channel without logo
    channel_number = CONSTANTS.channel_number_without_logo
    logging.info("Zap to channel n %s" % channel_number)
    test.screens.playback.dca(channel_number)
    test.wait(2*CONSTANTS.GENERIC_WAIT)
    status, logo = test.get_channel_logo_display('focused_channel_info')
    logging.info("status get_channel_logo_display: %s " % status)
    test.log_assert(not status, "Channel logo is displayed and is not expected on this channel (%s)" % test.milestones.get_value_by_key(test.milestones.getElements(),'focused_channel_info'))
    status, channel_name = test.get_channel_name_display('focused_channel_info')
    logging.info("status get_channel_name_display: %s " % status)
    test.log_assert(status, "Channel name is not displayed and is expected on this channel (%s)." % test.milestones.get_value_by_key(test.milestones.getElements(),'focused_channel_info'))

    # Zap to a channel with logo
    channel_number = CONSTANTS.channel_number_classic_1
    test.screens.playback.dca(channel_number)
    logging.info("Zap to channel n %s" % channel_number)
    test.wait(2*CONSTANTS.GENERIC_WAIT)
    # Check that Channel name is displayed as no logo is available
    status, logo = test.get_channel_logo_display('focused_channel_info')
    test.log_assert(status, "Channel logo is NOT displayed and is expected on this channel (%s)" % test.milestones.get_value_by_key(test.milestones.getElements(),'focused_channel_info'))
    test.wait(CONSTANTS.GENERIC_WAIT)

    test.end()
