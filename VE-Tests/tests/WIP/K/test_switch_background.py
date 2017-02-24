from tests_framework.ve_tests.ve_test import VeTestApi
from datetime import datetime
from pytz import timezone
from tests_framework.ui_building_blocks.screen import ScreenActions
import pytest
import logging

VIDEO_AFTER_FOREGROUND_TIMEOUT = 10
BEFORE_BACKGROUND_TIMEOUT = 10
REMAIN_IN_BACKGROUND_TIMEOUT = 60
GENERIC_WAIT = 2


def access_to_fullcontent_in_store(test):
    tree = test.screens.store.create_category_tree()
    for section in tree.children:
        if section.type == "content_full":
            section_name = str(section.name).upper()
            logging.info("Access to section_name: %s" % section_name)
            category_element = test.milestones.getElement([("name", "text_view", "==")])
            test.appium.tap_element(category_element)
            test.wait(GENERIC_WAIT)
            return True
    return False


def navigate_and_switch(test, screen_name, time_in_background=REMAIN_IN_BACKGROUND_TIMEOUT):
    screen = test.screens.getScreenByName(screen_name)
    test.screens.navigateSingle(screen)
    test.wait(GENERIC_WAIT)
    switch_and_check(test, screen, time_in_background)


def switch_and_check(test, screen, time_in_background=REMAIN_IN_BACKGROUND_TIMEOUT):
    test.wait(GENERIC_WAIT)
    test.appium.send_app_to_background()
    test.wait(time_in_background)
    test.appium.send_app_to_foreground()
    test.wait(GENERIC_WAIT)
    screen.verify_active()
    logging.info("Succeed to switch and come-back to: {0}".format(screen.screen_name))


def check_playback_status(test, playback_status_before, playback_status_after):
    # Check channel
    test.log_assert(playback_status_after["currentChannelId"] == playback_status_before["currentChannelId"],
                    "channel changed !. After: {0}. Before: {1}".format(playback_status_after["currentChannelId"],
                                                                        playback_status_before["currentChannelId"]))

    # Check playbackState
    test.log_assert(playback_status_after["playbackState"] == playback_status_before["playbackState"],
                    "Playback state is not correct !. After: {0}. Before: {1}".format(
                        playback_status_after["playbackState"], playback_status_before["playbackState"]))

    # Check sessionId (shall be different due to stop playback
    test.log_assert(playback_status_after["sso"]["sessionId"] != playback_status_before["sso"]["sessionId"],
                    "session was not created !\n SessionId before: {0}\n SessionId after:  {1}".format(
                        playback_status_before["sso"]["sessionId"], playback_status_after["sso"]["sessionId"]))


def get_current_event_remaining_time(ve_test):
    """
    return the broadcasting time from the event in current full screen
    """
    elements = ve_test.milestones.getElements()

    trickmodeInfo = ve_test.milestones.getElement([("name", "trickmode_bar", "==")], elements)
    end_time = trickmodeInfo["end_time"].split(":")
    end_time_in_min = int(end_time[0])*60+int(end_time[1])

    UI_TIMEZONE = 'Europe/Berlin'

    he_current_time = datetime.now(timezone(UI_TIMEZONE))
    current_time_in_min = int(he_current_time.hour)*60+int(he_current_time.minute)
    if(end_time_in_min < current_time_in_min):
        end_time_in_min = end_time_in_min +60*24 #next day = add 24h

    time_to_end_in_min = end_time_in_min - current_time_in_min

    return time_to_end_in_min

@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_nav_to_hub_and_switch():
    """
    Navigate to Hub, set the application in background then wake-up it after 1 min.
    Check that the Hub is displayed at wake-up
    :return:
    """
    test = VeTestApi("test_nav_to_hub_and_switch")
    test.begin()
    navigate_and_switch(test, 'tv_filter')
    test.end()


@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_nav_to_linear_action_menu_and_switch():
    """
    Navigate to Linear Action Menu, set the application in background then wake-up it after 1 min.
    Check that the Linear Action Menu is displayed at wake-up
    :return:
    """
    test = VeTestApi("test_nav_to_linear_action_menu_and_switch")
    test.begin()
    test.screens.fullscreen.navigate()
    navigate_and_switch(test, 'action_menu')
    test.end()


@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_nav_to_search_and_switch():
    """
    Navigate to Search, set the application in background then wake-up it after 1 min.
    Check that the Search is displayed at wake-up
    :return:
    """
    test = VeTestApi("test_nav_to_search_and_switch")
    test.begin()
    navigate_and_switch(test, 'tv_search')
    test.end()


@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_nav_to_guide_and_switch():
    """
    Navigate to Guide, set the application in background then wake-up it after 1 min.
    Check that the Guide is displayed at wake-up
    :return:
    """
    test = VeTestApi("test_nav_to_guide_and_switch")
    test.begin()
    navigate_and_switch(test, 'guide')
    test.end()


@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_nav_to_zaplist_and_switch():
    """
    Navigate to Channel List, set the application in background then wake-up it after 1 min.
    Check that the Channel List is displayed at wake-up
    :return:
    """
    test = VeTestApi("test_nav_to_zaplist_and_switch")
    test.begin()
    navigate_and_switch(test, 'zap_list')
    test.end()


@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_nav_to_timeline_and_switch():
    """
    Navigate to Timeline, set the application in background then wake-up it after 1 min.
    Check that the Timeline is displayed at wake-up
    :return:
    """
    test = VeTestApi("test_nav_to_timeline_and_switch")
    test.begin()
    navigate_and_switch(test, "timeline")
    test.end()


@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_nav_to_fullcontent_and_switch():
    """
    Navigate to Fullcontent, set the application in background then wake-up it after 1 min.
    Check that the Fullcontent is displayed at wake-up
    :return:
    """
    test = VeTestApi("test_nav_to_fullcontent_and_switch")
    test.begin()

    test.screens.store_filter.navigate()
    status = access_to_fullcontent_in_store(test)
    test.log_assert(status, "Failure to find fullcontent in Store")

    screen = test.screens.getScreenByName('full_content_screen')
    switch_and_check(test, screen)

    test.end()

@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_background_vod_short():
    '''test_background_vod_short'''
    # Test with a short (30s) background time
    test = VeTestApi("test_background_vod_short")
    test.begin()
    VOD_TO_PLAY = "Man in Black SVOD"
    store = test.screens.store_filter
    store.play_vod_by_title(VOD_TO_PLAY)
    test.wait(5)

    screen = test.milestones.get_current_screen()
    test.log_assert(screen == "fullscreen" ,"Current screen should be fullscreen but is "+str(screen))
    logging.info("Exit application ")
    test.appium.send_app_to_background()
    test.wait(30)
    test.appium.send_app_to_foreground()
    logging.info("Back in application/fullscreen vod ")
    test.wait(5)
    screen = test.milestones.get_current_screen()
    test.log_assert(screen == "fullscreen" ,"Current screen should be fullscreen but is "+str(screen))

    test.end()


@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_background_live():
    """
    verify that we get the same live channel after going to background
    """
    test = VeTestApi("test_background_live")
    test.begin()

    test.screens.fullscreen.navigate()
    playback_status_before = test.milestones.getPlaybackStatus()

    test.appium.send_app_to_background()
    test.wait(REMAIN_IN_BACKGROUND_TIMEOUT)
    test.appium.send_app_to_foreground()
    test.wait(VIDEO_AFTER_FOREGROUND_TIMEOUT)

    playback_status_after = test.milestones.getPlaybackStatus()
    check_playback_status(test, playback_status_before, playback_status_after)

    test.end()

@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_background_timeline_short_nochange():
    '''test_background_timeline_short_nochange'''
    # Test with a short (10s) background time, on the 1st element
    # Check that foreground is timeline, same channel, same event is displayed first
    test = VeTestApi("test_background_timeline_short_nochange")
    test.begin(screen=None)

    # Go to timeline
    timeline = test.screens.timeline
    timeline.navigate()
    test.wait(5)
    time_to_end_in_min = get_current_event_remaining_time(test)

    #Check that the current event does not finish in the following minutes as to have the same one when coming back from background
    if time_to_end_in_min > 1:
        need_zapping = False
    else:
        need_zapping = True

    while need_zapping:
        test.screens.fullscreen.swipe_channel(direction=ScreenActions.UP)
        test.wait(2)
        timeline = test.screens.timeline
        timeline.navigate()

        time_to_end_in_min = get_current_event_remaining_time(test)
        if time_to_end_in_min > 1:
            need_zapping = False

    test.wait(5)
    elements = test.milestones.getElements()


    horizontalAssetsScroller = test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_LINEAR", "==")], elements)
    channel_id = horizontalAssetsScroller["channel_id"]
    event_id = horizontalAssetsScroller["event_id"]

    screen = test.milestones.get_current_screen()
    test.log_assert(screen == "timeline" ,"Current screen should be timeline but is "+str(screen))
    logging.info("Exit application ")
    test.appium.send_app_to_background()
    test.wait(10)
    logging.info("Go back in application/timeline ")
    test.appium.send_app_to_foreground()
    test.wait(5)
    screen = test.milestones.get_current_screen()
    test.log_assert(screen == "timeline" ,"Current screen should be timeline but is "+str(screen))
    elements = test.milestones.getElements()
    horizontalAssetsScroller = test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_LINEAR", "==")], elements)
    channel_id_foreground = horizontalAssetsScroller["channel_id"]
    event_id_foreground = horizontalAssetsScroller["event_id"]
    test.log_assert(channel_id == channel_id_foreground ,"Channel Id should not have changed, was "+str(channel_id)+ ", is "+str(channel_id_foreground))
    test.log_assert(event_id == event_id_foreground ,"event_id should not have changed, was "+str(event_id)+ ", is "+str(event_id_foreground))

    test.end()

@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_background_timeline_medium_first():
    '''test_background_timeline_medium_first'''
    # Test with a medium (5 min) background time, on the 1st element
    # Check that foreground is timeline, same channel, different event is displayed first
    test = VeTestApi("test_background_timeline_medium_first")

    test.begin(screen=None)

    # Go to timeline
    logging.info("Go to timeline ")
    timeline = test.screens.timeline
    timeline.navigate()
    test.wait(5)
    time_to_end_in_min = get_current_event_remaining_time(test)

    # Find a channel where the current vent ends in less than 5 minutes to have a different one when we come back from background after 5 min
    if time_to_end_in_min > 4:
        need_zapping = True
    else:
        if time_to_end_in_min == 0:
            need_zapping = True #event just finished/started so cannot know when it will actually finish
        else:
            need_zapping = False

    while need_zapping:
        test.screens.fullscreen.swipe_channel(direction=ScreenActions.UP)
        test.wait(2)
        timeline = test.screens.timeline
        timeline.navigate()

        time_to_end_in_min = get_current_event_remaining_time(test)
        if time_to_end_in_min > 4:
            need_zapping = True
        else:
            if time_to_end_in_min == 0:
                need_zapping = True #event just finished/started so cannot know when it will actually finish
            else:
                need_zapping = False

    test.wait(5)
    elements = test.milestones.getElements()
    horizontalAssetsScroller = test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_LINEAR", "==")], elements)
    channel_id = horizontalAssetsScroller["channel_id"]
    event_id = horizontalAssetsScroller["event_id"]

    screen = test.milestones.get_current_screen()
    test.log_assert(screen == "timeline" ,"Current screen should be timeline but is "+str(screen))
    logging.info("Exit application ")
    test.appium.send_app_to_background()
    test.wait(300)
    logging.info("Go back in application/timeline ")
    test.appium.send_app_to_foreground()
    test.wait(5)
    screen = test.milestones.get_current_screen()
    test.log_assert(screen == "timeline" ,"Current screen should be timeline but is "+str(screen))
    elements = test.milestones.getElements()
    horizontalAssetsScroller = test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_LINEAR", "==")], elements)
    channel_id_foreground = horizontalAssetsScroller["channel_id"]
    event_id_foreground = horizontalAssetsScroller["event_id"]
    logging.info("channel_id_foreground "+str(channel_id_foreground))
    logging.info("event_id_foreground "+str(event_id_foreground))
    test.log_assert(channel_id == channel_id_foreground ,"Channel Id should not have changed, was "+str(channel_id)+ ", is "+str(channel_id_foreground))
    test.log_assert(event_id != event_id_foreground ,"event_id should have changed, was "+str(event_id)+ ", is "+str(event_id_foreground))

    test.end()


@pytest.mark.MF2059_Behavior_after_app_background
@pytest.mark.regression
@pytest.mark.FS_Standby
@pytest.mark.level2
def test_background_timeline_long():
    '''test_background_timeline_long'''
    # Test with a long (11 min) background time
    # Check that foreground is hub
    test = VeTestApi("test_background_timeline_long")
    test.begin(screen=test.screens.fullscreen)

    # Now go to timeline
    timeline = test.screens.timeline
    timeline.navigate()

    screen = test.milestones.get_current_screen()
    test.log_assert(screen == "timeline" ,"Current screen should be timeline but is "+str(screen))
    logging.info("Exit application ")
    test.appium.send_app_to_background()
    test.wait(660)
    logging.info("Go back in application ")
    test.appium.send_app_to_foreground()
    test.wait(5)
    #Check that the screen is main_hub (not timeline)
    screen = test.milestones.get_current_screen()
    test.log_assert(screen == "main_hub" ,"Current screen should be hub but is "+str(screen))


    test.end()