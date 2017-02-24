import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions
from vgw_test_utils.IHmarks import IHmark

' Global constants '
TUNING_WAIT = 10

def one_finger_swipe(mytest, direction):
    mytest.ui.one_finger_swipe(direction)
    mytest.wait(TUNING_WAIT)
    mytest.screens.notification.dismiss_notification()
    mytest.screens.infolayer.dismiss()
    current_lcn = mytest.screens.playback.get_current_channel()
    return current_lcn

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF960
@pytest.mark.commit
@pytest.mark.MF960_channelChange
@pytest.mark.ios_regression
def test_channel_change_tune_to_various():
    ''' tune to encrypted and clear ABR content from fullscreen and verify that the playback was successful  '''
    test = VeTestApi("channel change tune to various")
    test.begin()

    playback = test.screens.playback
    playback_time=5
    playback.play_linear_encrypted_content(playback_time=playback_time, screen=test.screens.fullscreen)
    playback.store()
    playback.play_linear_clear_content(playback_time=playback_time, screen=test.screens.fullscreen)
    playback.verify_not_stored()

    test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF959
@pytest.mark.level2
@pytest.mark.regression
@pytest.mark.MF959_channelchange
@pytest.mark.export_regression_MF959_channelchange
def test_channel_change_gesture():

    mytest = VeTestApi("test_channel_change_gesture")
    mytest.begin()

    tuned_channel, channel_prop = mytest.he_utils.getLinearContentABR('clear')
    mytest.screens.zaplist.tune_to_channel_by_sek(tuned_channel, verify_streaming_started =False)

    mytest.screens.notification.dismiss_notification()
    mytest.screens.infolayer.dismiss()
    first_channel_lcn = tuned_channel

    logging.info('swipe down screen distance')
    current_lcn = one_finger_swipe(mytest, ScreenActions.DOWN)
    mytest.log_assert(current_lcn != first_channel_lcn, "Failed to change channel via swipe up, distance of a quarter screen")

    logging.info('swipe up screen distance')
    current_lcn = one_finger_swipe(mytest, ScreenActions.UP)
    mytest.log_assert(current_lcn == first_channel_lcn, "Failed to change channel via a swipe down, distance of a third screen")

    logging.info('swipe down screen distance')
    current_lcn = one_finger_swipe(mytest, ScreenActions.DOWN)
    mytest.log_assert(current_lcn != first_channel_lcn, "Failed to change channel via swipe up, distance of a half screen")

    mytest.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF959
@pytest.mark.MF959_channelchange
#MF959 - Channel change via gesture [Android]
#Play the 1st channel or default channel  in lineup (or the default channel), swipe 1 channel up, then 1 channel down. Verify that the URL that the app receives for the channel matches that one it received before.
def test_channel_change_metadata():
    mytest = VeTestApi("test_channel_change_metadata")

    mytest.begin()

    fullscreen = mytest.screens.fullscreen

    #verify that there are a minimum of 2 linear assets in channel lineup
    total_services = mytest.he_utils.get_total_services_num()
    mytest.log_assert(total_services >= 2, "Swiping through channel lineup requires at least 2 services")

    tuned_channel, channel_prop = mytest.he_utils.getLinearContentABR('clear')
    mytest.screens.zaplist.tune_to_channel_by_sek(tuned_channel, verify_streaming_started =True)
    mytest.wait(TUNING_WAIT)
    mytest.screens.infolayer.dismiss()
    elements = mytest.milestones.getElements()
    first_channel_lcn = mytest.milestones.get_value_by_key(elements, "channelId")

    logging.info('Swipe Down')
    fullscreen.channel_change(ScreenActions.DOWN,verify_playing=False)
    status = mytest.screens.playback.verify_streaming_playing()
    plbUrl = status['sso']['sessionPlaybackUrl']
    mytest.screens.infolayer.dismiss()
    elements = mytest.milestones.getElements()
    current_lcn = mytest.milestones.get_value_by_key(elements, "channelId")
    mytest.log_assert(current_lcn != first_channel_lcn, "Failed to change channel via swipe up with two fingers")
    up_from_first_lcn = current_lcn

    logging.info('Swipe up')
    fullscreen.channel_change(ScreenActions.UP,  verify_playing=False)
    status = mytest.screens.playback.verify_streaming_playing()
    mytest.log_assert(status['sso']['sessionPlaybackUrl'] != plbUrl," Metadata should not be the same as the previous channel after a channel change")
    mytest.screens.infolayer.dismiss()
    elements = mytest.milestones.getElements()
    current_lcn = mytest.milestones.get_value_by_key(elements, "channelId")
    mytest.log_assert(current_lcn == first_channel_lcn, "Metadata verification failed on channel change with swipe down.Should have returned to the first channel tuned to from the hub")

    logging.info('Swipe down')
    fullscreen.channel_change(ScreenActions.DOWN,  verify_playing=False)
    status = mytest.screens.playback.verify_streaming_playing()
    mytest.log_assert(status['sso']['sessionPlaybackUrl'] == plbUrl," Metadata comparison check failed")
    mytest.screens.infolayer.dismiss()
    elements = mytest.milestones.getElements()
    current_lcn = mytest.milestones.get_value_by_key(elements, "channelId")
    mytest.log_assert(current_lcn == up_from_first_lcn, "Metadata verification failed on channel change with swipe up.")

    mytest.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF959
@pytest.mark.MF959_channelchange
def test_channel_change_stability_cyclic():

    ve_test = VeTestApi("test_channel_change_stability_cyclic")

    ve_test.begin()

    fullscreen = ve_test.screens.fullscreen

    tuned_channel, channel_prop = ve_test.he_utils.getLinearContentABR('clear')
    ve_test.screens.zaplist.tune_to_channel_by_sek(tuned_channel, verify_streaming_started =False)
    first_channel_sek = tuned_channel
    ve_test.screens.infolayer.dismiss()

    total_services = ve_test.he_utils.get_total_services_num()

    logging.info('cycling through channel list until we return to the starting point, first channel tuned to from the hub. total services = %s' % total_services)
    for iteration in range(total_services + 1):
        fullscreen.navigate()
        fullscreen.channel_change(ScreenActions.DOWN, skip_not_playable_channel=True)
        ve_test.wait(2)
        ve_test.screens.infolayer.dismiss()
        elements = ve_test.milestones.getElements()
        current_sek = ve_test.milestones.get_value_by_key(elements, "channelId")
        logging.info('current iteration: %s, current lcn: %s'%(iteration,current_sek))
        if current_sek == first_channel_sek:
            logging.info("getting back to first channel %s" % first_channel_sek)
            break

    ve_test.log_assert(iteration +1 == total_services, "Could not validate cycling through the entire channel line up")
    ve_test.end()