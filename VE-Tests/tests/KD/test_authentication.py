__author__ = 'mibenami'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.playback import START_STREAMING_TIMEOUT
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

'''
verify happy scenario as per flow - get main hub screen after sign in
'''
@pytest.mark.MF359_Device_authentication
@pytest.mark.MF1111_Device_authentication
def test_authentication_signin():
    ve_test = VeTestApi("test_authentication_signin")
    ve_test.begin(ve_test.login_types.login)

    ve_test.end()

'''
verify re- authentication after flush cookies and App cach
'''
@pytest.mark.MF359_Device_authentication
@pytest.mark.regression
@pytest.mark.export_regression_MF359_Device_authentication
@pytest.mark.MF1111_Device_authentication
@pytest.mark.commit
@pytest.mark.ios_regression

def test_reauthentication_flushcookies():
    ve_test = VeTestApi("test_reauthentication_flushcookies")
    ve_test.begin(ve_test.login_types.login)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)

    ve_test.milestones.flushCookies()

    ve_test.milestones.flushAppCache()

    ve_test.wait(START_STREAMING_TIMEOUT)
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.screens.linear_action_menu.navigate()

    ve_test.end()

'''
Re-authentication during playback
validate playback is still playing
'''
@pytest.mark.MF359_Device_authentication
@pytest.mark.MF1111_Device_authentication
def test_reauthentication_during_playback():
    ve_test = VeTestApi("test_reauthentication_during_playback")
    ve_test.begin(ve_test.login_types.login)

    ve_test.screens.main_hub.tune_to_linear_channel_by_position(EventViewPosition.right_event)
    ve_test.wait(START_STREAMING_TIMEOUT)
    ve_test.milestones.flushCookies()
    ve_test.milestones.flushAppCache()
    ve_test.wait(5)
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.screens.linear_action_menu.navigate()
    ve_test.wait(3)
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()
