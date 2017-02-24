__author__ = 'eacarq'

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ve_tests.assert_mgr import AssertMgr
import pytest
import logging

'''Globals'''
GENERIC_WAIT = 2

@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.F_Audio_Language
@pytest.mark.sanity
@pytest.mark.LV_L2
def test_vod_default_language():
    ve_test = VeTestApi("test_vod_default_language")
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.fullscreen) 

    dico_langs={"deu":"GERMAN","eng":"ENGLISH","fra":"FRENCH","ita":"ITALIAN","por":"PORTUGUESE","spa":"SPANISH","last":"FALSE"}

    # go to main hub
    ve_test.screens.main_hub.navigate()
    ve_test.wait(GENERIC_WAIT)

    # play a multi audio vod to get the current audio
    ve_test.screens.playback.vod_manager.play_multi_language_asset_from_hub()
    cur_audio = ve_test.screens.playback.vod_manager.get_current_playback_audio_language()  # get current audio to change for test
    logging.info("current audio = %s"%(cur_audio))
    l_audios = ve_test.screens.playback.vod_manager.get_all_playback_audio_language()        # get all audios of the vod
    logging.info("liste des audio = %s"%(l_audios))
    
    for audio_lang in dico_langs.keys():                        # check all audio that can exist
        logging.info("try: " + audio_lang) 
        if audio_lang != cur_audio and audio_lang in l_audios:  # if not the current one and in the flux
            logging.info(" -> i   chosen")                       # we choose it
            break
    
    else:                                                       # no break then no new possible audio found
        assertmgr.addCheckPoint("test_vod_default_language", 1 , False, "Current audio '%s' cannot be changed.  possible audios: %s"%(cur_audio,l_audios))

    while audio_lang != "last":                                # at this step we are going to change the audio and relaunch the vod
        new_audio = dico_langs[audio_lang]
        ve_test.screens.main_hub.navigate()
        status = ve_test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES")
        assertmgr.addCheckPoint("test_vod_default_language",2,status, "couldn't navigate to PREFERENCES submenu")
        if status == False:
            break
        status = ve_test.screens.main_hub.select_settings_sub_sub_menu("AUDIO",new_audio)
        assertmgr.addCheckPoint("test_vod_default_language",3,status, "couldn't select " + new_audio) # new audio changed in settings
        if status == False:
            break
 
        # go to fullscreen()
        ve_test.appium.key_event("KEYCODE_BACK")
        ve_test.wait(GENERIC_WAIT)
        ve_test.appium.key_event("KEYCODE_BACK")
        ve_test.wait(GENERIC_WAIT)

        # go to main hub
        ve_test.screens.main_hub.navigate()
        ve_test.wait(GENERIC_WAIT)

        ve_test.screens.playback.vod_manager.play_multi_language_asset_from_hub()                    # relaunch the vod
        cur_audio = ve_test.screens.playback.vod_manager.get_current_playback_audio_language()      # get the audio played
        logging.info("changed current audio = %s"%(cur_audio))
        
        if dico_langs.has_key(cur_audio):                                       # check the new audio is good
            if cur_audio != audio_lang:
                assertmgr.addCheckPoint("test_vod_default_language", 4 , False, "Current audio '%s' is not the good one"%(cur_audio))
            else:
                logging.info("the new audio is good")
            break
        else:
            assertmgr.addCheckPoint("test_vod_default_language", 5 , False, "Current audio '%s' is unknown"%(cur_audio))
        break    
    
    assertmgr.verifyAllCheckPoints()
    ve_test.end()
    logging.info("##### End test_vod_default_language #####")
