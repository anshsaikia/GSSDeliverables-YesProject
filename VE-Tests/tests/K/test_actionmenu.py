from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
from tests_framework.ui_building_blocks.screen import Screen
from vgw_test_utils.IHmarks import IHmark

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2057
@pytest.mark.MF2057_ActionMenu
@pytest.mark.level2
def test_linear_action_menu_data():
    test = VeTestApi("test_linear_action_menu_data")
    test.begin()
    linear_action_menu = test.screens.linear_action_menu
    linear_action_menu.navigate()
    linear_action_menu.verify_data()
    test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2057
@pytest.mark.MF2057_ActionMenu
@pytest.mark.level2
def test_vod_action_menu_data():
    test = VeTestApi("test_vod_action_menu_data")
    test.begin()
    vod_action_menu = test.screens.vod_action_menu
    vod_action_menu.navigate_from_vod()
    vod_action_menu.verify_data()
    test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2057
@pytest.mark.MF2057_ActionMenu
def test_linear_action_from_timeline():
    test = VeTestApi("test_ActionMenu_fromTimeline")
    test.begin()
    linear_action_menu = test.screens.linear_action_menu
    linear_action_menu.navigate_from_timeline()
    test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2057
@pytest.mark.MF2057_ActionMenu
@pytest.mark.stability
def test_linear_action_sterss():
    test = VeTestApi("test_ActionMenu_stress")
    test.begin()
    for x in range(0, 10):
        linear_action_menu = test.screens.linear_action_menu
        print "x is" + str(x)
        linear_action_menu.navigate()
        tv_filter = test.screens.tv_filter
        tv_filter.navigate()
    test.end()