import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ui_building_blocks.screen import ScreenDismiss
from vgw_test_utils.IHmarks import IHmark

__author__ = 'mibenami'

def channel_change_and_verify_info_layer(direction, test):
    infoLayer = test.screens.infolayer
    fullscreen = test.screens.fullscreen

    fullscreen.channel_change(direction,  verify_playing=False)
    current_tuned_channel = test.screens.playback.get_current_tuned()
    elements = test.milestones.getElements()
    while not test.screens.playback.isChannelPlayable(current_tuned_channel):
        test.wait(1)
        infoLayer.dismiss_notification()
        fullscreen.channel_change(direction,  verify_playing=False)
        elements = test.milestones.getElements()
        current_tuned_channel = test.screens.playback.get_current_tuned()

    lcn1 = infoLayer.getLCN(elements)
    infoLayer.verify_data(lcn1, elements)
    infoLayer.dismiss()

# Short swipe up/down on full screen should tune and raise info layer
@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF962
@pytest.mark.MF962_infoLayer
@pytest.mark.ios_regression
@pytest.mark.commit
@pytest.mark.level2
def test_fullscreen_to_infolayer():

    my_test = VeTestApi("infoLayer: fullscreen to infolayer")
    my_test.begin()

    '''Go to info layer via short swipe down'''
    channel_change_and_verify_info_layer(ScreenActions.DOWN, my_test)
    my_test.wait(2)
    '''Go to info layer via short swipe up'''
    channel_change_and_verify_info_layer(ScreenActions.UP, my_test)

    my_test.end()


# Tap on non playing/playing channel from zap list or tv hub should tune and raise info layer
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF962
@pytest.mark.MF962_infoLayer
@pytest.mark.regression
@pytest.mark.export_regression_MF961_Info_Layer

def test_infolayer_from_tune():

    my_test = VeTestApi("test_infolayer_from_tune")
    my_test.begin()
    infoLayer = my_test.screens.infolayer
    zaplist = my_test.screens.zaplist

    "Tune to non playing channel from zaplist and verify info layer data"
    channel_id, channel_prop = my_test.he_utils.getLinearContentABR('clear')
    my_test.screens.zaplist.tune_to_channel_by_sek(channel_id, verify_streaming_started =True)
    elements = my_test.milestones.getElements()
    infoLayer.verify_active(1)
    infoLayer.verify_data(channel_id, elements)
    infoLayer.dismiss()

    "Tune to currently playing channel from zaplist and verify info layer data"
    zaplist.navigate(ScreenActions.UP)
    current_event =  zaplist.get_tuned_event()
    channel_id = current_event['channel_id']
    lcn = current_event['channel_number']
    zaplist.tune_to_channel_by_sek(channel_id)
    elements = my_test.milestones.getElements()
    infoLayer.verify_active(1)
    infoLayer.verify_data(lcn, elements)

    my_test.end()

#Dismiss by tap on background, and verify dismiss after timeout
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF962
@pytest.mark.MF962_infoLayer
def test_infolayer_dismiss():
    my_test = VeTestApi("test_infolayer_dismiss")

    my_test.begin()
    infoLayer = my_test.screens.infolayer
    mainHub = my_test.screens.main_hub

    # dismiss by tap
    mainHub.tune_to_linear_channel_by_position(EventViewPosition.right_event, verify_streaming=False)
    infoLayer.verify_active()
    infoLayer.dismiss(ScreenDismiss.TAP)

    # dismiss by timeout
    mainHub.tune_to_linear_channel_by_position(EventViewPosition.right_event, verify_streaming=True)
    infoLayer.verify_active()
    infoLayer.dismiss(ScreenDismiss.TIMEOUT)

    my_test.end()


