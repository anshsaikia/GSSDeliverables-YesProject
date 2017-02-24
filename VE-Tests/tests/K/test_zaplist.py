import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions
from vgw_test_utils.IHmarks import IHmark
import logging

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF970
@pytest.mark.MF970_zaplist
@pytest.mark.level2
def test_fullscreen_to_zaplist_and_back():
    #Start test
    my_test = VeTestApi("zaplist: fullscreen to zaplist")
    my_test.begin()
    #Store refs to screens
    zaplist = my_test.screens.zaplist
    fullscreen = my_test.screens.fullscreen
    #Go to zaplist via swipe up
    zaplist.navigate(ScreenActions.UP)
    #Go to fullscreen
    fullscreen.navigate()
    #Go to zaplist via swipe down
    zaplist.navigate()
    #Go to fullscreen
    fullscreen.navigate()
    #Stop test
    my_test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF970
@pytest.mark.MF970_zaplist
@pytest.mark.level2
def test_zaplist_various_scrolling():
    #Start test
    my_test = VeTestApi("zaplist:various scrolling")
    my_test.begin(autoPin=True)
    #Store refs to screens
    zaplist = my_test.screens.zaplist
    #navigate zap list
    zaplist.navigate(ScreenActions.UP)
    #Scroll slow upwards
    zaplist.scroll_from_center(2000, ScreenActions.UP)
    #Scroll fast upwards
    zaplist.scroll_from_center(100, ScreenActions.UP)
    #Scroll slow downwards
    zaplist.scroll_from_center(2000, ScreenActions.DOWN)
    #Scroll fast downwards
    zaplist.scroll_from_center(100, ScreenActions.DOWN)
    #Stop test
    my_test.end()

