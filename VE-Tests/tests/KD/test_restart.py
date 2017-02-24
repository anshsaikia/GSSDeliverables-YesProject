from vgw_test_utils.IHmarks import IHmark
from tests_framework.ve_tests.ve_test import VeTestApi

# @IHmark.LV_L2
@IHmark.MF2236
def test_restart_basic_flow():
    test = VeTestApi("test_restart_basic_flow")
    test.begin(autoPin=True)

    #: :type: tests_framework.ui_building_blocks.KD.action_menu.LinearActionMenu
    actionmenu = test.screens.linear_action_menu
    #: :type: tests_framework.ui_building_blocks.KD.action_menu.VodActionMenu
    restart_actionmenu = test.screens.vod_action_menu
    #: :type: tests_framework.ui_building_blocks.KD.action_menu.FullScreen
    fullscreen = test.screens.fullscreen

    channel_id, channel_prop = test.he_utils.getLinearContentABR('restart')
    test.screens.zaplist.tune_to_channel_by_sek(channel_id, verify_streaming_started=True)

    # open action menu
    actionmenu.navigate()
    # wait for first minute of the event before trying restart
    if not actionmenu.wait_for_seconds_from_event_start(seconds=90):
        actionmenu.dismiss()
        actionmenu.navigate()

    actionmenu.verify_and_press_button(actionmenu.button_type.LIVE_RESTART)
    fullscreen.verify_active()

    test.wait(5)

    # check position
    actionmenu.navigate()
    curr_position = restart_actionmenu.get_current_seek_bar_position()
    test.log_assert(curr_position < 120, "curr_position should be {0} < 120".format(curr_position))

    restart_actionmenu.navigate()
    x_pos, y_pos = restart_actionmenu.get_seek_bar_pos()
    restart_actionmenu.seek_on_tap(x_pos, y_pos, 50, verify=False)

    test.wait(5)

    if test.project_type == "KD":
        restart_actionmenu.press_restart()

        test.wait(5)
        # check position again
        actionmenu.navigate()
        curr_position = restart_actionmenu.get_current_seek_bar_position()
        test.log_assert(curr_position < 120, "curr_position should be {0} < 120".format(curr_position))

        test.wait(5)

    if test.project_type == "KD":
        restart_actionmenu.press_stop()

    elif test.project_type == "K":
        test.screens.playback.stop_playback()

    fullscreen.verify_active()
    test.end()
