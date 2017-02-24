__author__ = 'dshalev'

import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.pincode import YouthChanneltype
from tests_framework.ui_building_blocks.KD.pincode import PinCodescreen
from tests_framework.he_utils.he_utils import VodContentType


' Global constants '
TIMEOUT = 3
INVALID_PIN_CODE = "5050"
GRACE_TIME = 600

THRESHOLD = str(PinCodescreen.YOUTH_LIMIT_RATING)

# --------------------------- UTILS --------------------------


def get_time_left_till_end_of_event(ve_test, event):
    start_time_utc = ve_test.ctap_data_provider.get_event_time_utc(event['startDateTime'])
    now = ve_test.ctap_data_provider.ve_test.appium.get_device_time() * 1000 #UTC timestamp in mili
    logging.info("now: %d, event start time: %d, duration=%d "%(now, start_time_utc, event['duration']))
    time_till_event_end = (event['duration'] -(now - start_time_utc)) / 1000 #return time in seconds
    return time_till_event_end


def get_alternately_yp_cur_event(test, alternately_yp_channel_id):
    cur_event = test.ctap_data_provider.get_current_event_by_id(alternately_yp_channel_id)
    time_till_event_end = get_time_left_till_end_of_event(test, cur_event)
    "to avoide event change before the test is ready"
    if time_till_event_end < 30 :
        test.wait(30 + 10)
    cur_event = test.ctap_data_provider.get_current_event_by_id(alternately_yp_channel_id)
    return cur_event


def event_change_parental_validation(test, cur_event):
    if test.screens.pincode.is_youth_event(cur_event):
        logging.info("event change from LOCK->UNLOCK")
        test.screens.fullscreen.tap_unlock_program()
        time_till_event_end = get_time_left_till_end_of_event(test, cur_event)
        test.wait(time_till_event_end + 20)
        test.log_assert(test.screens.fullscreen.is_program_locked() == False, "Unlock button was not dismiss after event change from lock to unlock")
        test.log_assert(test.screens.playback.is_video_hidden() == False, "Video Is Hidden after event change from lock to unlock")
    else:
        logging.info("event change from UNLOCK->LOCK")
        time_till_event_end = get_time_left_till_end_of_event(test, cur_event)
        test.wait(time_till_event_end + 20)
        test.log_assert(test.screens.fullscreen.is_program_locked(), "Unlock button is not showing after event change from unlock to lock")
        test.log_assert(test.screens.playback.is_video_hidden() == True, "Video Is not Hidden after event change from lock to unlock")


def get_evet_after_grace_time_over(ve_test, grace_start_time, channel_id):
    data = ve_test.ctap_data_provider.send_request("GRID", None)
    schedule = None
    event_after = None

    for channel in data["channels"]:
        if str(channel["id"]).strip()== str(channel_id).strip():
            schedule = channel["schedule"]
            break

    if schedule is None:
        logging.log("no schedule found for channel %d", channel_id)
        return None

    grace_time_pass = grace_start_time + GRACE_TIME * 1000

    for event in schedule:
        if event['startDateTime'] > grace_time_pass and ve_test.screens.pincode.is_youth_event(event):
            start_time = ve_test.ctap_data_provider.get_event_time_utc(event['startDateTime'])
            logging.info('desired event found, grace start time: {0}, grace time: {1}, event start time: {2}'.format(grace_start_time, GRACE_TIME*1000, start_time))
            event_after = event
            break

    return event_after


def navigate_to_locked_vod_asset(ve_test):
    search = ve_test.screens.search
    full_content = ve_test.screens.full_content_screen

    high_rated_vod = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.HIGH_RATED])

    logging.info("asset: {0}".format(high_rated_vod))
    asset_title = high_rated_vod['title']
    ve_test.screens.tv_filter.navigate()

    search.navigate()
    logging.info("searching for vod asset named {0}".format(asset_title))
    search.input_event_into_search_filed_and_search(asset_title)
    if ve_test.platform == "Android":
        search.navigate_to_action_menu_by_event_title(asset_title)
    else:
        full_content.tap_event_by_title(asset_title)
    ve_test.wait(2)

def navigate_to_low_rated_vod_asset(ve_test):

    search = ve_test.screens.search
    full_content = ve_test.screens.full_content_screen

    asset = ve_test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.LOW_RATED, VodContentType.NON_EROTIC])

    logging.info("asset: {0}".format(asset))
    asset_title = asset['title']
    search.navigate()
    logging.info("searching for vod asset named {0}".format(asset_title))
    search.input_event_into_search_filed_and_search(asset_title)
    ve_test.wait(4)
    if ve_test.platform == "Android":
        search.navigate_to_action_menu_by_event_title(asset_title)
    else:
        full_content.tap_event_by_title(asset_title)
    ve_test.wait(2)

def set_parental_rating_threshold(ve_test, threshold=THRESHOLD):
    credentials= ve_test.he_utils.get_default_credentials()
    ve_test.he_utils.setParentalRatingThreshold(credentials[0], threshold)
    hhId = ve_test.configuration["he"]["generated_household"]
    ve_test.he_utils.setTenantValue(hhId, 'k')


def tune_to_open_channel_and_verify_playing(ve_test, youth_channel_type = YouthChanneltype.CURRENT_EVENT_LOW_RATED):
    pincode = ve_test.screens.pincode
    channel = pincode.get_youth_channel(youth_channel_type)
    if channel is None:
        logging.error("couldn't find low rated linear channel")
        return False
    logging.info("found open channel: %s", channel)
    ve_test.screens.zaplist.tune_to_channel_by_sek(channel,False)
    ve_test.wait(TIMEOUT)
    if ve_test.screens.playback.is_video_hidden():
        logging.error("video is hidden")
        return False
    return True


def tune_to_locked_channel_linear(ve_test, youth_channel_type = YouthChanneltype.CURRENT_EVENT_PROTECTED, verify_hidden = True):
    pincode = ve_test.screens.pincode
    channel = pincode.get_youth_channel(youth_channel_type)
    if channel is None:
        logging.error("couldn't find channel with {0} high rated event/s".format(youth_channel_type))
        return None
    logging.info("found channel with {0} high rated event/s, channel id: {1}".format(youth_channel_type, channel))
    ve_test.screens.zaplist.tune_to_channel_by_sek(channel,False)
    ve_test.wait(TIMEOUT)
    if verify_hidden and not ve_test.screens.playback.is_video_hidden():
        logging.error("video isn't hidden")
        return None
    return channel


def raise_and_verify_pin_screen_linear(ve_test):

    elements = ve_test.milestones.getElements()
    unlock_program = ve_test.screens.pincode.get_unlock_dic_value()
    unlock = ve_test.milestones.getElement([("title_text",unlock_program , "==")], elements)
    if unlock is None:
        logging.error("No unlock button!")
        return False
    logging.info("Unlock button found")
    ve_test.wait(TIMEOUT)
    ve_test.appium.tap_element(unlock)

    "Pin screen appears"
    ve_test.screens.pincode.verify_active()
    logging.info("video is hidden as expected")

    return True


def raise_and_verify_pin_screen_vod(ve_test):

    ve_test.screens.vod_action_menu.play_asset(verify_streaming=False)
    ve_test.wait(3)
    ve_test.screens.playback.verify_streaming_paused()
    ve_test.wait(TIMEOUT)
    elements = ve_test.milestones.getElements()
    screen_name = ve_test.milestones.get_current_screen(elements)
    if screen_name == "fullscreen":
        ve_test.ui.tap_localized_label("DIC_INFO_LAYER_UNLOCK")
    "Pin screen appears"
    ve_test.screens.pincode.verify_active()

    return True


def verify_pin_blocked(ve_test):
    pincode = ve_test.screens.pincode
    pin_exhaust_msg =  ve_test.milestones.get_dic_value_by_key("DIC_PIN_CODE_INVALID_BLOCKED")
    value_time_left = pincode.get_ctap_blocking_timeout()
    if(int(value_time_left)/60 == 0):
        time_left = int(value_time_left)/60
    else:
        time_left = int(value_time_left)/60 + 1
    pin_exhaust_msg = pin_exhaust_msg.replace("%1$s",str(time_left))
    element = ve_test.milestones.getElement([('title_text', pin_exhaust_msg, '==')])
    return element is not None


# --------------------------- TESTS ---------------------------


@pytest.mark.MF1893_Pin_Required_Linear
@pytest.mark.MF1893_Parental_Pin_export_regression
def test_pin_required_linear():
    ve_test = VeTestApi("test_pin_required")
    pincode = ve_test.screens.pincode

    ve_test.begin()
    set_parental_rating_threshold(ve_test)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    ve_test.log_assert(tune_to_open_channel_and_verify_playing(ve_test), "Failed while trying to tune to open channel")
    ve_test.log_assert(tune_to_locked_channel_linear(ve_test), "Failed while trying to tune to locked channel")
    ve_test.log_assert(raise_and_verify_pin_screen_linear(ve_test), "Failed while trying to raise pin screen")
    pincode.enter_pin()
    ve_test.wait(2)

    "verify if the content is playing"
    ve_test.log_assert(not ve_test.screens.infolayer.is_program_locked(), "Unlock button is showing after entering correct pin")
    ve_test.log_assert(not ve_test.screens.playback.is_video_hidden() == True, "Video Is Hidden after entering correct pin")

    logging.info('End test_pin_required')
    ve_test.end()


@pytest.mark.MF1893_Retry_Exhaust_Linear
@pytest.mark.MF1893_Parental_Pin_export_regression
def test_retry_exhaust_linear():
    ve_test = VeTestApi("test_retry_exhaust")
    pincode = ve_test.screens.pincode
    ve_test.begin()
    set_parental_rating_threshold(ve_test)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    ve_test.log_assert(tune_to_locked_channel_linear(ve_test), "Failed while trying to tune to locked channel")
    ve_test.log_assert(raise_and_verify_pin_screen_linear(ve_test), "Failed while trying to raise pin screen")

    for i in range(0,3):
        ve_test.wait(TIMEOUT)
        pincode.enter_pin(INVALID_PIN_CODE)

    logging.info("3 TIMES WRONG PIN ENTRY FINISHED")
    ve_test.wait(TIMEOUT)

    "verify if pin entry is disabled after 3 retries"
    """ve_test.log_assert(verify_pin_blocked(ve_test), "User Blocked notification was not found!")"""


    ve_test.screens.notification.dismiss()
    raise_and_verify_pin_screen_linear(ve_test)
    ve_test.wait(2)
    ve_test.log_assert(verify_pin_blocked(ve_test), "User Blocked notification was not found!")

    
    logging.info('End test_retry_exhaust')
    ve_test.end()


@pytest.mark.MF1893_Block_Time_Passed
def test_block_time_passed():
    ve_test = VeTestApi("test_block_time_passed")
    pincode = ve_test.screens.pincode
    notification = ve_test.screens.notification
    ve_test.begin()
    set_parental_rating_threshold(ve_test)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    ve_test.log_assert(tune_to_locked_channel_linear(ve_test), "Failed while trying to tune to locked channel")
    ve_test.log_assert(raise_and_verify_pin_screen_linear(ve_test), "Failed while trying to raise pin screen")

    for i in range(0,3):
        ve_test.wait(TIMEOUT)
        pincode.enter_pin(INVALID_PIN_CODE)

    logging.info("3 TIMES WRONG PIN ENTRY FINISHED")
    ve_test.wait(1)

    "verify if pin entry is disabled after 3 retries"
    verify_pin_blocked(ve_test)
    notification.dismiss()
    time_to_sleep = pincode.get_ctap_blocking_timeout() + 5
    logging.info("going to sleep for {0} seconds, waiting that block time will pass".format(time_to_sleep))
    ve_test.wait(time_to_sleep)

    logging.info("block time passed, trying to unlock")
    ve_test.log_assert(raise_and_verify_pin_screen_linear(ve_test), "Failed while trying to raise pin screen")
    pincode.enter_pin()
    "verify if the content is playing"
    ve_test.log_assert(not ve_test.screens.playback.is_video_hidden(), "Video is still hidden!")
    ve_test.screens.playback.verify_streaming_playing()

    logging.info('End test_block_time_passed')
    ve_test.end()


@pytest.mark.MF1893_Event_Boundary_Transitions
@pytest.mark.MF1893_Parental_Pin_export_regression
def test_event_boundary_transitions():
    ve_test = VeTestApi("test_pincode_test_event_boundary")
    playback = ve_test.screens.playback
    fullscreen = ve_test.screens.fullscreen
    ve_test.begin()

    set_parental_rating_threshold(ve_test)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    "Tune to alternately youth channel"
    alternately_channel = tune_to_locked_channel_linear(ve_test, YouthChanneltype.ALTERNATELY_EVENTS_PROTECTED, verify_hidden=False)

    "verify event change from [lock->unlock, unlock->lock]"
    cur_event = get_alternately_yp_cur_event(ve_test, alternately_channel)
    event_change_parental_validation(ve_test, cur_event)
    cur_event = get_alternately_yp_cur_event(ve_test, alternately_channel)
    event_change_parental_validation(ve_test, cur_event)

    "Tune to youth channel"
    protected_channel = tune_to_locked_channel_linear(ve_test, YouthChanneltype.ALL_EVENTS_PROTECTED)

    "verify event change from lock->lock"
    logging.info("event change from LOCK->LOCK")
    fullscreen.tap_unlock_program()
    cur_event = ve_test.ctap_data_provider.get_current_event_by_id(protected_channel)
    time_till_event_end = get_time_left_till_end_of_event(ve_test, cur_event)
    ve_test.wait(time_till_event_end + 20)
    ve_test.log_assert(fullscreen.is_program_locked(), "Unlock button is not showing after event change from lock to lock")
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden after event change from lock to lock")

    ve_test.end()


@pytest.mark.MF1893_Event_Boundary_With_Grace_Time_Linear
@pytest.mark.MF1893_Parental_Pin_export_regression
def test_event_boundary_with_grace_time():
    ve_test = VeTestApi("test_event_boundary_with_grace_time")
    playback = ve_test.screens.playback
    fullscreen = ve_test.screens.fullscreen
    event_remain_time = 300
    ve_test.begin()


    set_parental_rating_threshold(ve_test)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    "Tune to youth channel"
    protected_channel = tune_to_locked_channel_linear(ve_test, YouthChanneltype.ALL_EVENTS_PROTECTED)
    cur_event = ve_test.ctap_data_provider.get_current_event_by_id(protected_channel)
    time_till_event_end = get_time_left_till_end_of_event(ve_test, cur_event)
    if time_till_event_end > 300:
        logging.info('going to sleep for {} seconds, waiting for event to reach 5 minutes from the end'.format(time_till_event_end - event_remain_time))
        ve_test.wait(time_till_event_end - event_remain_time)
        time_till_event_end = event_remain_time

    raise_and_verify_pin_screen_linear(ve_test)
    ve_test.screens.pincode.enter_pin()
    ve_test.wait(2)
    ve_test.log_assert(not fullscreen.is_program_locked(), "Unlock button is showing after event change from lock to lock after correct pin entered")
    ve_test.log_assert(not playback.is_video_hidden() == True, "Video Is Hidden after event change from lock to lock after correct pin entered")
    logging.info("event is not locked after correct pin entered, as expected")
    grace_start_time = ve_test.ctap_data_provider.ve_test.appium.get_device_time() * 1000
    ve_test.wait(time_till_event_end + 10)

    # TODO remove code when channel stream is fixed --------------
    logging.info("changing channel up and down - to recover from stuck stream on channel")
    from tests_framework.ui_building_blocks.screen import ScreenActions
    fullscreen.channel_change(direction=ScreenActions.DOWN)
    ve_test.wait(2)
    fullscreen.channel_change(direction=ScreenActions.UP)
    ve_test.wait(2)
    # remove the above lines --------------------

    ve_test.log_assert(not fullscreen.is_program_locked(), "Unlock button is showing after event change from lock to lock after correct pin entered")
    ve_test.log_assert(not playback.is_video_hidden() == True, "Video Is Hidden after event change from lock to lock after correct pin entered")
    event_after = get_evet_after_grace_time_over(ve_test, grace_start_time, protected_channel)
    logging.info("event changed, not locked due to grace time as expected")
    now = ve_test.ctap_data_provider.ve_test.appium.get_device_time() * 1000
    event_end_time = ve_test.ctap_data_provider.get_event_time_utc(event_after['startDateTime']) + event_after["duration"]
    time_to_sleep = (event_end_time - now)/1000 - 20
    logging.info("event after grace time is approching, sleeping for {} seconds, 20 sec before it starts".format(time_to_sleep))
    ve_test.wait(time_to_sleep)

    # TODO remove code when channel stream is fixed ------------
    logging.info("changing channel up and down - to recover from stuck stream on channel")
    fullscreen.channel_change(direction=ScreenActions.DOWN)
    ve_test.wait(2)
    fullscreen.channel_change(direction=ScreenActions.UP)
    ve_test.wait(20)
    # remove the above lines ------------

    ve_test.log_assert(fullscreen.is_program_locked(), "Unlock button is not showing after event change from lock to lock")
    ve_test.log_assert(playback.is_video_hidden() == True, "Video Is not Hidden after event change from lock to lock")

    ve_test.end()


@pytest.mark.MF1893_Pin_Required_VOD
@pytest.mark.MF1893_Parental_Pin_export_regression
def test_pin_required_vod():
    ve_test = VeTestApi("test_pin_required_vod")
    pincode = ve_test.screens.pincode
    ve_test.begin()
    
    set_parental_rating_threshold(ve_test)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    " playing low rated vod asset"
    navigate_to_low_rated_vod_asset(ve_test)
    ve_test.wait(2)
    ve_test.screens.vod_action_menu.play_asset()
    ve_test.wait(2)
    ve_test.screens.trick_bar.navigate()
    ve_test.wait(2)
    ve_test.screens.search.navigate()
    ve_test.wait(2)
    " playing pin protected VOD asset"
    navigate_to_locked_vod_asset(ve_test)
    ve_test.wait(2)
    ve_test.log_assert(raise_and_verify_pin_screen_vod(ve_test), "Failed while trying to raise pin screen")
    pincode.enter_pin()
    ve_test.wait(3)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()


@pytest.mark.MF1893_Retry_Exhaust_VOD
@pytest.mark.MF1893_Parental_Pin_export_regression
def test_retry_exhaust_vod():
    ve_test = VeTestApi("test_retry_exhaust_vod")
    pincode = ve_test.screens.pincode
    ve_test.begin()
    set_parental_rating_threshold(ve_test)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    navigate_to_locked_vod_asset(ve_test)
    ve_test.screens.vod_action_menu.play_asset(verify_streaming=False, verify_fullscreen=False)
    
    elements = ve_test.milestones.getElements()
    screen_name = ve_test.milestones.get_current_screen(elements)
    if screen_name == "fullscreen":
        logging.info("tapping cancel")
        ve_test.ui.tap_localized_label("DIC_INFO_LAYER_UNLOCK")
    
    for i in range(0,3):
        ve_test.wait(TIMEOUT)
        pincode.enter_pin(INVALID_PIN_CODE)

    logging.info("3 TIMES WRONG PIN ENTRY FINISHED")
    ve_test.wait(TIMEOUT)

    "verify if pin entry is disabled after 3 retries"
    ve_test.log_assert(verify_pin_blocked(ve_test), "User Blocked notification was not found!")

    ve_test.screens.notification.dismiss()
    ve_test.screens.vod_action_menu.play_asset(verify_streaming=False, verify_fullscreen=False)
    ve_test.wait(2)
    ve_test.log_assert(verify_pin_blocked(ve_test), "User Blocked notification was not found!")

    ve_test.end()


@pytest.mark.MF1893_Grace_Time_Vod_To_Linear
@pytest.mark.MF1893_Parental_Pin_export_regression
def test_grace_time_vod_to_linear():
    ve_test = VeTestApi("test_grace_time_vod_to_linear")
    pincode = ve_test.screens.pincode
    tv_filter = ve_test.screens.tv_filter
    ve_test.begin()
    set_parental_rating_threshold(ve_test)
    
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    " playing pin protected VOD asset"
    navigate_to_locked_vod_asset(ve_test)
    ve_test.wait(2)
    ve_test.log_assert(raise_and_verify_pin_screen_vod(ve_test), "Failed while trying to raise pin screen")
    pincode.enter_pin()
    ve_test.wait(3)
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.screens.playback.stop_playback()

    tv_filter.navigate()
    ve_test.wait(2)
    tune_to_locked_channel_linear(ve_test, verify_hidden=False)
    ve_test.wait(2)
    ve_test.log_assert(not ve_test.screens.fullscreen.is_program_locked(), "Unlock button is showing after tuning to high rated event while in grace time")
    ve_test.log_assert(not ve_test.screens.playback.is_video_hidden() == True, "Video Is Hidden after tuning to high rated event while in grace time")

    ve_test.end()


@pytest.mark.MF1893_Grace_Time_Linear_To_Vod
@pytest.mark.MF1893_Parental_Pin_export_regression
def test_grace_time_linear_to_vod():
    ve_test = VeTestApi("test_grace_time_linear_to_vod")
    pincode = ve_test.screens.pincode
    ve_test.begin()
    set_parental_rating_threshold(ve_test)
    " relaunch app so new parental threshold will be cached"
    ve_test.appium.restart_app()
    ve_test.screens.tv_filter.verify_active()
    ve_test.log_assert(tune_to_locked_channel_linear(ve_test), "Failed while trying to tune to locked channel")
    ve_test.log_assert(raise_and_verify_pin_screen_linear(ve_test), "Failed while trying to raise pin screen")
    pincode.enter_pin()
    ve_test.wait(2)

    "verify if the content is playing"
    ve_test.log_assert(not ve_test.screens.fullscreen.is_program_locked(), "Unlock button is showing after entering correct pin")
    ve_test.log_assert(not ve_test.screens.playback.is_video_hidden() == True, "Video Is Hidden after entering correct pin")

    navigate_to_locked_vod_asset(ve_test)
    ve_test.screens.vod_action_menu.play_asset()
    ve_test.wait(2)

    logging.info('End test_grace_time_linear_to_vod')
    ve_test.end()