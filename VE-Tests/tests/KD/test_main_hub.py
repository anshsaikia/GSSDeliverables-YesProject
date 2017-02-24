__author__ = 'isinitsi'


import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ui_building_blocks.KD.main_hub import Showcases
from tests_framework.ui_building_blocks.screen import ScreenDismiss
from tests_framework.he_utils.he_utils import VodContentType
from vgw_test_utils.IHmarks import IHmark
import logging

''' Global constants '''
MAIN_HUB_DISMISS_TIMEOUT = 15


@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF974
@pytest.mark.MF974_HUB_television_main_screen
@pytest.mark.level2
def test_main_hub_verify_navigation():
    ve_test = VeTestApi("main_hub:test_verify_navigation")
    ve_test.begin()

    "Navigation"
    ve_test.screens.guide.navigate()
    ve_test.screens.library.navigate()
    ve_test.screens.store.navigate()
    ve_test.screens.settings.navigate()
    ve_test.screens.fullscreen.navigate()

    ve_test.end()


# 1. Verify tuning on first Launch
# 2. Verify second tuning
# 3. Verify tuning of asset in second level (zoom the main hub)
# 4. Verify that tuning is not performed when channel is played in background.
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF974
@pytest.mark.MF974_HUB_television_main_screen
def test_main_hub_verify_tunings():
    ve_test = VeTestApi("main_hub:test_verify_tunings")
    main_hub = ve_test.screens.main_hub
    playback = ve_test.screens.playback
    infolayer = ve_test.screens.infolayer
    notification = ve_test.screens.notification
    fullscreen = ve_test.screens.fullscreen

    ve_test.begin()

    "1. Verify tuning on first Launch"
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event, verify_streaming=False)

    ve_test.wait(2)
    "2. Verify tuning of asset in second level (zoom the main hub)"
    "3. Verify second tuning"
    main_hub.navigate()
    main_hub.zoom(Showcases.GUIDE)
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event, verify_streaming=False)

    "4. Verify that tuning is not performed when channel is played in background"
    if notification.is_active():
        notification.dismiss()

    if infolayer.is_active():
        infolayer.dismiss()

    if fullscreen.is_active():
        before_streaming_session_id = playback.get_streaming_session_id()
        main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event, verify_streaming=False)
        infolayer.dismiss()
        after_streaming_session_id = playback.get_streaming_session_id()
        ve_test.log_assert(before_streaming_session_id == after_streaming_session_id, "Playing current played asset caused to a creation of a new session ")

    ve_test.end()

'''
1. Verify that MainHub dismisses after X seconds (timeout) when some Linear channel is being played in background.
2. Verify that action restarts the dismiss timeout
3. Verify that after tap on background video main hub will dismiss
4. Verify that MainHub doesnt dismiss after X seconds when no Linear channel is being played in background
'''
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF974
@pytest.mark.MF974_HUB_television_main_screen
def test_main_hub_dismiss():
    ve_test = VeTestApi("main_hub:test_main_hub_dismiss")
    main_hub = ve_test.screens.main_hub
    ve_test.begin()

    "main hub with playing video"
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)
    ve_test.wait(10)
    main_hub.navigate()
    timeout = main_hub.dismiss(ScreenDismiss.TIMEOUT)
    logging.info("mainHub dismissed in %d"% timeout)
    ve_test.log_assert(timeout <= MAIN_HUB_DISMISS_TIMEOUT and timeout >= (MAIN_HUB_DISMISS_TIMEOUT - 4), "Main hub dismiss timeout is wrong. expected=%d sec actual=%d sec"%(MAIN_HUB_DISMISS_TIMEOUT, timeout))

    "actions on main hub"
    ve_test.wait(2)
    main_hub.navigate()
    main_hub.focus_showcase(Showcases.STORE)
    ve_test.wait(5)
    main_hub.focus_showcase(Showcases.GUIDE)
    timeout = main_hub.dismiss(ScreenDismiss.TIMEOUT)
    logging.info("mainHub dismissed in %d"% timeout)
    ve_test.log_assert(timeout <= MAIN_HUB_DISMISS_TIMEOUT and timeout>=(MAIN_HUB_DISMISS_TIMEOUT - 4), "Main hub dismiss timeout is wrong. expected=%d sec actual=%d sec"%(MAIN_HUB_DISMISS_TIMEOUT, timeout))

    "tap on background"
    main_hub.navigate()
    ve_test.wait(3)
    main_hub.dismiss(ScreenDismiss.TAP)

    "main hub without playing video - tune to QAM only channel"
    channels = ve_test.he_utils.cable_only_services
    ve_test.log_assert(channels and len(channels) > 0,"No QAM channels found")
    ve_test.screens.zaplist.navigate()
    channelId = channels[0]['serviceEquivalenceKey']
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelId, False)
    ve_test.wait(1)
    ve_test.screens.notification.verify_active()
    main_hub.navigate() # should navigate by tap on 'home'
    ve_test.wait(MAIN_HUB_DISMISS_TIMEOUT + 10)
    main_hub.verify_active() # still mainhub after timeout

    ve_test.end()

# Verify the zoom feature is able to navigate though channels
# Verify the acyclic behaviour of zoom
@pytest.mark.regression
@pytest.mark.export_regression_MF974_HUB_television_main_screen
@pytest.mark.MF974_HUB_television_main_screen
def test_main_hub_zoom():
    ve_test = VeTestApi("main_hub:test_main_hub_zoom")
    main_hub = ve_test.screens.main_hub
    milestones = ve_test.milestones

    ve_test.begin()

    main_hub.navigate()
    main_hub.focus_showcase(Showcases.GUIDE)

    elements = milestones.getElements(update=True)
    channel = get_channels(elements)

    "Getting channels after zoom"
    for i in range(main_hub.ZOOM_PINCH_COUNT):
        main_hub.zoom(showcase=Showcases.GUIDE)
        ve_test.wait(3)
        elements = milestones.getElements(update=True)
        last_channels = get_channels(elements)
        channel = channel + last_channels

    '''Count non dummy channels'''
    channel_count = count_real_channels(channel)
   # channel_count = len(list(set(channel)))
    result = channel_count == main_hub.MAIN_HUB_TOTAL_CHANNEL_COUNT
    result_string = "The channel count in Main hub should be %d, the count is %d" %(main_hub.MAIN_HUB_TOTAL_CHANNEL_COUNT, channel_count)
    ve_test.log_assert(result, result_string)

    "Testing acyclic zoom behaviour"
    main_hub.zoom(showcase=Showcases.GUIDE)
    ve_test.wait(3)

    elements = milestones.getElements(update=True)
    result_channels = last_channels + list(set(get_channels(elements)) - set(last_channels))

    '''Count non dummy channels'''
    channel_count = count_real_channels(result_channels)
    result = channel_count == main_hub.MAIN_HUB_SHOWED_CHANNEL_COUNT

    ve_test.log_assert(result, "Acyclic zoom test failed")
    ve_test.end()

def count_real_channels(chanels):
    channel_count = 0
    for i in range(0, len(chanels)):
        if chanels[ i ] != u'':
            channel_count = channel_count + 1
    return channel_count

# Verify the pinch feature is able to navigate though channels
# Verify the acyclic behaviour of pinch feature
@pytest.mark.MF974_HUB_television_main_screen
def test_main_hub_pinch():
    ve_test = VeTestApi("main_hub:test_main_hub_pinch")
    main_hub = ve_test.screens.main_hub
    milestones = ve_test.milestones

    ve_test.begin()

    main_hub.navigate()
    main_hub.focus_showcase(Showcases.GUIDE)

    "Zooming to the last channels"
    for i in range(main_hub.ZOOM_PINCH_COUNT + 1):
        main_hub.zoom(showcase=Showcases.GUIDE)
        ve_test.wait(1)

    elements = milestones.getElements(update=True)
    channels = get_channels(elements)

    "Getting channels after pinch"
    for i in range(main_hub.ZOOM_PINCH_COUNT):
        main_hub.pinch(showcase=Showcases.GUIDE)
        ve_test.wait(3)
        elements = milestones.getElements(update=True)
        last_channels = get_channels(elements)
        channels = channels + last_channels

    channel_count = count_real_channels(channels)
    result = channel_count == main_hub.MAIN_HUB_TOTAL_CHANNEL_COUNT
    result_string = "The channel count in Main hub should be %d, the count is %d" %(main_hub.MAIN_HUB_TOTAL_CHANNEL_COUNT, channel_count)
    ve_test.log_assert(result, result_string)

    "Testing acyclic pinch behaviour"
    main_hub.pinch(showcase=Showcases.GUIDE)
    ve_test.wait(3)
    elements = milestones.getElements(update=True)

    result_channels = last_channels + list(set(get_channels(elements)) - set(last_channels))
    channel_count = count_real_channels(result_channels)
    result = channel_count == main_hub.MAIN_HUB_SHOWED_CHANNEL_COUNT

    ve_test.log_assert(result, "Acyclic pinch test failed")
    ve_test.end()


# Verify whether the last selected channel has moved to first position in main hub
@pytest.mark.MF974_HUB_television_main_screen
def test_main_hub_channel_position_movement():
    ve_test = VeTestApi("main_hub:test_channel_position_movement")
    main_hub = ve_test.screens.main_hub

    milestones = ve_test.milestones
    ve_test.begin()

    main_hub.navigate()
    main_hub.focus_showcase(Showcases.GUIDE)
    main_hub.zoom(showcase=Showcases.GUIDE)
    ve_test.wait(1)

    elements = milestones.getElements(update=True)
    channels = remove_dummy_channels(get_channels(elements))
    selected_channel = channels[2]

    "Playing the right most channel"
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event, verify_streaming=True)
    ve_test.wait(5)
    main_hub.navigate()
    ve_test.wait(3)
    main_hub.focus_showcase(Showcases.GUIDE)
    elements = milestones.getElements(update=True)
    channels = remove_dummy_channels(get_channels(elements))
    first_channel = channels[0]

    "Verifying whether the selected channel have moved to first position in main hub"
    ve_test.log_assert(selected_channel == first_channel, "The selected channel was not moved to first position")
    ve_test.end()

def remove_dummy_channels(channels):
    result = []
    for channel in channels:
        if channel != u'':
            result.append(channel)
    return result

# Verify whether the last selected channel has moved to first position in main hub
# Verify whether the updated channel position is maintained after minimising the app and launching it again
@pytest.mark.MF974_HUB_television_main_screen
def test_main_hub_channel_position_after_relaunch():
    ve_test = VeTestApi("main_hub:test_channel_position_after_relaunch")
    main_hub = ve_test.screens.main_hub

    milestones = ve_test.milestones
    ve_test.begin()

    main_hub.navigate()
    main_hub.focus_showcase(Showcases.GUIDE)
    main_hub.zoom(showcase=Showcases.GUIDE)
    ve_test.wait(3)

    elements = milestones.getElements(update=True)
    channels = remove_dummy_channels(get_channels(elements))
    selected_channel = channels[2]

    "Playing the right most channel"
    main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event, verify_streaming=True)
    ve_test.wait(5)
    main_hub.navigate()
    ve_test.wait(1)
    main_hub.focus_showcase(Showcases.GUIDE)
    elements = milestones.getElements(update=True)
    channels = remove_dummy_channels(get_channels(elements))
    playing_channel = channels[0]

    "Verifying whether the selected channel have moved to first position in main hub"
    ve_test.log_assert(selected_channel == playing_channel, "The selected channel was not moved to first position")

    "Minimising the App"
    ve_test.appium.send_app_to_background()
    ve_test.wait(3)

    "Resuming KD App again"
    ve_test.appium.send_app_to_foreground()
    ve_test.wait(2)

    main_hub.navigate()
    ve_test.wait(3)
    main_hub.focus_showcase(Showcases.GUIDE)
    elements = milestones.getElements(update=True)
    channels = remove_dummy_channels(get_channels(elements))
    playing_channel = channels[0]

    "Verifying whether the selected channel state is maintained, after resume of app"
    error_msg = "Selected channel state is not maintained, after resuming of app from background"
    ve_test.log_assert(selected_channel == playing_channel, error_msg)
    ve_test.end()

# 1. Verify Last Played Channel with UPM and CTAP, by playing random linear content
# 2. Verify whether the Last played channel remains same after VOD play
# 3. Verify the linear recommendations with CTAP
@pytest.mark.MF647_Linear_recommendations_on_hub
def test_main_hub_current_events_with_ctap():
    ve_test = VeTestApi("main_hub:test_main_hub_current_events_with_ctap")

    ve_test.begin()

    main_hub = ve_test.screens.main_hub
    "Verify Last Played Channel with UPM and CTAP, by playing random linear content"
    main_hub.verify_last_play_by_selection()

    "Verify whether the Last played channel remains same after VOD play"

    last_played = main_hub.get_first_event_channel()
    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED, VodContentType.NON_EROTIC], {'policy':'false'})

    # Navigate to fullscreen before going to main hub, to avoid any timeouts
    ve_test.screens.fullscreen.navigate()
    ve_test.wait(2)
    main_hub.navigate()
    ve_test.wait(2)

    ve_test.screens.store.play_vod_by_title(asset['title'], verify_streaming = False)
    current_channel = main_hub.get_first_event_channel()

    ve_test.log_assert(last_played == current_channel,\
                       "Last played channel is not same after VOD play. Last Played: %s, Current: %s" \
                       %(last_played, current_channel))

    "Verify the linear recommendations with CTAP"
    main_hub.verify_linear_recommendation_metadata()

    ve_test.end()

# Verify the current events displayed in main hub with ctap
@pytest.mark.MF1363_VOD_recommendations_on_hub
@pytest.mark.regression
@pytest.mark.export_regression_MF1363_VOD_recommendations_on_hub
def test_main_hub_recommended_events_with_ctap():
    ve_test = VeTestApi("main_hub:test_current_events_with_ctap")

    ve_test.begin()
    ve_test.wait(3)
    main_hub = ve_test.screens.main_hub
    main_hub.verify_vod_metadata()
    main_hub.open_vod_action_menu_by_position(EventViewPosition.left_event)
    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2480
@pytest.mark.MF2480_main_hub_standalone
# Verify that in non-standalone mode the LIBRARY is displayed
def test_main_hub_pvr_mode():
    ve_test = VeTestApi("main_hub:test_main_hub_pvr_mode")
    ve_test.begin()
    ve_test.wait(3)

    main_hub = ve_test.screens.main_hub
    main_hub.navigate()
    ve_test.log_assert(main_hub.get_showcase_by_type(Showcases.GUIDE) is not None, "GUIDE stack layer is not displayed!")
    ve_test.log_assert(main_hub.get_showcase_by_type(Showcases.STORE) is not None, "STORE stack layer is not displayed!")
    ve_test.log_assert(main_hub.get_showcase_by_type(Showcases.LIBRARY) is not None, "Library stack layer is not displayed!")

    ve_test.end()

# Verify that in standalone mode the LIBRARY is not displayed
@pytest.mark.MF2480_main_hub_standalone
def test_main_hub_no_pvr_mode():
    ve_test = VeTestApi("main_hub:test_main_hub_no_pvr_mode")
    hhId, login = ve_test.he_utils.createTestHouseHold(withSTB=False, withPVR=False)
    ve_test.begin(login=None)
    ve_test.he_utils.setHHoffers(hhId)
    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123', verify_startup_screen = False)
    ve_test.wait(3)

    main_hub = ve_test.screens.main_hub
    main_hub.navigate()
    ve_test.log_assert(main_hub.get_showcase_by_type(Showcases.GUIDE) is not None, "GUIDE stack layer is not displayed!")
    ve_test.log_assert(main_hub.get_showcase_by_type(Showcases.STORE) is not None, "STORE stack layer is not displayed!")
    ve_test.log_assert(main_hub.get_showcase_by_type(Showcases.LIBRARY) is None, "Library stack layer is displayed in standalone mode!")

    ve_test.end()

def get_channels(elements):
    return [element['channel_name'] for element in elements if 'channel_name' in element]
