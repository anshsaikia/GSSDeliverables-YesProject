__author__ = 'nahassan'
# -*- coding: utf-8 -*-
from tests_framework.ve_tests.ve_test import VeTestApi
from time import sleep
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from vgw_test_utils.IHmarks import IHmark
import logging
import datetime
import time
import pytest

SUGGESTION_KEY = "THE"

#1.1
@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF362
@pytest.mark.commit
@pytest.mark.MF362_Search
@pytest.mark.ios_regression
@pytest.mark.level2
def test_search_current_channel_from_main_hub():
    '''go to main hub
    get current channel
    type the channel title text in the search field
    tap on first suggestion - building blocks
    go back
    check if there is text in the search field'''
    test = VeTestApi("test_search_current_channel_from_main_hub")
    test.begin()
    '''go to main hub'''
    test.startup_screen.navigate()
    '''get current channel'''
    current_channel = test.startup_screen.get_current_channel()
    '''go to search'''
    search = test.screens.search
    search.navigate()

    elements = test.milestones.getElements() #remove this line

    '''type the channel title text in the search field'''
    test.appium.type_keyboard(str(current_channel))
    '''tap on the first suggestion'''
    test.wait(2)
    search.tap_on_the_first_result()
    test.wait(2)
    '''check if screen is on action menu screen'''
    elements = test.milestones.getElements()
    tap_event = test.milestones.getElementsArray([("name", "event_view", "_)")],elements)
    test.log_assert(tap_event and len(tap_event) > 0, "Can't find the result item on the screen")
    test.appium.tap_element(tap_event[0])
    test.wait(3)
    elements = test.milestones.getElements()
    screen_name = test.milestones.get_current_screen(elements)

    test.log_assert((screen_name == "action_menu") | (screen_name == "fullscreen") | (screen_name == "infolayer") ,"not tune to channel")
    # action_menu = test.screens.action_menu
    # action_menu.verify_active()

    test.screens.playback.verify_streaming_playing()
    '''go to previous screen'''
    test.screens.search.navigate()

    '''checking if the text in the search field was saved'''

    search_filed = test.milestones.getElementsArray([("name", "edit_text", "_)")])
    test.log_assert(search_filed[0]['title_text'] == str(current_channel).upper() ,"The app is not save the search filed")

    test.end()


# 3.1
'''  CLIENT/ CTAP Robustness
Search -> search key gibrish  (strange characters)->
verify (no results message in suggestions) -> tap search
-> verify (no results message in search results screen)
'''
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF362
@pytest.mark.MF362_Search
def test_no_search_results():
    test = VeTestApi("test_no_search_results")
    test.begin()

    main_hub = test.screens.main_hub

    test.wait(2)
    search = test.screens.search
    search.navigate()
    #suggestions
    search.input_text_into_search_field("1234#asdfgh!@#$();")
    search.verify_no_suggestions()

    #search
    test.appium.send_enter()

    test.wait(2)
    search.verify_no_results()

    test.wait(2)
    test.end()

# 9.1
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF362
@pytest.mark.MF362_Search
def test_type_text_and_delete():
    '''go to main hub
    get current channel
    type the channel title text in the search field
    delete all text
    check that there are no "no_suggestion" text'''
    test = VeTestApi("test_type_text_and_delete")
    test.begin()
    '''go to search screen'''
    search = test.screens.search
    search.navigate()
    '''type the channel title text in the search field'''
    test.appium.type_keyboard(SUGGESTION_KEY)
    test.wait(1)
    '''delete in loop the text on search filed '''
    len_current_channel = len(SUGGESTION_KEY)
    for index in range(len_current_channel):
        test.appium.send_backspace()
    '''check that there are no "no_suggestion" text'''
    test.wait(1)

    no_suggestions = search.wait_for_suggestions()
    test.log_assert(no_suggestions == None, "The page presents suggestion")
    test.end()


