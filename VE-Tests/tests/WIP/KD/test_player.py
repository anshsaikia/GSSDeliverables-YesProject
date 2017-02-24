from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ui_building_blocks.KD.pincode import YouthChanneltype

playback_time = 5

def channel_change_and_verify_info_layer(direction, test):
    infoLayer = test.screens.infolayer
    fullScreen = test.screens.fullscreen
    fullScreen.channel_change(direction,  verify_playing=False)
    current_tuned_channel = test.screens.playback.get_current_tuned()
    while not (test.screens.playback.isChannelPlayable(current_tuned_channel) and infoLayer.event_data_available):
        test.wait(1)
        infoLayer.dismiss_notification()
        fullScreen.channel_change(direction,  verify_playing=False)
        current_tuned_channel = test.screens.playback.get_current_tuned()
    lcn = infoLayer.getLCN()
    infoLayer.verify_data(lcn)
    infoLayer.dismiss()

def test_navigation():
    test = VeTestApi("test_navigation")
    test.begin()
    player = test.screens.infolayer
    test.screens.navigate(test.screens.fullscreen)
    player.show()
    channel_change_and_verify_info_layer(ScreenActions.UP, test)
    test.wait(2)
    channel_change_and_verify_info_layer(ScreenActions.DOWN, test)
    test.end()

def test_player_tune_clear():
    test = VeTestApi("test_player_tune_clear")
    test.begin(screen=test.screens.zaplist)
    playback = test.screens.playback
    '''play clear content from zaplist'''
    playback.play_linear_clear_content(playback_time=playback_time, screen=test.screens.zaplist)
    infoLayer = test.screens.infolayer
    lcn= infoLayer.getLCN()
    infoLayer.verify_data(lcn)
    test.end()

def test_player_tune_encrypted():
    test = VeTestApi("test_player_tune_encrypted")
    test.begin(screen=test.screens.zaplist)
    playback = test.screens.playback
    #play encrypted content from zaplist
    playback.play_linear_encrypted_content(playback_time=playback_time, screen=test.screens.zaplist)
    infoLayer = test.screens.infolayer
    lcn = infoLayer.getLCN()
    infoLayer.verify_data(lcn)
    test.end()

def test_player_from_zap_playback_qam():
    test = VeTestApi("test_sanity_playback_qam")
    test.begin(screen=test.screens.zaplist)
    zaplist = test.screens.zaplist
    playback = test.screens.playback
    current_channel =  zaplist.get_centered_event_view(test.milestones.getElements())
    channel_id = current_channel['channel_id']
    while  playback.isChannelPlayable(channel_id):
        zaplist.scroll_channels(-1)
        current_channel =  zaplist.get_centered_event_view(test.milestones.getElements())
        channel_id = current_channel['channel_id']
    if( not playback.isChannelPlayable(channel_id)):
        zaplist.tune_to_channel_by_sek(channel_id, False)
        elements = test.milestones.getElements()
        test.log_assert(test.ui.element_exists("error_msg", elements), "QAM Message Not Displayed")
    else:
        test.log("We have no QAM channels for this tennant")
    test.end()

def remove_test_player_from_zap():
    test = VeTestApi("remove_test_player_from_zap")
    test.begin(screen=test.screens.zaplist)
    zapList = test.screens.zaplist
    playBack = test.screens.playback
    infoLayer = test.screens.infolayer
    test.screens.navigate(zapList)
    current_channel =  zapList.get_centered_event_view(test.milestones.getElements())
    channel_id = current_channel['channel_id']
    playable = playBack.isChannelPlayable(channel_id)
    while not playable:
        zapList.scroll_channels(1)
        current_channel =  zapList.get_centered_event_view(test.milestones.getElements())
        channel_id = current_channel['channel_id']
        playable = playBack.isChannelPlayable(channel_id)
    if(playable):
        zapList.tune_to_channel_by_sek(channel_id, False)
        lcn = infoLayer.getLCN()
        infoLayer.verify_data(lcn)
    else:
        test.log("We have no playable channels for this tennant")
    test.end()

def test_protected_youth_channel():
    test = VeTestApi("test_protected_youth_channel")
    test.begin(login=None)
    test.screens.login_screen.sign_in('h3', user_name='h3', password='123', verify_startup_screen = False)
    zapList = test.screens.zaplist
    playBack = test.screens.playback
    infoLayer = test.screens.infolayer
    test.screens.navigate(zapList)
    pinCode = test.screens.pincode
    yp_channel = pinCode.get_youth_channel(type=YouthChanneltype.ALL_EVENTS_PROTECTED)
    zapList.tune_to_channel_by_sek(yp_channel)
    test.log_assert(playBack.is_video_hidden() == True, "Video Is not Hidden on Locked channel %s" % yp_channel)
    lcn = infoLayer.getLCN()
    infoLayer.verify_data(lcn)
    test.end()