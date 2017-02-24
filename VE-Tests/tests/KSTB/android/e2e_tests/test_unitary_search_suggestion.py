from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import pytest
import logging


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Suggestion
@pytest.mark.LV_L2
def test_search_single_letter_suggestions():
    '''
    Check that a suggestion list is displayed when a letter is present in the input string
    :return:
    '''

    test = VeTestApi(title="test_search_single_letter_suggestions")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select wanted letter
    letter = 'A'
    status = test.screens.search.search_select_char(letter, True)
    assertmgr.addCheckPoint("test_search_single_letter_suggestions", 1, status, "Fail to selected character: %s" % letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone,'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    test.wait(CONSTANTS.GENERIC_WAIT)

    # navigate once to suggestions and check there is one
    test.move_towards('down')
    milestone = test.milestones.getElements()
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')
    # check all suggestions in list has a word starting with "letter"
    status = test.screens.search.check_suggestions_start_with(suggestions_list, letter)
    assertmgr.addCheckPoint("test_search_single_letter_suggestions", 2, status, "Fail to have word beginning by: %s" % letter)
    logging.info("%s suggestions have been checked" % suggestions_nb)
    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_single_letter_suggestions #####")



@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Suggestion
@pytest.mark.LV_L3
def test_search_suggestion_navigate_into():
    '''
    Check that the User can navigate through the suggestions list
    :return:
    '''
    test = VeTestApi("test_search_suggestion_navigate_into")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select a letter
    #####################
    letter = 'P'
    logging.info("-----> Press %s" % letter)
    status = test.screens.search.search_select_char(letter, True)
    assertmgr.addCheckPoint("test_search_suggestion_navigate_into", 1, status,
                            "Fail to selected character: %s" % letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone,'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)

    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # check all suggestions in list has a word starting with "letter"
    status = test.screens.search.check_suggestions_start_with(suggestions_list, letter)
    assertmgr.addCheckPoint("test_search_suggestion_navigate_into", 2, status,
                            "Fail to have word beginning by: %s  in %s" % (letter, suggestions_list))

    # Select each suggestion and check there are into the suggestion list
    suggestion_found = True
    for counter in range(suggestions_nb):
        test.move_towards('down', 1)
        milestone = test.milestones.getElements()
        current_suggestion = test.milestones.get_value_by_key(milestone,'search_result')
        logging.info("--> current_suggestion: %s" %current_suggestion)
        # Ignore any weird characters in the suggestion
        current_suggestion = current_suggestion.strip()
        if current_suggestion.upper() != suggestions_list[counter].upper():
            suggestion_found = False
            assertmgr.addCheckPoint("test_search_suggestion_navigate_into", 3, suggestion_found,
                                    "Fail to have selected suggestion: %s in the suggestion list: %s" % (current_suggestion, suggestions_list))
            break

    logging.info("Succeed to navigate into all suggestion by Down key")

    # Select each suggestion and check there are into the suggestion list
    suggestion_found = True
    for counter in range(suggestions_nb-1):
        test.move_towards('up', 1)
        milestone = test.milestones.getElements()
        current_suggestion = test.milestones.get_value_by_key(milestone, 'search_result')
        if current_suggestion == False:
            test.log_assert("Failure to retrieve suggestion: %s. Selected_char: %s " % (current_suggestion, test.milestones.get_value_by_key(milestone, 'selected_char')))
        #logging.info("--> current_suggestion: %s" % current_suggestion)
        # Ignore any weird characters in the suggestion
        current_suggestion = current_suggestion.strip()
        if current_suggestion.upper() != suggestions_list[suggestions_nb-2-counter].upper():
            suggestion_found = False
            assertmgr.addCheckPoint("test_search_suggestion_navigate_into", 5, suggestion_found,
                                    "Fail to have selected suggestion: %s in the suggestion list: %s at place: %s" % (current_suggestion, suggestions_list, suggestions_list[suggestions_nb - 2 - counter]))
            break

    logging.info("Succeed to navigate into all suggestion by Up key")

    # Check that the User can move on keyboard from suggestion list
    test.move_towards('up', 1)
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    assertmgr.addCheckPoint("test_search_suggestion_navigate_into", 6, selected_char == 'A',
                            "Fail to go to keyboard from suggestion list. Selected: %s" % selected_char)

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_suggestion_navigate_into #####")



@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Suggestion
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_no_suggestion():
    '''
    Check that the User is notified when no suggestion is matching.
    :return:
    '''
    test = VeTestApi(title="test_search_no_suggestion")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Find some suggestions
    find_suggestion = False
    input_keyword = ""
    for letter in CONSTANTS.g_keyboard1_chars:
        logging.info("--> Select letter: %s" % letter)
        status = test.screens.search.search_select_char(letter, True)
        assertmgr.addCheckPoint("test_search_no_suggestion", 1, status,
                                "Fail to selected character: %s" % letter)
        input_keyword = input_keyword + letter
        status = test.screens.search.wait_for_search_suggestions(10)
        test.log_assert(status, "Suggestions field stays empty")
        milestone = test.milestones.getElements()
        suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
        logging.info("%s suggestions have been found" % suggestions_nb)
        if suggestions_nb == 1:
            logging.info("Erase last letter")
            status = test.screens.search.search_select_char('<', True)
        else:
            suggestions_list_new = test.milestones.get_value_by_key(milestone, 'suggestions_list')
            for next_letter in CONSTANTS.g_keyboard1_chars:
                status = test.screens.search.search_select_char(next_letter, True)
                assertmgr.addCheckPoint("test_search_no_suggestion", 2, status,
                                        "Fail to selected character: %s" % next_letter)
                logging.info("--> input_keyword: %s" % input_keyword)
                status = test.screens.search.wait_for_search_suggestions_list_update(suggestions_list_new, 60)
                test.log_assert(status, "Suggestions are not updated after second letter")
                milestone = test.milestones.getElements()
                suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
                logging.info("%s suggestions have been found" % suggestions_nb)
                if suggestions_nb == 1:
                    status = test.screens.search.search_select_char('<', True)
                    logging.info("Erase last letter")

                else:
                    input_keyword = input_keyword + next_letter
                    find_suggestion = True
                    break
        if find_suggestion == True:
            break
    test.log_assert(find_suggestion, "Fail to find suggestions from a 2 letters keyword")
    milestone = test.milestones.getElements()
    old_suggestions_list = test.milestones.get_value_by_key(milestone,'suggestions_list')

    # Type a numeric in order to have no suggestion
    number = '8'
    logging.info("-----> Press %s" % number)
    status = test.screens.search.search_select_char(number, True)
    assertmgr.addCheckPoint("test_search_no_suggestion", 3, status,
                            "Fail to selected character: %s" % number)
    input_keyword = input_keyword + str(number)
    logging.info("--> input_keyword: %s" % input_keyword)
    status = test.screens.search.wait_for_search_suggestions_list_update(old_suggestions_list, 60)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    if suggestions_nb == 1:
        new_suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')
        if new_suggestions_list != CONSTANTS.g_no_suggestions_msg_text:
            test.log_assert("Failed to display No suggestion available")
        old_suggestions_list = new_suggestions_list

    # Delete the last letter (number) and check that suggestions are proposed
    letter = '<'
    status = test.screens.search.search_select_char(letter, True)
    assertmgr.addCheckPoint("test_search_no_suggestion", 4, status,
                            "Fail to selected character: %s" % letter)
    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions_list_update(old_suggestions_list, 60)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone,'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    old_suggestions_list = test.milestones.get_value_by_key(milestone,'suggestions_list')

    letter = '<'
    status = test.screens.search.search_select_char(letter, True)
    assertmgr.addCheckPoint("test_search_no_suggestion", 5, status,
                            "Fail to selected character: %s" % letter)
    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions_list_update(old_suggestions_list, 60)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # checking message is empty again and there are no suggestions
    letter = '<'
    status = test.screens.search.search_select_char(letter, True)
    assertmgr.addCheckPoint("test_search_no_suggestion", 6, status,
                            "Fail to selected character: %s" % letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(not status, "Suggestions field is not empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    if suggestions_nb != 0:
        assertmgr.addCheckPoint("test_search_no_suggestion", 7, status,
                                "Fail to erase the suggestion list on:  %s" % test.milestones.get_value_by_key(milestone,'keyboard_text'))

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_no_suggestion #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Suggestion
@pytest.mark.LV_L3
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_refresh_suggestion():
    '''
    Check that the suggestion list is refreshed according to the input string each time a letter is added to it
    :return:
    '''
    test = VeTestApi(title="test_search_refresh_suggestion")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select wanted char
    first_letter = 'D'
    status = test.screens.search.search_select_char(first_letter, True)
    assertmgr.addCheckPoint("test_search_refresh_suggestion", 1, status,
                            "Fail to selected character: %s" % first_letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb1 = test.milestones.get_value_by_key(milestone,'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb1)

    first_list = test.milestones.get_value_by_key(milestone,'suggestions_list')

    # check all suggestions in list has a word starting with "letter"
    status = test.screens.search.check_suggestions_start_with(first_list, first_letter)
    assertmgr.addCheckPoint("test_search_refresh_suggestion", 2, status, "Fail to have word beginning by: %s  in %s" % (first_letter, first_list))

    # find all suggestions in list starting with D so we will type second letter
    # find all suggestions in list starting with D so we will type second letter
    second_letter = test.screens.search.get_next_letter(suggestions_list=first_list, start_string=first_letter)
    if not second_letter:
        test.log_assert(False, 'Fail to have a valid second letter from the suggestions list')

    # Select 2nd char
    second_letter = second_letter.upper()
    logging.info("second_letter: %s" % second_letter)
    status = test.screens.search.search_select_char(second_letter, True)
    assertmgr.addCheckPoint("test_search_refresh_suggestion", 3, status,
                            "Fail to selected character: %s" % second_letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions_list_update(first_list, 60)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb2 = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb2)

    second_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # check all suggestions in list has a word starting with "letter"
    status = test.screens.search.check_suggestions_start_with(second_list, first_letter+second_letter)
    assertmgr.addCheckPoint("test_search_refresh_suggestion", 4, status, "Fail to have word beginning by: %s  in %s" % (first_letter+second_letter, second_list))

    assertmgr.addCheckPoint("test_search_refresh_suggestion", 5, first_list != second_list,
                            "Suggestion list has not been updated: \n old: %s \n new: %s" % (first_list, second_list))

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_refresh_suggestion #####")

@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Suggestion
@pytest.mark.LV_L2
def test_search_suggestion_refresh_after_erase_letter():
    '''
    Check that the suggestion is refreshed according to the input string after erasing the last letter
    :return:
    '''
    test = VeTestApi(title="test_search_suggestion_refresh_after_erase_letter")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select first letter
    #####################
    first_letter = 'L'
    logging.info("-----> Press %s" % first_letter)
    status = test.screens.search.search_select_char(first_letter, True)
    test.log_assert(status, "Fail to selected character: %s" % first_letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb1 = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb1)

    first_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # check all suggestions in list has a word starting with "letter"
    status = test.screens.search.check_suggestions_start_with(first_list, first_letter)
    test.log_assert(status, "Fail to have word beginning by: %s  in %s" % (first_letter, first_list))

    # find all suggestions in list starting with T so we will type second letter
    second_letter = test.screens.search.get_next_letter(suggestions_list=first_list, start_string=first_letter)
    test.log_assert(second_letter, 'Fail to have a valid second letter from the suggestions list (%s)' % second_letter)

    # Select 2nd char
    #################
    second_letter = second_letter.upper()
    logging.info("-----> Press %s" % second_letter)
    status = test.screens.search.search_select_char(second_letter, True)
    test.log_assert(status, "Fail to selected character: %s" % second_letter)

    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions_list_update(first_list, 60)
    test.log_assert(status, "Suggestions list is not updated")
    milestone = test.milestones.getElements()
    suggestions_nb2 = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb2)

    second_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # check all suggestions in list has a word starting with "letter"
    status = test.screens.search.check_suggestions_start_with(second_list, first_letter + second_letter)
    test.log_assert(status, "Fail to have word beginning by: %s  in %s" % (first_letter + second_letter, second_list))

    # Erase last letter
    ###################
    letter = '<'
    logging.info("-----> Press %s" % letter)
    status = test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "Fail to selected character: %s" % letter)
    # Wait until suggestions are available
    status = test.screens.search.wait_for_search_suggestions_list_update(second_list, 60)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone,'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list = test.milestones.get_value_by_key(milestone, 'suggestions_list')
    # check all suggestions in list has a word starting with "letter"
    status = test.screens.search.check_suggestions_start_with(suggestions_list, first_letter)
    test.log_assert(status, "Fail to have word beginning by: %s  in %s" % (first_letter, suggestions_list))

    test.end()
    logging.info("##### End test_search_suggestion_refresh_after_erase_letter #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.F_Search_Suggestion
@pytest.mark.LV_L3
def test_search_multikeywords():
    '''
    Check that is several words is set in put string, each suggestion contains these words
    :return:
    '''
    test = VeTestApi(title="test_search_multikeywords")
    assertmgr = AssertMgr(test)
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    letter = 'D'
    status = test.screens.search.search_select_char(letter, True)
    status = test.screens.search.wait_for_search_suggestions(10)
    test.log_assert(status, "Suggestions field stays empty")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone, 'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list1 = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    letter = ' '
    status = test.screens.search.search_select_char(letter, True)
    letter = 'K'
    status = test.screens.search.search_select_char(letter, True)

    status = test.screens.search.wait_for_search_suggestions_list_update(suggestions_list1, 60)
    test.log_assert(status, "Suggestions list has not been refreshed")
    milestone = test.milestones.getElements()
    suggestions_nb = test.milestones.get_value_by_key(milestone,'suggestions_nb')
    logging.info("%s suggestions have been found" % suggestions_nb)
    suggestions_list2 = test.milestones.get_value_by_key(milestone, 'suggestions_list')

    # Check that the suggestion list contains suggestions with words started by 'D' and 'K'

    assertmgr.verifyAllCheckPoints()
    test.end()
    logging.info("##### End test_search_multikeywords #####")


