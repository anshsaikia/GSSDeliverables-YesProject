__author__ = 'gmaman'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition


@pytest.mark.ui_sanity
def test_sanity_navigation_ui():
    ve_test = VeTestApi("test_sanity_navigation_ui")
    ve_test.begin(login=ve_test.login_types.none)

    zaplist = ve_test.screens.zaplist
    infolayer = ve_test.screens.infolayer
    fullscreen = ve_test.screens.fullscreen
    main_hub = ve_test.screens.main_hub
    timeline = ve_test.screens.timeline
    guide = ve_test.screens.guide
    actionmenu = ve_test.screens.linear_action_menu

    "channel change from full screen"
    fullscreen.channel_change()
    ve_test.wait(10)

    "Tuning from main hub"
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event, verify_streaming=False)

    "verify info layer display"
    infolayer.verify_active()
    infolayer.dismiss()
    ve_test.wait(10)

    "open action menu"
    actionmenu.navigate()
    ve_test.wait(10)

    "open timeline"
    timeline.navigate()
    ve_test.wait(20)

    "scroll zaplist"
    zaplist.navigate()
    zaplist.scroll_channels(-1)
    ve_test.wait(10)

    "open guide"
    guide.navigate()
    ve_test.wait(5)

    ve_test.end()
