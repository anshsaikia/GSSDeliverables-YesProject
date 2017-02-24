__author__ = 'Oceane Team'

from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import pytest
import logging

#########################################################
#                     DOCUMENTATION FUNCTIONS           #
#########################################################
# Functions below are here for documentation pupose only.
# The goal of this is to centralize documentation of QA tests
# using tests from other testLevels (L1/L2/L3).
# Documentation is automatically generated here :
# http://ubu-iptv01.cisco.com/dropbox/Android_sf_k_stb_QA_Tests_doc

def doc_test_qa_search_from_hub():
    """
    TEST: Check that the User can access to search from the Main Hub screen

    Steps : Access to Search from the Hub
        Action
          - Go to search from Hub
          - Go back on Hub from Search
        Checkup
          - Check going to search from hub
          - Check that default focus is on 'A'
          - Check going back to Hub

    executes test from :
    e2e_tests/test_unitary_search.py:test_search_from_main_hub()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_access
    """

def doc_test_qa_search_from_store():
    """
    TEST: Check that the User can access to search from the Store screen

     Steps : Access to Search from store
        Action
          - Go to search from Hub
          - Go back on Hub from Search
        Checkup
          - Check going to search from hub
          - Check that default focus is on 'A'
          - Check going back to Hub

    executes test from :
    e2e_tests/test_unitary_search.py:test_search_from_store()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_access
    """

def doc_test_qa_search_navigation_input_screen():
    """
    TEST:  Check it is possible to navigate horizontally and vertically in the Search input screen

    Steps : Navigation in the input screen
        Action
          - Navigate from 'A'('Z') to 'Z'('A')
          - Navigate from '_' to '9' then from '9' to 'A'
          - Select 'A' in the keyboard to be able to delete it
          - Delete 'A' from the screen input
        Checkup
          - Check that default focus is on 'A'
          - Check all of the above caracter

    executes test from :
    e2e_tests/test_unitary_search_input.py:test_search_selected_chatest_search_selected_char()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_nagivation
    """

def doc_test_qa_search_no_suggestion():
    """
    TEST:  Check that the User is notified when no suggestion is matching

     Steps : Test no suggestion case
        Action
          - Find some suggestions
          - Type a numeric in order to have no suggestion
          - Delete the last letter (number)
        Checkup
          - Check if suggestion are proposed
          - Check that there is no suggestion available
          - Check again that suggestions are proposed

    executes test from :
    e2e_tests/test_unitary_search_suggestion.py:test_search_no_suggestion()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_search_refresh_suggestion():
    """
    TEST:  Check that the suggestion list is refreshed according to the input string each time a letter is added to it.

     Steps : Refresh suggestion in search
        Action
          - Select wanted char
          - Refresh suggestions by typing a 2nd char

        Checkup
          - Check available suggestions
          - Check all suggestions in the list has a word starting with wanted char
          - Check all suggestions in new list has a word starting with 2nd char

    executes test from :
    e2e_tests/test_unitary_search_suggestion.py:test_search_refresh_suggestion()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_search_check_sorts_alpha_from_hub():
    """
    TEST: Check the sorting type "Alphabetical" in Hub search.

     Steps : Sort alpha from Hub
        Action
          - Enter characters for search
          - Select Alphabetical sorting
        Checkup
          - Check available suggestions
          - Check alphabetical sorting if succeed

    executes test from :
    e2e_tests/test_unitary_search_suggestion.py:test_search_results_check_sorts_alpha_from_hub()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_search_results_check_sorts_switching_from_hub():
    """
    TEST: Check it is possible to sort back the proposed search results list by source.
    Steps : Sort back list by source
        Action
          - Enter characters for search
          - Check that the default sorting is by Source
          - Select Alphabetical sorting
          - Select Source sorting
        Checkup
          - Check available suggestions
          - Check if source sorting is the expected one
          - Check Alphabetical sorting if succeed
          - Check Source sorting if succeed

    executes test from :
    e2e_tests/test_unitary_search_suggestion.py:test_search_results_check_sorts_switching_from_hub()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_search_check_results():
    """
    TEST: Check that the User can access to the search results page.

     Steps : Refresh suggestion in search
        Action
          - Enter characters for search
          - Wait until suggestions are available
          - Validate the first suggestion to go to the search result screen
          - Erase the keyboard input
        Checkup
          - Check available suggestions
          - Check going in search result screen

    executes test from :
    e2e_tests/test_unitary_search_suggestion.py:test_search_check_results()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_search_back_from_fullresults():
    """
    TEST: Check that the User can access to the search results page and come-back to the search screen.
     Steps : Search back from full results
        Action
          - Enter a character for search
          - Validate the first suggestion
          - Press Back
          - Press Back
        Checkup
          - Check available suggestions
          - check all suggestions again that contains the input letter
          - Check Hub main screen

    executes test from :
    e2e_tests/test_unitary_search_suggestion.py:test_search_back_from_fullresults()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_vod_adult_contents_filtering_in_search():
    """
    TEST: Check that the Adults movies are not part in the results of Search in VOD asset.
     Steps : Search VOD results always without adults assets
        Action
          - Extract adult content from cmdc
          - Enter store search screen
          - Typing adult asset keywork
          - Get keywords list
        Checkup
          - Check vod adult asset exists in cmdc
          - Check adult asset title is not in keyword list

    executes test from :
    e2e_tests/test_vod_rent.py:test_vod_adult_contents_filtering_in_search()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_search_erase_char():
    """
    TEST: Check that the User can erase the previous selected characters.

    Steps : Erase selected characters
        Action
          - Access to Search from the Hub
          - Enter input text
          - Erase character by character
          - Get keywords list
        Checkup
          - Verify that the letter is set in the input text
          - Verify at the end that delete touch is no more accessible

    executes test from :
    e2e_tests/test_unitary_search_input.py:test_search_erase_char()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_search_results_check_sorts_source_from_hub():
    """
    TEST: Check that the "on demand contents" are displayed first if we search from store.

     Steps : Linear contents are displayed first in a LIVE context
        Action
          - Access to Search from the hub
          - Do specific search in order to have several sources in the results
        Checkup
          - Check available suggestions
          - Verify that linear contents are sorted first in a LIVE context

    executes test from :
    e2e_tests/test_unitary_search_result.py:test_search_results_check_sorts_source_from_hub()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """

def doc_test_qa_search_results_check_sorts_source_from_store():
    """
    TEST: Check that the "on demand contents" are displayed first if we search from store.

    Steps : Vod contents are displayed first in a store context
    Action
      - Access to Search from the store
      - Do specific search in order to have several sources in the results
    Checkup
      - Check available suggestions
      - Verify that the vod contents are sorted first in a store context

    executes test from :
    e2e_tests/test_unitary_search_result.py:test_search_results_check_sorts_source_from_store()

    markers :
    @pytest.mark.QA
    @pytest.mark.QA_search
    @pytest.mark.QA_search_selection
    """


#########################################################
#                       TESTS Functions                 #
#########################################################

@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_qa_search_german_keyboard():
    """
    TEST: Check that the user can switch to german keyboard

     Steps : Erase selected characters
        Action
          - Access to Search from the Hub
          - Enter input text
          - Erase character by character
          - Get keywords list
        Checkup
          - Verify that the letter is set in the input text
          - Verify at the end that delete touch is no more accessible
    """
    logging.info("##### BEGIN test_qa_search_german_keyboard #####")

    test = VeTestApi(title="test_qa_search_german_keyboard")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    status = test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES")
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.log_assert(status, "SEARCH:SELECTION: Failed to go into Preferences sub-menu")
    status = test.screens.filter.modify_uilanguage(ui_language='DEUTSCH')
    test.log_assert(status, "SEARCH:SELECTION: Failed to switch in DEUTSCH")
    test.wait(CONSTANTS.GENERIC_WAIT)
    logging.info("SEARCH:SELECTION: Search in German keyboard")
    # Update cookie
    test.he_utils.updateCookies()
    # come-back to Search and check the keyboard
    test.go_to_previous_screen()
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.screens.search.navigate()
    test.log_assert(status, "SEARCH:SELECTION: Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check the German keyboard
    milestone = test.milestones.getElements()
    nb_characters_line1 = test.milestones.get_value_by_key(milestone,'template_count')
    test.log_assert(nb_characters_line1 == len(CONSTANTS.g_keyboard1_chars_deu), "SEARCH:SELECTION: Fail on keyboard nb character: %s  instead of %s" % (nb_characters_line1, CONSTANTS.g_keyboard1_chars_deu))

    for i in range(1, nb_characters_line1):
        test.move_towards('right')
        test.wait(1)
        milestone = test.milestones.getElements()
        selected_char = test.milestones.get_value_by_key(milestone,'selected_char')
        test.log_assert(selected_char == CONSTANTS.g_keyboard1_chars_deu[i], "SEARCH:SELECTION: Fail on keyboard character: %s  instead of %s" % (selected_char, CONSTANTS.g_keyboard1_chars_deu[i]))

    test.move_towards('down')
    test.wait(CONSTANTS.GENERIC_WAIT)
    milestone = test.milestones.getElements()
    nb_characters_line2 = test.milestones.get_value_by_key(milestone,'template_count')
    test.log_assert(nb_characters_line2 == len(CONSTANTS.g_keyboard2_chars_deu), "SEARCH:SELECTION: Fail on keyboard nb character: %s  instead of %s" % (nb_characters_line2, CONSTANTS.g_keyboard1_chars_deu))
    for i in range(1, nb_characters_line2):
        test.move_towards('right')
        test.wait(1)
        milestone = test.milestones.getElements()
        selected_char = test.milestones.get_value_by_key(milestone,'selected_char')
        test.log_assert(selected_char == CONSTANTS.g_keyboard2_chars_deu[i], "SEARCH:SELECTION: Fail on keyboard character: %s  instead of %s" % (selected_char, CONSTANTS.g_keyboard2_chars_deu[i]))

    test.move_towards('up')
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select character
    #####################
    letter = 'C'
    logging.info("SEARCH:SELECTION: Select letter %s" % letter)
    test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "SEARCH:SELECTION: Fail to selected character: %s" % letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "SEARCH:SELECTION: Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone,'suggestions_nb')
    logging.info("SEARCH:SELECTION: %s suggestions have been found" % suggestions_nb)
    suggestions_list = test.milestones.get_value_by_key(milestone,'suggestions_list')

    # validate the first suggestion to go to the search result screen
    if suggestions_nb == 1 and suggestions_list[0] == CONSTANTS.g_no_suggestions_msg_text:
        test.log_assert("SEARCH:SELECTION: No suggestion available")

    asset = suggestions_list[0]
    test.screens.search.scroll_to_suggestion(asset)
    test.validate_focused_item()
    status = test.screens.fullcontent.is_in_full_content()
    test.log_assert(status, "SEARCH:SELECTION: Fail to go in search result screen (%s) for asset: %s" % (test.milestones.get_current_screen(), asset))

    # Press Back
    test.go_to_previous_screen(wait_few_seconds=5)
    test.wait(CONSTANTS.GENERIC_WAIT)
    status = test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "search")
    test.log_assert(status, "SEARCH:SELECTION: Fail to go in search input screen: %s" % test.milestones.get_current_screen())

    # Press <
    status = test.screens.search.search_select_char('<', True)
    test.log_assert(status, "SEARCH:SELECTION: Fail to selected character: <")

    # Verify that is not suggestion available
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone,'suggestions_nb')
    if suggestions_nb != 0 :
        test.log_assert("SEARCH:SELECTION: Nothing should be appeared in the search results as search input is deleted")

    # Verify that the letter is set in the input text
    input_text = test.milestones.get_value_by_key(milestone,'keyboard_text')
    test.log_assert(input_text == '_', "SEARCH:SELECTION: Fail to erase last character in letter")

    test.end()
    logging.info("##### End of test_qa_search_german_keyboard #####")

