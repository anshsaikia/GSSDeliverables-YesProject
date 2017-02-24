import pytest
import json
from vgw_test_utils.IHmarks import IHmark

__author__ = 'aterem'
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
import logging

WAIT_AFTER_RESTART = 16

def getFirstChannelId(test):
    ctap_grid_info =  test.ctap_data_provider.send_request('GRID', None)
    firstChannel = ctap_grid_info["channels"][0]
    logging.info("first channel is " + json.dumps(firstChannel))
    firstChannelId = firstChannel['id']
    return firstChannelId

def restartAndVerifyPlayingChannelId(ve_test, channelId):
    ve_test.appium.restart_app()
    ve_test.screens.main_hub.verify_active(timeout=WAIT_AFTER_RESTART)
    verifyPlayingChannelId(ve_test, channelId)

def verifyPlayingChannelId(ve_test, channelId):
    if channelId:
        logging.info("validate application tunes to channel " + channelId + " upon finish of boot sequence ")
    playingChannel = ve_test.screens.playback.get_current_channel()
    ve_test.log_assert(channelId == playingChannel,"Incorrect last played channel playing after restart " + str(playingChannel) + " while expecting " + str(channelId))

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1164
@pytest.mark.MF1164_Boot_flow
@pytest.mark.MF1173_Boot_flow
#@pytest.mark.regression
@pytest.mark.commit
@pytest.mark.export_regression_MF1164_Boot_flow
@pytest.mark.level2
def test_last_played_channel():

    ve_test = VeTestApi("bootflow:test_last_played_channel")
    main_hub = ve_test.screens.main_hub

    ve_test.begin()

    hhId = ve_test.configuration["he"]["generated_household"]
    firstChannelId = ve_test.he_utils.get_last_tuned_channel_for_device(hhId, None)
    verifyPlayingChannelId(ve_test, firstChannelId)

    last_played_channel, channel_prop = ve_test.he_utils.getLinearContentABR('clear')
    ve_test.screens.zaplist.tune_to_channel_by_sek(last_played_channel, verify_streaming_started =True)

    logging.info("last_played_channel before restart={}".format(last_played_channel))
    restartAndVerifyPlayingChannelId(ve_test, last_played_channel)

    #first chnanel in line up is not correct after recommendations pushed

    #logging.info("validate played channel is the first in lineup")
    #hubEvents = main_hub.get_events_by_type("EVENT_CONTENT_TYPE_STANDALONE")
    #ve_test.log_assert('channel_id' in hubEvents[0], "Cannot find channel id in the first event:" + str(hubEvents[0]))
    #firstChannelInHub = hubEvents[0]['channel_id']
    #ve_test.log_assert(last_played_channel == firstChannelInHub, "Last played channel should be first in hub after restart. Last played channel is " + last_played_channel + " while first in hub is " + firstChannelInHub)

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1173
@IHmark.MF1164
@pytest.mark.commit
@pytest.mark.MF1173_Boot_flow
@pytest.mark.MF1164_Boot_flow
def test_last_played_channel_invalid():
    ve_test = VeTestApi("bootflow:test_last_played_channel_invalid")
    main_hub = ve_test.screens.main_hub

    ve_test.begin()

    main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)
    ve_test.wait(2) #wait before setting, so set of channel by CTAP will not be done after our set
    hhId = ve_test.configuration["he"]["generated_household"]
    notavailable=str("notAvailable")
    ve_test.he_utils.set_last_tuned_channel_for_device(hhId, None,notavailable)
    lastTunedChannel = ve_test.he_utils.get_last_tuned_channel_for_device(hhId, None)
    logging.info("the last tuned channel was set to: " + lastTunedChannel)
    if repr(lastTunedChannel) != repr('"notAvailable"'):
        ve_test.log_assert(repr(lastTunedChannel) == repr('"notAvailable"'), "set of last tuned channel failed!!")
    firstChannelId = getFirstChannelId(ve_test)
    logging.info("first channel id is " + firstChannelId)
    restartAndVerifyPlayingChannelId(ve_test, firstChannelId)

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1173
@IHmark.MF1164
@pytest.mark.MF1173_Boot_flow
@pytest.mark.MF1164_Boot_flow
def test_last_played_channel_protected():
    ve_test = VeTestApi("bootflow:test_last_played_channel_protected")
    pincode = ve_test.screens.pincode
    zap_list = ve_test.screens.zaplist

    ve_test.begin()

    channel_with_yp =pincode.get_youth_channel()
    zap_list.navigate()
    zap_list.tune_to_channel_by_sek(channel_with_yp)
    restartAndVerifyPlayingChannelId(ve_test, channel_with_yp)
    ve_test.log_assert(ve_test.screens.playback.get_playback_status()['hiddenVideo'], "video is not hidden on protected channel")

    ve_test.end()
