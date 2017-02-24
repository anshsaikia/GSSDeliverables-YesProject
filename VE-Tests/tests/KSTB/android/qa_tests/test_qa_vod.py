__author__ = 'Oceane Team'

import pytest
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.playback import VODManager
from tests_framework.ve_tests.assert_mgr import AssertMgr

#########################################################
#                       PRIVATES Functions              #
#########################################################


def check_qa_pincode_screen(test_vod):
    """
    private function, checks pin code screen
    :param test_vod: instance of object VeTestApi()
    :return: None
    """
    # Pincode entry should be displayed
    elements = test_vod.milestones.getElements()
    logging.info("[VOD][INFO] >> getElements = "+str(elements))
    pincode_msg = test_vod.milestones.get_value_by_key(elements, "pincode_message")
    logging.info("[VOD][INFO] >> getElements pincode_msg "+str(pincode_msg))
    test_vod.log_assert(pincode_msg == 'LOCKED PROGRAM\nPlease enter your PINCODE',
                    "VOD:RATING: expected pincode message LOCKED PROGRAM\nPlease enter your PINCODE, "
                    "actual message "+str(pincode_msg))


#########################################################
#                       TESTS Functions                 #
#########################################################

# TO DO : writing test scenario : playback VOD asset after rent

@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_catalogue_browsing
def test_qa_vod_catalogue_browsing():
    """
     TEST: Check that we can browse VOD catalogue, categories list and sub-categories

      1st step : we are in HUB Screen
         Action
         - go to STORE
         Checkup
         - check that VOD catalogue is displayed using the default UI language

      2nd step : we are in STORE Screen
         Action
         - go to the list retrieved
         Checkup
         - check the VOD categories list retrieve from the Head End, and enable the user to select from that list

      3rd step : we are in STORE Screen
         Action
         - navigate through the retrieved list
         Checkup
         - check it is possible to browse through assets and/or sub-categories that belong to a category

     """
    logging.info("##### BEGIN test_qa_vod_catalogue_browsing #####")
    store_assets_list = []
    test_vod = VeTestApi(title="test_qa_vod_catalogue_browsing")
    # Test starting
    test_vod.begin(screen=test_vod.screens.fullscreen)
    test_vod.screens.main_hub.navigate()
    # Go to STORE
    status = test_vod.screens.main_hub.focus_store_item_in_hub()
    test_vod.log_assert(status,"CATALOGUE:BROWSING: Fail to go to Store")

    # Retrieve editorial contents from CMDC request:
    # Get CatalogId
    catId = test_vod.he_utils.getCatalogueId(test_vod.he_utils.platform)
    logging.info("[VOD][INFO] >> CatalogueId : %s" % catId)
    test_vod.log_assert((catId is not 0), "CATALOGUE:BROWSING: No Cat ID Found by CMDC")

    # Get Root ClassificationId from CatalogId
    rootclass_id = test_vod.he_utils.get_rootClassificationID_from_catalogId(catId)
    logging.info("[VOD][INFO] >> rootclass_id : %s" % rootclass_id)
    test_vod.log_assert((rootclass_id != 0), "CATALOGUE:BROWSING: No rootclassID Found by CMDC")

    # Get Classification Type 41 in root classification from CatalogID and Root CatalogId
    # editorial classification type is 41
    class_type41_list = test_vod.he_utils.get_classification_from_catId_rootclassId_typeId(catId, rootclass_id, 41)
    test_vod.log_assert((class_type41_list != []), "CATALOGUE:BROWSING: No Classification type41 in catalog")

    # Get all assets ID & InstanceID of all 41 type classificationId from Classification List
    diccmdcassetsids, cmdc_assets_list = test_vod.he_utils.get_assetIds_from_classif_list(catId, class_type41_list)
    test_vod.log_assert((diccmdcassetsids != {}), "CATALOGUE:BROWSING: No assets typed type41 in catalog")

    # Retrieve assets displayed to Store Menu
    all_elements = test_vod.milestones.getElements()
    asset_name = test_vod.milestones.get_value_by_key(all_elements,"focused_asset")

    while asset_name not in store_assets_list:  # loop to count assets
        logging.info("[VOD][INFO] >> assetName: %s" % asset_name)
        store_assets_list.append(asset_name)
        test_vod.move_towards('right', 1)  # next asset
        all_elements = test_vod.milestones.getElements()
        asset_name = test_vod.milestones.get_value_by_key(all_elements,"focused_asset")  # get the next focused asset

    if len(cmdc_assets_list) > len(store_assets_list):
        for asset in store_assets_list:
            status = asset in cmdc_assets_list
            test_vod.log_assert(status, "%s CATALOGUE:BROWSING: does not belong to cmdc editorial assets list" % asset)
    else:
        for asset in cmdc_assets_list:
            status = asset in store_assets_list
            test_vod.log_assert(status, "%s CATALOGUE:BROWSING: does not belong to Hub Store assets list" % asset)

    # Check that the user can select each asset from the retrieved assets list
    nb_assets = len(store_assets_list)
    for _nb in range(1, nb_assets):
        # Press "OK" to select an asset
        test_vod.validate_focused_item(CONSTANTS.LONG_WAIT)
        # check the hub screen is displayed
        screen_name = test_vod.milestones.get_current_screen()
        test_vod.log_assert(screen_name == 'action_menu', "CATALOGUE:BROWSING: expected screen is action_menu, "
                                                          "but actual screen is " + str(screen_name))
        # Press Back to leave the action menu screen
        test_vod.appium.key_event("KEYCODE_BACK")
        test_vod.wait(CONSTANTS.GENERIC_WAIT)
        test_vod.move_towards("left")

    logging.info("##### END test_qa_vod_catalogue_browsing #####")
    test_vod.end()


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_play
def doc_test_qa_vod_playback_play():
    """
    First step : Play a vod asset
        Action
        - launch a VOD asset
        Checkup
        - check that  user is able to play a VOD asset and default audio is selected
    logging.info("##### Begin test_qa_vod_playback_play #####")
    test_ui_vod_play()
    logging.info("##### End test_qa_vod_playback_play #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_forward
def doc_test_qa_vod_playback_fast_forward():
    """
    First step : select a vod asset
        Action
        - play a VOD asset
        Checkup
        - check that user is able to perform fast forward during playback of VOD asset
    
    logging.info("##### Begin test_qa_vod_playback_fast_forward #####")
    test_ui_vod_seek_forward_during_play()
    logging.info("##### End test_qa_vod_playback_fast_forward #####")
    """

@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_backward
def doc_test_qa_vod_playback_fast_backward():
    """
    First step : select a vod asset
        Action
        - play a VOD asset
        Checkup
        - check that user is able to perform fast fast backward during playback of VOD asset
    logging.info("##### Begin test_qa_vod_playback_fast_backward #####")
    test_ui_vod_seek_backward_during_play()
    logging.info("##### End test_qa_vod_playback_fast_backward #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_eof_ffwd
def doc_test_qa_vod_playback_eof_ffwd():
    """
    First step : select a vod asset
        Action
        - play a VOD asset
        Checkup
        - check that user is able to reach the end of the playback in fast forward mode with FastFWD
    logging.info("##### Begin test_qa_vod_playback_eof_ffwd #####")
    test_ui_vod_seek_eof_in_play_mode()
    logging.info("##### End test_qa_vod_playback_eof_ffwd #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_bof_fbwd
def doc_test_qa_vod_playback_bof_fbwd():
    """
    First step : select a vod asset
        Action
        - play a VOD asset
        Checkup
        - check that user is able to reach the start of the playback in fast backward mode with FastRWD
    logging.info("##### Begin test_qa_vod_playback_bof_fbwd #####")
    test_ui_vod_seek_bof_in_play_mode()
    logging.info("##### End test_qa_vod_playback_bof_fbwd #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_stop
def doc_test_qa_vod_playback_stop():
    """
    First step : select a vod asset
        Action
        - play a VOD asset
        Checkup
        - check that user is able to explicitly stop the playback of VOD content (with STOP action or with back key)
    logging.info("##### Begin test_qa_vod_playback_stop #####")
    test_ui_vod_stop()
    logging.info("##### End test_qa_vod_playback_stop #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_resume
def doc_test_qa_vod_playback_resume():
    """
    First step : select a vod asset
        Action
        - play a VOD asset
        - press "pause" key
        - press "pause" key
        Checkup
        - check that user is able to resume the playback of VOD content
    logging.info("##### Begin test_qa_vod_playback_resume #####")
    test_ui_vod_resume()
    logging.info("##### End test_qa_vod_playback_resume #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_rating
def test_qa_vod_playback_rating():
    """
    First step : select a vod asset with rating
        Action
        - play a VOD asset with rating
        Checkup
        - check that user has to enter his parental PIN code for playing a VOD asset with rating
    """
    logging.info("##### Begin test_qa_vod_playback_rating #####")
    test_vod = VeTestApi("test_qa_vod_playback_rating")
    test_vod.begin(screen=test_vod.screens.fullscreen)

    # go to main hub
    test_vod.screens.main_hub.navigate()
    test_vod.wait(CONSTANTS.GENERIC_WAIT)

    # Search a Parental Rating asset VOD by giving title asset keyword 'FURY' (part of the asset title)
    # Enter store search screen
    test_vod.log_assert(test_vod.screens.search.navigate(), "Moving to search screen from hub has failed")

    # Typing adult asset keywork (part of the asset title)
    # TO DO : secure the code for the case of asset title doesn't exist
    # TO DO : change the framework api search_keyword_typing() to treat the number and the special character for other languages
    test_vod.screens.filter.search_keyword_typing('FURY')

    # choose the first word on the list
    test_vod.move_towards("down")

    # validate the choice to go to asset page
    test_vod.validate_focused_item(CONSTANTS.GENERIC_WAIT)
    # validate to go to action Menu
    test_vod.validate_focused_item(CONSTANTS.GENERIC_WAIT)
    status = test_vod.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
    test_vod.log_assert(status, "VOD:RATING: expected action menu screen")

    # set ON the Threshold on UPM
    logging.info("[VOD][INFO] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logging.info("[VOD][INFO] >> current_parental_threshold = " +str(test_vod.he_utils.getHouseHoldPrentalThreshold()))
    credentials = test_vod.he_utils.get_default_credentials()
    hhid = credentials[0]
    # Set Parent Control threshold very low to make sure to have the pin code screen '''
    rating = CONSTANTS.LOW_RATING
    logging.info("[VOD][INFO] >> set parental ThresHold to " + str(rating))
    test_vod.he_utils.setParentalPin(hhid, "1111")
    test_vod.he_utils.setParentalRatingThreshold(hhid, str(rating))
    #test_vod.he_utils.setParentalRatingThreshold(hhid, rating)
    logging.info("[VOD][INFO] >> current_parental_threshold 2 = " +str(test_vod.he_utils.getHouseHoldPrentalThreshold()))
    logging.info("[VOD][INFO] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    # Go to PLAY option
    test_vod.move_towards("up", CONSTANTS.SMALL_WAIT)
    elements = test_vod.milestones.getElements()
    logging.info("[VOD][INFO] >> getElements ActionMenu "+str(elements))
    action = test_vod.milestones.get_value_by_key(elements, "focused_item")
    test_vod.log_assert(action == 'PLAY', "VOD:RATING: expected PLAY action, actual action "+str(action))
    # Press OK on PLAY
    test_vod.validate_focused_item(CONSTANTS.GENERIC_WAIT)

    # Check that LOCKED PROGRAM\n Please enter your PINCODE screen is displayed
    check_qa_pincode_screen(test_vod)
    # Enter correct pin code
    test_vod.screens.pincode.enter_correct_pincode(test_vod)
    # check that the trick mode screen is displayed
    screen = test_vod.milestones.get_current_screen()
    logging.info("[VOD][INFO] >> screen " + str(screen))
    test_vod.log_assert(screen == 'trickmode', "VOD:RATING: expected screen trickmode, actual screen " + str(screen))
    # check that the movie is displayed
    status = test_vod.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT, 'fullscreen')
    test_vod.log_assert(status, "VOD:RATING: expected fullscreen , actual screen " + str(test_vod.milestones.get_current_screen()))
    test_vod.wait(2*CONSTANTS.GENERIC_WAIT)
    logging.info("##### End test_qa_vod_playback_rating #####")
    test_vod.end()


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_app_background_foreground
def doc_test_qa_vod_playback_app_background_foreground():
    """
    First step : select a vod asset
        Action
        - play a VOD asset
        - press on Android Home key Button
        - relaunch app
        Checkup
        - check that playback is paused and Android TV launcher menu get displayed on screen.
        - check if app is resumed, then the playback screen with the content that was played visible in pause
          is displayed and the user can resume playback from the paused position.

    logging.info("##### Begin test_qa_vod_playback_app_background_foreground #####")
    test_background_vod()
    logging.info("##### End test_qa_vod_playback_app_background_foreground #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_cc
def doc_test_qa_vod_playback_closed_caption():
    """
    First step : select a vod asset with cc
        Action
        - play a VOD asset with cc
        - enable cc in settings/preferences/closed caption, the select cc1
        Checkup
        - check that the closed caption is displayed during playback of VOD asset

    logging.info("##### Begin test_qa_vod_playback_closed_caption #####")
    test_ui_vod_play_closedCaption()
    logging.info("##### End test_qa_vod_playback_closed_caption #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_default_audio_language
def test_qa_vod_playback_default_audio_language():
    """
    First step : select a vod asset with Multi Audio
        Action
        - play a VOD asset
        Checkup
        - check that the default audio language is applied during playback of VOD asset

    """
    logging.info("##### Begin test_qa_vod_playback_default_audio_language #####")
    index_default_audio_language_in_manifest = 0
    test_vod = VeTestApi("test_qa_vod_playback_default_audio_language")
    test_vod.begin(screen=test_vod.screens.fullscreen)
    assertmgr = AssertMgr(test_vod)
    # go to main hub
    test_vod.screens.main_hub.navigate()
    test_vod.wait(CONSTANTS.GENERIC_WAIT)

    # Get the default audio language defined in server UPM
    default_audio_language_from_upm = test_vod.he_utils.getAudioLanguage()
    logging.info("[VOD][INFO] >> PLAYBACK:DEFAULT AUDIO FROM UPM: The default audio language defined in UPM is : %s"
                 % default_audio_language_from_upm)

    # Instantiate VOD manager
    vod_manager = VODManager(test_vod)
    # play multi-language Vod asset
    vod_manager.play_multi_language_asset_from_hub()

    # Get the list of available audio language defined in manifest file of streaming
    audio_language_from_manifest_list = test_vod.screens.action_menu.retrieve_audio_languages()
    logging.info("[VOD][INFO] >> PLAYBACK:AUDIO FROM MANIFEST: The list audio language defined in manifest is : %s"
                 % str(audio_language_from_manifest_list))

    # Determine the default expected audio language to be checked
    expected_audio_language = default_audio_language_from_upm
    if default_audio_language_from_upm not in audio_language_from_manifest_list:
        logging.info("[VOD][INFO] >> DEFAULT AUDIO: couldn't find %s in %s" % (default_audio_language_from_upm,
                                                                    str(audio_language_from_manifest_list)))
        expected_audio_language = audio_language_from_manifest_list[index_default_audio_language_in_manifest]
    logging.info("[VOD][INFO] >> PLAYBACK:DEFAULT AUDIO: The default expected audio language to be checked is : %s"
                 % expected_audio_language)

    # check that the default audio language is applied
    vod_manager.check_playback_audio_language(assertmgr, "test_qa_vod_playback_default_audio_language", 1,
                                              expected_audio_language)

    assertmgr.verifyAllCheckPoints()
    logging.info("##### End test_qa_vod_playback_default_audio_language #####")
    test_vod.end()


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_selected_audio_language
def doc_test_qa_vod_playback_selected_audio_language():
    """
    First step : select a vod asset with Multi Audio
        Action
        - play a VOD asset
        - press"OK" to launch action menu
        - go to item LANGUAGES, then select a language
        Checkup
        - check that the selected audio language is applied during playback of VOD asset

    logging.info("##### Begin test_qa_vod_playback_selected_audio_language #####")
    test_vod_action_menu_language()
    logging.info("##### End test_qa_vod_playback_selected_audio_language #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_action
def doc_test_qa_vod_playback_action():
    """
    First step : select a vod asset
        Action
        - play a VOD asset
        - press"OK" to launch action menu
        Checkup
        - check that user is provided list of options while playing any VOD asset : Trick modes, Stop, Summary


    logging.info("##### Begin test_qa_vod_playback_action #####")
    test_actionmenu_in_hub_showcase_vod_asset()
    logging.info("##### End test_qa_vod_playback_action #####")
    """


@pytest.mark.QA
@pytest.mark.QA_vod
@pytest.mark.QA_playback_info
def test_qa_vod_playback_info():
    """
    First step : select a vod asset
        Action
        - view VOD Asset Information on Focus
        Checkup
        - check it is possible to navigate between assets, select it and view the Asset information

    2nd step : select a vod asset
        Action
        -  View VOD Asset Summary
        Checkup
        - check that  user is able to view the summary of selected VOD asset and also Check that following info is
          displayed. - Title - Duration in minutes - Synopsis
    """
    logging.info("##### Begin test_qa_vod_playback_info #####")

    test_vod = VeTestApi("test_qa_vod_playback_info")
    assertmgr = AssertMgr(test_vod)
    test_vod.begin(screen=test_vod.screens.fullscreen)
    vod_manager = VODManager(test_vod)
    status = test_vod.screens.main_hub.navigate()
    #test_vod.log_assert(status, "VOD:INFO: Shall be on the main hub screen.")
    test_vod.wait(CONSTANTS.GENERIC_WAIT)
    # Select an asset, so the actionMenu screen is displayed
    vod_manager.go_to_vod_asset(test_vod, "SVOD")
    test_vod.appium.key_event("KEYCODE_DPAD_CENTER")
    test_vod.wait(CONSTANTS.GENERIC_WAIT)

    # Retrieve asset vod title from ActionMenu
    elements = test_vod.milestones.getElements()
    logging.info("[VOD][INFO] >> getElements = "+str(elements))
    am_vod_asset_vod_title = test_vod.milestones.get_value_by_key(elements, "prog_title")
    logging.info("[VOD][INFO] >> asset vod title from ActionMenu: %s" % am_vod_asset_vod_title)

    # CHECK SUMMARY

    summary = test_vod.screens.action_menu.get_summary()
    logging.info("[VOD][INFO] >> Summary = " +str(summary))
    assertmgr.addCheckPoint(test_vod, 7, status, "Summary is not displayed")
    #test_vod.log_assert(not isinstance(summary,bool) and len(summary) > 0,"VOD:INFO: Failure to get summary")

    # Go to previous screen, to the list of vod assets
    test_vod.go_to_previous_screen()
    test_vod.wait(2*CONSTANTS.GENERIC_WAIT)
    # Retrieve focused asset vod title
    elements = test_vod.milestones.getElements()
    logging.info("[VOD][INFO] >> getElements = "+str(elements))
    focused_asset_vod_title = test_vod.milestones.get_value_by_key(elements, "selected_item")
    logging.info("[VOD][INFO] >> focused asset vod title: %s" % focused_asset_vod_title)

    # Check asset VOD title
    test_vod.log_assert(focused_asset_vod_title == am_vod_asset_vod_title,
                        "VOD:INFO: Compare asset vod title failed. focused asset vod title: %s"
                        " asset vod title from ActionMenu: %s"
                        % (focused_asset_vod_title, am_vod_asset_vod_title))

    logging.info("##### End test_qa_vod_playback_info #####")
    test_vod.end()
