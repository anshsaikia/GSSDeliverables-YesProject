from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import pytest
import logging


# ====================
# UTILITIES FUNCTIONS
# ====================


def compare_alphanumerical(string1, string2):
    """
    Compare 2 strings in alphabetical, numerical special characters order
    :param string1:
    :param string2:
    :return: -1 if string1<string2, 0 sif string1==string2, 1 if string1>string2
    """
    characters_order = ur""" !"#$%&'():*+,-./0123456789;<=>?@[\]^_`{|}~""" + \
                       u"\xA0" + \
                       u"aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ"
    # compare the 2 strings character by character
    for char in range(0, len(characters_order)):
        char1 = characters_order.find(string1[char])   # retrieve the index of the character into the table
        if char1 == -1:     # not found
            char1 = len(characters_order) + ord(string1[char])
        char2 = characters_order.find(string2[char])
        if char2 == -1:     # not found
            char2 = len(characters_order) + ord(string2[char])
        if char1 < char2:
            return -1
        if char1 > char2:
            return 1
    # if the first characters are the same and the length not, the shorter word is before
    if len(string1) - len(string2) < 0:
        return -1
    else:
        if len(string1) - len(string2) > 0:
            return 1
        else:
            return 0


def check_alphanumerical_sorting(asset_list):
    """
    Check if the list in parameters are alphanumerical sorted
    :param test:
    :param asset_list:
    :return: True/False
    """
    # retrieve the asset's title
    sorted_title_list = []
    title_list_display = []
    for asset in asset_list:
        sorted_title_list.append(asset["title"].upper())
        title_list_display.append(asset["title"].upper())

    # sort the asset's title
    sorted_title_list.sort(cmp=compare_alphanumerical)
    logging.info("title_asset_list_display: {0}\n sorted_title_list: {1}".format(title_list_display, sorted_title_list))

    # Compare if the python's sorting is the same than the display one
    status = sorted_title_list == title_list_display
    return status


# ===================================================
#  TESTS
# ===================================================


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_check_results():
    '''
    Check that the User can access to the search results page
    '''
    test = VeTestApi(title="test_search_check_results")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select first letter
    #####################
    first_letter = 'S'
    logging.info("Select letter %s" % first_letter)
    status = test.screens.search.search_select_char(first_letter, True)
    test.log_assert(status, "Fail to selected character: %s" % first_letter)
    letter = 'T'
    status = test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "Fail to selected character: %s" % letter)
    letter = 'E'
    status = test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "Fail to selected character: %s" % letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # validate the first suggestion to go to the search result screen
    if suggestions_nb == 1 and suggestions_list[0] == CONSTANTS.g_no_suggestions_msg_text:
        test.log_assert("No suggestion available")
    asset = suggestions_list[0]
    logging.info("suggestions_list[0]: %s" % suggestions_list[0])

    # Erase the keyboard input
    for i in range(1, 4):
        test.wait(CONSTANTS.GENERIC_WAIT)
        letter = '<'
        logging.info("Select letter %s" % letter)
        status = test.screens.search.search_select_char(letter, True)
        test.log_assert(status, "Fail to erase last letter")
        test.wait(CONSTANTS.GENERIC_WAIT)

    status = test.screens.search.go_to_search_results(asset)

    test.log_assert(status, "Fail to go in search result screen (%s) for asset: %s" % (test.milestones.get_current_screen(), asset))

    test.end()
    logging.info("##### End test_search_check_results #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_back_from_fullresults():
    '''
     Check that the User can access to the search results page and come-back to the search screen
     '''
    test = VeTestApi(title="test_search_back_from_fullresults")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select first letter
    #####################
    first_letter = 'C'
    logging.info("Select letter %s" % first_letter)
    status = test.screens.search.search_select_char(first_letter, True)
    test.log_assert(status, "Fail to selected character: %s" % first_letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # validate the first suggestion to go to the search result screen
    if suggestions_nb == 1 and suggestions_list[0] == CONSTANTS.g_no_suggestions_msg_text:
        test.log_assert("No suggestion available")

    asset = suggestions_list[0]
    milestone = test.milestones.getElements()
    input_string1 = test.milestones.get_value_by_key(milestone,'keyboard_text')
    test.screens.search.scroll_to_suggestion(asset)
    test.validate_focused_item()
    status = test.screens.fullcontent.is_in_full_content()
    test.log_assert(status, "Fail to go in search result screen (%s) for asset: %s" % (test.milestones.get_current_screen(), asset))

    # Press Back
    test.go_to_previous_screen(wait_few_seconds=5)
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "search")
    test.log_assert(status, "Fail to go in search input screen: %s" % test.milestones.get_current_screen())

    # check that suggestion list contains suggestion with same input letter
    milestone = test.milestones.getElements()
    input_string2 = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_string1 == input_string2, "Fail to have previous input string: %s   and   %s" % (input_string1, input_string2))
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')
    if suggestions_nb == 0:
        test.log_assert("Suggestion list is empty")
    if suggestions_nb == 1 and suggestions_list[0] == CONSTANTS.g_no_suggestions_msg_text:
        test.log_assert("No suggestion available")
    # check all suggestions in list has a word starting with "letter"
    status = test.screens.search.check_suggestions_start_with(suggestions_list, first_letter)
    test.log_assert(status, "Fail to have word beginning by: %s  in %s" % (first_letter, suggestions_list))

    # Press Back
    test.go_to_previous_screen(wait_few_seconds=5)
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
    test.log_assert(status, "Fail to go in main_hub screen: %s" % test.milestones.get_current_screen())

    test.end()
    logging.info("##### End test_search_back_from_fullresults #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_results_check_sorts_source_from_hub():
    """
    Check the default sorting type "By Source" in Hub search
    """
    test = VeTestApi(title="test_search_results_check_sorts_source_from_hub")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # NEED to add book when MF will be present
    # test.book_current_event_by_channel(channel_with_needed_cast)

    # Do specific search in order to have several sources in the results
    # Enter characters for search
    search_string = "PITT"
    logging.info("Search for string: %s" % search_string)
    status = test.screens.search.find_suggestion_contains(search_string)
    test.log_assert(status, "No suggestion found containing: %s" % search_string)
    status = test.wait_for_screen(wait_in_seconds=10, screen_name='full_content')
    test.log_assert(status, "Failure to go in Full Content")

    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # select sorting
    test.screens.fullcontent.focus_sort_in_fullcontent()
    sorting_list = test.screens.fullcontent.fullcontent_get_sorting_list()
    test.log_assert(sorting_list == CONSTANTS.supported_sorts, "Sorting list is not the expected one: %s" % sorting_list)

    source_sort_order = ['linear', 'pvr', 'vod']
    status = test.screens.fullcontent.fullcontent_check_sort_source(asset_list, source_sort_order)
    test.log_assert(status, "Sorting is not the expected one: %s" % sorting_list)

    if status:
        logging.info("--> Source sorting is succeed")

    test.end()
    logging.info("##### End test_search_results_check_sorts_source_from_hub #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_results_check_sorts_source_from_store():
    """
    Check the default sorting type "By Source" in Store search
    """
    test = VeTestApi(title="test_search_results_check_sorts_source_from_store")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to Search from the Store
    status = test.screens.main_hub.navigate_to_store()
    test.log_assert(status, "Fail to go to Store from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    test.log_assert(status, "Fail to go to Search from Store. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # NEED to add book when MF will be present
    # test.book_current_event_by_channel(channel_with_needed_cast)

    # Do specific search in order to have several sources in the results
    # Enter characters for search
    search_string = "SPIELBERG"
    logging.info("Search for string: %s" % search_string)
    status = test.screens.search.find_suggestion_contains(search_string)
    test.log_assert(status, "No suggestion found containing: %s" % search_string)
    status = test.wait_for_screen(wait_in_seconds=10, screen_name='full_content')
    test.log_assert(status, "Failure to go in Full Content")

    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # select sorting
    test.screens.fullcontent.focus_sort_in_fullcontent()
    sorting_list = test.screens.fullcontent.fullcontent_get_sorting_list()
    test.log_assert(sorting_list == CONSTANTS.supported_sorts, "Sorting list is not the expected one: %s" % sorting_list)

    source_sort_order = ['vod', 'pvr', 'linear']
    status = test.screens.fullcontent.fullcontent_check_sort_source(asset_list, source_sort_order)
    test.log_assert(status, "Sorting is not the expected one: %s" % sorting_list)

    if status:
        logging.info("--> Source sorting is succeed")

    test.end()
    logging.info("##### End test_search_results_check_sorts_source_from_store #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
def test_search_results_check_sorts_source_from_tvfilter():
    """
    Check the default sorting type "By Source" in TV Filter search
    """
    test = VeTestApi(title="test_search_results_check_sorts_source_from_tvfilter")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to TV Filter
    status = test.screens.main_hub.to_tvfilter_from_hub()
    test.log_assert(status, "Fail to go to TvFilter from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    test.log_assert(status, "Fail to go to Search from TvFilter. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # NEED to add book when MF will be present
    # test.book_current_event_by_channel(channel_with_needed_cast)

    # Do specific search in order to have several sources in the results
    # Enter characters for search
    search_string = "SPIELBERG"
    logging.info("Search for string: %s" % search_string)
    status = test.screens.search.find_suggestion_contains(search_string)
    test.log_assert(status, "No suggestion found containing: %s" % search_string)
    status = test.wait_for_screen(wait_in_seconds=10, screen_name='full_content')
    test.log_assert(status, "Failure to go in Full Content")

    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # select sorting
    test.screens.fullcontent.focus_sort_in_fullcontent()
    sorting_list = test.screens.fullcontent.fullcontent_get_sorting_list()
    test.log_assert(sorting_list == CONSTANTS.supported_sorts, "Sorting list is not the expected one: %s" % sorting_list)

    source_sort_order = ['linear', 'pvr', 'vod']
    status = test.screens.fullcontent.fullcontent_check_sort_source(asset_list, source_sort_order)
    test.log_assert(status, "Sorting is not the expected one: %s" % sorting_list)

    if status:
        logging.info("--> Source sorting is succeed")

    test.end()
    logging.info("##### End test_search_results_check_sorts_source_from_tvfilter #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_results_check_sorts_alpha_from_hub():
    """
    Check the sorting type "Alphabetical" in Hub search
    """
    test = VeTestApi(title="test_search_results_check_sorts_alpha_from_hub")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # NEED to add book when MF will be present
    # test.book_current_event_by_channel(channel_with_needed_cast)

    # Do specific search in order to have several sources in the results
    # Enter characters for search
    search_string = "SPIELBERG"
    logging.info("Search for string: {0}".format(search_string))
    status = test.screens.search.find_suggestion_contains(search_string)
    test.log_assert(status, "No suggestion found containing: {0}".format(search_string))
    status = test.screens.fullcontent.is_in_full_content()
    test.log_assert(status, "Fail to go in search result screen (%s) for search_string: %s" % (test.milestones.get_current_screen(), search_string))

    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # Go on sorting menu
    test.appium.key_event("KEYCODE_DPAD_UP")

    # Select Alphabetical sorting
    status = test.screens.fullcontent.fullcontent_select_alphabetical_order()
    test.log_assert(status, "Fail to select Alphabetical order")
    test.wait(2*CONSTANTS.GENERIC_WAIT)

    # Retrieve the asset list displayed
    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # Check if the asset list is well sorted
    status = check_alphanumerical_sorting(asset_list)
    test.log_assert(status, "Sorting is NOT the expected one.")
    logging.info("--> Alphabetical sorting is succeed")

    test.end()
    logging.info("##### End test_search_results_check_sorts_alpha_from_hub #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
def test_search_results_check_sorts_alpha_from_store():
    """
    Check the sorting type "Alphabetical" in Store search
    """
    test = VeTestApi(title="test_search_results_check_sorts_alpha_from_store")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to Search from the Store
    status = test.screens.main_hub.navigate_to_store()
    test.log_assert(status, "Fail to go to Store from Main Hub. Current screen: {0}".format(test.milestones.get_current_screen()))
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    test.log_assert(status, "Fail to go to Search from Store. Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Do specific search in order to have several sources in the results
    # Enter characters for search
    search_string = "SPIELBERG"
    logging.info("Search for string: {0}".format(search_string))


    status = test.screens.search.find_suggestion_contains(search_string)
    test.log_assert(status, "No suggestion found containing: {0}".format(search_string))
    status = test.screens.fullcontent.is_in_full_content()
    test.log_assert(status, "Fail to go in search result screen (%s) for search_string: %s" % (test.milestones.get_current_screen(), search_string))

    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # Go on sorting menu
    test.appium.key_event("KEYCODE_DPAD_UP")

    # Select Alphabetical sorting
    status = test.screens.fullcontent.fullcontent_select_alphabetical_order()
    test.log_assert(status, "Fail to select Alphabetical order")
    test.wait(2*CONSTANTS.GENERIC_WAIT)
    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # Check if the asset list is well sorted
    status = check_alphanumerical_sorting(asset_list)
    test.log_assert(status, "Sorting is NOT the expected one.")
    logging.info("--> Alphabetical sorting is succeed")

    test.end()
    logging.info("##### End test_search_results_check_sorts_alpha_from_store #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
def test_search_results_check_sorts_alpha_from_tvfilter():
    """
    Check the sorting type "Alphabetical" in TvFilter search
    """
    test = VeTestApi(title="test_search_results_check_sorts_alpha_from_tvfilter")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to TV Filter
    status = test.screens.main_hub.to_tvfilter_from_hub()
    test.log_assert(status, "Fail to go to TvFilter from Main Hub. Current screen: {0}".format(test.milestones.get_current_screen()))
    status = test.screens.filter.select_item_in_filterscreen_ux('SEARCH')
    test.log_assert(status, "Fail to go to Search from TvFilter. Current screen: {0}".format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    # NEED to add book when MF will be present
    # test.book_current_event_by_channel(channel_with_needed_cast)

    # Do specific search in order to have several sources in the results
    # Enter characters for search
    search_string = "SPIELBERG"
    logging.info("Search for string: {0}".format(search_string))

    status = test.screens.search.find_suggestion_contains(search_string)

    test.log_assert(status, "No suggestion found containing: {0}".format(search_string))

    status = test.wait_for_screen(wait_in_seconds=10, screen_name='full_content')
    test.log_assert(status, "Failure to go in Full Content")

    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # Go on sorting menu
    test.appium.key_event("KEYCODE_DPAD_UP")

    # Select Alphabetical sorting
    status = test.screens.fullcontent.fullcontent_select_alphabetical_order()
    test.log_assert(status, "Fail to select Alphabetical order")
    test.wait(2*CONSTANTS.GENERIC_WAIT)
    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # Check if the asset list is well sorted
    status = check_alphanumerical_sorting(asset_list)
    test.log_assert(status, "Sorting is NOT the expected one.")
    logging.info("--> Alphabetical sorting is succeed")

    test.end()
    logging.info("##### End test_search_results_check_sorts_alpha_from_tvfilter #####")



@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_results_check_sorts_switching_from_hub():
    """
    Set default sorting type to "By Source"
    Enable sorting by A-Z and sources (default)
    Test : Sort by A-Z
    """
    test = VeTestApi(title="test_search_results_check_sorts_switching_from_hub")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # NEED to add book when MF will be present
    # test.book_current_event_by_channel(channel_with_needed_cast)

    # Do specific search in order to have several sources in the results
    # Enter characters for search
    search_string = "SPIELBERG"
    logging.info("Search for string: {0}".format(search_string))
    status = test.screens.search.find_suggestion_contains(search_string)
    test.log_assert(status, "No suggestion found containing: {0}".format(search_string))
    status = test.screens.fullcontent.is_in_full_content()
    test.log_assert(status, "Fail to go in search result screen (%s) for search_string: %s" % (test.milestones.get_current_screen(), search_string))

    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # select sorting
    test.screens.fullcontent.focus_sort_in_fullcontent()
    sorting_list = test.screens.fullcontent.fullcontent_get_sorting_list()
    test.log_assert(sorting_list == CONSTANTS.supported_sorts, "Sorting list is not the expected one: {0}".format(sorting_list))

    source_sort_order = ['linear', 'pvr', 'vod']
    status = test.screens.fullcontent.fullcontent_check_sort_source(asset_list, source_sort_order)
    test.log_assert(status, "Sorting is not the expected one: {0}".format(sorting_list))

    if status:
        logging.info("--> Source sorting is succeed")

    # Go on sorting menu
    test.appium.key_event("KEYCODE_DPAD_UP")

    # Select Alphabetical sorting
    status = test.screens.fullcontent.fullcontent_select_alphabetical_order()
    test.log_assert(status, "Fail to select Alphabetical order")
    test.wait(2*CONSTANTS.GENERIC_WAIT)
    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # Check if the asset list is well sorted
    status = check_alphanumerical_sorting(asset_list)
    test.log_assert(status, "Sorting is NOT the expected one.")
    logging.info("--> Alphabetical sorting is succeed")

    # select Source sorting
    status = test.screens.fullcontent.fullcontent_select_item('BY SOURCE')
    test.log_assert(status, "Fail to select By source order")
    milestone = test.milestones.getElements()
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    source_sort_order = ['linear', 'pvr', 'vod']
    status = test.screens.fullcontent.fullcontent_check_sort_source(asset_list, source_sort_order)
    test.log_assert(status, "Sorting is not the expected one: {0}".format(sorting_list))

    if status:
        logging.info("--> Source sorting is succeed")

    test.end()
    logging.info("##### End test_search_results_check_sorts_switching_from_hub #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
def test_search_results_check_poster_asset_format():
    """
    Check the default sorting type "By Source" in Hub search
    """
    test = VeTestApi(title="test_search_results_check_poster_asset_format")
    test.begin(screen=test.screens.fullscreen)
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.main_hub.navigate_to_store()
    test.log_assert(status, "Fail to go to Store from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search in Store home. Current screen: %s" % test.milestones.get_current_screen())

    # NEED to add book when MF will be present
    # test.book_current_event_by_channel(channel_with_needed_cast)

    # Do specific search in order to have several sources in the results
    # Enter characters for search
    search_string = "SPIELBERG"
    logging.info("Search for string: %s" % search_string)
    status = test.screens.search.find_suggestion_contains(search_string)
    test.log_assert(status, "No suggestion found containing: %s" % search_string)
    status = test.screens.fullcontent.is_in_full_content()
    test.log_assert(status, "Fail to go in search result screen (%s) for search_string: %s" % (test.milestones.get_current_screen(), search_string))

    milestone = test.milestones.getElements()
    # logging.info("milestone: %s" % milestone)
    asset_list = test.milestones.get_value_by_key(milestone, 'asset_list')
    # logging.info("asset_list: %s" % asset_list)
    test.log_assert(asset_list is not False, "Any asset displayed in FullContent")

    # check poster format
    status = test.screens.fullcontent.fullcontent_check_poster_format_by_source(asset_list)
    test.log_assert(status, "Failure on asset poster format")

    test.end()
    logging.info("##### End test_search_results_check_poster_asset_format #####")


@pytest.mark.non_regression
@pytest.mark.short
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.F_Clock
@pytest.mark.LV_L3
def test_check_clock_in_search_fullcontent():
    test = VeTestApi(title="test_check_clock_in_search_fullcontent")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select first letter
    #####################
    first_letter = 'C'
    logging.info("Select letter %s" % first_letter)
    status = test.screens.search.search_select_char(first_letter, True)
    test.log_assert(status, "Fail to selected character: %s" % first_letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # validate the first suggestion to go to the search result screen
    if suggestions_nb == 1 and suggestions_list[0] == CONSTANTS.g_no_suggestions_msg_text:
        test.log_assert("No suggestion available")

    asset = suggestions_list[0]
    milestone = test.milestones.getElements()
    test.screens.search.scroll_to_suggestion(asset)
    test.validate_focused_item()
    status = test.screens.fullcontent.is_in_full_content()
    test.log_assert(status, "Fail to go in search result screen (%s) for asset: %s" % (test.milestones.get_current_screen(), asset))

    clock_time = test.get_clock_time()
    if not clock_time:
        test.log_assert(False, "The Clock is not displayed in Search fullcontent")
    else:
        logging.info("Clock is displayed: %s" % clock_time)

    # wait 1 min and check time is updated
    status = test.check_clock_time_update(clock_time)
    test.log_assert(status, "Clock is not more displayed after 1 min. Current screen: %s" % test.milestones.get_current_screen())

    test.end()
    logging.info("##### End test_check_clock_in_search_fullcontent #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Results
@pytest.mark.LV_L3
def test_fullcontent_missing_channel_logo():
    """
    Check that the channel is displayed in case of no channel logo is available
    :return:
    """
    test = VeTestApi(title="test_fullcontent_missing_channel_logo")
    test.begin(screen=test.screens.fullscreen)

    # Zap to the channel without channel logo and wait foa a current event not ended in few seconds
    channel_number = CONSTANTS.channel_number_without_logo
    logging.info("Zap to channel n %s" % channel_number)
    test.screens.playback.dca(channel_number)
    test.wait(CONSTANTS.INFOLAYER_TIMEOUT)

    test.screens.fullscreen.wait_for_event_with_minimum_time_until_end(min_time_in_seconds=240)

    event_title = test.screens.fullscreen.get_current_event_title()
    test.log_assert(event_title, "Fail to retrieve the current event: %s" % event_title)
    logging.info("Current event title: %s" % event_title)
    # Access to Search
    status = test.screens.main_hub.navigate()
    test.log_assert(status, "Fail to go to Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    event_title_start = event_title.split(':')
    test.screens.search.find_suggestion_contains(suggestion_string=str(event_title_start[0]))
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.fullcontent.is_in_full_content()
    test.log_assert(status, "Failure to be in fullcontent. Current screen: %s" % test.milestones.get_current_screen())

    test.wait(CONSTANTS.GENERIC_WAIT)
    status, logo = test.get_channel_logo_display('selected_item_channel_info')
    test.log_assert(not status, "Channel logo is displayed and is not expected on this channel (%s)" % test.milestones.get_value_by_key(test.milestones.getElements(), 'prog_channel_info'))
    status, channel_name = test.get_channel_name_display('selected_item_channel_info')
    test.log_assert(status, "Channel name is not displayed and is expected on this channel (%s)." % test.milestones.get_value_by_key(test.milestones.getElements(), 'prog_channel_info'))

    test.end()
