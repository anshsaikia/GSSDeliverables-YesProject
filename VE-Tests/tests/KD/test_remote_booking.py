__author__ = 'darumugh'
import pytest
import random
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

TIMELINE_RETRIES = 3

@IHmark.LV_L2
@pytest.mark.MF406
@pytest.mark.level2
def test_remote_booking():
    ve_test = VeTestApi("tv:test_remote_booking")
    ve_test.begin()
    verify_record_behaviour(ve_test)
    ve_test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF910
@pytest.mark.MF910_Indicators_in_GRID
@pytest.mark.export_regression_MF910_Indicators_in_GRID
@pytest.mark.level2
def test_booking_indicators_in_grid():
    ve_test = VeTestApi("test_booking_indicators_in_grid")
    ve_test.begin()

    booking_recording = ve_test.screens.booking_recording
    guide = ve_test.screens.guide

    ctap_event = get_future_recordable_content_from_ctap(ve_test)
    payload = {"event_id": ctap_event["id"]}
    content_instances = ve_test.ctap_data_provider.send_request('ACTION_MENU', payload)

    'book future event from guide'
    booking_recording.book_event(ctap_event["id"], content_instances["channel"]["id"], screen=ve_test.screens.guide)
    ve_test.wait(2)

    'press back to return to guide and verify record icon'
    ve_test.screens.linear_action_menu.go_to_previous_screen()
    guide.verify_active()
    event_element = guide.scroll_to_event(ctap_event["id"], content_instances["channel"]["id"])
    booking_recording.verify_record_icon(event_element)

    'exit from guide'
    ve_test.screens.main_hub.navigate()

    'navigate to guide and verify that record icon is displayed'
    guide.navigate()
    event_element = guide.scroll_to_event(ctap_event["id"], content_instances["channel"]["id"])
    booking_recording.verify_record_icon(event_element)

    ve_test.end()

def verify_record_behaviour(ve_test):
    # Verify Record Button's presence

    linear_action_menu = ve_test.screens.linear_action_menu
    booking_recording = ve_test.screens.booking_recording

    selected_event = get_recordable_content(ve_test)
    select_event_by_name(ve_test, selected_event)

    ve_test.log_assert(linear_action_menu.is_active(), "Linear action menu is not active")
    linear_action_menu.verify_and_press_record_button()

    ve_test.wait(2)
    # Verify Cancel Record Button's presence after Record Button getting pressed
    linear_action_menu.verify_cancel_record_button(is_present=True)

# Try to get a recordable content from the current channel
# If we do not get recordable contents, we scroll the timeline and find recordable content
def get_recordable_content(ve_test):
    # ve_test.he_utils.is_ppv_event(event_id)
    timeline = ve_test.screens.timeline
    booking_recording = ve_test.screens.booking_recording
    selected_event = None

    timeline.navigate()
    ve_test.wait(3)

    # We dont need the current event to be recorded,
    # this boolean is to avoid recording current(first) event
    first_attempt = True
    for j in xrange(TIMELINE_RETRIES):
        if first_attempt:
            start = 2
            first_attempt = False
        else:
            start = 0

        current_channel_events = get_current_channel_events(ve_test)
        for i in xrange(start, len(current_channel_events)):
            event = current_channel_events[i]
            event_id = event["event_id"]
            timeline.navigate()
            if booking_recording.is_event_recordable(event_id) and not booking_recording.is_event_booked(event_id):
                selected_event = event
                break

        if selected_event:
            break
        else:
            # Scroll the channel to find more events
            stop_x = current_channel_events[0]['x_pos']
            stop_y = current_channel_events[0]['y_pos']

            start_x = current_channel_events[2]['x_pos']
            start_y = current_channel_events[2]['y_pos']
            ve_test.appium.swipe_area(start_x, start_y, stop_x, stop_y)
            ve_test.wait(2)

    ve_test.log_assert(selected_event, "Unable to get a recordable event")
    return selected_event

def get_current_channel_events(ve_test):

    elements = ve_test.milestones.getElements()
    channel_elements = []
    current_channel = None
    for element in elements:
        if "channel_id" in element and not current_channel:
            current_channel = element["channel_id"]

        if "channel_id" in element and element["channel_id"] == current_channel:
            channel_elements.append(element)

    ve_test.log_assert(len(channel_elements) >= 2,\
            "The current channel should have atleast 3 events, only %d found,\n Response: %s " \
            %(len(channel_elements), channel_elements))

    return channel_elements

# Select's the event from current channel, by scrolling
def select_event_by_name(ve_test, selected_event):
    timeline = ve_test.screens.timeline
    event_name = selected_event["title_text"]
    milestones = ve_test.milestones
    ve_test.screens.fullscreen.navigate()
    ve_test.wait(1)
    timeline.navigate()
    ve_test.wait(3)

    for i in xrange(TIMELINE_RETRIES):
        current_channel_events = milestones.getElements()
        event = milestones.getElementContains(current_channel_events, event_name, key='title_text')
        if event:
            break
        else:
            stop_x = current_channel_events[0]['x_pos']
            stop_y = current_channel_events[0]['y_pos']

            start_x = current_channel_events[2]['x_pos']
            start_y = current_channel_events[2]['y_pos']
            ve_test.appium.swipe_area(start_x, start_y, stop_x, stop_y)
            ve_test.wait(2)

    ve_test.log_assert(event, "Unable to get the event, %s" % str(selected_event))
    timeline.tap_on_element(selected_event)
    ve_test.wait(1)

def get_future_recordable_content_from_ctap(ve_test):
    booking_recording = ve_test.screens.booking_recording
    grid_info = ve_test.ctap_data_provider.send_request('GRID', None)

    recordable_event = None
    for channel in grid_info['channels']:
        channel_events = channel["schedule"]
        for i in range(5, len(channel_events)):
            if booking_recording.is_event_recordable(channel_events[i]['id']):
                recordable_event = channel_events[i]
                return recordable_event

    ve_test.log_assert(recordable_event != None, "No recordable content Found")

