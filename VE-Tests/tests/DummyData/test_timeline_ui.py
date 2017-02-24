__author__ = 'isinitsi'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

@pytest.mark.dummy_MF956_channel_timeline
@pytest.mark.ui_regression
def test_timeline_ui():
    ve_test = VeTestApi("test_timeline_ui")
    ve_test.begin(login=ve_test.login_types.none)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)
    ve_test.screens.timeline.navigate()

    ve_test.android_mock_server.compare_milestones_to_reference("timeline")

    ve_test.end()
