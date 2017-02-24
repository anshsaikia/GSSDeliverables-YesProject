import pytest
import logging
import random
import time
import datetime
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ui_building_blocks.K.library_filter import FilterType
from tests_framework.ui_building_blocks.KD.action_menu import ButtonType_k
from tests_framework.ui_building_blocks.screen import ScreenDismiss
from tests_framework.ui_building_blocks.KD.notification import NotificationStrings
from vgw_test_utils.settings import Settings
from vgw_test_utils.IHmarks import IHmark

TUNING_WAIT = 10


def single_finger_swipe(mytest, direction):
    if mytest.platform == "Android":
        mytest.wait(4)
        window_width, window_height = mytest.milestones.getWindowSize()
        mytest.appium.tap(window_width / 2, window_height / 2)
        mytest.wait(4)
    mytest.ui.one_finger_swipe(direction)
    mytest.wait(TUNING_WAIT)
    mytest.screens.notification.dismiss_notification()
    mytest.screens.infolayer.dismiss()
    current_lcn = mytest.screens.playback.get_current_tuned()
    return current_lcn

@IHmark.O_Foxboro
@IHmark.LV_L1
@pytest.mark.parametrize("test_name, asset", [
    ("test_record", "single_event"),
    ("test_episode_record", "episode"),
    ("test_season_record", "season"),
    ("test_full_record", "full_single_event"),
    ("test_full_episode_record", "full_episode"),
])
def test_generic_record(test_name, asset):
    test = VeTestApi(test_name)
    assets = test.assets
    test.begin()
    asset = getattr(assets, asset)
    asset.labels_set() # Should be after test.begin()
    assets.generic_book_record_and_check(asset)
    test.end()


@pytest.mark.parametrize("test_name, asset", [
    pytest.mark.test_delete_record(("test_delete_record", "single_event")),
    pytest.mark.test_timeline_record_delete(("test_timeline_record_delete", "timeline_single_event")),
    pytest.mark.test_timeline_episode_delete(("test_timeline_episode_delete", "episode")),
])
def test_generic_delete_record(test_name, asset):
    test = VeTestApi(test_name)
    assets = test.assets
    asset = getattr(assets, asset)
    test.begin()
    asset.labels_set() # Should be after test.begin()
    assets.generic_book_record_and_check(asset)
    assets.record_stop_and_delete(asset)

    test.end()


def test_stop_record():
    test = VeTestApi("test_stop_record")
    assets = test.assets
    test.begin()
    asset = assets.single_event
    asset.labels_set() # Should be after test.begin()
    assets.record_and_stop_recording(asset)
    test.end()

@pytest.mark.parametrize("test_name, asset", [
    pytest.mark.test_cancel_record(("test_cancel_record", "single_event")),
    pytest.mark.test_cancel_full_record(("test_cancel_full_record", "full_single_event")),
    pytest.mark.test_cancel_episode(("test_cancel_episode", "episode")),
    pytest.mark.test_cancel_full_episode(("test_cancel_full_episode", "full_episode")),
    pytest.mark.test_cancel_season(("test_cancel_season", "season")),
    pytest.mark.L2_DVR(("test_cancel_episode","episode")),
    pytest.mark.LV_L1(("test_cancel_episode","episode")),
])
def test_generic_cancel(test_name, asset):
    test = VeTestApi(test_name)
    assets = test.assets
    test.begin()
    asset = getattr(assets, asset)
    asset.labels_set() # Should be after test.begin()
    assets.check_cancel(asset)
    test.end()

@pytest.mark.parametrize("test_name, asset", [
    pytest.mark.test_grid_record(("test_grid_record", "single_event")),
    pytest.mark.test_grid_episode_record(("test_grid_episode_record", "episode")),
    # can't check: pytest.mark.test_grid_season_record(("test_grid_season_record", "season")),
])
def test_generic_grid(test_name, asset):
    test = VeTestApi(test_name)
    if test.platform != "iOS":
        pytest.skip("add milestones to android !")
    assets = test.assets
    test.begin()
    asset = getattr(assets, asset)
    asset.labels_set() # Should be after test.begin()
    assets.grid_check(asset)
    test.end()


def test_grid_osd_on_auth_error():
    test = VeTestApi("test_osd_on_auth_error_grid")
    if test.platform != "iOS":
        pytest.skip("add milestones to android !")
    assets = test.assets
    asset = assets.single_event
    test.begin()
    asset.labels_set() # Should be after test.begin()
    assets.grid_check(asset)

    Settings['household_id'] = test.configuration["he"]["generated_household"]
    upmDeviceId = test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    test.screens.full_content_screen.tap_event_by_title(asset.title)
    test.screens.linear_action_menu.verify_active()
    test.screens.linear_action_menu.verify_and_press_stop_button()

    # verify and press YES on stop recording confirmation screen
    test.screens.notification.verify_notification_message(NotificationStrings.STOP_RECORDING.value)
    test.screens.notification.get_and_tap_notification_button("DIC_YES")

    # in iOS should refresh
    test.he_utils.wait_for_recording_status(asset.title, status="RECORDED")
    test.screens.library_filter.go_to_previous_screen()
    test.screens.full_content_screen.tap_event_by_title(asset.title)
    test.screens.linear_action_menu.verify_active()

    # verify that action has updated to "DELETE RECORDING"
    test.ui.verify_button(test.screens.linear_action_menu.button_type.DELETE, True, 10)

    # remove subscription to HH
    test.he_utils.deleteSubscriptionUsingUpm(Settings['household_id'])

    # verify playback fails
    logging.info("Going to play event:%s", asset.title)
    play_element = test.milestones.getElement([("id", "play", "==")])
    test.appium.tap_element(play_element)
    logging.info("Verify playback Error on event:%s", asset.title)
    test.screens.notification.verify_notification_message(NotificationStrings.AUTH_ERROR.value)

    test.end()


def test_cancel_booking_from_grid():
    ve_test = VeTestApi("test_cancel_booking_from_grid")
    ve_test.begin()
    ve_test.screens.guide.navigate()

    # Open ActionMenu when tapping on non-current event on any channel
    ve_test.wait(3)
    elements = ve_test.milestones.getElements()
    for element in elements:
        if ("event_source" in element and element["event_source"] == "EVENT_SOURCE_TYPE_LINEAR"):
            if element["is_current"] == False:
                ve_test.appium.tap_element(element)
                break
    ve_test.wait(2)
    # Record the chosen event and verify booking
    ve_test.screens.linear_action_menu.verify_and_press_record_button()
    ve_test.ui.verify_button(ButtonType_k.CANCEL, True, 10)

    # Cancel the future booking and verify still in Action menu
    ve_test.screens.linear_action_menu.verify_and_press_cancel_booking_button()
    ve_test.ui.verify_button(ButtonType_k.RECORD, True, 10)

    ve_test.end()

def test_cancel_booking_from_library():
    ve_test = VeTestApi("test_cancel_booking_from_library")
    ve_test.begin()

    ve_test.screens.guide.navigate()
    ve_test.wait(3)
    #Open ActionMenu when tapping on non-current event on any channel
    elements = ve_test.milestones.getElements()
    for element in elements:
        if ("event_source" in element and element["event_source"] == "EVENT_SOURCE_TYPE_LINEAR"):
            if element["is_current"] == False:
                ve_test.appium.tap_element(element)
                break
    ve_test.wait(2)
    # Record the chosen event and verify booking
    ve_test.screens.linear_action_menu.verify_and_press_record_button()
    ve_test.ui.verify_button(ButtonType_k.CANCEL, True, 10)

    # navigate to Library scheduled events
    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.SCHEDULED)
    elements = ve_test.milestones.getElements()
    print "elements =", elements
    # tap on first booked event (should be latest to be booked)
    for element in elements:
        if ("event_source" in element and element["event_source"] == "EVENT_SOURCE_TYPE_PVR"):
            ve_test.appium.tap_element(element)
            break

    ve_test.wait(2)
    # Cancel the future booking and verify we go back to SCHEDULED recordings
    ve_test.screens.linear_action_menu.verify_and_press_cancel_booking_button()
    ve_test.ui.verify_screen(ve_test.screens.library_filter)
    ve_test.end()

@pytest.mark.test_cancel_season_library
def test_cancel_season_from_library():
    ve_test = VeTestApi("test_cancel_season_from_library")
    assets = ve_test.assets
    sessionAsset = ve_test.sessionAsset
    asset=getattr(assets, "season")
    ve_test.begin()

    asset.labels_set()
    sessionAsset.record_from_action_menu(asset)
    assets.cancel_season_action_menu(asset)

    ve_test.end()

@pytest.mark.test_cancel_season_grid
def test_cancel_season_from_grid():
    ve_test = VeTestApi("test_cancel_season_from_grid")
    assets = ve_test.assets
    sessionAsset = ve_test.sessionAsset
    asset=getattr(assets, "season")
    ve_test.begin()
    asset.labels_set()
    sessionAsset.record_from_action_menu(asset)
    asset.channel = assets.get_current_episode_channel()
    channel_id = asset.channel.serviceEquivalenceKey
    manage_recording = ve_test.milestones.get_dic_value_by_key("DIC_TIMELINE_MANAGE_RECORDINGS").upper()
    ve_test.ui.verify_and_press_button_by_title(manage_recording)

    ve_test.screens.guide.navigate()

    ve_test.screens.guide.tune_to_channel_by_sek(channel_id,False)

    ve_test.ui.verify_and_press_button_by_title(manage_recording)
    assets.cancel_season_action_menu(asset)

    ve_test.end()

def test_timeline_episode_record():
    test = VeTestApi("test_episode_record_from_timeline")
    assets = test.assets
    test.begin()
    asset = assets.timeline_episode
    asset.labels_set() # Should be after test.begin()
    assets.generic_book_record_and_check(asset)
    test.end()

#@pytest.mark.skip
def test_tuner_conflict():
    num_of_tuner = 4
    test = VeTestApi("test_tuner_conflict")
    assets = test.assets
    test.begin()

    logging.info('get info from Tanent')
    tuned_channel, channel_prop = test.he_utils.getLinearContentABR('clear')
    logging.info("the tuned channel is: %s",str(tuned_channel))

    logging.info('tune to tuned_channel')
    test.screens.zaplist.tune_to_channel_by_sek(str(tuned_channel), verify_streaming_started=False)

    logging.info('dismiss info layer')
    test.screens.notification.dismiss_notification()
    test.screens.infolayer.dismiss()
    first_channel_lcn = tuned_channel
    current_lcn = tuned_channel

    asset = assets.single_event
    asset.labels_set() # Should be after test.begin()

    for i in range(num_of_tuner):
        if i > 0:
           logging.info('swipe up to tune to the next channel')
           current_lcn = single_finger_swipe(test, ScreenActions.UP)
           test.log_assert(current_lcn != first_channel_lcn,
                    "Failed to change channel via swipe up, distance of a quarter screen")
        logging.info('%s) Book the current asset on the channel %s', str(i), str(current_lcn))
        assets.generic_book(asset)
        if test.platform == "Android":
            test.ui.wait_for_label("CANCEL BOOKING")

    logging.info('swipe up to tune to the next channel')
    current_lcn = single_finger_swipe(test, ScreenActions.UP)
    test.log_assert(current_lcn != first_channel_lcn,
                    "Failed to change channel via swipe up, distance of a quarter screen")

    logging.info('Book the current asset on the last channel %s (should fail with tuner conflict)', str(current_lcn))
    assets.generic_book(asset, False)

    logging.info('check that the Tuner_Conflict OSD appears')
    notification = test.screens.notification
    notification.verify_notification_message_by_key("DIC_ERROR_BOOKING_TUNER_CONFLICT", type="general")

    test.end()


def test_stop_recording_library_action_menu():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_stop_recording_library_action_menu")
    if ve_test.platform == "iOS":
        pytest.skip("add milestones to iOS !")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    # Work only on ABR channels
    target_channel_id, event_title = ve_test.he_utils.get_channel_to_record_current_event()
    print "target_channel_id: ", target_channel_id

    # Navigate to current event and start the recording
    event_title = ve_test.screens.guide.navigateToCurrentEventOnChannel(target_channel_id)
    ve_test.screens.linear_action_menu.record_current_event(event_title)
    ve_test.wait(5) # lets wait to avoid from race condition - as there some cases filters are still not include the event

    # Go to Recording filter and stop recording
    logging.info("Go to library filter:%s expected to find event:%s", event_title, FilterType.RECORDINGS)
    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.RECORDINGS)

    ve_test.screens.full_content_screen.tap_event_by_title(event_title)
    ve_test.screens.linear_action_menu.verify_active()

    ve_test.screens.linear_action_menu.verify_and_press_stop_button()
    elements = ve_test.milestones.getElements()

    ve_test.screens.notification.verify_notification_message("Are you sure that you want to stop this recording?")
    ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

    #verify that action has updated to "DELETE RECORDING"
    ve_test.ui.verify_button(ve_test.screens.linear_action_menu.button_type.DELETE, True, 10)

    ve_test.end()

def test_stop_recording_timeline_info_layer():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_stop_recording_timeline_info_layer")
    if ve_test.platform == "iOS":
        pytest.skip("add milestones to iOS !")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    # Work only on ABR channels
    target_channel_id, event_title = ve_test.he_utils.get_channel_to_record_current_event()
    event_title = ve_test.screens.guide.navigateToCurrentEventOnChannel(target_channel_id)

    play_element = ve_test.milestones.getElement([("id", "actions_menu_play_button", "==")])
    ve_test.appium.tap_element(play_element)
    logging.info("Verify playback on event:%s", event_title)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.wait(5)
    ve_test.screens.infolayer.show()

    ve_test.screens.linear_action_menu.record_current_event(event_title)
    ve_test.wait(5) # lets wait to avoid from race condition - as there some cases filters are still not include the event

    # refresh info layer to get STOP_RECORDING BUTTON
    ve_test.screens.infolayer.dismiss(action = ScreenDismiss.TAP)
    ve_test.screens.infolayer.show()
    ve_test.wait(5)

    ve_test.screens.linear_action_menu.verify_and_press_stop_button()
    elements = ve_test.milestones.getElements()

    ve_test.screens.notification.verify_notification_message("Are you sure that you want to stop this recording?")
    ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

    #verify that action has updated to "DELETE RECORDING"
    ve_test.ui.verify_button(ve_test.screens.linear_action_menu.button_type.DELETE, True, 10)

    ve_test.end()


def test_booking_series_on_multiple_channels_without_duplicates():
    ve_test = VeTestApi("test_booking_series_on_multiple_channels_without_duplicates")
    ve_test.begin()

    foundEpisode = False
    elementsTemp = None
    countDuplicateEpisodeInLibrary = 0

    allServices = ve_test.cmdc.get_cmdc_all_services()
    allEpisodesOnAllServicesArray = ve_test.cmdc.get_cmdc_all_episodes_on_all_service(allServices)
    allEpisodesOnAllServicesProgramId = ve_test.cmdc.get_all_episodes_id_on_all_services(allEpisodesOnAllServicesArray)
    allduplicateEpisodesProgramId = ve_test.cmdc.get_all_duplicated_episodes_id(allEpisodesOnAllServicesProgramId)
    allduplicateEpisodesOnAllServices = ve_test.cmdc.get_all_duplicated_episodes_on_all_services(allduplicateEpisodesProgramId, allEpisodesOnAllServicesArray)
    allduplicateEpisodesOnMultipuleServices = ve_test.cmdc.get_all_duplicated_episodes_on_multi_services(allduplicateEpisodesOnAllServices)

    for dupEpisode in allduplicateEpisodesOnMultipuleServices:
        if foundEpisode:
            break
        dupEpisodeId = dupEpisode['id'].split('://', 1)[1]
        ve_test.screens.timeline.navigate()
        ve_test.screens.timeline.scroll_to_channel_by_sek(dupEpisode['serviceEquivalenceKey'])
        elements = ve_test.milestones.getElements()

        while foundEpisode == False and elementsTemp != elements:
            elements = ve_test.milestones.getElements()
            for element in elements:
                if ("event_id" in element and dupEpisodeId in element["event_id"]):
                    foundEpisode = True
                    break
                else:
                    if 'event_type' in element and element['event_type'] == 'EVENT_CONTENT_TYPE_STANDALONE':
                        ve_test.appium.move_element(element['x_pos'], element['y_pos'], (element['width'] / 1.5),
                                                    ScreenActions.LEFT)
                        elementsTemp = ve_test.milestones.getElements()

    ve_test.log_assert (foundEpisode == True, "Failed reason: None of the duplicated episodes can be found via timeline")

    ve_test.ui.verify_and_press_button_by_title("MORE INFO")
    ve_test.wait(3)
    ve_test.ui.verify_and_press_button_by_title("MANAGE RECORDINGS")
    ve_test.ui.verify_and_press_button_by_title("RECORD THIS SEASON")
    splash = "THIS SEASON WILL BE RECORDED."
    ve_test.ui.wait_for_label(splash)
    ve_test.ui.wait_for_label_removed(splash)
    ve_test.wait(3)
    ve_test.ui.verify_button_by_title("CANCEL BOOKING", True)

    ve_test.ui.verify_and_press_button_by_title("exit", "id")
    ve_test.ui.verify_and_press_button_by_title("exit", "id")
    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.SCHEDULED)

    allAssetsInLibraryScheduledFilter = ve_test.screens.full_content_screen.get_all_assets_in_full_content_screen("EVENT_TYPE_PVR_ASSET")

    for indexElement in allAssetsInLibraryScheduledFilter:
            if "event_id" in indexElement and dupEpisodeId in indexElement["event_id"]:
                countDuplicateEpisodeInLibrary += 1

    ve_test.log_assert(countDuplicateEpisodeInLibrary == 1,
                       "Failed reason: Episode in the library with the same programId is: {} while is should be exactly 1".format(countDuplicateEpisodeInLibrary))
    ve_test.end()


def test_delete_recording_library_action_menu():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_delete_recording_library_action_menu")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    # Work only on ABR channels
    target_channel_id, event_title = ve_test.he_utils.get_channel_to_record_current_event()

    # Navigate to current event and start the recording
    event_title = ve_test.screens.guide.navigateToCurrentEventOnChannel(target_channel_id)
    ve_test.screens.linear_action_menu.record_current_event(event_title)
    ve_test.wait(5) # lets wait to avoid from race condition - as there some cases filters are still not include the event

    # Go to Recording filter and stop recording
    logging.info("Go to library filter:%s expected to find event:%s", event_title, FilterType.RECORDINGS)
    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_event(0)
    ve_test.screens.full_content_screen.tap_event_by_title(event_title)
    ve_test.screens.linear_action_menu.verify_active()

    ve_test.screens.linear_action_menu.verify_and_press_stop_button()

    ve_test.screens.notification.verify_notification_message("Are you sure that you want to stop this recording?")
    ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

    #verify that action has updated to "DELETE RECORDING"
    ve_test.ui.verify_button(ve_test.screens.linear_action_menu.button_type.DELETE, True, 10)
    ve_test.screens.linear_action_menu.verify_and_press_delete_button()

    ve_test.screens.notification.verify_notification_message("Are you sure that you want to delete this recording?")
    ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

    # verify that we are back at library filter scheduled and that it is empty
    ve_test.wait(5)
    ve_test.log_assert(ve_test.milestones.get_current_screen() == "full_content_screen", "Failed returning to Library")

    ve_test.log_assert(ve_test.screens.full_content_screen.screen_empty(), "Library is not empty after recording deleted")

    ve_test.end()


def test_delete_recording_timeline_info_layer():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_delete_recording_timeline_info_layer")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    # Work only on ABR channels
    target_channel_id, event_title = ve_test.he_utils.get_channel_to_record_current_event()
    event_title = ve_test.screens.guide.navigateToCurrentEventOnChannel(target_channel_id)

    play_element = ve_test.milestones.getElement([("id", "actions_menu_play_button", "==")])
    ve_test.appium.tap_element(play_element)
    logging.info("Verify playback on event:%s", event_title)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.wait(5)
    ve_test.screens.infolayer.show()

    ve_test.screens.linear_action_menu.record_current_event(event_title)
    ve_test.wait(5) # lets wait to avoid from race condition - as there some cases filters are still not include the event

    # refresh info layer to get STOP_RECORDING BUTTON
    ve_test.screens.infolayer.dismiss(action = ScreenDismiss.TAP)
    ve_test.screens.infolayer.show()
    ve_test.wait(5)

    ve_test.screens.linear_action_menu.verify_and_press_stop_button()

    ve_test.screens.notification.verify_notification_message("Are you sure that you want to stop this recording?")
    ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

    #verify that action has updated to "DELETE RECORDING"
    ve_test.ui.verify_button(ve_test.screens.linear_action_menu.button_type.DELETE, True, 10)
    ve_test.screens.linear_action_menu.verify_and_press_delete_button()

    ve_test.screens.notification.verify_notification_message("Are you sure that you want to delete this recording?")
    ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

    #verify that action has updated back to "RECORD"
    ve_test.ui.verify_button(ve_test.screens.linear_action_menu.button_type.RECORD, True, 10)

    ve_test.end()

def test_booking_error():
    test = VeTestApi("test_booking_error")
    assets = test.assets
    test.begin()

    logging.info('get info from Tanent')
    tuned_channel, channel_prop = test.he_utils.getLinearContentABR('clear')
    logging.info("the tuned channel is: %s",str(tuned_channel))

    logging.info('tune to tuned_channel')
    test.screens.zaplist.tune_to_channel_by_sek(str(51), verify_streaming_started=False)

    logging.info('dismiss info layer')
    test.screens.notification.dismiss_notification()
    test.screens.infolayer.dismiss()
    current_lcn = tuned_channel

    hh_id = test.configuration["he"]["generated_household"]
    device_id=random.randint(100, 10000)
    logging.info('add random device %s to HH:%s', device_id, hh_id)
    test.he_utils.addHouseHoldDevices(hh_id, [str(device_id)], deviceFullType="MANAGED", drmDeviceType=None, createPVR=True)
    test.wait(5)

    logging.info('Book the current event on the current channel %s (should fail with booking error)', str(current_lcn))
    asset = assets.single_event
    asset.labels_set() # Should be after test.begin()
    assets.generic_book(asset, False)

    logging.info('check that the booking_general OSD appears')
    notification = test.screens.notification
    logging.info('delete device %s from HH:%s', device_id, hh_id)
    test.he_utils.deleteDevicefromHousehold(hh_id, device_id)
    notification.verify_notification_message_by_key("DIC_ERROR_BOOKING_GENERAL", type="general")

    test.end()


def test_library_fullcontent_paging(num_recorded=100, num_scheduled=100):
    # vgw test ithils must be installed for running this test
    from vgw_test_utils.settings import Settings
    from vgw_test_utils.headend_bulk import simulate_future_events, simulate_recorded_events

    ve_test = VeTestApi("test_library_fullcontent_paging")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    simulate_recorded_events(num_recorded)
    simulate_future_events(num_scheduled)
    time.sleep(5)

    ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.SCHEDULED)
    ve_test.screens.full_content_screen.verify_full_content_and_sort(FilterType.SCHEDULED)

    ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.RECORDINGS)
    ve_test.screens.full_content_screen.verify_full_content_and_sort(FilterType.RECORDINGS)

    ve_test.end()

def test_series_filter():
    ve_test = VeTestApi("test_series_filter")
    ve_test.begin()

    foundEpisode = False
    elementsTemp = None
    service = ve_test.cmdc

    allServices = service.get_cmdc_all_services(service.test)
    allEpisodesOnAllServicesArray = ve_test.cmdc.get_cmdc_all_episodes_on_all_service(allServices)

    for episode in allEpisodesOnAllServicesArray:
        if foundEpisode:
            break
        episodeId = episode['id'].split('://', 1)[1]
        ve_test.screens.timeline.navigate()
        ve_test.screens.timeline.scroll_to_channel_by_sek(episode['serviceEquivalenceKey'])
        elements = ve_test.milestones.getElements()

        while foundEpisode == False and elementsTemp != elements:
            elements = ve_test.milestones.getElements()
            for element in elements:
                if ("event_id" in element and episodeId in element["event_id"]):
                    foundEpisode = True
                    break
                else:
                    if 'event_type' in element and element['event_type'] == 'EVENT_CONTENT_TYPE_STANDALONE':
                        ve_test.appium.move_element(element['x_pos'], element['y_pos'], (element['width'] / 1.5),
                                                    ScreenActions.LEFT)
                        elementsTemp = ve_test.milestones.getElements()

    ve_test.log_assert(foundEpisode == True, "Failed reason: None of the episodes can be found via timeline")

    ve_test.ui.verify_and_press_button_by_title("MORE INFO")
    ve_test.wait(3)

    if ve_test.ui.verify_button_by_title("CANCEL BOOKING", True, assertFlag=False):
        ve_test.ui.verify_and_press_button_by_title("CANCEL BOOKING")
        ve_test.wait(3)

    ve_test.ui.verify_and_press_button_by_title("MANAGE RECORDINGS")
    ve_test.ui.verify_and_press_button_by_title("RECORD THIS SEASON")
    splash = "THIS SEASON WILL BE RECORDED."
    ve_test.ui.wait_for_label(splash)
    ve_test.ui.wait_for_label_removed(splash)
    ve_test.wait(60)

    ve_test.ui.verify_button_by_title("CANCEL BOOKING", True)

    ve_test.ui.verify_and_press_button_by_title("exit", "id")
    ve_test.ui.verify_and_press_button_by_title("exit", "id")

    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_series()

    ve_test.end()


'''
This test is currently testing the same functionality as in test_series_filter for android since the record for series button has no milestones for android.
once the milestones will be ready need to merge both tests.
'''
def test_series_filter_android():
    ve_test = VeTestApi("test_series_filter")
    ve_test.begin()
    assets = ve_test.assets
    asset = assets.single_event
    asset.labels_set() # Should be after test.begin()

    service = ve_test.cmdc

    allServices = service.get_cmdc_all_services(service.test)
    allEpisodesOnAllServicesArray = ve_test.cmdc.get_cmdc_all_episodes_on_all_service(allServices)

    tune_channel = allEpisodesOnAllServicesArray[0]['serviceEquivalenceKey']
    ve_test.screens.zaplist.tune_to_channel_by_sek(tune_channel, verify_streaming_started=False)
    assets.generic_book(asset, False)
    ve_test.appium.tap(522 + 20, 1200 + 80) # reltive to record bottom
    ve_test.ui.wait_for_label("CANCEL BOOKING")
    ve_test.wait(60)

    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_series_Android()

    ve_test.end()

#Author: Shmuel Bouhman
@pytest.mark.level2
@pytest.mark.series_collapsing_MF2283
def test_series_collapsing():
    ve_test = VeTestApi("test_series_collapsing")
    ve_test.begin()

    #set channel1 and channel2 and duration1 and duration2
    service = ve_test.cmdc
    channel1=None
    channel2=None

    allServices = service.get_cmdc_all_services(service.test)
    allEpisodesOnAllServicesArray = ve_test.cmdc.get_cmdc_all_episodes_on_all_service(allServices)

    for episode in allEpisodesOnAllServicesArray:
        if 'serviceEquivalenceKey' in episode and 'duration' in episode:
            if not channel1:
                channel1 = episode['serviceEquivalenceKey']
                duration1 = episode['duration']
            elif episode['serviceEquivalenceKey'] != channel1:
                channel2 = episode['serviceEquivalenceKey']
                duration2 = episode['duration']

    #Calc the wait time until the next asset
    min = datetime.datetime.now().minute % duration1
    if min >= duration1 - duration1/2:
        wait = duration1 - min
    else:
        wait = 0

    #goto timeline
    ve_test.screens.timeline.navigate()

    #waiting until the begining of the next asset
    ve_test.wait(wait*60)

    #tune to channel1
    ve_test.screens.timeline.scroll_to_channel_by_sek(channel1)

    # find the element of the Episode to record
    elements = ve_test.milestones.getElements()
    elements = ve_test.milestones.get_value_by_key(elements,'event_id')
    ve_test.log_assert(elements, "Failed reason: None of the episodes can be found via timeline")

    events = ve_test.milestones.getElementsArray([('event_type','EVENT_CONTENT_TYPE_STANDALONE','==')])

    #Tab on the 1st asset
    if 'x_pos' in events[0] and  'x_pos' in events[1]:
        if events[0]['x_pos']< events[1]['x_pos']:
            ve_test.appium.tap_element(events[0])
        else:
            ve_test.appium.tap_element(events[1])
        ve_test.wait(1)

    #Verify we are in action menu
    ve_test.log_assert(ve_test.milestones.getElement([("id", 'play', "==")]), "Failed reason: MORE INFO screen doesnt appear")

    #book the 1st Episode
    manage_recording = ve_test.milestones.get_dic_value_by_key("DIC_TIMELINE_MANAGE_RECORDINGS").upper()
    ve_test.ui.verify_and_press_button_by_title(manage_recording)
    record_this_episode = ve_test.milestones.get_dic_value_by_key("DIC_ACTION_MENU_ACTION_RECORD_THIS_EPISODE").upper()
    ve_test.ui.verify_and_press_button_by_title(record_this_episode)
    ve_test.wait(5)

    ve_test.ui.verify_and_press_button_by_title(manage_recording)
    cancel_this_episode = ve_test.milestones.get_dic_value_by_key("DIC_ACTION_MENU_ACTION_CANCEL_EPISODE_BOOKING").upper()
    ve_test.ui.verify_button_by_title(cancel_this_episode, True)

    ve_test.ui.verify_and_press_button_by_title(manage_recording)
    #Click on EXIT to return to the previous screen
    ve_test.ui.verify_and_press_button_by_title("exit", "id")

    #Tab on the 2nd asset
    if 'x_pos' in events[0] and  'x_pos' in events[1]:
        if events[0]['x_pos']> events[1]['x_pos']:
            ve_test.appium.tap_element(events[0])
        else:
            ve_test.appium.tap_element(events[1])
        ve_test.wait(1)

    #Verify we are in action menu
    elements = ve_test.milestones.getElements()
    elements = ve_test.milestones.get_value_by_key(elements,'event_id')
    ve_test.log_assert('programid' in elements,"Failed reason: action menu screen doesnt appear")

    #book the 2nd Episode
    ve_test.ui.verify_and_press_button_by_title(manage_recording)
    ve_test.ui.verify_and_press_button_by_title(record_this_episode)
    ve_test.wait(5)

    ve_test.ui.verify_and_press_button_by_title(manage_recording)
    ve_test.ui.verify_button_by_title(cancel_this_episode, True)
    ve_test.ui.verify_and_press_button_by_title(manage_recording)

    #Click on EXIT twice to return to the previous screen
    ve_test.ui.verify_and_press_button_by_title("exit", "id")
    ve_test.ui.verify_and_press_button_by_title("exit", "id")

    #Go back to TV FILTER
    ve_test.screens.tv_filter.navigate()

    #Go to timeline
    ve_test.screens.timeline.navigate()

    #Calc the wait time until the next asset
    min = datetime.datetime.now().minute % duration2
    if min >= duration2 - duration2/2:
        wait = duration2 - min
    else:
        wait = 0

    #waiting until the begining of the next asset
    ve_test.wait(wait*60)

    #tune to channel2
    ve_test.screens.timeline.scroll_to_channel_by_sek(channel2)

    # find the element of the Episode to record
    elements = ve_test.milestones.getElements()
    elements = ve_test.milestones.get_value_by_key(elements, 'event_id')

    ve_test.log_assert(elements, "Failed reason: None of the episodes can be found via timeline")

    events = ve_test.milestones.getElementsArray([('event_type', 'EVENT_CONTENT_TYPE_STANDALONE', '==')])

    # Tab on the 1st asset
    if 'x_pos' in events[0] and 'x_pos' in events[1]:
        if events[0]['x_pos'] < events[1]['x_pos']:
            ve_test.appium.tap_element(events[0])
        else:
            ve_test.appium.tap_element(events[1])
        ve_test.wait(1)

    ve_test.log_assert(ve_test.milestones.getElement([("id", 'play', "==")]), "Failed reason: MORE INFO screen doesnt appear")

    ve_test.ui.verify_and_press_button_by_title(manage_recording)
    ve_test.wait(1)

    #book the 1st Episode
    ve_test.ui.verify_and_press_button_by_title(record_this_episode)
    ve_test.wait(5)

    ve_test.ui.verify_and_press_button_by_title(manage_recording)
    ve_test.ui.verify_button_by_title(cancel_this_episode, True)
    ve_test.ui.verify_and_press_button_by_title(manage_recording)

    #Click on EXIT to return to the previous screen
    ve_test.ui.verify_and_press_button_by_title("exit", "id")
    ve_test.ui.verify_and_press_button_by_title("exit", "id")
    ve_test.ui.verify_and_press_button_by_title("exit", "id")

    #Navigate to Library
    ve_test.screens.library_filter.navigate()

    #Get the series asset and the episode asset
    elements = ve_test.milestones.getElements()
    series = ve_test.milestones.getElementsArray([('section','SERIES','=='),('name','event_view','==')],elements)
    isEpisode = False
    isSeries = False
    Episode = None
    Series = None
    for ser in series:
        if 'event_id' in ser:
            if 'PPS' in ser['event_id']:
                isEpisode = True
                Episode = ser
            if 'groupid' in ser['event_id']:
                isSeries = True
                Series = ser

    ve_test.log_assert(isSeries == True, "Failed reason: No full Series can be found in the Library")
    ve_test.log_assert(isEpisode == True, "Failed reason: No Series with only one Episode can be found in the Library")

    #Click on the found episode
    ve_test.appium.tap_element(Episode)
    ve_test.wait(1)

    #Check that the asset is playable
    element = ve_test.milestones.getElement([("id", 'play', "==")])
    ve_test.log_assert(element, "Failed reason: The asset isn't playable !!!")

    #Click on EXIT twice to return to the previous screen
    ve_test.ui.verify_and_press_button_by_title("exit", "id")

    #Click on the found series
    ve_test.appium.tap_element(Series)
    ve_test.wait(1)

    # Verify that there is any episode in this series
    element = ve_test.milestones.getElement([("event_type", 'EVENT_TYPE_PVR_ASSET', "==")])
    ve_test.log_assert(element, "Failed reason: No Episodes can be found in this Series")

    #Click on the 1st episode
    ve_test.appium.tap_element(element)
    ve_test.wait(1)

    #Check that the asset is playable
    element = ve_test.milestones.getElement([("id", 'play', "==")])
    ve_test.log_assert(element, "Failed reason: The asset isn't playable !!!")

    #Click on EXIT to return to the previous screen
    ve_test.ui.verify_and_press_button_by_title("exit", "id")

    ve_test.end()

