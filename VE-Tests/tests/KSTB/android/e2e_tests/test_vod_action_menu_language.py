__author__ = 'eacarq'

#
#             Current test is skipped until a multi-language Vod is available
#
# To do : change the search for the Euronews multi-language Vod asset once integrated in the Vod catalogue. 
#
#

import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ve_tests.assert_mgr import AssertMgr


@pytest.mark.sanity
@pytest.mark.FS_VOD
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_selected_audio_language
def test_vod_action_menu_language():
    test = VeTestApi("test_vod_action_menu_language")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.wait(1)
    
#   play muti-language Vod asset
    test.screens.main_hub.navigate()
    test.wait(2)

    test.screens.playback.vod_manager.play_multi_language_asset_from_hub()
    test.screens.playback.vod_manager.select_playback_audio_language('PORTUGUESE')

#   check that audio is set to portuguese
    test.screens.playback.vod_manager.check_playback_audio_language(assertmgr, "test_vod_default_language", 1, 'por')
    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_vod_action_menu_language #####")
