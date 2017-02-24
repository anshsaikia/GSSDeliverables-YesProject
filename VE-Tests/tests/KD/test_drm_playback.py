__author__ = 'gmaman'

import pytest

from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF82
@IHmark.MF1012
@pytest.mark.MF82_playLinear_drm_encrypted
@pytest.mark.export_regression_MF82_playLinear_drm_encrypted
@pytest.mark.regression
@pytest.mark.commit
@pytest.mark.ios_regression
@pytest.mark.MF1012_playLinear_drm_encrypted
@pytest.mark.level2
def test_play_encrypted_linear():
    ve_test = VeTestApi("drm:test_play_encrypted_linear")
    ve_test.begin()

    ve_test.screens.playback.play_linear_encrypted_content(playback_time=60)

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.FS_Playback
@pytest.mark.stability
@pytest.mark.linear_drm_playback_stability
def test_play_long_encrypted_linear():
    ve_test = VeTestApi("drm:test_play_long_encrypted_linear")
    ve_test.begin()

    ve_test.screens.playback.play_linear_encrypted_content(playback_time=60*60*4,  verification_units=60)

    ve_test.end()