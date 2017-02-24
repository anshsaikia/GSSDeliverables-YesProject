from tests_framework.ve_tests.ve_test import VeTestApi
import pytest

@pytest.mark.commit
def test_sanity_nav_to_timeline_and_switch():
    '''navigate to timeline and then back to KD Manager and then back to application'''
    test = VeTestApi("test_sanity_navigation")
    test.begin()
    '''navigate to timeline'''
    test.screens.timeline.navigate()
    test.appium.send_app_to_background()
    test.appium.send_app_to_foreground()
    test.screens.linear_action_menu.verify_active()
    test.end()
