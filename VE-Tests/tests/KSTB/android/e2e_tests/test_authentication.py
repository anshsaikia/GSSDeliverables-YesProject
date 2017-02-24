__author__ = 'mibenami'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi

'''
verify happy scenario as per flow - get main hub screen after sign in
'''
@pytest.mark.sanity
@pytest.mark.FS_Drm
@pytest.mark.non_regression
@pytest.mark.LV_L2
def test_authentication_signin():
    ve_test = VeTestApi("test_authentication_signin")
    ve_test.begin(ve_test.login_types.login)

    ve_test.end()


'''
Re-authentication during playback
validate playback is still playing
'''
@pytest.mark.sanity
@pytest.mark.FS_Drm
@pytest.mark.LV_L3
def test_reauthentication_during_playback():
    ve_test = VeTestApi("test_reauthentication_during_playback")
    ve_test.begin(ve_test.login_types.login)

    # todo modify this with fullscreen.navigate() once this is working
    ve_test.wait(10)
    ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
    ve_test.wait(5)

    ve_test.milestones.flushCookies()
    ve_test.milestones.flushAppCache()
    ve_test.wait(10)
    ve_test.screens.playback.verify_streaming_playing()
    ve_test.screens.zaplist.navigate()
    ve_test.wait(3)
    ve_test.screens.zaplist.dismiss()
    ve_test.screens.playback.verify_streaming_playing()

    ve_test.end()
