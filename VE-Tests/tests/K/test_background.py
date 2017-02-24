from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
from vgw_test_utils.IHmarks import IHmark
from tests_framework.he_utils.he_utils import VodContentType

REMAIN_IN_BACKGROUND_TIMEOUT = 10


def goto_background_and_return(test, time_in_background=REMAIN_IN_BACKGROUND_TIMEOUT):
    test.appium.send_app_to_background()
    test.wait(time_in_background)
    test.appium.send_app_to_foreground()
    test.wait(5)


@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2059
@pytest.mark.MF2059_background
def test_background_functionality():
    test = VeTestApi("test_background_functionality")

    test.begin(preload="vod")

    ''' Go to guide, go to BG, return and verify that guide is active '''
    test.screens.guide.navigate()
    goto_background_and_return(test)
    test.screens.guide.verify_active()

    ''' Go to library, go to BG, return and verify that library is active '''
    test.screens.library_filter.navigate()
    goto_background_and_return(test)
    test.screens.library_filter.verify_active()

    ''' Go to full screen, go to BG, return and verify that video is playing and info layer / action menu is active '''
    test.screens.fullscreen.navigate()
    goto_background_and_return(test)
    status = test.milestones.getPlaybackStatus("playbackState")
    test.log_assert(status == "PLAYING", "expecting playback status PLAYING, but status is " + status)
    elements = test.milestones.getElements()
    screen = test.milestones.get_current_screen(elements)
    if screen != "infolayer" and screen != "action_menu":
        test.log_assert(False, "Screen should be either infolayer (for tablet/phablet) or action_menu (for smartphone), but screen is " + screen)

    ''' Go to action menu, go to BG, return and verify that video is playing and action menu is active '''
    if screen == "infolayer":
        test.screens.action_menu.navigate()
        goto_background_and_return(test)
        status = test.milestones.getPlaybackStatus("playbackState")
        test.log_assert(status == "PLAYING", "expecting playback status PLAYING, but status is " + status)
        test.screens.action_menu.verify_active()

    ''' Play VOD content, go to BG, return and verify that trick bar / action menu is active and video is paused '''
    asset = test.he_utils.getVodContent([VodContentType.SVOD, VodContentType.ENCRYPTED, VodContentType.LOW_RATED], {'policy':'false'})
    test.screens.store_filter.play_vod_by_title(asset['title'])
    goto_background_and_return(test)
    elements = test.milestones.getElements()
    screen = test.milestones.get_current_screen(elements)
    if screen != "trick_bar" and screen != "action_menu":
        test.log_assert(False, "Screen should be either trick_bar (for tablet/phablet) or action_menu (for smartphone), but screen is " + screen)
    if screen == "trick_bar":
        status = test.milestones.getPlaybackStatus("playbackState")
        test.log_assert(status == "PAUSED", "expecting playback status PAUSED, but status is " + status)

    test.end()


@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2059
@pytest.mark.MF2059_background
def test_background_over_10_minutes():
    test = VeTestApi("test_background_over_10_minutes")
    test.begin()
    test.screens.navigate(test.screens.fullscreen)
    goto_background_and_return(test, 601)
    test.screens.tv_filter.verify_active()
    test.end()


@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2059
@pytest.mark.MF2059_background
def test_background_stress():
    test = VeTestApi("test_background_stress")
    test.begin()
    test.screens.navigate(test.screens.fullscreen)
    for i in range(20):
        test.log("iteration number %d" % i)
        goto_background_and_return(test)
        test.screens.infolayer.verify_active()
        status = test.milestones.getPlaybackStatus("playbackState")
        test.log("status:" + status)
        test.log_assert(status == "PLAYING", "expecting video playback")
        test.wait(5)
    test.end()
