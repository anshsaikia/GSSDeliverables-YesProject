import pytest
import logging
import random
import json


from tests_framework.ui_building_blocks.K.library_filter import FilterType
from tests_framework.ui_building_blocks.KD.notification import NotificationStrings

from vgw_test_utils.headend_util import get_all_catalog

from tests_framework.ve_tests.ve_test import VeTestApi

MAX_CONCURENCY_SESSIONS = 2


defaultSetupParamsPlayback = {
    'deviceId':'2222',
    'contentType':'CDVR',
    'contentIdType':'RECORDING_ID',
    'contentId':'programid://536870914~programid://1073741845',
    'catalogId' : '2000',
    'householdId' : 'HH'
}

defaultIdentity = {"cmdcRegion":"16384~16385","upId":"2_HH_0","hhId":"2_HH","devId":"619FDF82A2E5FF35","deviceFeatures":["COMPANION","ABR"],"tenant":"k","sessionId":"158f4a2d-e84e-404e-8e63-04a69aa2ad68","region":"1"}
smHeaders = {'Content-Type': 'application/json',
    'X-Forwarded-For': '110.78.131.21'
}


def test_osd_on_auth_error():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_osd_on_auth_error")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    # Work only on ABR channels
    target_channel_id = ve_test.he_utils.get_channel_to_record_current_event()

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
    
    # verify and press YES on stop recording confirmation screen
    ve_test.screens.notification.verify_notification_message(NotificationStrings.STOP_RECORDING.value)
    ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

    #verify that action has updated to "DELETE RECORDING"
    ve_test.ui.verify_button(ve_test.screens.linear_action_menu.button_type.DELETE, True, 10)
    
    #remove subscription to HH
    ve_test.he_utils.deleteSubscriptionUsingUpm(Settings['household_id'])
    
    #verify playback fails
    logging.info("Going to play event:%s", event_title)
    play_element = ve_test.milestones.getElement([("id", "actions_menu_play_button", "==")])
    ve_test.appium.tap_element(play_element)
    logging.info("Verify playback Error on event:%s", event_title)
    ve_test.screens.notification.verify_notification_message(NotificationStrings.AUTH_ERROR.value)
    ve_test.end()

'''
#add it to headend_util.py
def get_planner(self, filter=None):
    url = 'http://{agr_address}:{agr_port}/ctap/{ref_api_version}/agg/library/planner'.format(**Settings)
    if filter:
        url += ("?%s" % filter)
    res = self.session.get(url)
    return res.json()'''

def streaming_session_setup( contentId, HHid=None, deviceId=None,ve_test = None):


    he_utils = ve_test.he_utils

    url = he_utils.PrmUrl + he_utils.StreamingSessionPath
    setupParams = dict(defaultSetupParamsPlayback)

    setupParams["contentId"] = contentId
    setupParams["householdId"] = HHid
    setupParams["deviceId"] = deviceId

    defaultIdentity['hhId'] = HHid
    defaultIdentity['devId'] = deviceId

    smHeaders['x-cisco-vcs-identity'] = json.dumps(defaultIdentity)

    jData = json.dumps(setupParams, indent = 2)
    r = ve_test.requests.post(url, data = jData, headers=smHeaders)

    return r


def test_osd_on_concurency_error():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_osd_on_concurency_error")
    ve_test.begin()
    assets = ve_test.assets
    asset = assets.single_event
    asset.labels_set()
    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    logging.info(" ve_test.platform   ---------> %s" ,ve_test.platform)

    # Work only on ABR channels
    logging.info('get info from Tanent')
    tuned_channel, channel_prop = ve_test.he_utils.getLinearContentABR('clear')
    logging.info("the tuned channel is: %s",str(tuned_channel))

    #ve_test.screens.zaplist.tune_to_channel_by_sek(str(tuned_channel), verify_streaming_started=False)
    ve_test.screens.zaplist.tune_to_channel_by_sek(str(51), verify_streaming_started=False)
    
    event_title = assets.generic_book(asset, False)
    if ve_test.platform == "Android":
        ve_test.ui.wait_for_label("CANCEL BOOKING")

    ve_test.wait(60) # wait to asset to appear in library screen

    # Go to Recording filter and stop recording
    logging.info("Go to library filter:%s expected to find event:%s", event_title, FilterType.RECORDINGS)
    ve_test.screens.library_filter.navigate()
    ve_test.screens.library_filter.navigate_to_manage_recording_filter(FilterType.RECORDINGS)


    ve_test.screens.full_content_screen.tap_event_by_title(event_title)
    ve_test.screens.linear_action_menu.verify_active()
    ve_test.screens.linear_action_menu.verify_and_press_stop_button()

    # verify and press YES on stop recording confirmation screen
    ve_test.screens.notification.verify_notification_message(NotificationStrings.STOP_RECORDING.value)
    ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

    catalog = get_all_catalog()

    contentId = catalog[0]['contentPlayUri']
    sessionIds = []

    for i in range(0,MAX_CONCURENCY_SESSIONS):
        deviceId = str(random.randint(100, 10000))
        ve_test.he_utils.addHouseHoldDevices(Settings['household_id'], [deviceId], deviceFullType="Android-Phone",drmDeviceType = None)
        logging.info('Sending streaming session setup request on device %s  maxApcSessions=%s' %(deviceId,MAX_CONCURENCY_SESSIONS))
        r = streaming_session_setup(contentId, HHid =Settings['household_id'] ,deviceId=deviceId,ve_test = ve_test)
        ve_test.log_assert(r.status_code == 200, ' Post request for streaming session failed')
        response = json.loads(r.text)

        sessionId=response['streamingSession']['smSessionId']
        sessionIds.append(sessionId)

    logging.info("Going to play event:%s", event_title)
    play_element = ve_test.milestones.getElement([("id", "play", "==")])
    ve_test.appium.tap_element(play_element)
    logging.info("Verify playback Error on event:%s", event_title)
    ve_test.screens.notification.verify_notification_message(NotificationStrings.DIC_ERROR_PLAYBACK_CONCURRENCY.value)
    logging.info("test passed with osd : %s", NotificationStrings.DIC_ERROR_PLAYBACK_CONCURRENCY.value)

    # close play session

    ve_test.end()