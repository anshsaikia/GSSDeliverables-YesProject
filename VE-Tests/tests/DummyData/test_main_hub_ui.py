__author__ = 'isinitsi'


import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import Showcases
from lib import set_mock_data_multiple_and_begin_test


@pytest.mark.ui
@pytest.mark.ui_regression
def test_main_hub_ui():
    ve_test = VeTestApi("test_main_hub_ui")
    ve_test.begin(login=ve_test.login_types.none)

    index = 0
    for showcase in [Showcases.TV, Showcases.LIBRARY, Showcases.STORE]:
        ve_test.screens.main_hub.focus_showcase(showcase)
        for layer in range(3):
            ve_test.android_mock_server.compare_milestones_to_reference("mainhub_" + str(index))
            ve_test.screens.main_hub.zoom()
            index += 1

    ve_test.end()

@pytest.mark.ui
@pytest.mark.ui_regression
def test_main_hub_ui_partial_content():
    ve_test = VeTestApi("test_main_hub_ui_partial_content")

    data_table = {"agg_grid_current_events": ve_test.android_mock_server.get_mock_address_data("bundle_agg_grid_current_events_MH_missing.json"),
                  "agg_content_classification_2000": ve_test.android_mock_server.get_mock_address_data("bundle_agg_content_classification_2000_MH_missing.json")}
    set_mock_data_multiple_and_begin_test(ve_test, data_table)

    index = 0
    for showcase in [Showcases.TV, Showcases.LIBRARY, Showcases.STORE]:
        ve_test.screens.main_hub.focus_showcase(showcase)
        for layer in range(3):
            ve_test.android_mock_server.compare_milestones_to_reference("mainhub_partial_content_" + str(index))
            ve_test.screens.main_hub.zoom()
            index += 1

    ve_test.end()
