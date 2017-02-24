from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
import logging



@pytest.mark.MF2629_menu_config_change
@pytest.mark.non_regression
@pytest.mark.FS_HUB
def test_menu_config_change():
    '''test_menu_config_change'''
    # Test that check that added menu options are displayed
    test = VeTestApi("test_menu_config_change")
    test.begin(screen=None)

    # Check that the item has been added in the filterMenuItems (vertical menu)
    # Get the x position of the vertical menu
    elements = test.milestones.getElements()
    on_air_title = test.milestones.get_dic_value_by_key("DIC_FILTER_TV_ON_AIR").upper()
    on_air_option = test.milestones.getElement([("title_text", on_air_title, "==")], elements)
    test.log_assert(on_air_option is not None, "Option ON AIR should exist ")
    filter_menu_x_pos = on_air_option["x_pos"]

    # Check that a menu option that has been added (NICKELODEON) is displayed at the correct position
    added_filter_option = test.milestones.getElement([("title_text", "NICKELODEON", "=="), ("x_pos", filter_menu_x_pos, "==")], elements)
    test.log_assert(added_filter_option is not None, "Option NICKELODEON should exist in vertical filter hub ")

    # Check that the item has been added in the hubTopItems (horizontal menu)
    # Get the y position of the horizontal menu
    elements = test.milestones.getElements()
    television_option = test.milestones.getElement([("title_text", "TELEVISION", "==")], elements)
    test.log_assert(television_option is not None, "Option TELEVISION should exist ")
    hub_menu_y_pos = television_option["y_pos"]

    # Check that a menu option that has been added is displayed at the correct position
    added_hub_option = test.milestones.getElement([("title_text", "GENRES", "=="), ("y_pos", hub_menu_y_pos, "==")], elements)
    test.log_assert(added_hub_option is not None, "Option GENRES should exist in horizontal hub ")

    # tap the added option and check that it is not empty (check that ACTION genre folder exists)
    test.appium.tap_element(added_hub_option)
    test.wait(5)
    elements = test.milestones.getElements()
    action_option = test.milestones.getElement([("title_text", "ACTION", "==")], elements)
    test.log_assert(action_option is not None, "Option ACTION should exist ")
    test.end()