import time

import pytest
import logging
from tests_framework.ui_building_blocks.K.library_filter import FilterType
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.settings import Settings
from tests_framework.ui_building_blocks.KD.notification import NotificationStrings
from vgw_test_utils.IHmarks import IHmark
from  retrying import retry
from datetime import datetime

logger = logging.getLogger(__name__)

def stop_ongoing_recording(test, event_title):
    from vgw_test_utils.headend_util import get_all_catalog, stop_recording
    catalog = get_all_catalog(filter_to_use="state=RECORDING")
    for event in catalog:
        if event['content']['title'].upper() == event_title.upper():
            stop_recording(event['uri'])
            return True
    return False


@pytest.mark.MF2057
def test_playback_navigation_on_current_recording():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_playback_navigation")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    # Work only on ABR channels
    target_channel_id = 3  # currently hardcoded as we had a problem with the some channels
    target_channel = None
    abr_channels = ve_test.he_utils.abr_services
    for ch in abr_channels:
        if abr_channels[ch]['logicalChannelNumber'] == target_channel_id:
            target_channel = abr_channels[ch]
    ve_test.log_assert(target_channel, "Target channel not found!")
    logging.info("Scroll to channel:%s through Guide screen",str(target_channel['logicalChannelNumber']))
    ve_test.screens.guide.navigate()
    ve_test.screens.guide.scroll_to_channel_by_sek(target_channel['serviceEquivalenceKey'])
    current_event = ve_test.screens.guide.CurrentCenteredChannelActionMenu()
    event_title = current_event['title_text']

    # Record the current event and verify booking
    ve_test.screens.linear_action_menu.record_current_event(event_title)
    ve_test.wait(5) # lets wait to avoid from race condition - as there some cases filters are still not include the event

    # Go to Recording filter and start playback
    logging.info("Go to library filter:%s expected to find event:%s", event_title, FilterType.RECORDINGS)
    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.RECORDINGS)
    ve_test.screens.full_content_screen.tap_event_by_title(event_title)
    ve_test.screens.linear_action_menu.verify_active()
    logging.info("Going to play event:%s", event_title)
    play_element = ve_test.milestones.getElement([("id", "actions_menu_play_button", "==")])
    #ve_test.log_assert(play_element['state'] == 'STOPPED', "Playback not in STOPPED state:" + play_element['state'])
    ve_test.appium.tap_element(play_element)
    logging.info("Verify playback on event:%s", event_title)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()

@IHmark.O_Malka
@IHmark.LV_L1
def test_playback_skip_and_jamp_disable():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_playback_skip_and_jamp_disable")
    ve_test.begin()

    assets = ve_test.assets
    asset = assets.single_event
    asset.labels_set()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    hhid = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    #go to restricted channel
    restricted_channel_sek = ve_test.he_utils.find_blocked_channel("trickSkipRwEnabled", "sek")
    logging.info('restricted_channel_sek:%s', str(restricted_channel_sek))
    if restricted_channel_sek == None:
        logging.info('Blocked rw channel not found. Test PASS :-) ')
        ve_test.end()
        return
    ve_test.screens.zaplist.tune_to_channel_by_sek(str(restricted_channel_sek), verify_streaming_started=False)

    event_title = assets.generic_book(asset, False)
    ve_test.wait(30) # wait to asset to appear in library screen

    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_event(0)

    ve_test.screens.linear_action_menu.verify_active()
    logging.info("Going to play event:%s", event_title)
    play_element = ve_test.milestones.getElement([("id", "play", "==")])

    ve_test.appium.tap_element(play_element)

    pin_code = ve_test.he_utils.getParentalRatingPin(hhid)
    ve_test.wait(10)
    pin_screen = ve_test.screens.pincode
    if pin_screen.is_active():
        pin_screen.enter_pin(pin_code)
    logging.info("Verify playback on event:%s", event_title)
    ve_test.screens.playback.verify_streaming_playing()

    # === check skip button ( -15Sec ) ===
    logging.info("Going to skip button")
    window_width, window_height = ve_test.milestones.getWindowSize()
    ve_test.appium.tap(window_width / 2, window_height / 2)

    ve_test.wait(30)
    time_before = ve_test.milestones.getElement([('id', 'startTime', '==')])[u'title_text']
    skip_element = ve_test.milestones.getElement([("id", "rewind15SecButton", "==")])
    jamp_bar = ve_test.milestones.getElement([('id', 'playBackScrubberBar', '==')])

    ve_test.appium.tap_element(skip_element)
    ve_test.wait(1)
    time_after = ve_test.milestones.getElement([('id', 'startTime', '==')])[u'title_text']
    # verify rewind succeed
    logging.info('Verify rewind not succeed on event')

    delta =  datetime.strptime(time_after, '%M:%S') - datetime.strptime(time_before, '%M:%S')
    logging.info('Rewind was disabled delta is {} seconds after {} before {} delta {}'.format(delta.seconds,
                                                                   datetime.strptime(time_after, '%M:%S'),
                                                                   datetime.strptime(time_before, '%M:%S'),
                                                                   delta))
    if (delta.days >= 0) :
         logging.info('Rewind was disabled delta is {} seconds'.format(delta.seconds))
    else:
        ve_test.log_assert(False,
                                'succeded to rewind 15 seconds! rewind was {} seconds. Time before rewind: {}, time after rewind: {}'.format(
                                    delta.seconds, time_before, time_after))


    # === check skip bar ===
    logging.info("Going to ScrubberBar")
    time_before = time_after

    logging.info("Try to move ScrubberBar begining")
    ve_test.appium.tap(int(jamp_bar['x_pos']), int(jamp_bar['y_pos']))
    ve_test.screens.trick_bar.verify_active()

    ve_test.wait(1)
    time_after = ve_test.milestones.getElement([('id', 'startTime', '==')])[u'title_text']
    # verify jump succeed
    logging.info('Verify jump not succeed on event')

    delta =  datetime.strptime(time_after, '%M:%S') - datetime.strptime(time_before, '%M:%S')
    logging.info('jump was disabled delta is {} seconds after {} before {} delta {}'.format(delta.seconds,
                                                                   datetime.strptime(time_after, '%M:%S'),
                                                                   datetime.strptime(time_before, '%M:%S'),
                                                                   delta))
    if (delta.days >= 0) :
         logging.info('jump was disabled delta is {} seconds'.format(delta.seconds))
    else:
        ve_test.log_assert(False,
                                'succeded to Jump to beging! rewind was {} seconds. Time before rewind: {}, time after rewind: {}'.format(
                                    delta.seconds, time_before, time_after))
    ve_test.end()

def test_playback_pause_grade_out():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_playback_pause_grade_out")
    ve_test.begin()

    assets = ve_test.assets
    asset = assets.single_event
    asset.labels_set()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    hhid = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    #go to restricted channel
    restricted_channel_sek = ve_test.he_utils.find_blocked_channel("pauseAllowed", "sek")
    if restricted_channel_sek == None:
        logging.info('Blocked pause channel not found. Test PASS :-) ')
        ve_test.end()
        return
    ve_test.screens.zaplist.tune_to_channel_by_sek(str(restricted_channel_sek), verify_streaming_started=False)

    event_title = assets.generic_book(asset, False)
    asset.check_booking(event_title)
    ve_test.screens.library_filter.navigate_to_event(0)

    ve_test.screens.linear_action_menu.verify_active()
    logging.info("Going to play event:%s", event_title)
    play_element = ve_test.milestones.getElement([("id", "play", "==")])

    ve_test.appium.tap_element(play_element)

    pin_code = ve_test.he_utils.getParentalRatingPin(hhid)
    ve_test.wait(10)
    pin_screen = ve_test.screens.pincode
    if pin_screen.is_active():
        pin_screen.enter_pin(pin_code)
    logging.info("Verify playback on event:%s", event_title)
    ve_test.screens.playback.verify_streaming_playing()

    logging.info("Going to pause the event")
    window_width, window_height = ve_test.milestones.getWindowSize()
    ve_test.appium.tap(window_width / 2, window_height / 2)

    ve_test.wait(30)
    pause_element = ve_test.milestones.getElement([("id", "playPauseButton", "==")])
    ve_test.appium.tap_element(pause_element)
    ve_test.wait(2)

    playback_status = ve_test.milestones.getPlaybackStatus()
    state = playback_status["playbackState"]
    ve_test.log_assert(state == "PLAYING", "Playback stopped after pressing pause button")
    ve_test.end()

@pytest.mark.MF2057
def test_playback_stop_and_resume():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.headend_util import find_shortest_current_events
    from vgw_test_utils.test_utils import TestApi
    from vgw_test_utils.settings import Settings

    ve_test = VeTestApi("test_playback_stop_and_resume")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    play_duration = 30  # duration for playback in secs
    excluded_channels = [1, 4, 6, 7, 9]  # exclude series channels (4, 6) and channels with no metadata (7, 9)
    max_diff_allowed = 10000  # max dif allowed with btween the position where the playback stop and the position
                              # after resume

    abr_channels = [val['logicalChannelNumber'] for key,val in ve_test.he_utils.abr_services.iteritems() if val['logicalChannelNumber'] not in excluded_channels]
    target_events = find_shortest_current_events(channels=abr_channels)
    logger.info(target_events)
    # Work only on ABR channels
    ve_test.screens.guide.navigate()
    ve_test.screens.guide.scroll_to_channel_by_sek(target_events[0][1]['serviceEquivalenceKey'])
    current_event = ve_test.screens.guide.CurrentCenteredChannelActionMenu()
    event_title = current_event['title_text']

    # Record the current event and verify booking
    event = ve_test.screens.linear_action_menu.record_current_event(event_title)
    ve_test.wait(5) # lets wait to avoid from race condition - as there some cases filters are still not include the event

    # Wait until EGT
    TestApi.step("Wait until event is ended")
    event_end_time = int((event['content']['broadcastDateTime'] + event['content']['duration']) / 1000) - int(time.time())
    TestApi.step("Going to wait:%d sec (+30) until the end of event recording" % (event_end_time))
    time.sleep(event_end_time + 30)

    # check event is recording
    ve_test.he_utils.wait_for_recording_status(event_title, status='RECORDING')

    def play_event():
        # Go to Recording filter and start playback
        TestApi.step("Go to library filter:%s expected to find event:%s" % (event_title, FilterType.RECORDINGS))
        ve_test.screens.library_filter.navigate()
        ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.RECORDINGS)
        ve_test.screens.full_content_screen.tap_event_by_title(event_title)
        ve_test.screens.linear_action_menu.verify_active()

        TestApi.step("Going to play event:%s" % event_title)
        play_element = ve_test.milestones.getElement([("id", "actions_menu_play_button", "==")])
        ve_test.appium.tap_element(play_element)
        TestApi.step("Verify playback on event:%s" % event_title)
        ve_test.screens.playback.verify_streaming_playing(verify_position=True)

    play_event()
    TestApi.step('play for %s secs' % play_duration)
    time.sleep(play_duration)
    play_position = ve_test.milestones.getPlaybackStatus()['playbackBufferCurrent']

    # Stop playback
    ve_test.screens.playback.stop_playback()

    TestApi.step('start playback again')
    play_event()
    new_play_position = ve_test.milestones.getPlaybackStatus()['playbackBufferCurrent']
    TestApi.step('play_position: %s, new_play_position: %s' % (play_position, new_play_position))
    assert abs(new_play_position - play_position) < max_diff_allowed

    TestApi.step("Going to stop playback event:%s" % event_title)
    ve_test.screens.playback.stop_playback()

    ve_test.end()


@pytest.mark.MF2057
def test_trickmodes_pause():
    test = VeTestApi('test_trickmodes_pause')
    if test.platform != "iOS":
        pytest.skip('add milestones to android (DE8270)!')
    assets = test.assets
    asset = assets.single_event
    test.begin()
    asset.labels_set()
    assets.grid_check(asset)

    Settings['household_id'] = test.configuration['he']['generated_household']
    upmDeviceId = test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings['device_id'] = upmDeviceId

    test.screens.full_content_screen.tap_event_by_title(asset.title)
    test.screens.linear_action_menu.verify_active()

    # record 30 seconds
    test.wait(30)

    # delete and verify notification, press YES on stop recording confirmation screen
    test.screens.linear_action_menu.verify_and_press_stop_button()
    test.screens.notification.verify_notification_message(NotificationStrings.STOP_RECORDING.value)
    test.screens.notification.get_and_tap_notification_button('DIC_YES')

    # in iOS should refresh
    test.he_utils.wait_for_recording_status(asset.title, status='RECORDED')
    test.screens.library_filter.go_to_previous_screen()
    test.screens.full_content_screen.tap_event_by_title(asset.title)
    test.screens.linear_action_menu.verify_active()

    # verify that action has updated to "DELETE RECORDING"
    test.ui.verify_button(test.screens.linear_action_menu.button_type.DELETE, True, 10)

    # Press play and verify playback
    logging.info("Going to play event: {}".format(asset.title))
    test.screens.pvr_action_menu.play_asset()

    # Press pause and verify paused
    logging.info("Going to pause event: {}".format(asset.title))
    test.screens.playback.pause_playback()

    test.end()


@pytest.mark.MF2057
def test_trickmodes_rewind():
    test = VeTestApi('test_trickmodes_rewind')
    if test.platform != 'iOS':
        pytest.skip('add milestones to android (DE8270)!')
    assets = test.assets
    asset = assets.single_event
    time = 15
    test.begin()
    asset.labels_set()
    assets.grid_check(asset)

    Settings['household_id'] = test.configuration['he']['generated_household']
    upmDeviceId = test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings['device_id'] = upmDeviceId

    test.screens.full_content_screen.tap_event_by_title(asset.title)
    test.screens.linear_action_menu.verify_active()

    # record 15 seconds
    test.wait(time)

    # delete and verify notification, press YES on stop recording confirmation screen
    test.screens.linear_action_menu.verify_and_press_stop_button()
    test.screens.notification.verify_notification_message(NotificationStrings.STOP_RECORDING.value)
    test.screens.notification.get_and_tap_notification_button('DIC_YES')

    # in iOS should refresh
    test.he_utils.wait_for_recording_status(asset.title, status='RECORDED')
    test.screens.library_filter.go_to_previous_screen()
    test.screens.full_content_screen.tap_event_by_title(asset.title)
    test.screens.linear_action_menu.verify_active()

    # verify that action has updated to "DELETE RECORDING"
    test.ui.verify_button(test.screens.linear_action_menu.button_type.DELETE, True, 10)

    # Press play and verify playback
    logging.info('Going to play event: {}'.format(asset.title))
    test.screens.pvr_action_menu.play_asset()

    # play 15 seconds
    test.wait(time)

    # rewind and take time before and after
    logging.info('Going to rewind event: {}'.format(asset.title))
    test.screens.playback.rewind_playback()

    test.end()


@pytest.mark.MF2057
def test_trickmodes_jump():
    test = VeTestApi('test_trickmodes_jump')
    if test.platform != 'iOS':
        pytest.skip('add milestones to android (DE8270)!')
    assets = test.assets
    asset = assets.single_event
    time = 30
    test.begin()
    asset.labels_set()
    assets.grid_check(asset)

    Settings['household_id'] = test.configuration['he']['generated_household']
    upmDeviceId = test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings['device_id'] = upmDeviceId

    test.screens.full_content_screen.tap_event_by_title(asset.title)
    test.screens.linear_action_menu.verify_active()

    # record 30 seconds
    test.wait(time)

    # delete and verify notification, press YES on stop recording confirmation screen
    test.screens.linear_action_menu.verify_and_press_stop_button()
    test.screens.notification.verify_notification_message(NotificationStrings.STOP_RECORDING.value)
    test.screens.notification.get_and_tap_notification_button('DIC_YES')

    # in iOS should refresh
    test.he_utils.wait_for_recording_status(asset.title, status='RECORDED')
    test.screens.library_filter.go_to_previous_screen()
    test.screens.full_content_screen.tap_event_by_title(asset.title)
    test.screens.linear_action_menu.verify_active()

    # verify that action has updated to "DELETE RECORDING"
    test.ui.verify_button(test.screens.linear_action_menu.button_type.DELETE, True, 10)

    # Press play and verify playback
    logging.info("Going to play event: {}".format(asset.title))
    test.screens.pvr_action_menu.play_asset()

    # play 30 seconds
    test.wait(time)

    # jump and take time before and after
    logging.info('Going to jump on event: {}'.format(asset.title))
    test.screens.playback.jump_playback()

    test.end()


@pytest.mark.MF2057
@pytest.mark.DE7838
def test_playback_EOF():
    """
    Test EOF case while playing.
    If EOF arrived app should navigate to the previous screen
    Schenario:
    1. record current event from guide
    2. wait some time (20sec) and stop the recording
    3. play the event from library until the end of it
    Expected result:
        in the end of the playback we navigate to a different screen (currently we are going to Action Menu)
    """

    # vgw test utils must be installed for running this test
    from vgw_test_utils.test_utils import TestApi
    from vgw_test_utils.settings import Settings

    ve_test = VeTestApi("test_playback_stop_and_resume")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    play_duration = 20  # duration for playback in secs

    # Record the current event and verify booking
    # Work only on ABR channels
    target_channel_id = ve_test.he_utils.get_channel_to_record_current_event(remaining_time_minutes=4, ignor_series=True)
    print "target_channel_id: ", target_channel_id

    # Navigate to current event and start the recording
    TestApi.step("Book current event")
    event_title = ve_test.screens.guide.navigateToCurrentEventOnChannel(target_channel_id)
    ve_test.screens.linear_action_menu.record_current_event(event_title)

    # check event is recording
    TestApi.step("Wait for for recording to start. title%s" % event_title)
    ve_test.he_utils.wait_for_recording_status(event_title)

    # Give some meet to the recording
    TestApi.step("Wait for %s seconds in order to give some meet to the recording." % str(play_duration))
    ve_test.wait(play_duration) # lets wait to avoid from race condition - as there some cases filters are still not include the event

    # Stop recording
    TestApi.step("Stop the recording")
    stop_ongoing_recording(ve_test, event_title)

    # check event is been recorded
    ve_test.he_utils.wait_for_recording_status(event_title, status='RECORDED')

    # Go to Recording filter and start playback
    TestApi.step("Go to library filter:%s expected to find event:%s" % (event_title, FilterType.RECORDINGS))
    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.RECORDINGS)
    ve_test.screens.full_content_screen.tap_event_by_title(event_title)
    ve_test.screens.linear_action_menu.verify_active()

    TestApi.step("Going to play event:%s" % event_title)
    play_element = ve_test.milestones.getElement([("id", "actions_menu_play_button", "==")])
    ve_test.appium.tap_element(play_element)
    TestApi.step("Verify playback on event:%s" % event_title)
    ve_test.screens.playback.verify_streaming_playing(verify_position=True)

    # keep the playback screen name
    orig_screen = ve_test.milestones.get_current_screen()

    # Play untill the end and check we change screen when EOF
    TestApi.step('play for %s secs' % str(play_duration+5))
    time.sleep(play_duration+5)  # add some delta in order to overcome some inaccurate duration
    TestApi.step("Wait for screen to be changed. current screen:%s" % orig_screen)
    ve_test.screens.wait_for_screen(orig_screen, is_match=False)

    ve_test.end()

