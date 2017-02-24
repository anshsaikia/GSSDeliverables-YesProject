__author__ = 'nahassan'
# -*- coding: utf-8 -*-
from tests_framework.ve_tests.ve_test import VeTestApi
from time import sleep
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
import logging
import datetime
import time
import pytest
from vgw_test_utils.IHmarks import IHmark

SUGGESTION_KEY = "THE"

def get_playable_vod_event_title(self):
    vod_asset = self.test.he_utils.vod_assets[0]
    title = vod_asset['title']
    return title



def get_assets(key, d):
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list):
            for i in d[k]:
                for j in get_assets(key, i):
                    yield j
        elif isinstance(d[k], dict):
            for result in get_assets(key, d[k]):
                yield result

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

    test = VeTestApi("test_search_current_channel_from_main_hub")
    test.begin()
    '''go to main hub'''
    test.startup_screen.navigate()
    '''get current channel'''
    current_channel = test.startup_screen.get_current_channel()
    '''go to search'''
    search = test.screens.search
    search.navigate()

    '''type the channel title text in the search field'''
    test.appium.type_keyboard(str(current_channel))
    '''tap on the first suggestion'''
    test.wait(2)
    search.tap_on_the_first_result()
    test.wait(2)
    '''check if screen is on action menu screen'''
    elements = test.milestones.getElements()

    tap_events = test.milestones.getElementsArray([("id", "KDEventContentView", "_)")], elements)
    for element in tap_events:
        if element['title_text'] is not None and element['channel_number'] is not None:
            test.appium.tap_element(element)
            test.wait(2)
            break
    elements = test.milestones.getElements()
    screen_name = test.milestones.get_current_screen(elements)

    test.log_assert((screen_name == "action_menu") | (screen_name == "fullscreen") | (screen_name == "infolayer") ,"not tune to channel")

    test.screens.playback.verify_streaming_playing()
    '''go to previous screen'''
    # test.screens.search.navigate()
    test.screens.action_menu.navigate()
    test.screen.go_to_previous_screen()
    test.screens.full_content_screen.verify_active()

    test.screen.go_to_previous_screen()
    test.screens.search.verify_active()

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

#2.1 , 7.1
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF362
@pytest.mark.MF362_Search
def test_search_ctap_comp():
    test = VeTestApi("test_search_ctap_comp")
    test.begin()

    main_hub = test.screens.main_hub
    search = test.screens.search

    main_hub.navigate()
    search.navigate()

    mylist = list(SUGGESTION_KEY)
    for digit in mylist:
        test.appium.type_keyboard(str(digit))
        test.wait(0.4)

    payload = {'q':SUGGESTION_KEY, 'limit': str(SUGGESTION_LIMIT), 'type':'vod,ltv'}
    ctap_data = test.ctap_data_provider.send_request("SEARCH_SUGG", payload)

    ctap_asset_list = list(get_assets(key="name", d=ctap_data))
    ctap_asset_list = [x.upper() for x in ctap_asset_list]

    test_data = search.get_all_suggestions()
    screen_assets_list = [d['title_text'] for d in test_data]

    logging.info("screen results: ")
    logging.info(screen_assets_list)
    logging.info("ctap results: ")
    logging.info(ctap_asset_list)

    test.log_assert(any(map(lambda v: v in screen_assets_list, ctap_asset_list)) == True, "sugggestion lists aren't the same")
    test.log_assert(any(map(lambda v: v in ctap_asset_list, screen_assets_list)) == True ,"sugggestion lists aren't the same")

    test.log_assert(len(screen_assets_list) <= SUGGESTION_LIMIT ,"size of sugggestion list is over the maximum")

    test.end()

# 1.2
@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF362
@pytest.mark.MF362_Search
@pytest.mark.level2
def test_search_future_event_from_timeline():
    test = VeTestApi("test_search_future_event_from_timeline")
    test.begin()
    '''get future event'''
    test.screens.timeline.navigate()
    elements = test.milestones.getElements()
    future_events = test.ui.get_sorted_events("event_view", 'x_pos', elements, "title_text")
    test.log_assert(future_events, "Cannot find future events")

    future_event_name = test.milestones.get_value(future_events, 1, "title_text")
    '''go to main hub'''
    main_hub = test.screens.main_hub
    main_hub.navigate()
    '''go to search screen'''
    search = test.screens.search
    search.navigate()
    '''type the channel title text in the search field'''
    test.appium.type_keyboard(str(future_event_name))
    test.wait(1)
    '''tap on the first suggestion'''
    search.tap_on_the_first_result()
    test.wait(2)
    '''check if screen is on action menu screen'''
    elements = test.milestones.getElements()
    tap_events = test.milestones.getElementsArray([("id", "KDEventContentView", "_)")], elements)

    for element in tap_events:
        if element['title_text'] is not None and element['channel_number'] is not None:
            test.appium.tap_element(element)
            test.wait(2)
            break
    test.screens.linear_action_menu.verify_active()
    test.end()


# TODO Should be fixed
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF362
@pytest.mark.MF362_Search
def _test_search_performance():
    '''Test average 10 time if we get the suggestion in 1.5 sec and the test results in 3 sec'''
    average_suggestions = 0
    average_results = 0
    ten_time_suggestions = 0
    ten_time_results = 0
    test = VeTestApi("test_search_performance")
    test.begin()
    for i in range(PERFORMANCE_ITERATIONS_COUNT):
        '''Go to "main hub" for text in the search field deleted'''
        main_hub = test.screens.main_hub
        main_hub.navigate()
        '''Go to search screen'''
        search = test.screens.search
        search.navigate()

        '''PERFORMANCE SEARCH SUGGESTIONS'''
        start_time_suggestions = datetime.datetime.now()
        test.appium.type_keyboard(SUGGESTION_KEY)
        test_data = search.wait_for_suggestions()
        if len(test_data) > 0:
            end_time_suggestions = datetime.datetime.now()
            time = str(end_time_suggestions - start_time_suggestions)
            time = time[6:]
            time = float(time)
            average_suggestions = average_suggestions + time
            ten_time_suggestions = 1 + ten_time_suggestions

        '''PERFORMANCE SEARCH RESULTS'''
        # test.appium.hide_keyboard('Go')
        test.appium.send_enter()

        start_time_results = datetime.datetime.now()
        test_data_results = test.milestones.getElementsArray([("name", "event_view", "_)")])
        if len(test_data_results) > 0:
            end_time_results = datetime.datetime.now()
            time = str(end_time_results - start_time_results)
            time = time[6:]
            time = float(time)
            average_results = average_results + time
            ten_time_results = ten_time_results + 1

    '''calculate the average and miss 1 because getelement function add 1 sec sleep avery time'''
    average_suggestions = (average_suggestions / PERFORMANCE_ITERATIONS_COUNT) - 1
    average_results = (average_results / PERFORMANCE_ITERATIONS_COUNT) - 1

    '''Checking the performance'''
    test.log_assert(
        (average_suggestions < PERFORMANCE_SUGGESTION_LIMIT) and (ten_time_suggestions == PERFORMANCE_ITERATIONS_COUNT),
        "Performance of suggestions is over the limit")
    test.log_assert(
        (average_results < PERFORMANCE_RESULTS_LIMIT) and (ten_time_results == PERFORMANCE_ITERATIONS_COUNT),
        "Performance of results screen is over the limit")
    test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF362
@pytest.mark.MF362_Search
def test_search_performance_alt():
    test = VeTestApi("test_search_performance")
    test.begin()
    test.wait(2)
    search = test.screens.search
    search.navigate()

    success_suggestions_counter = 0
    success_result_counter = 0

    for i in range(10):

        '''PERFORMANCE SEARCH SUGGESTIONS'''
        test.appium.type_keyboard(SUGGESTION_KEY)
        test.wait(1)
        test_data = search.get_suggestions()
        if (test_data != None and len(test_data) > 0):
            success_suggestions_counter += 1

        test.appium.send_enter()
        test.wait(2)

        '''PERFORMANCE SEARCH SUGGESTIONS'''
        elements = test.milestones.getElements()
        test_data_results = test.milestones.getElementsArray([("name", "event_view", "_)")], elements)
        if (test_data_results != None and len(test_data_results) > 0):
            success_result_counter += 1

        '''go to main hub'''
        test.startup_screen.navigate()
        '''get current channel'''
        current_channel = test.startup_screen.get_element_on_screen
        '''go to search'''
        search = test.screens.search
        search.navigate()

    '''Checking the performance'''
    success_ratio_suggestions = float(success_suggestions_counter) / PERFORMANCE_MINIMAL_SUCCESS_RATE
    success_ratio_results = float(success_result_counter) / PERFORMANCE_MINIMAL_SUCCESS_RATE
    test.log_assert(success_ratio_suggestions >= PERFORMANCE_MINIMAL_SUCCESS_RATE,
                    "Performance of suggestions is too low. Success ratio: {0} %".format(
                        success_ratio_suggestions * 100))
    test.log_assert(success_ratio_results >= PERFORMANCE_MINIMAL_SUCCESS_RATE,
                    "Performance of results is too low. Success ration: {0} %".format(success_ratio_results * 100))
    test.end()







