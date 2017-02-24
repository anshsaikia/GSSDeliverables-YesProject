import pytest
import logging
from time import sleep
import random
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

'''----------------------------------------------------------------------------------------Tests-------------------------------------------------------------'''

'''
1. Tune to non current channel from zaplist
2. select current channel from zaplist and make sure No tuning
'''
@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF969
@pytest.mark.MF969_Linear_zaplist
@pytest.mark.regression
@pytest.mark.export_regression_MF969_Linear_zaplist
@pytest.mark.level2
def test_tuning_from_zaplist():
    ve_test = VeTestApi("zaplist:test_tuning_from_zaplist")
    ve_test.begin()

    zaplist = ve_test.screens.zaplist
    playback = ve_test.screens.playback

    zaplist.navigate()

    'tunning to non current channel'
    current_channel =  zaplist.get_centered_event_view(ve_test.milestones.getElements())

    non_current_channel = zaplist.get_next_event(current_channel)
    channel_id = non_current_channel['channel_id']

    while not playback.isChannelPlayable(channel_id):
        non_current_channel = zaplist.get_next_event(non_current_channel)
        channel_id = non_current_channel['channel_id']

    zaplist.tune_to_channel_by_sek(channel_id, False)
    channel = ve_test.he_utils.getChannel(channel_id)
    if 'url' in channel:
        play_status = playback.verify_streaming_playing(channel['url'])
    else:
        play_status = playback.verify_streaming_playing()

    sleep(5)
    zaplist.verify_playing_channel_position(channel_id)

    'tunning to current channel'
    zaplist.tune_to_channel_by_sek(channel_id, False)

    if 'url' in channel:
        play_status_same_channel = playback.verify_streaming_playing(channel['url'])
    else:
        play_status_same_channel = playback.verify_streaming_playing()

    ve_test.log_assert(play_status['sso']['sessionId']==play_status_same_channel['sso']['sessionId'], "New tunning is made when tunning to current channel")

    ve_test.end()

'''
Compare zaplist events metadata against ctap
'''
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF969
@pytest.mark.MF969_Linear_zaplist
def test_zaplist_metadata():
    ve_test = VeTestApi("zaplist:test_zaplist_metadata")
    ve_test.begin()

    zaplist = ve_test.screens.zaplist
    zaplist.verify_metadata()

    ve_test.end()

'''
Verify zaplist is no longer display after timeout from last user interaction
'''
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF969
@pytest.mark.MF969_Linear_zaplist
def test_zaplist_timeout():
    ve_test = VeTestApi("test_zaplist_timeout")
    ve_test.begin()

    zaplist = ve_test.screens.zaplist

    'verify zapllist dimiss after timeout from zaplist open'
    zaplist.navigate()
    ve_test.wait(zaplist.timeout+1)
    screen = ve_test.milestones.get_current_screen()
    ve_test.log_assert(screen!='zap_list', "zaplist was not dismiss after %s seconds" % zaplist.timeout)
    ve_test.log_assert(screen=='fullscreen', "not returnning to fullscreen after zaplist dismissed")

    'verify zapllist dismiss after timeout from last user interaction'
    zaplist.navigate()
    ve_test.wait(zaplist.timeout-5)
    zaplist.scroll_from_center(duration=1000, direction=ScreenActions.UP)
    ve_test.wait(zaplist.timeout-2)
    screen = ve_test.milestones.get_current_screen()
    ve_test.log_assert(screen=='zap_list', "zaplist dismissed before %d seconds pass from latest user interaction" % zaplist.timeout)
    ve_test.wait(4)
    screen = ve_test.milestones.get_current_screen()
    ve_test.log_assert(screen!='zap_list', "zaplist was not dismiss after %s seconds from last user interaction" % zaplist.timeout)
    ve_test.end()\

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF970
@pytest.mark.MF970_zaplist
@pytest.mark.commit
@pytest.mark.ios_regression
def test_zaplist_various_scrolling():
    #Start test
    my_test = VeTestApi("zaplist:various scrolling")
    my_test.begin(autoPin=True)
    #Store refs to screens
    zaplist = my_test.screens.zaplist
    #navigate zap list
    zaplist.navigate(ScreenActions.UP)
    #Scroll slow upwards
    zaplist.scroll_from_center(2000, ScreenActions.UP)
    #Scroll fast upwards
    zaplist.scroll_from_center(500, ScreenActions.UP)
    #Scroll slow downwards
    zaplist.scroll_from_center(2000, ScreenActions.DOWN)
    #Scroll fast downwards
    zaplist.scroll_from_center(500, ScreenActions.DOWN)
    #Stop test
    my_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.stability
def test_zaplist_check_intervals():
    #Start test
    my_test = VeTestApi("zaplist:check intervals")
    my_test.begin()
    #Store refs to screens
    zaplist = my_test.screens.zaplist
    fullscreen = my_test.screens.fullscreen
    #Run zaplist in intervals
    intervals = [1,3,5,10,30,60]
    for intervalIndex in range(0, len(intervals)):
        #navigate zaplist
        zaplist.navigate(ScreenActions.UP)
        #navigate fullscreen
        fullscreen.navigate()
        #Wait interval since start of test
        intervalSeconds = intervals[intervalIndex]*60
        logging.info("waiting ..." + str(intervalSeconds))
        my_test.interval(intervalSeconds)
    #Stop test
    my_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.stability
def test_zaplist_check_performance():
    time_list = list()
    #Start test
    my_test = VeTestApi("zaplist: check scrolling stamina")
    my_test.begin()
    #Store refs to screens
    zaplist = my_test.screens.zaplist
    fullscreen = my_test.screens.fullscreen

    for repeatIndex in range(0, 100):
        logging.info("repeat: " + str(repeatIndex))
        #Start measure of performance
        my_test.performance.start()
        #navigate zaplist
        zaplist.navigate(ScreenActions.UP)
        #End measure of performance
        sec = my_test.performance.stop()
        #Add to time list
        time_list.append(sec)
        #navigate fullscreen
        fullscreen.navigate()
    #Verify performance results
    my_test.performance.verifylist(time_list, 0.80, 1.0)
    my_test.performance.verifylist(time_list, 0.20, 2.0)
    #Stop test
    my_test.end()


@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF969
@pytest.mark.stability
def test_zaplist_check_stress():
    #Start test
    my_test = VeTestApi("zaplist: check stress")
    my_test.begin()
    #Store refs to screens
    zaplist = my_test.screens.zaplist
    fullscreen = my_test.screens.fullscreen

    direction = ScreenActions.UP

    for repeatIndex in range(0, 100):
        logging.info("repeat: " + str(repeatIndex))
        #navigate zaplist
        zaplist.navigate(ScreenActions.UP)
        #Random scroll
        if direction == ScreenActions.UP:
            direction = ScreenActions.DOWN
        else:
            direction = ScreenActions.UP
        seconds = random.randrange(1, 3)
        zaplist.scroll_from_center(seconds, direction)
        #Tune to channel
        zaplist.tap_channel(0)
        #Wait for 3 seconds
        my_test.wait(3)
    #Stop test
    my_test.end()




