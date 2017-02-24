__author__ = 'rzawrbac and spachter'

import logging
from vgw_test_utils.IHmarks import IHmark
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.he_utils.he_utils import VodContentType

TIMEOUT = 5


@IHmark.MF868
@IHmark.FS_VE_VOD
@IHmark.FS_Playback
@IHmark.F_Playback_Trailer
@IHmark.O_Three_Rivers
def test_play_trailer_not_restricted():
    test = VeTestApi("test_vod_trailer")
    test.begin()

    asset = test.he_utils.getVodContent([VodContentType.WITH_LOW_RATED_TRAILER])
    test.screens.store.play_vod_by_title(asset['title'], trailer=True)

    test.wait(TIMEOUT)
    test.end()


@IHmark.MF868
@IHmark.FS_VE_VOD
@IHmark.FS_Playback
@IHmark.F_Playback_Trailer
@IHmark.O_Three_Rivers
def test_play_trailer_restricted():
    test = VeTestApi("test_vod_trailer")
    test.begin()

    is_pin_required = 'true'
    asset = test.he_utils.getVodContent([VodContentType.WITH_HIGH_RATED_TRAILER])
    test.screens.store.play_vod_by_title(asset['title'],trailer=True)

    # Check that we get to pin screen
    test.log_assert(test.screens.infolayer.is_program_locked(), "Unlock button is showing")

    # Insert pin
    test.screens.infolayer.tap_unlock_program()
    logging.info("enter correct pin")
    test.screens.pincode.enter_pin()

    test.wait(TIMEOUT)
    test.end()


@IHmark.MF868
@IHmark.FS_VE_VOD
@IHmark.FS_Playback
@IHmark.F_Playback_Trailer
@IHmark.O_Three_Rivers
def test_stop_play_trailer():
    test = VeTestApi("test_vod_trailer")
    test.begin()

    asset = test.he_utils.getVodContent([VodContentType.WITH_LOW_RATED_TRAILER])
    test.screens.store.play_vod_by_title(asset['title'], trailer=True)

    test.wait(TIMEOUT)
    test.screens.action_menu.navigate()
    test.screens.vod_action_menu.press_stop()
    test.wait(TIMEOUT)

    test.screens.vod_action_menu.verify_active()

    test.end()


@IHmark.MF868
@IHmark.FS_VE_VOD
@IHmark.FS_Playback
@IHmark.F_Playback_Trailer
@IHmark.O_Three_Rivers
def test_end_of_play_trailer():
    test = VeTestApi("test_vod_trailer")
    test.begin()

    asset = test.he_utils.getVodContent([VodContentType.WITH_LOW_RATED_TRAILER])
    test.screens.store.play_vod_by_title(asset['title'], trailer=True)

    test.wait(TIMEOUT)
    test.screens.action_menu.navigate()
    test.screens.vod_action_menu.seek(is_tap=True, percent=85)
    test.wait(TIMEOUT)

    test.screens.vod_action_menu.verify_active()

    test.end()
