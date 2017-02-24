import pytest
from vgw_test_utils.IHmarks import IHmark

from tests_framework.ve_tests.ve_test import VeTestApi


# @IHmark.FS_Navigation
@IHmark.LV_L1
@pytest.mark.FS_Navigation
# @IHmark.F_Navigation_All_Screens
@IHmark.O_iOS
@IHmark.O_Android
# @IHmark.F_Navigation
@pytest.mark.commit
@pytest.mark.level1
@pytest.mark.delivery_criteria
@pytest.mark.ve_tests_repo_delivery_criteria
def test_sanity_navigation():
    """navigate to all of the screen"""
    test = VeTestApi("test_sanity_navigation")
    test.begin(autoPin=True)
    screens = test.screens
    if test.supported_screens:
        screens.navigate(test.supported_screens)
    else:
        '''navigate to main screens'''
        main_screens = [screens.main_hub,
                        screens.fullscreen,
                        screens.zaplist,
                        screens.timeline,
                        screens.guide]
        screens.navigate(main_screens)

        '''navigate to extra screens'''
        extra_screens = [screens.linear_action_menu,
                         screens.vod_action_menu,
                         screens.settings,
                         screens.search,
                         screens.library,
                         screens.store]
        screens.navigate(extra_screens)
    test.end()


@IHmark.FS_Playback
@IHmark.LV_L1
# @IHmark.F_Playback_clear
@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.commit
@pytest.mark.level1
def test_sanity_playback_clear():
    """navigate to all of the screen"""
    test = VeTestApi("test_sanity_playback_clear")
    test.begin(screen=test.screens.zaplist, autoPin=True)

    playback = test.screens.playback
    playback_time = 5
    # play clear content from zaplist
    playback.play_linear_clear_content(playback_time=playback_time, screen=test.screens.zaplist)

    test.end()


@IHmark.FS_Playback
@IHmark.LV_L1
# @IHmark.F_Playback_encrypted
@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.commit
@pytest.mark.level1
def test_sanity_playback_encrypted():
    """navigate to all of the screen"""
    test = VeTestApi("test_sanity_playback_encrypted")
    test.begin(screen=test.screens.zaplist, autoPin=True)

    playback = test.screens.playback
    playback_time = 5
    # play encrypted content from zaplist
    playback.play_linear_encrypted_content(playback_time=playback_time, screen=test.screens.zaplist)

    test.end()

@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.heart_beat_devices
def test_heart_beat_devices():
    test = VeTestApi("heart_beat_devices")
    test.begin()
    test.end()
