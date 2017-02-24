from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
from tests_framework.ui_building_blocks.screen import ScreenDismiss
from vgw_test_utils.IHmarks import IHmark
from tests_framework.ui_building_blocks.screen import ScreenActions


CHANNEL_WITH_CATCHUP = 1;
CHANNEL_WITHOUT_CATCHUP = 2;


@IHmark.LV_L2
@IHmark.O_Valhalla
@IHmark.MF1310
@pytest.mark.MF1310_timeline_catchup
@pytest.mark.level2
def test_close_catchup():

    test = VeTestApi("test_close_catchup")
    test.begin()

    catchup = test.screens.timeline_catchup
    catchup_dismiss = [ScreenDismiss.TAP, ScreenDismiss.CLOSE_BUTTON, ScreenDismiss.TAP_ON_EVENT]
    for item in catchup_dismiss:
        catchup.navigate()
        catchup.dismiss(item)
    test.end()


@IHmark.LV_L2
@IHmark.O_Valhalla
@IHmark.MF1310
@pytest.mark.MF1310_timeline_catchup
@pytest.mark.level2
def test_verify_timeline_catchup_data():

    test = VeTestApi("test_verify_timeline_catchup_data")
    test.begin()

    catchup = test.screens.timeline_catchup
    catchup.navigate()

    '''get milestones elements and server data'''
    elements = test.milestones.getElements()
    server_data = test.ctap_data_provider.send_request('GRID', payload={'eventsLimit':'0','pastEventsLimit':'10'})
    current_channel_id = test.milestones.getElement([("screen", "timeline_catchup", "==")], elements)["channel_id"]

    '''go to a channel with catchup'''
    down_arrow = test.milestones.getElement([("id", "downImageViewCatchup", "==")], elements)
    for i in range(0,CHANNEL_WITH_CATCHUP):
        '''tap on down arrow'''
        current_channel_id = catchup.find_next_channel_id(current_channel_id, server_data)
        test.appium.tap_element(down_arrow)
        test.wait(3)

    elements = test.milestones.getElements()

    '''compare events metadata'''
    catchup.compare_events_metadata(server_data, elements, current_channel_id, False)

    '''compare logos of channels in channels panel'''
    catchup.compare_channels_logos(server_data, elements, current_channel_id)

    '''no catchup message should no be present'''
    test.log_assert(not test.ui.localized_label_exists("DIC_TIMELINE_CATCHUP_NO_INFORMATION", elements=elements), "the no catchup message should no be present in this screen")

    test.end()


@IHmark.LV_L2
@IHmark.O_Valhalla
@IHmark.MF1310
@pytest.mark.MF1310_timeline_catchup
@pytest.mark.level2
def test_verify_timeline_no_catchup_data():

    test = VeTestApi("test_verify_timeline_no_catchup_data")
    test.begin()

    catchup = test.screens.timeline_catchup
    catchup.navigate()

    '''get milestones elements and server data'''
    elements = test.milestones.getElements()
    server_data = test.ctap_data_provider.send_request('GRID', payload={'eventsLimit':'0','pastEventsLimit':'10'})
    current_channel_id = test.milestones.getElement([("screen", "timeline_catchup", "==")], elements)["channel_id"]

    '''go to a channel with no catchup'''
    down_arrow = test.milestones.getElement([("id", "downImageViewCatchup", "==")], elements)
    for i in range(0,CHANNEL_WITHOUT_CATCHUP):
        '''tap on down arrow'''
        current_channel_id = catchup.find_next_channel_id(current_channel_id, server_data)
        test.appium.tap_element(down_arrow)
        test.wait(3)

    elements = test.milestones.getElements()

    '''compare events metadata for current channel id'''
    catchup.compare_no_events_catchup(server_data, elements, current_channel_id, True)

    '''compare logos of channels in channels panel'''
    catchup.compare_channels_logos(server_data, elements, current_channel_id)

    '''search for the no catchup message'''
    test.log_assert(test.ui.localized_label_exists("DIC_TIMELINE_CATCHUP_NO_INFORMATION", elements=elements), "cannot find the no catchup message in this screen")

    test.end()


@IHmark.LV_L2
@IHmark.O_Valhalla
@IHmark.MF1310
@pytest.mark.MF1310_timeline_catchup
@pytest.mark.level2
def test_verify_catchup_timeline_navigation():

    test = VeTestApi("test_verify_catchup_timeline_navigation")
    test.begin()

    fullscreen = test.screens.fullscreen
    fullscreen.navigate()

    '''test right swipe to go to timeline catchup from fullscreen'''
    test.ui.one_finger_swipe(ScreenActions.RIGHT)
    test.wait(3)
    test.screens.timeline_catchup.verify_active()

    '''test left swipe to go to infolayer from timeline catchup'''
    test.ui.one_finger_swipe(ScreenActions.LEFT)
    test.wait(3)
    test.screens.infolayer.verify_active()

    '''test right swipe to go to timeline catchup from infolayer'''
    test.ui.one_finger_swipe(ScreenActions.RIGHT)
    test.wait(3)
    test.screens.timeline_catchup.verify_active()

    '''test left swipe to go to infolayer from timeline catchup'''
    test.ui.one_finger_swipe(ScreenActions.LEFT)
    test.wait(3)
    test.screens.infolayer.verify_active()

    '''test tap on arrow button to go to timeline catchup from infolayer'''
    test.ui.tap_center_element("timeline_catchup")
    test.wait(3)
    test.screens.timeline_catchup.verify_active()

    '''test tap on X button to go to infolayer from timeline catchup'''
    elements = test.milestones.getElements()
    exit_icon = test.milestones.getElement([("id", "exit", "==")], elements)
    test.appium.tap_center_element(exit_icon)
    test.wait(3)
    test.screens.infolayer.verify_active()

    test.end()


@IHmark.LV_L2
@IHmark.O_Valhalla
@IHmark.MF1310
@pytest.mark.MF1310_timeline_catchup
@pytest.mark.level2
def test_catchup_action_menu_data():

    test = VeTestApi("test_catchup_action_menu_data")
    test.begin()

    catchup = test.screens.timeline_catchup
    catchup.navigate()

    '''go to a channel with catchup'''
    elements = test.milestones.getElements()
    down_arrow = test.milestones.getElement([("id", "downImageViewCatchup", "==")], elements)
    for i in range(0,CHANNEL_WITH_CATCHUP):
        '''tap on down arrow'''
        test.appium.tap_element(down_arrow)
        test.wait(3)

    '''go to action menu for a catchup event'''
    elements = test.milestones.getElements()
    catchup = test.screens.timeline_catchup
    event = catchup.find_catchup_event(elements)
    test.appium.tap_center_element(event)
    test.wait(3)
    test.screens.action_menu.verify_active()

    vod_action_menu = test.screens.vod_action_menu
    vod_action_menu.verify_data()

    test.end()


@IHmark.LV_L2
@IHmark.O_Valhalla
@IHmark.MF1310
@pytest.mark.MF1310_timeline_catchup
@pytest.mark.level2
def test_verify_catchup_playback_navigation():

    test = VeTestApi("test_verify_catchup_playback_navigation")
    test.begin()

    test.screens.infolayer.show()

    elements = test.milestones.getElements()
    playing_channel_id = test.milestones.getElement([("screen", "infolayer", "==")], elements)["channel_id"]

    test.screens.timeline_catchup.navigate()

    '''go to a channel with catchup'''
    elements = test.milestones.getElements()
    down_arrow = test.milestones.getElement([("id", "downImageViewCatchup", "==")], elements)
    for i in range(0,CHANNEL_WITH_CATCHUP):
        '''tap on down arrow'''
        test.appium.tap_element(down_arrow)
        test.wait(3)

    elements = test.milestones.getElements()
    catchup_channel_id = test.milestones.getElement([("screen", "timeline_catchup", "==")], elements)["channel_id"]

    '''go to action menu for a catchup event'''
    elements = test.milestones.getElements()
    catchup = test.screens.timeline_catchup
    event = catchup.find_catchup_event(elements)
    catchup_id = event["event_id"]
    test.appium.tap_center_element(event)
    test.wait(3)
    test.screens.action_menu.verify_active()

    elements = test.milestones.getElements()
    test.log_assert(test.milestones.getElement([("event_id", catchup_id, "==")], elements), "cannot find the catchup asset in action menu")

    '''play catchup event'''
    play_icon = test.milestones.getElement([("id", "play", "==")], elements)
    test.appium.tap_center_element(play_icon)
    test.wait(5)
    test.screens.fullscreen.verify_active()


    '''go to trick_bar'''
    test.ui.top_tap()
    test.wait(3)
    test.screens.trick_bar.verify_active()


    '''go back to action menu'''
    elements = test.milestones.getElements()
    back_icon = test.milestones.getElement([("id", "back", "==")], elements)
    test.appium.tap_center_element(back_icon)
    test.wait(3)
    test.screens.action_menu.verify_active()

    elements = test.milestones.getElements()
    event_id = test.ctap_data_provider.get_event_id(elements,"catchup")
    test.log_assert(event_id==catchup_id, "action menu asset is not the expected one")
    test.log_assert(test.milestones.getElement([("name", "pip_view", "==")], elements), "can not find the pip")
    #test.log_assert(test.milestones.getElement([("id", "play", "==")], elements)==None, "the play button should not be present")

    '''go back to fullscreen'''
    pip_element = test.milestones.getElement([("name", "pip_view", "==")], elements)
    test.appium.tap_center_element(pip_element)
    test.wait(3)
    test.screens.fullscreen.verify_active()


    '''go to trick_bar'''
    test.ui.top_tap()
    test.wait(3)
    test.screens.trick_bar.verify_active()


    '''go back to timeline'''
    elements = test.milestones.getElements()
    exit_icon = test.milestones.getElement([("id", "exit", "==")], elements)
    test.appium.tap_center_element(exit_icon)
    test.wait(3)
    test.screens.timeline_catchup.verify_active()

    elements = test.milestones.getElements()
    test.log_assert(test.milestones.getElement([("screen", "timeline_catchup", "==")], elements)["channel_id"]==catchup_channel_id, "timeline_catchup is not on the same channel as before")


    '''left swipe to go to infolayer from timeline catchup'''
    test.ui.one_finger_swipe(ScreenActions.LEFT)
    test.wait(3)
    test.screens.infolayer.verify_active()

    elements = test.milestones.getElements()
    test.log_assert(test.milestones.getElement([("screen", "infolayer", "==")], elements)["channel_id"]==playing_channel_id, "infolayer is not on the same channel as before")


    test.end()


@IHmark.LV_L2
@IHmark.O_Valhalla
@IHmark.MF1310
@pytest.mark.MF1310_timeline_catchup
@pytest.mark.level2
def test_verify_catchup_playback_eof():

    test = VeTestApi("test_verify_catchup_playback_eof")
    test.begin()

    test.screens.infolayer.show()

    elements = test.milestones.getElements()
    playing_channel_id = test.milestones.getElement([("screen", "infolayer", "==")], elements)["channel_id"]

    test.screens.timeline_catchup.navigate()

    '''go to a channel with catchup'''
    elements = test.milestones.getElements()
    down_arrow = test.milestones.getElement([("id", "downImageViewCatchup", "==")], elements)
    for i in range(0,CHANNEL_WITH_CATCHUP):
        '''tap on down arrow'''
        test.appium.tap_element(down_arrow)
        test.wait(3)

    elements = test.milestones.getElements()
    catchup_channel_id = test.milestones.getElement([("screen", "timeline_catchup", "==")], elements)["channel_id"]

    '''go to action menu for a catchup event'''
    elements = test.milestones.getElements()
    catchup = test.screens.timeline_catchup
    event = catchup.find_catchup_event(elements)
    catchup_id = event["event_id"]
    test.appium.tap_center_element(event)
    test.wait(3)
    test.screens.action_menu.verify_active()


    '''play catchup event'''
    elements = test.milestones.getElements()
    play_icon = test.milestones.getElement([("id", "play", "==")], elements)
    test.appium.tap_center_element(play_icon)
    test.wait(5)
    test.screens.fullscreen.verify_active()


    '''go to eof'''
    test.ui.top_tap()
    test.wait(10)
    trick_bar = test.screens.trick_bar
    trick_bar.seek(True, 95)

    '''wait until eof'''
    test.wait(120)


    '''we should be on action menu without pip'''
    test.screens.action_menu.verify_active()
    elements = test.milestones.getElements()
    test.log_assert(test.milestones.getElement([("event_id", catchup_id, "==")], elements), "cannot find the catchup asset in action menu")
    test.log_assert(test.milestones.getElement([("name", "pip_view", "==")], elements)==None, "the pip should not be present")
    test.log_assert(test.milestones.getElement([("id", "play", "==")], elements), "the play button should be present")


    '''go back to timeline catchup'''
    exit_button = test.milestones.getElement([("id", "exit", "==")], elements)
    test.appium.tap_center_element(exit_button)
    test.screens.timeline_catchup.verify_active()

    elements = test.milestones.getElements()
    test.log_assert(test.milestones.getElement([("screen", "timeline_catchup", "==")], elements)["channel_id"]==catchup_channel_id, "timeline_catchup is not on the same channel as before")


    '''left swipe to go to infolayer from timeline catchup'''
    test.ui.one_finger_swipe(ScreenActions.LEFT)
    test.wait(3)
    test.screens.infolayer.verify_active()

    elements = test.milestones.getElements()
    test.log_assert(test.milestones.getElement([("screen", "infolayer", "==")], elements)["channel_id"]==playing_channel_id, "infolayer is not on the same channel as before")


    test.end()


@IHmark.LV_L2
@IHmark.O_Valhalla
@IHmark.MF1310
@pytest.mark.MF1310_timeline_catchup
@pytest.mark.level2
def test_verify_catchup_watch_playback_navigation():

    test = VeTestApi("test_verify_catchup_watch_playback_navigation")
    test.begin()

    test.screens.infolayer.show()

    elements = test.milestones.getElements()
    playing_channel_id = test.milestones.getElement([("screen", "infolayer", "==")], elements)["channel_id"]

    test.screens.timeline_catchup.navigate()

    '''go to a channel with catchup'''
    elements = test.milestones.getElements()
    down_arrow = test.milestones.getElement([("id", "downImageViewCatchup", "==")], elements)
    for i in range(0,CHANNEL_WITH_CATCHUP):
        '''tap on down arrow'''
        test.appium.tap_element(down_arrow)
        test.wait(3)

    elements = test.milestones.getElements()
    catchup_channel_id = test.milestones.getElement([("screen", "timeline_catchup", "==")], elements)["channel_id"]

    '''tap on watch button'''
    elements = test.milestones.getElements()
    test.ui.tap_localized_label("DIC_TIMELINE_WATCH", True, elements)
    test.wait(5)
    test.screens.fullscreen.verify_active()


    '''go to trick_bar'''
    test.ui.top_tap()
    test.wait(3)
    test.screens.trick_bar.verify_active()


    '''go back to action menu'''
    elements = test.milestones.getElements()
    back_icon = test.milestones.getElement([("id", "back", "==")], elements)
    test.appium.tap_center_element(back_icon)
    test.wait(3)
    test.screens.action_menu.verify_active()

    elements = test.milestones.getElements()
    event_id = test.ctap_data_provider.get_event_id(elements,"catchup")
    test.log_assert(test.milestones.getElement([("name", "pip_view", "==")], elements), "can not find the pip")
    #test.log_assert(test.milestones.getElement([("id", "play", "==")], elements)==None, "the play button should not be present")

    '''go back to fullscreen'''
    pip_element = test.milestones.getElement([("name", "pip_view", "==")], elements)
    test.appium.tap_center_element(pip_element)
    test.wait(3)
    test.screens.fullscreen.verify_active()


    '''go to trick_bar'''
    test.ui.top_tap()
    test.wait(3)
    test.screens.trick_bar.verify_active()


    '''go back to timeline'''
    elements = test.milestones.getElements()
    exit_icon = test.milestones.getElement([("id", "exit", "==")], elements)
    test.appium.tap_center_element(exit_icon)
    test.wait(3)
    test.screens.timeline_catchup.verify_active()

    elements = test.milestones.getElements()
    test.log_assert(test.milestones.getElement([("screen", "timeline_catchup", "==")], elements)["channel_id"]==catchup_channel_id, "timeline_catchup is not on the same channel as before")


    '''left swipe to go to infolayer from timeline catchup'''
    test.ui.one_finger_swipe(ScreenActions.LEFT)
    test.wait(3)
    test.screens.infolayer.verify_active()

    elements = test.milestones.getElements()
    test.log_assert(test.milestones.getElement([("screen", "infolayer", "==")], elements)["channel_id"]==playing_channel_id, "infolayer is not on the same channel as before")


    test.end()
