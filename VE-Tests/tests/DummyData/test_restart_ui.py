
import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ui_building_blocks.screen import ScreenDismiss

@pytest.mark.ui_sanity
def test_sanity_restart_ui():
    ve_test = VeTestApi("test_sanity_restart_ui_KD")
    ve_test.begin(login=ve_test.login_types.none)

    main_hub = ve_test.screens.main_hub
    #: :type: tests_framework.ui_building_blocks.KD.action_menu.LinearActionMenu
    actionmenu = ve_test.screens.linear_action_menu
    #: :type: tests_framework.ui_building_blocks.KD.action_menu.VodActionMenu
    restart_actionmenu = ve_test.screens.vod_action_menu
    #: :type: tests_framework.ui_building_blocks.KD.action_menu.FullScreen
    fullscreen = ve_test.screens.fullscreen

    # Tuning from main hub
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event, verify_streaming=False)

    # open action menu
    actionmenu.navigate()
    actionmenu.verify_and_press_button(actionmenu.button_type.LIVE_RESTART)
    fullscreen.verify_active()

    # check position
    actionmenu.navigate()
    ve_test.wait(5)
    curr_position = restart_actionmenu.get_current_seek_bar_position()
    ve_test.log_assert(curr_position < 5, "curr_position should be {0} < 5".format(curr_position))

    restart_actionmenu.seek(True, 50)
    ve_test.wait(5)
    restart_actionmenu.press_stop()

    fullscreen.verify_active()
    ve_test.end()


@pytest.mark.ui_sanity
def test_sanity_restart_ui_k():

    ve_test = VeTestApi("test_sanity_restart_ui_K")
    ve_test.begin(login=ve_test.login_types.none)

    #: :type: tests_framework.ui_building_blocks.KD.action_menu.LinearActionMenu
    actionmenu = ve_test.screens.linear_action_menu
    #: :type: tests_framework.ui_building_blocks.KD.action_menu.VodActionMenu
    restart_actionmenu = ve_test.screens.vod_action_menu
    #: :type: tests_framework.ui_building_blocks.KD.action_menu.FullScreen
    fullscreen = ve_test.screens.fullscreen
    #: :type: tests_framework.ui_building_blocks.K.trick_bar.TrickBar
    trick_bar = ve_test.screens.trick_bar
    #: :type: tests_framework.ui_building_blocks.KD.infolayer.InfoLayer

    infolayer = ve_test.screens.infolayer
    fullscreen.navigate()

    # open action menu
    actionmenu.navigate()
    actionmenu.verify_and_press_button(actionmenu.button_type.LIVE_RESTART)
    fullscreen.verify_active()

    # check position
    ve_test.wait(5)
    curr_position = trick_bar.get_current_seek_bar_position()
    ve_test.log_assert(curr_position < 5, "curr_position should be {0} < 5".format(curr_position))

    trick_bar.seek(True, 50)
    ve_test.wait(5)
    trick_bar.dismiss(action=ScreenDismiss.CLOSE_BUTTON)

    infolayer.verify_active()
    infolayer.dismiss(action=ScreenDismiss.TAP)

    fullscreen.verify_active()

    ve_test.end()
