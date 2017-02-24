__author__ = 'bwarshaw'


import calendar
from dateutil.parser import parse as date_parser
from time import time
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition


def measure_time_left_for_event_in_seconds(start_time, duration):
    start_time = date_parser(start_time)
    start_time_in_seconds = calendar.timegm(start_time.utctimetuple())
    duration = int(round(duration/1000))
    current_time = int(round(time()))
    return start_time_in_seconds + duration - current_time


def test_action_menu_event_update():
    ve_test = VeTestApi("test_action_menu_event_update")

    ve_test.begin()
    server_data = ve_test.ctap_data_provider.send_request('GRID', payload={'duration':'50000'})

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event)
    first_event_data = server_data["channels"][0]["schedule"][0]
    next_event_data = server_data["channels"][0]["schedule"][1]

    ve_test.screens.linear_action_menu.navigate()
    first_event_view = ve_test.milestones.getElement([("event_id", first_event_data["id"], "==")])
    ve_test.appium.take_screenshot("before_2_min_sleep")
    ve_test.log_assert(first_event_view, "Expected first event not found on action menu")

    timeout = measure_time_left_for_event_in_seconds(first_event_data["startTime"], first_event_data["duration"])

    # Wait 120 (just in case more 10 seconds) until the event will get refreshed.
    ve_test.wait(timeout+10)

    ve_test.screens.linear_action_menu.dismiss()
    ve_test.screens.linear_action_menu.navigate()
    next_event_view = ve_test.milestones.getElement([("event_id", next_event_data["id"], "==")])
    ve_test.appium.take_screenshot("after_2_min_sleep")
    ve_test.log_assert(next_event_view, "Expected second event not found on action menu")

    ve_test.end()
