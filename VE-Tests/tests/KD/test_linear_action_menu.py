import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
import logging
from vgw_test_utils.IHmarks import IHmark

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF954
@pytest.mark.MF954_linear_action_menu
def test_action_menu_related_scroller():
    my_test = VeTestApi("linear_action_menu:related_scrolles")
    my_test.begin(my_test.login_types.login)
    linear_action_menu = my_test.screens.linear_action_menu
    linear_action_menu.navigate()
    linear_action_menu.reveal_full_action_menu()
    my_test.wait(1.5)
    linear_action_menu.scroll_related_section()
    my_test.end()

@IHmark.MF604
@IHmark.O_Three_Rivers
@IHmark.FS_Recommendations
@IHmark.F_Related_Recommendations
def test_action_menu_tap_related():
    my_test = VeTestApi("linear_action_menu:test_action_menu_tap_related")
    my_test.begin(my_test.login_types.login)

    related_channel = '56'
    zap_list = my_test.screens.zaplist
    zap_list.tune_to_channel_by_sek(related_channel)

    linear_action_menu = my_test.screens.linear_action_menu
    linear_action_menu.navigate()
    linear_action_menu.reveal_full_action_menu()
    linear_action_menu.scroll_related_section()
    linear_action_menu.tap_related_content()
    my_test.end()

#AM Pane UP/Down (all over the screen)
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF954
@pytest.mark.MF954_linear_action_menu
def test_action_menu_scrolling_functionality():
    my_test = VeTestApi("test_action_menu_scrolling_functionality")
    my_test.begin(my_test.login_types.login)

    linear_action_menu = my_test.screens.linear_action_menu
    fullscreen = my_test.screens.fullscreen
    fullscreen.navigate()
    linear_action_menu.navigate()
    linear_action_menu.scroll_draggable_section()
    my_test.end()

# Verify action menu data == server data
@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF954
@IHmark.MF953
@pytest.mark.MF954_linear_action_menu
@pytest.mark.MF953_linear_action_menu
@pytest.mark.level2
def test_action_menu_data():
    my_test = VeTestApi("test_action_menu_data")

    my_test.begin(my_test.login_types.login)
    linear_action_menu = my_test.screens.linear_action_menu
    my_test.wait(3)
    linear_action_menu.navigate()
    my_test.wait(2)
    linear_action_menu.verify_data()
    my_test.end()

#regression test
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF954
@IHmark.MF953
@pytest.mark.MF954_linear_action_menu
@pytest.mark.MF953_linear_action_menu
def no_test_action_menu_regression():
    my_test = VeTestApi("no_test_action_menu_regression")
    my_test.begin()
    my_test.screens.linear_action_menu.navigate()
    my_test.android_mock_server.compare_milestones_to_reference("action_menu", needToSave=False)
    my_test.end()

#injest data to test missing data
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF954
@IHmark.MF953
@pytest.mark.MF954_linear_action_menu
@pytest.mark.MF953_linear_action_menu
def no_test_action_menu_missing_data():
    my_test = VeTestApi("no_test_action_menu_missing_data")
    my_test.begin()
    linear_action_menu = my_test.screens.linear_action_menu
    linear_action_menu.startServer()
    linear_action_menu.navigate()
    my_test.end()

#Stress - do all navigations * 100
@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.stability
@pytest.mark.action_menu_stability
def test_stress_action_menu():
    my_test = VeTestApi("test_stress_action_menu")

    my_test.begin(my_test.login_types.login)
    linear_action_menu = my_test.screens.linear_action_menu
    fullscreen = my_test.screens.fullscreen
    for i in range(10):
        logging.info("iteration number %d" % i)
        fullscreen.navigate()
        linear_action_menu.navigate()
        linear_action_menu.reveal_full_action_menu()
        my_test.wait(1.5)
        linear_action_menu.scroll_related_section()
        linear_action_menu.scroll_draggable_section()
        linear_action_menu.dismiss()
    my_test.end()



