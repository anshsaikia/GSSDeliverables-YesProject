__author__ = 'nbriskin'
import pytest
import random
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

def get_recordable_ev(ve_test):

    booking_recording = ve_test.screens.booking_recording
    playback = ve_test.screens.playback
    zaplist = ve_test.screens.zaplist
    event_wRec = None

    zaplist.navigate()
    for j in xrange(15):
        elements = ve_test.milestones.getElements()
        event_id = ve_test.ctap_data_provider.get_event_id(elements)
        if booking_recording.is_event_recordable(event_id) and not booking_recording.is_event_booked(event_id):
            event_wRec = event_id
            ve_test.log("event id is" + event_wRec)
            break
        else:
            zaplist.scroll_channels(1)
            current_channel =  zaplist.get_centered_event_view(ve_test.milestones.getElements())
            channel_id = current_channel['channel_id']
            while not playback.isChannelPlayable(channel_id):
                non_current_channel = zaplist.get_next_event(current_channel)
                channel_id = non_current_channel['channel_id']

    if(event_wRec):
        current_channel =  zaplist.get_centered_event_view(ve_test.milestones.getElements())
        channel_id = current_channel['channel_id']
        zaplist.tune_to_channel_by_sek(channel_id, False)
    return event_wRec

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1536
@pytest.mark.MF1536
@pytest.mark.level2
def test_rec_option_not_exist():
    ve_test = VeTestApi("tv:rec_option_not_exist")
    hhId, login = ve_test.he_utils.createTestHouseHold(withSTB=False, withPVR = False)
    ve_test.begin(login=None)
    ve_test.he_utils.setHHoffers(hhId)
    #ve_test.appium.launch_app()
    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123', verify_startup_screen = False)
    fullscreen = ve_test.screens.fullscreen
    fullscreen.navigate()
    is_rec = get_recordable_ev(ve_test)
    if(is_rec):
        linear_action_menu = ve_test.screens.linear_action_menu
        linear_action_menu.navigate()
        ve_test.log_assert(linear_action_menu.is_active(), "Linear action menu is not active")
        linear_action_menu.verify_record_button(False)
    else:
        ve_test.log("NO RECORDABLE EVENTS EXISTS")
    ve_test.end()

@pytest.mark.MF1536
def test_rec_option_exist():
    ve_test = VeTestApi("tv:rec_option_exist")
    hhId, login = ve_test.he_utils.createTestHouseHold(withSTB=False, withPVR=True)
    ve_test.begin(login=None)
    #ve_test.appium.launch_app()
    ve_test.screens.login_screen.sign_in(hhId, user_name=hhId, password='123', verify_startup_screen = False)
    #ve_test.he_utils.setHHoffers(hhId)

    fullscreen = ve_test.screens.fullscreen
    fullscreen.navigate()
    is_rec = get_recordable_ev(ve_test)
    if(is_rec):
        linear_action_menu = ve_test.screens.linear_action_menu
        linear_action_menu.navigate()
        ve_test.log_assert(linear_action_menu.is_active(), "Linear action menu is not active")
        linear_action_menu.verify_record_button(True)
    else:
       ve_test.log("NO RECORDABLE EVENTS EXISTS")
    ve_test.end()
