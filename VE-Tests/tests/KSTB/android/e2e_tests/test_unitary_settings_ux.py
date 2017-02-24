#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import json

import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
import logging
import sys


'''Globals'''
GENERIC_WAIT = 2
WAIT_TIMEOUT = 10

PREF_INDEX = 0      # preferences index
PIN_CODE_PC_INDEX = 1        # pin code and parental control index
SI_INDEX = 2        # system information index

local_debug = True                          # to get more traces with infos on states of the tests


def go_to_setting_from_hub(test, check):
    test.screens.main_hub.navigate()
    check(test.screens.main_hub.focus_settings_item_in_hub(), "can not find setting menu",False)


def check_first_item( test, mylist, mylist2, check, item_key ):

    selected_item = test.milestones.get_value_by_key(test.milestones.getElements(), item_key)     # what is the default focused item at this position
    
    if selected_item != mylist[CONSTANTS.DEFAULT_FOCUSED_INDEX] and selected_item != mylist2[CONSTANTS.DEFAULT_FOCUSED_INDEX]:
        check(False, "first item %s is displayed instead of %s" % (selected_item, mylist[CONSTANTS.DEFAULT_FOCUSED_INDEX]),False)
        if local_debug:
            logging.info("1 check_first_item: we are NOT on the good item: %s (%s)"%(selected_item,mylist[CONSTANTS.DEFAULT_FOCUSED_INDEX]))
    
    elif local_debug:
        logging.info("2 check_first_item: we are on the good item: %s" % selected_item)


def focus_item(test, mylist, mylist2, check, item_key, item_index, direction):
    selected_item = ""                        # valeur d'init par defaut pour pas planter

    for nb in range(0, len(mylist)):
        selected_item = test.milestones.get_value_by_key(test.milestones.getElements(), item_key)
        if selected_item != mylist[item_index] and selected_item != mylist2[item_index]:
            if local_debug:
                logging.info("focus item:  try to go on %s item but is on %s " %(mylist[item_index],selected_item))
            test.move_towards(direction)
        else:
            break
            
    #'verify the item'
    if selected_item != mylist[item_index] and selected_item != mylist2[item_index]:
        check(False, "Failed to find item index %s in setting" % str(item_index),False)
        if local_debug:
            logging.info("2 hs: the final focused item is bad %s (%s)"%(selected_item,mylist[item_index]))
        return False
    elif local_debug:
        logging.info("3 ok: the final focused item is good (%s), go to it..." % selected_item)

    return True


def check_items(test, mylist, mylist2, check, nb_key, item_key, direction):
    nb_items = test.milestones.get_value_by_key(test.milestones.getElements(), nb_key)
    if nb_items != len(mylist):
        check(False, "nb_items is not correct: %d" % nb_items,False)
        if local_debug:
            logging.info("1 hs: number of items is BAD %d/%d"%(nb_items , len(mylist)))
    else:
        # Browse all the items and compare to the expected ones'
        if local_debug:
            logging.info("2 ok: number of items is GOOD %d" % nb_items)
        for nb in range(1, nb_items):
            test.move_towards(direction)
            selected_item = test.milestones.get_value_by_key(test.milestones.getElements(), item_key)
            
            if selected_item != mylist[nb]  and selected_item != mylist2[nb]:
                check( False, "%s is displayed instead of %s" % (selected_item, mylist[nb]),False)
                if local_debug:
                    logging.info("1 hs: items is bad %s (%s)"% (selected_item, mylist[nb]))
            elif local_debug:
                logging.info('2  %d)  focused item is good  %s' % (nb, selected_item))


def check_possible_assets(test, list_choices, check):
    nb_assets = len(list_choices)
    selected_asset = ""
    if nb_assets == 0:
        check(False, "number of assets is zero !",False)
        if local_debug:
            logging.info("1 hs: number of assets is 0")
        return ""
    
    else:
        if local_debug:
            logging.info("0 ok: number of possible assets is: %d" % nb_assets)
        for nb_asset in range(0, nb_assets):
            # Check the label associated to Language (English, Deutsch)'
            focused_asset = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")
            if focused_asset.lower() != list_choices[nb_asset].lower():
                check(False, "%s is displayed instead of %s" % (focused_asset.lower(), list_choices[nb_asset].lower()),False)
                if local_debug:
                    logging.info("1 : asset pos is bad: %s (%s)" %(focused_asset.lower() ,list_choices[nb_asset].lower()))
            elif local_debug:
                    logging.info("2 : asset pos is GOOD: %s (%s)" %(focused_asset.lower() ,list_choices[nb_asset].lower()))
            
            if test.milestones.get_value_by_key(test.milestones.getElements(), "isSelected" )== "true":
                selected_asset = focused_asset
                if local_debug:
                    logging.info("3 : selected asset is: %s" % selected_asset)
            test.move_towards('right')           # focus the next language

        for nb_asset in range(0, nb_assets):
            test.move_towards('left')           # come back to the first position

    return selected_asset


def select_asset(test, expected_asset, list_choices, list_choices2, check, wrap='right'):
    #selected_item = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_item")

    new_focused_asset = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")    # get the new focused asset after validation
    max_mov=len(list_choices)
    while (new_focused_asset != expected_asset) and max_mov:     # the focused has changed and is surely the more on the left
        test.move_towards(wrap,1)                                # new focused language
        new_focused_asset = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")
        max_mov -= 1

    # try to select another asset
    if new_focused_asset.lower() == expected_asset.lower():  # if selected is not the focused
        test.validate_focused_item(3)        # select the focused asset, wait a few, because it can be longer than 1s
        if local_debug:
            logging.info("1 select_asset: select the focused asset: %s" % expected_asset)
    else:
        check(False, "Fail to change selected asset. Focused {} instead of Expected : {}".format(new_focused_asset, expected_asset), False)

    check_selected_asset(test, expected_asset, list_choices, list_choices2, check)

    
def check_selected_asset(test, expected_asset, list_choices, list_choices2, check):
    new_focused_asset = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")    # get the new focused asset after validation
    max_mov=len(list_choices)
    while (new_focused_asset != expected_asset) and max_mov:        # the focused has changed and is surely the more on the left
        test.move_towards('right',1)                                # new focused language
        if local_debug:
            logging.info("2 check_selected_asset: --> move to focused asset" )
        new_focused_asset = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")
        max_mov -= 1

    if test.milestones.get_value_by_key(test.milestones.getElements(), "isSelected") != "true":
        check(False, "Fail to check selected asset (underline):foc: %s" %expected_asset, False)
        if local_debug:
            logging.info("3 hs: focused asset can t be selected: %s " %expected_asset)
    elif local_debug:
        logging.info("4 ok: New selected asset (underline): %s " %expected_asset)


def check_language_changed(test, selected_item, check):
    new_selected_item = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_item")
    if new_selected_item != selected_item:              # check that language became sprache or reverse
        check( False, "Fail to change selected language (display): texts: before: %s  after: %s" % (selected_item , new_selected_item),False)
        if local_debug:
            logging.info("1 display of new selected language fail: must be:%s  should:%s" %(selected_item ,new_selected_item))
    elif local_debug:

        logging.info("2 display of new selected language is GOOD: must be:%s  should:%s" %(selected_item ,new_selected_item))


def check_audio_language(test, check):
    test.wait(GENERIC_WAIT)
    all_elements = test.milestones.getElements()
    if test.milestones.get_value_by_key(all_elements, "isSelected") != "true":
        check(False,"SETTINGS:AUDIO: The preferred audio language is NOT underlined", False)
    else:
        audio_language_selected_item = test.milestones.get_value_by_key(all_elements, "focused_asset")
        if local_debug:
            logging.info(
                "SETTINGS:AUDIO: The preferred audio language is underlined: %s" % audio_language_selected_item)
        he_utils = test.he_utils
        audio_language_from_upm = he_utils.getAudioLanguage()
        full_name_audio_language_from_upm = CONSTANTS.dico_languages[audio_language_from_upm]
        if audio_language_selected_item.lower() != full_name_audio_language_from_upm.lower():
            check(False, "SETTINGS:AUDIO: The preferred audio language is NOT defined in the UPM:"
                         "audio_language_selected_item: %s  audio_language_from_upm: %s"
                         % (audio_language_selected_item,full_name_audio_language_from_upm), False)
        elif local_debug:
            logging.info("SETTINGS:AUDIO: The preferred audio language is the one defined in UPM: %s"
                         % audio_language_selected_item)


def check_closed_caption(test, expected_cc, check):
    test.wait(5)
    playbackStatus = test.milestones.getClientPlaybackStatus()
    ccTrack = playbackStatus['ccTrack']

    # Check if a trackId exists in the list
    if ccTrack['trackId'] != "":
        check(ccTrack['trackId'].lower() == expected_cc.lower(),
              "The current Closed Caption is " + ccTrack['trackId'] + " but " + expected_cc +" is expected",False)

    else :
        check(expected_cc == "None", "The Closed caption should not be presented",False)
    return


def to_preferences_item_from_hub(test, pref_index, check):
    go_to_setting_from_hub(test, check)

    focus_item( test, CONSTANTS.list_settings_eng, CONSTANTS.list_settings_ger, check, "focused_asset", PREF_INDEX, "right")

    # Access to Preferences'
    test.validate_focused_item(1)

    # Check first item'
    check_first_item(test, CONSTANTS.list_preferences_eng, CONSTANTS.list_preferences_ger, check, "focused_item")


    # focus preference item'
    focus_item(test, CONSTANTS.list_preferences_eng, CONSTANTS.list_preferences_ger, check, "focused_item", pref_index, "up")

    test.wait(2)


def settings_preferences(test_title, pref_index, list_choices, list_choices2):
    """
    Check that Preferences has correct items
    """
    test = VeTestApi(title=test_title, useAssertMgr=True)
    test.assertmgr.setup(test_title)
    check = test.assertmgr.addCheckPointLight
    test.begin(screen=test.screens.fullscreen)

    try:
        if pref_index == CONSTANTS.PREF_CLOSED_CAPTION_INDEX:
            # Go to channel for ClosedCaption
            logging.info("Zap on channel number {}".format(CONSTANTS.channel_number_with_closed_caption))
            test.screens.playback.dca(CONSTANTS.channel_number_with_closed_caption, with_ok=True)
            test.wait(CONSTANTS.INFOLAYER_TIMEOUT+ CONSTANTS.GENERIC_WAIT)

            channel_lcn = test.milestones.get_value_by_key(test.milestones.getElements(),"current_channel")

            check(channel_lcn == CONSTANTS.channel_number_with_closed_caption,
                  "Initials Conditions: Zapping on channel n {0} fails, Current channel playing n {1}"
                  .format(CONSTANTS.channel_number_with_closed_caption,channel_lcn))

            check(test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING",
                  "Initials Conditions: Zapping on channel n {}, the video is not playing"
                  .format(CONSTANTS.channel_number_with_closed_caption))

        reload(sys)
        # To treat string as utf8 (ascii by default) to avoid crash with text containing Ü or Ä ...
        sys.setdefaultencoding("utf-8")

        # Select the preference index
        to_preferences_item_from_hub(test, pref_index, check)

        # start the item test
        # Check possible assets
        selected_asset = check_possible_assets(test ,list_choices ,check)
        check(selected_asset != "", "no item selected by default")

        # Should take into account the None case
        NONE_IS_PRESENT = (list_choices[CONSTANTS.DEFAULT_FOCUSED_INDEX] == "None")
        logging.info('NONE_IS_PRESENT %s' %str(NONE_IS_PRESENT))

        if NONE_IS_PRESENT and pref_index == CONSTANTS.PREF_CLOSED_CAPTION_INDEX:
            check_closed_caption( test,"None",check)

        # Check the default language after boot is underlined and is the preferred one defined in the UPM
        if pref_index == CONSTANTS.PREF_AUDIO_INDEX:
            check_audio_language(test, check)

        zap_up = True              # to switch between zap+ and zap- to don't go on non existing channel
        for expected_asset in list_choices:

            logging.info('Expected asset {} will be selected'.format(expected_asset))

            # Select then validated another asset and check that the selected item is modified
            select_asset(test,expected_asset,list_choices,list_choices2,check)

            # TODO the navigation does not work correctly if the UI language is changed
            # we should not navigate in this case

            if pref_index != CONSTANTS.PREF_LANGUAGE_INDEX:
                # Go to full screen in order to know if the preference settings is persistent after a zapping
                logging.info('zapping to check persistent info -->')
                # test.screens.main_hub.navigate()
                test.screens.fullscreen.navigate()

                # zap and go back to preferences
                if zap_up:
                    test.screens.playback.zap_to_next_channel(8)
                    zap_up = False
                else:
                    test.screens.playback.zap_to_previous_channel(8)
                    zap_up = True

                test.screens.main_hub.navigate()
                to_preferences_item_from_hub(test, pref_index, check)
                logging.info('<-- has zapped, will check for persistent info ')
                # Check the selected item is not changed after zapping
                check_selected_asset(test, expected_asset, list_choices, list_choices2, check)

            # special for language test
            if pref_index == CONSTANTS.PREF_LANGUAGE_INDEX: # check the ui has changed after the selection
                # list_items_languages
                lang_id = list_choices.index(expected_asset)
                check_language_changed( test, CONSTANTS.list_items_languages[lang_id], check )
                # Go to hub to go back to:  hub:settings -> preference -> language
                # and verify ui language on each item
                test.screens.fullscreen.navigate()
                test.screens.main_hub.navigate()
                maxitem = 15           # max try to go on an item
                loop = maxitem         # until a complete loop
                first_item = ""
                l_items_live = ["LIVE TV","LIVE","Ao Vivo"]
                l_items_settings = ["SETTINGS","EINSTELLUNGEN","Configurações"]
                l_assets_settings = ["PREFERENCES","VORLIEBEN","PREFERÊNCIAS"]
                # select the first lists to find items/assets in
                l_items = l_items_settings
                l_assets = l_assets_settings

                while loop:
                    item = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_item")
                    asset = test.milestones.get_value_by_key( test.milestones.getElements(), "focused_asset")
                    if first_item == "":
                        first_item = item

                    # Item live must be with good language and current asset good extension ex: S1103S51E075:LONG:eng
                    # for english
                    if item in l_items_live:
                        logging.info("on live item")
                        if item == l_items_live[lang_id]:
                            logging.info("ui live item has good language")
                            if ":" in asset:
                                lang_extension = asset.split(":")[-1]
                                if lang_extension == CONSTANTS.list_devices_languages[lang_id]:
                                    logging.info("asset of live has good language extension")
                                else:
                                    check(False, "asset of live has bad language extension {} instead of {}"
                                          .format(lang_extension , CONSTANTS.list_devices_languages[lang_id]),False)
                        else:
                            check(False, "ui has bad live item language: {} instead of {}"
                                  .format(item ,l_items_live[lang_id]),False)
                    elif first_item == item:
                        logging.info("complete loop without finding good item !")
                        check(False, "item not found in the list %s" % ([""]),False)
                        break

                    if item == l_items[lang_id] and asset == l_assets[lang_id]:   # on the good item of the screen
                        if l_items == l_items_settings:
                            logging.info("on the good item, validating it to go to the next screen")
                            test.validate_focused_item(2)           # we check it
                            logging.info("select new list of item to check on this screen")
                            # to go to the next level
                            l_items = CONSTANTS.list_items_languages
                            # by default, the focus is on the first asset of the list not the selected asset
                            l_assets = [CONSTANTS.list_languages[0],CONSTANTS.list_languages[0],CONSTANTS.list_languages[0]]
                        else:
                            logging.info("on the last screen: it s good !")
                            break
                        loop = maxitem
                    #else:
                    test.move_towards('up',2)   # move to next item
                    loop -= 1
                    if loop == 0:
                        logging.info("max item reached:  lost in the test moving")
                        check(False, "lost when moving in the test, max item reached",False)

            elif pref_index == CONSTANTS.PREF_CLOSED_CAPTION_INDEX:
                check_closed_caption(test, expected_asset, check)
            elif pref_index == CONSTANTS.PREF_AUDIO_INDEX:
                # Check the new selected audio language is underlined
                # and than the preferred audio language defined in the UPM is updated
                check_audio_language(test, check)

            # Re-Select the first asset (mainly to check None case)
            select_asset(test,list_choices[0],list_choices,list_choices2,check ,wrap='left')

            # After select we need to go out the preferences and go in again to refresh the cookies
            test.screens.main_hub.navigate()
            to_preferences_item_from_hub(test, pref_index, check)
            if pref_index == CONSTANTS.PREF_CLOSED_CAPTION_INDEX:
                check_closed_caption(test, list_choices[0], check)

    except AssertMgr.Failure:
        test.log("Aborting {}".format(test_title))

    test.assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### end of %s #####" %test_title)


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.LV_L2
def test_settings_home_page_items():
    '''
    Check that Settings Home page has correct items
    '''
    test_title = "test_settings_home_page_items"
    test = VeTestApi(title=test_title, useAssertMgr=True)
    test.assertmgr.setup(test_title)
    check = test.assertmgr.addCheckPointLight
    test.begin(screen=test.screens.fullscreen)
    go_to_setting_from_hub(test, check)

    # Check first item'
    check_first_item(test,CONSTANTS.list_settings_eng,CONSTANTS.list_settings_ger,check,"focused_asset")
    
    # Check the items in list setting'
    check_items(test,CONSTANTS.list_settings_eng,CONSTANTS.list_settings_ger,check,"nb_asset_label","focused_asset","right")

    # Check that the list is not circular by upping one more time
    test.move_towards('right')
    selected_item = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")
    if local_debug:
        logging.info('focused item is %s' %(selected_item))
    if selected_item != CONSTANTS.list_settings_eng[len(CONSTANTS.list_settings_eng)-1] and selected_item != CONSTANTS.list_settings_ger[len(CONSTANTS.list_settings_eng)-1]:
        check(False, "last item %s is displayed instead of %s" % (selected_item, CONSTANTS.list_settings_eng[len(CONSTANTS.list_settings_eng)-1]),False)
        if local_debug:
            logging.info("3.1 tshpi hs: the list seems circular, last item: %s (%s)"% (selected_item, CONSTANTS.list_settings_eng[len(CONSTANTS.list_settings_eng)-1]))
    elif local_debug:
        logging.info("3.2 tshpi ok: the list is not circular")
    
    test.assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_settings_home_page_items #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Settings
@pytest.mark.F_Clock
@pytest.mark.LV_L3
def test_check_clock_in_settings():
    test_title = "test_check_clock_in_settings"
    test = VeTestApi(title=test_title)

    test.begin(screen=test.screens.fullscreen)

    status = test.screens.main_hub.navigate()
    test.log_assert(status, "Failed to go to MainHub. Current screen: %s" % test.milestones.get_current_screen())

    status = test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES")
    test.log_assert(status, "Failed to go to the full Screen. Current screen: %s" % test.milestones.get_current_screen())

    clock_time = test.get_clock_time()
    if not clock_time:
        test.log_assert(False, "The Clock is not displayed in live ActionMenu")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = test.check_clock_time_update(clock_time)
    test.log_assert(status, "Clock is not more displayed after 1 min. Current screen: %s" % test.milestones.get_current_screen())

    test.end()
    logging.info("##### End test_check_clock_in_settings #####")


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.LV_L2
def test_settings_system_information():
    '''
    Check that the App version is displayed in the System Information
    '''
    test_title = "test_settings_system_information"
    test = VeTestApi(title=test_title, useAssertMgr=True)
    test.assertmgr.setup(test_title)

    check = test.assertmgr.addCheckPointLight
    test.begin(screen=test.screens.fullscreen)
    
    go_to_setting_from_hub(test, check)

    if focus_item(test,CONSTANTS.list_settings_eng,CONSTANTS.list_settings_ger,check,"focused_asset",SI_INDEX,"right"):
        test.validate_focused_item(1)  # go into SI item
       
        if focus_item(test,CONSTANTS.list_sysinfo_eng,CONSTANTS.list_sysinfo_ger,check,"focused_item",CONSTANTS.SETTINGS_SYSINFO_SYSINFO_INDEX,"up"):
            dict_SysInfo = {}
            milelements = test.milestones.getElements()
            nb_text = int(test.milestones.get_value_by_key(milelements, "list_size"))
            nb_pairs = int(test.milestones.get_value_by_key(milelements, "pair_size"))
    
            for i in range(0, nb_text):
                for j in range(0, nb_pairs):
                    key = test.milestones.get_value_by_key(milelements, "pair_key_%s_%s" %(i,j))
                    value = test.milestones.get_value_by_key(milelements, "pair_value_%s_%s" %(i,j))
                    if local_debug:
                        logging.info("tssi: key: %s  value:%s" %(key, value))
                    dict_SysInfo[key] = value
    
            # Check that the IPTV App Version is displayed with a value associated'
            if dict_SysInfo.has_key("IPTV App Version") == False:
                check( False, "IPTV App Version key is NOT displayed",False)
                if local_debug:
                    logging.info("2.1  tssi hs: IPTV App Version key is NOT displayed")
    
            # Get the version from the app'
            device_details = test.milestones.getDeviceDetails()
            current_app_version = device_details["app-version-name"]
    
            # Compare the 2 versions: this will only indicate that something is displayed'
            if current_app_version != dict_SysInfo.get("IPTV App Version"):
                check( False, "IPTV App Version value is NOT correct: %s" %dict_SysInfo.get("IPTV App Version"),False)
                if local_debug:
                    logging.info("3.1  tssi hs: IIPTV App Version value is NOT correct: %s (%s)"%(dict_SysInfo.get("IPTV App Version"),current_app_version))

    test.assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_settings_system_information #####")


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.LV_L2
def test_settings_preferences_home_page():
    '''
    Check that Preferences Home page has correct items
    '''
    test_title = "test_settings_pref_home_page"
    test = VeTestApi(title=test_title, useAssertMgr=True)
    test.assertmgr.setup(test_title)
    check = test.assertmgr.addCheckPointLight
    test.begin(screen=test.screens.fullscreen)

    go_to_setting_from_hub(test, check)

    focus_item(test,CONSTANTS.list_settings_eng,CONSTANTS.list_settings_ger,check,"focused_asset",PREF_INDEX,"right")
    
    test.validate_focused_item(2)  # go into preferences item
    
    # Check first item'
    check_first_item(test,CONSTANTS.list_preferences_eng,CONSTANTS.list_preferences_ger,check,"focused_item")

    # Check the items in list preferences' 
    check_items(test,CONSTANTS.list_preferences_eng,CONSTANTS.list_preferences_ger,check,"number_of_nodes","focused_item","up")

    test.assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_settings_preferences_home_page #####")
     

@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.F_Preferences
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_settings
@pytest.mark.QA_language
def test_settings_preferences_language():

    settings_preferences("test_settings_pref_language",CONSTANTS.PREF_LANGUAGE_INDEX,CONSTANTS.list_languages,CONSTANTS.list_languages)


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.F_Preferences
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_settings
@pytest.mark.QA_subtitle
def test_settings_preferences_subtitle():

    settings_preferences("test_settings_pref_subtitle",CONSTANTS.PREF_SUBTITLE_INDEX,CONSTANTS.list_subtitles_eng,CONSTANTS.list_subtitles_ger)


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.F_Preferences
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_settings
@pytest.mark.QA_audio
def test_settings_preferences_audio():

    settings_preferences("test_settings_pref_audio",CONSTANTS.PREF_AUDIO_INDEX,CONSTANTS.list_audio_language_eng,CONSTANTS.list_audio_language_ger)


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.F_Preferences
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_settings
@pytest.mark.QA_close_caption
def test_settings_preferences_closed_caption():

    settings_preferences("test_settings_pref_closed_caption",CONSTANTS.PREF_CLOSED_CAPTION_INDEX,CONSTANTS.list_closedcaption_eng,CONSTANTS.list_closedcaption_ger)


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.LV_L2
def test_settings_logout():    
    '''
    Check that logout default option is return to hub
    '''
    test_title = "test_settings_logout"
    test = VeTestApi(title=test_title, useAssertMgr=True)
    test.assertmgr.setup(test_title)
    check = test.assertmgr.addCheckPointLight
    test.begin(screen=test.screens.fullscreen)
    go_to_setting_from_hub(test, check)

    # Access to the Preferences'
    if focus_item(test,CONSTANTS.list_settings_eng,CONSTANTS.list_settings_ger,check,"focused_asset",SI_INDEX,"right"):
        test.validate_focused_item(1)  # go into SI item
        if focus_item(test,CONSTANTS.list_sysinfo_eng,CONSTANTS.list_sysinfo_ger,check,"focused_item",CONSTANTS.SETTINGS_SYSINFO_LOGOUT_INDEX,"up"):
            focused_asset = test.milestones.get_value_by_key(test.milestones.getElements(), "focused_asset")
            if focused_asset.lower() not in ['no','nein']:
                check(2, False, "default asset is not 'no' (%s)"%focused_asset,False)
                if local_debug:
                    logging.info("2.1  tsl hs: the default asset is not 'no' (%s)"%focused_asset)
            else:
                if local_debug:
                    logging.info("3.0  tsl ok: the default asset is  'no'")
                test.validate_focused_item(2)        # verifiy we go back to hub
                    # check the hub screen is displayed
                screen_name = test.milestones.get_current_screen()
                if screen_name != 'main_hub':
                    check( False, "Failed to return to hub",False)
                    if local_debug:
                        logging.info("3.1  tsl hs: Failed to return to hub (%s)" % screen_name)
                elif local_debug:
                    logging.info("3.2  tsl ok: we returned to hub")

    test.assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_settings_logout #####")


def get_pincode_message(test):
    '''
    Get Message displayed to the screen
    '''

    msg = test.milestones.get_value_by_key(test.milestones.getElements(), "pincode_message")
    pincode_msg = msg.replace("\n"," ").strip()     # retire les debuts/fin de ligne foireux

    logging.info("test_settings_pincode_parentalcontrol pincode_msg %s " %(pincode_msg))

    return pincode_msg


def check_pincode_message(test, expected_msg, exact=True):
    '''
    Check message is correct
    msg: string to compare to expected_msg
    expected_msg: array of strings to which msg has to be compared
    exact: true when we are expecting expected_msg exactly, false when we are expecting that expected_msg is contained into the message
    '''

    msg = get_pincode_message(test)

    if exact:
        test.log_assert(msg == expected_msg[0] or msg == expected_msg[1], "expected pincode message: '%s' or '%s', actual message: '%s'" %(expected_msg[0],expected_msg[1],msg))
    else:
        test.log_assert(expected_msg[0] in msg or expected_msg[1] in msg, "expected pincode message: '%s' or '%s', actual message: '%s"'' %(expected_msg[0],expected_msg[1],msg))


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.LV_L2
def test_settings_change_parental_code():
    '''
    Check parental pin code change:
    - Step 1: check wrong pin entered
    - Step 2: check effective change
    - Step 3: check wrong pin format
    - Step 4: check wrong pin confirmation
    '''
    test_title = "test_settings_change_parental_code"
    test = VeTestApi(title=test_title, useAssertMgr=True)
    test.assertmgr.setup(test_title)
    check = test.assertmgr.addCheckPointLight

    test.begin(screen=test.screens.fullscreen)

    # Set current pin code
    he_utils = test.he_utils
    credentials = he_utils.get_default_credentials()
    hhid = credentials[0]
    logging.info("test_settings_pincode_parentalcontrol hhid " + hhid)

    PIN_FIRST = "1234"
    PIN_1234 = ["KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ]
    PIN_SECOND = "2345"
    PIN_2345 = ["KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ]
    PIN_WRONG = "1112"
    PIN_1112 = ["KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ]

    # strings below are identified by their keys in CTAP dictionnary
    PIN_WRONG_PIN = "dict.parentalControl.modifyYouthPin.EPinInvalid"
    ENTER_CURRENT_PIN_MSG = "dict.parentalControl.modifyYouthPin.definedPin"
    ENTER_NEW_PIN_MSG = "dict.parentalControl.modifyYouthPin.newPin"
    RE_ENTER_NEW_PIN_MSG = "dict.parentalControl.modifyYouthPin.verifyNewPin"
    PIN_HAS_CHANGED_MSG = "dict.parentalControl.modifyYouthPin.success"
    PIN_WRONG_FORMAT_MSG = "dict.parentalControl.modifyYouthPin.EPinFormat"
    PIN_WRONG_CONFIRMATION_MSG = "dict.parentalControl.modifyYouthPin.EPinsDoesNotMatch"

    dict_PinCode = {}
    dict_PinCode[PIN_WRONG_PIN] = ["Wrong Pin","de_wrongYouthPinMsg"]
    dict_PinCode[ENTER_CURRENT_PIN_MSG] = ["Please enter your  current Parental PINCODE","de_definedPin"]
    dict_PinCode[ENTER_NEW_PIN_MSG] = ["Please enter your new PINCODE","de_enterNewYouthPinMsg"]
    dict_PinCode[RE_ENTER_NEW_PIN_MSG] = ["Please confirm your new PINCODE","de_reEnterNewYouthPinMsg"]
    dict_PinCode[PIN_HAS_CHANGED_MSG] = ["PIN has been changed successfully","de_succeedSetNewYouthPinMsg"]
    dict_PinCode[PIN_WRONG_FORMAT_MSG] = ["Policy fail Please enter different pin","de_policyFailNewYouthPinMsg"]
    dict_PinCode[PIN_WRONG_CONFIRMATION_MSG] = ["Pins do not match Please enter your new PINCODE","de_notEqualNewYouthPinMsg"]

    he_utils.setParentalPin(hhid, PIN_FIRST)
    test.log_assert(PIN_FIRST == he_utils.getParentalpincode(),"Parental Pin code should be set to %s" %PIN_FIRST)

    # Move to SETTINGS item
    go_to_setting_from_hub(test, check)

    # go into PIN CODE AND PARENTAL CONTROL menu
    if focus_item(test,CONSTANTS.list_settings_eng,CONSTANTS.list_settings_ger,check,"focused_asset",PIN_CODE_PC_INDEX,"right"):
        test.validate_focused_item(2)

        #########
        # Step 1: check wrong pin entered
        #########
        if focus_item(test,CONSTANTS.list_pin_parental_control_eng,CONSTANTS.list_pin_parental_control_ger,check,"focused_item",CONSTANTS.CHANGE_PARENTAL_PIN_INDEX,"up"):
        # go into CHANGE PARENTAL PIN CODE itemÒ
            test.validate_focused_item(2)

            # check pin code message "Please enter your current Parental PIN"
            check_pincode_message(test,dict_PinCode[ENTER_CURRENT_PIN_MSG])

            # enter different pin than current one
            test.screens.pincode.enter_pincode(PIN_2345)
            test.wait(2)

            # check message: "WRONG PIN 2 TRIES LEFT ..."
            check_pincode_message(test,dict_PinCode[PIN_WRONG_PIN],exact=False)

            # go back to PIN CODE AND PARENTAL CONTROL menu
            test.go_to_previous_screen(2)

        #########
        # Step 2: check effective change of parental pin code
        #########
        if focus_item(test,CONSTANTS.list_pin_parental_control_eng,CONSTANTS.list_pin_parental_control_ger,check,"focused_item",CONSTANTS.CHANGE_PARENTAL_PIN_INDEX,"up"):
            # go into CHANGE PARENTAL PIN CODE item
            test.validate_focused_item(2)

            # check pin code message "Please enter your current Parental PIN"
            check_pincode_message(test,dict_PinCode[ENTER_CURRENT_PIN_MSG])

            # enter current pin
            test.screens.pincode.enter_pincode(PIN_1234)
            test.wait(2)

            # check message "PLEASE ENTER YOUR NEW PINCODE"
            check_pincode_message(test,dict_PinCode[ENTER_NEW_PIN_MSG])

            # enter new pin
            test.screens.pincode.enter_pincode(PIN_2345)
            test.wait(2)

            # check message "PLEASE ENTER NEW PIN AGAIN"
            check_pincode_message(test,dict_PinCode[RE_ENTER_NEW_PIN_MSG])

            # re enter new pin
            test.screens.pincode.enter_pincode(PIN_2345)
            test.wait(2)

            # check message "PIN HAS BEEN CHANGED SUCCESSFULLY"
            check_pincode_message(test,dict_PinCode[PIN_HAS_CHANGED_MSG])

            # check pin change in household
            test.log_assert(PIN_SECOND == he_utils.getParentalpincode(),"Parental Pin code should be set to %s" %PIN_SECOND)

            # go back to PIN CODE AND PARENTAL CONTROL menu
            test.go_to_previous_screen(2)

        #########
        # Step 3: check entering wrong pin format
        #########
        if focus_item(test,CONSTANTS.list_pin_parental_control_eng,CONSTANTS.list_pin_parental_control_ger,check,"focused_item",CONSTANTS.CHANGE_PARENTAL_PIN_INDEX,"up"):
            # go into CHANGE PARENTAL PIN CODE item
            test.validate_focused_item(2)

            # check pin code message "Please enter your current Parental PIN"
            check_pincode_message(test,dict_PinCode[ENTER_CURRENT_PIN_MSG])

            # enter current pin
            test.screens.pincode.enter_pincode(PIN_2345)
            test.wait(2)

            # check message "PLEASE ENTER YOUR NEW PIN"
            check_pincode_message(test,dict_PinCode[ENTER_NEW_PIN_MSG])

            # enter new pin with wrong format
            test.screens.pincode.enter_pincode(PIN_1112)
            test.wait(2)

            # check message "Policy fail Please enter different pin"
            check_pincode_message(test,dict_PinCode[PIN_WRONG_FORMAT_MSG])

            # go back to PIN CODE AND PARENTAL CONTROL menu
            test.go_to_previous_screen(2)


        #########
        # Step 4: check entering wrong confirmation pin
        #########
        if focus_item(test,CONSTANTS.list_pin_parental_control_eng,CONSTANTS.list_pin_parental_control_ger,check,"focused_item",CONSTANTS.CHANGE_PARENTAL_PIN_INDEX,"up"):
            # go into CHANGE PARENTAL PIN CODE item
            test.validate_focused_item(2)

            # check pin code message "Please enter your current Parental PIN"
            check_pincode_message(test,dict_PinCode[ENTER_CURRENT_PIN_MSG])

            # enter current pin
            test.screens.pincode.enter_pincode(PIN_2345)
            test.wait(2)

            # check message "PLEASE ENTER YOUR NEW PIN"
            check_pincode_message(test,dict_PinCode[ENTER_NEW_PIN_MSG])

            # enter new pin
            test.screens.pincode.enter_pincode(PIN_1234)
            test.wait(2)

            # check message "PLEASE ENTER NEW PIN AGAIN"
            check_pincode_message(test,dict_PinCode[RE_ENTER_NEW_PIN_MSG])

            # enter different new pin
            test.screens.pincode.enter_pincode(PIN_2345)
            test.wait(2)

            # check message "PIN DOESN'T MATCH"
            check_pincode_message(test,dict_PinCode[PIN_WRONG_CONFIRMATION_MSG])

    test.assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_settings_pincode_parentalcontrol #####")


@pytest.mark.non_regression
@pytest.mark.FS_Settings
@pytest.mark.LV_L2
def test_settings_change_parental_threshold():
    '''
    Check parental threshold setting:
    - Step 1: go to menu "MODIFY PARENTAL THRESHOLD"
    - Step 2: Enter Parental Pin
    - Step 3: check Parent Threshold is set OFF
              check Parent Threshold is set C7+
              check Parent Threshold is set T13+
              check Parent Threshold is set YA17+
    '''
    test_title = "test_settings_change_parental_threshold"
    test = VeTestApi(title=test_title, useAssertMgr=True)
    test.assertmgr.setup(test_title)
    check = test.assertmgr.addCheckPointLight
    test.begin(screen=test.screens.fullscreen)

    # Set current pin code
    he_utils = test.he_utils
    hhid = he_utils.getHhId()

    logging.info("test_settings_threshold_parentalcontrol hhid " + hhid)
    PIN_CODE = "1234"
    PIN_SEQ = ["KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ,"KEYCODE_DPAD_RIGHT" ,"KEYCODE_DPAD_CENTER" ]
    ENTER_CURRENT_PIN_MSG = "dict.parentalControl.modifyYouthPin.definedPin"
    dict_PinCode = {}
    dict_PinCode[ENTER_CURRENT_PIN_MSG] = ["Please enter your current Parental PIN","de_definedPin"]

    he_utils.setParentalPin(hhid, PIN_CODE)
    test.wait(WAIT_TIMEOUT)

    pin = he_utils.getParentalpincode()
    assert PIN_CODE == pin
    logging.info("Parental Pin code should be set to" + pin)

    ###
    # Step1
    ###
    # Move to SETTINGS item
    test.wait(GENERIC_WAIT) #should be on fullscreen after the test.wait(WAIT_TIMEOUT) but wait GENERIC_WAIT to be sure
    test.repeat_key_press("KEYCODE_BACK", 1, 2) #go back on hub
    logging.info("Should be on main_hub ")

    go_to_setting_from_hub(test, check)
    test.wait(GENERIC_WAIT)
    # go into PIN CODE AND PARENTAL CONTROL menu
    if focus_item(test,CONSTANTS.list_settings_eng,CONSTANTS.list_settings_ger, check,"focused_asset",PIN_CODE_PC_INDEX,"right"):
        test.validate_focused_item(2)

    ###
    # Step2
    ###
        if focus_item(test,CONSTANTS.list_pin_parental_control_eng,CONSTANTS.list_pin_parental_control_ger,
                      check,"focused_item",CONSTANTS.MODIFY_PARENTAL_THRESHOLD_INDEX,"up"):
            # go into CHANGE PARENTAL PIN CODE item
            test.validate_focused_item(2)

            # check pin code message "Please enter your current Parental PIN"
            #check_pincode_message(test,dict_PinCode[ENTER_CURRENT_PIN_MSG])

            # enter pincode
            test.screens.pincode.enter_pincode(PIN_SEQ)
            test.wait(2)

            ###
            # Step3
            ###
            if focus_item(test,CONSTANTS.list_parental_threshold_policy,CONSTANTS.list_parental_threshold_policy2,
                          check,"focused_asset",CONSTANTS.POLICY_OFF_INDEX,"right"):
                ### setParental thr to OFF
                test.validate_focused_item(GENERIC_WAIT)
                assert str(he_utils.getHouseHoldPrentalThreshold()) == str(CONSTANTS.list_pcpe_maxrating[CONSTANTS.POLICY_OFF_INDEX])

            if focus_item(test,CONSTANTS.list_parental_threshold_policy,CONSTANTS.list_parental_threshold_policy2,
                          check,"focused_asset",CONSTANTS.POLICY_YA17_INDEX,"right"):
                # go to next PARENTAL THRESHOLD POLICY item
                test.validate_focused_item(WAIT_TIMEOUT)
                assert str(he_utils.getHouseHoldPrentalThreshold()) == str(CONSTANTS.list_pcpe_maxrating[CONSTANTS.POLICY_YA17_INDEX])

            if focus_item(test,CONSTANTS.list_parental_threshold_policy,CONSTANTS.list_parental_threshold_policy2,
                          check,"focused_asset",CONSTANTS.POLICY_T13_INDEX,"right"):
                # go to next PARENTAL THRESHOLD POLICY item
                test.validate_focused_item(WAIT_TIMEOUT)
                assert str(he_utils.getHouseHoldPrentalThreshold()) == str(CONSTANTS.list_pcpe_maxrating[CONSTANTS.POLICY_T13_INDEX])

            if focus_item(test,CONSTANTS.list_parental_threshold_policy,CONSTANTS.list_parental_threshold_policy2,
                          check,"focused_asset",CONSTANTS.POLICY_C7_INDEX,"right"):
                # go to next PARENTAL THRESHOLD POLICY item
                test.validate_focused_item(WAIT_TIMEOUT)
                assert str(he_utils.getHouseHoldPrentalThreshold()) == str(CONSTANTS.list_pcpe_maxrating[CONSTANTS.POLICY_C7_INDEX])

    test.assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_settings_threshold_parentalcontrol #####")

