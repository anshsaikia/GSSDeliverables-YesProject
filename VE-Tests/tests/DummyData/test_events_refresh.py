__author__ = 'bwarshaw'

import pytest
from lib import set_mock_data_and_begin_test
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.ve_test import VeTestApi

''' Globals '''
EVENT_UPDATE_TIMEOUT = 120

def filterViewsResult(views):
    filterResult = list()
    for view in views:
         if view['title_text'] != None and "event_id" in view:
            filterResult.append(view)
    return filterResult


@pytest.mark.events_update
def test_main_hub_event_refresh():
    ve_test = VeTestApi("test_main_hub_event_refresh")

    # The following dummy events contains 9 channels when 9 events each, every event has duration of 120 secnods.
    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    first_event_view = ve_test.milestones.getElement([("event_id", "programid://503808505~programid://125747479", "=="), ("title_text", "FIRST_EVENT", "==")])
    ve_test.log_assert(first_event_view, "Expected first event not found on main hub")

    ve_test.appium.take_screenshot("before_2_min_sleep")

    # Wait 120 (just in case more 20 seconds) until the event will get refreshed.
    ve_test.wait(EVENT_UPDATE_TIMEOUT+20)

    ve_test.appium.take_screenshot("after_2_min_sleep")

    next_event_view = ve_test.milestones.getElement([("event_id", "programid://503808503~programid://125747483", "=="), ("title_text", "SECOND_EVENT", "==")])
    ve_test.log_assert(next_event_view, "Expected second event not found on main hub")

    ve_test.end()

@pytest.mark.events_update
def test_main_hub_event_refresh_after_dismiss():
    ve_test = VeTestApi("test_main_hub_event_refresh_after_dismiss")

    # The following dummy events contains 9 channels when 9 events each, every event has duration of 120 secnods.
    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    first_event_view = ve_test.milestones.getElement([("event_id", "programid://503808505~programid://125747479", "=="), ("title_text", "FIRST_EVENT", "==")])
    ve_test.log_assert(first_event_view, "Expected first event not found on main hub")

    ve_test.appium.take_screenshot("before_2_min_sleep")
    ve_test.screens.fullscreen.navigate()

    # Wait 120 (just in case more 20 seconds) until the event will get refreshed.
    ve_test.wait(EVENT_UPDATE_TIMEOUT+20)

    ve_test.screens.main_hub.navigate()
    ve_test.appium.take_screenshot("after_2_min_sleep")

    next_event_view = ve_test.milestones.getElement([("event_id", "programid://503808503~programid://125747483", "=="), ("title_text", "SECOND_EVENT", "==")])
    ve_test.log_assert(next_event_view, "Expected second event not found on main hub")

    ve_test.end()

@pytest.mark.events_update
@pytest.mark.xfail
def test_main_hub_not_focused_event_refresh():
    ve_test = VeTestApi("test_main_hub_not_focused_event_refresh")

    # The following dummy events contains 9 channels when 9 events each, every event has duration of 120 secnods.
    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)


    first_event_view = ve_test.milestones.getElement([("event_id", "programid://503808505~programid://125747479", "=="), ("title_text", "FIRST_EVENT", "==")])
    ve_test.log_assert(first_event_view, "Expected first event not found on main hub")

    ve_test.appium.take_screenshot("before_2_min_sleep")
    ve_test.screens.main_hub.zoom()

    # Wait 120 (just in case more 20 seconds) until the event will get refreshed.
    ve_test.wait(EVENT_UPDATE_TIMEOUT+20)

    ve_test.screens.main_hub.pinch()
    ve_test.appium.take_screenshot("after_2_min_sleep")

    next_event_view = ve_test.milestones.getElement([("event_id", "programid://503808503~programid://125747483", "=="), ("title_text", "SECOND_EVENT", "==")])
    ve_test.log_assert(next_event_view, "Expected second event not found on main hub")

    ve_test.end()

def keep_zaplist_on(ve_test, events_scroller):
    direction = ScreenActions.DOWN
    time_spent = 0
    for i in range(12):
        if(direction == ScreenActions.UP):
                direction = ScreenActions.DOWN
        else:
                direction = ScreenActions.UP
        ve_test.appium.swipe_element(events_scroller, 50, direction, 200)
        ve_test.wait(10)
        time_spent += 10
        print("keep_zaplist_on()-> time spent {0} sec".format(time_spent))

@pytest.mark.events_update
def test_zap_list_event_refresh():
    ve_test = VeTestApi("test_zap_list_event_refresh")

    # The following dummy events contains 9 channels when 9 events each, every event has duration of 120 secnods.
    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    ve_test.screens.zaplist.navigate()
    first_event_view = ve_test.milestones.getElement([("event_id", "programid://503808505~programid://125747479", "=="), ("title_text", "FIRST_EVENT", "==")])
    ve_test.log_assert(first_event_view, "Expected first event not found on zap list")

    ve_test.appium.take_screenshot("before_2_min_sleep")

    events_scroller = ve_test.milestones.getElement([("name", "events_scroller", "==")])

    keep_zaplist_on(ve_test, events_scroller)

    ve_test.appium.take_screenshot("after_2_min_sleep")

    next_event_view = ve_test.milestones.getElement([("event_id", "programid://503808503~programid://125747483", "=="), ("title_text", "SECOND_EVENT", "==")])
    ve_test.log_assert(next_event_view, "Expected second event not found on zap list")

    ve_test.end()

@pytest.mark.events_update
def test_zap_list_event_refresh_after_dismiss():
    ve_test = VeTestApi("test_zap_list_event_refresh_after_dismiss")

    # The following dummy events contains 9 channels when 9 events each, every event has duration of 120 secnods.
    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    ve_test.screens.zaplist.navigate()

    first_event_view = ve_test.milestones.getElement([("event_id", "programid://503808505~programid://125747479", "=="), ("title_text", "FIRST_EVENT", "==")])
    ve_test.log_assert(first_event_view, "Expected first event not found on zap list")

    ve_test.appium.take_screenshot("before_2_min_sleep")
    ve_test.screens.fullscreen.navigate()

    # Wait 120 (just in case more 10 seconds) until the event will get refreshed.
    ve_test.wait(EVENT_UPDATE_TIMEOUT+10)

    ve_test.screens.zaplist.navigate()
    ve_test.appium.take_screenshot("after_2_min_sleep")

    next_event_view = ve_test.milestones.getElement([("event_id", "programid://503808503~programid://125747483", "=="), ("title_text", "SECOND_EVENT", "==")])
    ve_test.log_assert(next_event_view, "Expected second event not found on zap list")

    ve_test.end()

@pytest.mark.events_update
def test_zap_list_not_focused_event_refresh():
    ve_test = VeTestApi("test_zap_list_not_focused_event_refresh")

    # The following dummy events contains 9 channels when 9 events each, every event has duration of 120 secnods.
    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    first_event_view = ve_test.milestones.getElement([("event_id", "programid://503808505~programid://125747479", "=="), ("title_text", "FIRST_EVENT", "==")])
    ve_test.log_assert(first_event_view, "Expected first event not found on zap list")

    ve_test.appium.take_screenshot("before_2_min_sleep")
    ve_test.screens.zaplist.scroll_to_channel_by_sek(105)

    events_scroller = ve_test.milestones.getElement([("name", "events_scroller", "==")])
    keep_zaplist_on(ve_test, events_scroller)

    ve_test.screens.zaplist.scroll_to_channel_by_sek(101)
    ve_test.appium.take_screenshot("after_2_min_sleep")

    next_event_view = ve_test.milestones.getElement([("event_id", "programid://503808503~programid://125747483", "=="), ("title_text", "SECOND_EVENT", "==")])
    ve_test.log_assert(next_event_view, "Expected second event not found on zap list")

    ve_test.end()

@pytest.mark.events_update
def keep_timeline_on(ve_test, horizontalAssetsScroller):
    time_spent = 0
    for iteration in range(12):
            ve_test.wait(10)
            ve_test.appium.swipe_element(horizontalAssetsScroller, 200, ScreenActions.RIGHT)
            time_spent += 10
            print("keep_timeline_on()-> time spent {0} sec".format(time_spent))

@pytest.mark.events_update
def test_timeline_event_update_current():
    ve_test = VeTestApi("test_timeline_evennt_update_dismiss")

    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    ve_test.screens.timeline.navigate()
    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    horizontalChannelItems = filterViewsResult(horizontalChannelItems)

    ve_test.log_assert(len(horizontalChannelItems) > 0,"No vies found in horizontal scroller")
    current_event = horizontalChannelItems[ 0 ]

    keep_timeline_on(ve_test, horizontalAssetsScroller)

    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    horizontalChannelItems = filterViewsResult(horizontalChannelItems)

    ve_test.log_assert(current_event['event_id'] != horizontalChannelItems[ 0 ]['event_id'], "Event has not been updated. Ids: {0} - {1}".format(current_event['event_id'], horizontalChannelItems[ 0 ]['event_id']))
    ve_test.end()

@pytest.mark.events_update
def test_timeline_event_update_not_current():
    ve_test = VeTestApi("test_timeline_evennt_update_dismiss")

    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    ve_test.screens.timeline.navigate()

    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    horizontalChannelItems = filterViewsResult(horizontalChannelItems)

    ve_test.log_assert(len(horizontalChannelItems) > 0,"No views found in horizontal scroller")
    current_event = horizontalChannelItems[ 0 ]

    "Swipe down on clean area changes to previous channel"
    #Swipe down
    window_width, window_height = ve_test.milestones.getWindowSize()
    ve_test.mirror.swipe_area(window_width / 2, window_height / 10 * 8, window_width / 2, window_height / 10 , 0)

    keep_timeline_on(ve_test, horizontalAssetsScroller)

    "Swipe up on clean area changes to next channel"
    #Swipe up
    ve_test.mirror.swipe_area(window_width / 2, window_height / 4, window_width / 2, window_height / 4 * 3, 0)
    ve_test.wait(1.5)

    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    horizontalChannelItems = filterViewsResult(horizontalChannelItems)

    ve_test.log_assert(current_event['event_id'] != horizontalChannelItems[ 0 ]['event_id'], "Event has not been updated. Ids: {0} - {1}".format(current_event['event_id'], horizontalChannelItems[ 0 ]['event_id']))
    ve_test.end()

@pytest.mark.events_update
def test_timeline_event_update_dismiss():
    ve_test = VeTestApi("test_timeline_evennt_update_dismiss")

    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    ve_test.screens.timeline.navigate()
    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    horizontalChannelItems = filterViewsResult(horizontalChannelItems)

    ve_test.log_assert(len(horizontalChannelItems) > 0,"No views found in horizontal scroller")
    current_event = horizontalChannelItems[ 0 ]

    ve_test.screens.timeline.go_to_previous_screen()
    ve_test.wait(EVENT_UPDATE_TIMEOUT)

    ve_test.screens.timeline.navigate()
    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    horizontalChannelItems = filterViewsResult(horizontalChannelItems)

    ve_test.log_assert(current_event['event_id'] != horizontalChannelItems[ 0 ]['event_id'], "Event has not been updated. Ids: {0} - {1}".format(current_event['event_id'], horizontalChannelItems[ 0 ]['event_id']))

    ve_test.end()

@pytest.mark.events_update
def test_infolayer_event_update():
    ve_test = VeTestApi("test_infolayer_event_update")

    # The following dummy events contains 9 channels when 9 events each, every event has duration of 120 secnods.
    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_short_events_9_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event, verify_streaming=False)
    first_event_view = ve_test.milestones.getElement([("title_text", "FIRST_EVENT", "==")])
    ve_test.appium.take_screenshot("before_2_min_sleep")
    ve_test.log_assert(first_event_view, "Expected first event not found on infolayer")

    # Wait 120 (just in case more 10 seconds) until the event will get refreshed.
    ve_test.wait(EVENT_UPDATE_TIMEOUT+10)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event, verify_streaming=False)
    next_event_view = ve_test.milestones.getElement([("title_text", "SECOND_EVENT", "==")])
    ve_test.appium.take_screenshot("after_2_min_sleep")
    ve_test.log_assert(next_event_view, "Expected second event not found on infolayer")

    ve_test.end()
