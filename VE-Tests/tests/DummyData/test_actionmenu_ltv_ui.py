__author__ = 'isinitsi'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

@pytest.mark.ui_regression
@pytest.mark.MF953_linear_action_menu
def test_actionmenu_ui():
    ve_test = VeTestApi("test_actionmenu_ui")
    ve_test.begin(login=ve_test.login_types.none)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)
    ve_test.screens.linear_action_menu.navigate()

    ve_test.android_mock_server.compare_milestones_to_reference("actionmenu_ltv")

    ve_test.end()
