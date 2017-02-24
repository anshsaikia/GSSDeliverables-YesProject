__author__ = 'bngo'

import logging
import pytest
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.ve_tests.ve_test import VeTestApi


@pytest.mark.FS_Zaplist
@pytest.mark.LV_L2
def test_zaplist_navigation():
    ve_test = VeTestApi("Tests_ui_zaplist")
    ve_test.begin(screen=ve_test.screens.main_hub)
    status = ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen") # Navigate to fullscreen with timeout

    ve_test.log_assert(status, "Navigation to fullscreen from mainhub by timeout failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.screens.fullscreen.navigate()
    
    status = ve_test.screens.zaplist.navigate("down")
    ve_test.log_assert(status, "to_zaplist_from_fullscreen() failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    ve_test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen") # Navigate to fullscreen with timeout
    ve_test.log_assert(status, "Navigation to fullscreen from zaplist by timeout failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    
    status = ve_test.screens.zaplist.navigate("up")
    ve_test.log_assert(status, "to_zaplist_from_fullscreen() failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.zaplist.to_nextchannel("down")
    ve_test.log_assert(status, "to_nextchannel_in_zaplist() failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "to_fullscreen_from_zaplist() failed")
    
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    ve_test.wait(CONSTANTS.INFOLAYER_TIMEOUT)
    status = ve_test.screens.fullscreen.is_infolayer_shown()
    ve_test.log_assert(not status, "info_layer is not dismissed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)

    for i in range(1,5):
        status = ve_test.screens.zaplist.navigate("down")
        ve_test.log_assert(status, "to_zaplist_from_fullscreen() failed")
        ve_test.wait(CONSTANTS.GENERIC_WAIT)

    status = ve_test.screens.fullscreen.navigate()
    ve_test.log_assert(status, "to_fullscreen_from_zaplist() failed")
    ve_test.wait(CONSTANTS.GENERIC_WAIT)
    
    ve_test.end()
