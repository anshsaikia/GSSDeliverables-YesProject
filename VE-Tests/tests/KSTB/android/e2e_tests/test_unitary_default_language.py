#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as constants
import pytest
import logging


'''Globals'''
audio_language_dict = {"deu": "GERMAN",
                       "eng": "ENGLISH",
                       "fra": "FRENCH",
                       "ita": "ITALIAN",
                       "por": "PORTUGUESE",
                       "spa": "SPANISH"}


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.F_Audio_Language
@pytest.mark.sanity
@pytest.mark.LV_L2
def test_settings_default_language():
    """
    Check that Preferences language has correct items
    """
    test_name = "test_settings_default_language"
    test = VeTestApi(test_name, useAssertMgr=True)
    test.assertmgr.setup(test_name)
    check = test.assertmgr.addCheckPointLight
    audio_utility = test.screens.playback.vod_manager
    try:
        test.begin(screen=test.screens.fullscreen)
        # Perform channel change to a channel (with pref audio automatically chosen in the flux)
        test.screens.playback.dca(constants.channel_number_with_several_audio, time_out=constants.DCA_TIMEOUT)
        # Get current audio to change for test ex 'deu'
        current_audio = audio_utility.get_current_playback_audio_language()
        # Get all audios of the live
        audio_list = audio_utility.get_all_playback_audio_language()
        logging.info("current audio = {} - audio list = {} ".format(current_audio, audio_list))

        check(len(audio_list) >= 2, "audios list has only one element, test is impossible !")
        check(test.screens.main_hub.navigate(),
              "Can not access to Hub - current screen is ".format(test.milestones.get_current_screen()))

        check(test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES"), "Can not access to Preferences")

        check(test.screens.main_hub.focus_settings_sub_sub_menu("AUDIO"), "Can not access to AUDIO")
        test.wait(constants.GENERIC_WAIT)
    
        # Check current selected audio is current played audio
        elements = test.milestones.getElements()
        audio_selected = test.milestones.get_value_by_key(elements, "selected_asset").upper()

        for sel_audio, lang in audio_language_dict.items():
            if lang == audio_selected:          # ex: on FRENCH == GERMAN
                if sel_audio == current_audio:  # ex: fre == por
                    logging.info("Currently selected pref audio is the current audio: ok")
                    break
                else:
                    if sel_audio in audio_list:   # in the flux, then should have been selected by default
                        check(False,
                              "Default selected audio {} is not the current audio {}".format(sel_audio, current_audio))
                    else:
                        check(False, "Default selected audio {} is not in the flux".format(sel_audio))
                break
        # exit from 'for loop' without 'break'
        else:
            check(False, "Default selected audio {} is not in the list".format(audio_selected))

        # choose another audio (in the pref audio list) than current played audio
        audio_preferences_list = test.milestones.get_value_by_key(elements, "sub_items")
        nb_assets = len(audio_preferences_list)

        check(nb_assets >= 2, "Language list has less than two elements, test is impossible !")

        for i in range(nb_assets):          # all different audio assets
            logging.info("On asset audio {}".format(audio_preferences_list[i]))

            # Id in dico_lang of the asset focused
            audio_id = audio_language_dict.values().index(audio_preferences_list[i].upper())
            if audio_language_dict.keys()[audio_id] != current_audio \
                    and audio_language_dict.keys()[audio_id] in audio_list:
                logging.info("--> is chosen")
                break
            # Focus the next audio
            test.move_towards('right')
        # Exit from loop without break: no audio chosen
        else:
            check(False, "No new audio chosen settings list {} - audio list {} ".format(audio_preferences_list))

        # Select the focused audio language
        test.validate_focused_item(3)

        test.screens.fullscreen.navigate()
        test.wait(constants.INFOLAYER_TIMEOUT)

        # Get current audio to verify that changing is ok
        new_audio = audio_utility.get_current_playback_audio_language()
        logging.info("New audio on live: {} - old: {})".format(new_audio, current_audio))
        check(new_audio != current_audio, "Current audio is not changed")

    except AssertMgr.Failure:
        test.log("Aborting {}".format(test_name))

    test.assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_settings_default_language #####")
