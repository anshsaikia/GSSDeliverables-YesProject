from tests_framework.ve_tests.ve_test import VeTestApi
import pytest

def test_stability_screens():
    test = VeTestApi("test_stability_screens")
    test.begin()
    for repeat in range(0,30):
        test.log("Repeat #" + str(repeat))
        '''navigate to all of the screen'''
        test.screens.navigate(test.supported_screens)
    test.end()

def test_stability_short():
    test = VeTestApi("test_stability_short")
    test.begin()
    playback_time = 5
    for repeat in range(0,6):
        test.log("Repeat #" + str(repeat))
        '''navigate to all of the screen'''
        test.screens.navigate(test.supported_screens)
        '''play encrypted'''
        test.screens.playback.play_linear_encrypted_content(playback_time=playback_time, screen=test.screens.zaplist)
        '''navigate to all of the screen'''
        test.screens.navigate(test.supported_screens)
        '''play clear'''
        test.screens.playback.play_linear_clear_content(playback_time=playback_time, screen=test.screens.zaplist)
    test.end()

@pytest.mark.stability
@pytest.mark.stability_day_in_a_life
def test_stability_day_in_a_life():
    test = VeTestApi("test_stability_day_in_a_life")
    test.begin()
    playback_time = 30*60
    for repeat in range(0,6):
        test.log("Repeat #" + str(repeat))
        '''navigate to all of the screen'''
        test.screens.navigate(test.supported_screens)
        '''play encrypted'''
        test.screens.playback.play_linear_encrypted_content(playback_time=playback_time, screen=test.screens.zaplist)
        '''navigate to all of the screen'''
        test.screens.navigate(test.supported_screens)
        '''play clear'''
        test.screens.playback.play_linear_clear_content(playback_time=playback_time, screen=test.screens.zaplist)
    test.end()
