__author__ = 'bwarshaw'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ui_building_blocks.screen import ScreenActions
from lib import set_mock_data_and_begin_test

@pytest.mark.ui_regression
@pytest.mark.MF961_infolayer
def test_infolayer_normal_metadata():
    ve_test = VeTestApi("test_infolayer_normal_metadata")
    ve_test.begin(login=ve_test.login_types.none)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.middle_event)
    ve_test.log_assert(ve_test.screens.infolayer.is_active(timeout=10), "Infolayer did not show after tuning")
    elements = ve_test.milestones.getElements()
    ve_test.android_mock_server.compare_milestones_to_reference("fullscreen", elements=elements)
    ve_test.end()

@pytest.mark.ui_regression
@pytest.mark.MF961_infolayer
def test_infolayer_missing_metadata():
    ve_test = VeTestApi("test_infolayer_missing_metadata")#agg_grid_current_events

    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_agg_grid_current_events_missing_data.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event)
    ve_test.android_mock_server.compare_milestones_to_reference("infolayer_very_long_title")

    ve_test.wait(3)
    ve_test.ui.one_finger_swipe(ScreenActions.DOWN)
    ve_test.wait(3)
    ve_test.android_mock_server.compare_milestones_to_reference("infolayer_no_title_available")

    ve_test.end()
