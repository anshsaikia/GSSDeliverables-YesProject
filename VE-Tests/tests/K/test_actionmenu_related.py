from tests_framework.ve_tests.ve_test import VeTestApi
import pytest


@pytest.mark.MF2045_RelatedContent
@pytest.mark.level2
def test_linear_action_menu_related():
    test = VeTestApi("test_ActionMenu_related_linear")
    test.begin(preload="vod")
    linear_action_menu = test.screens.linear_action_menu
    linear_action_menu.navigate()
    linear_action_menu.examine_related_elements()
    test.end()


@pytest.mark.MF2045_RelatedContent
@pytest.mark.level2
def test_vod_action_menu_related():
    test = VeTestApi("test_ActionMenu_related_vod")
    test.begin(preload="vod")
    vod_action_menu = test.screens.vod_action_menu
    vod_action_menu.navigate_from_vod()
    vod_action_menu.examine_related_elements()
    test.end()

# No test for navigating from timeline,
# because the original action menu timeline test is not ready.

