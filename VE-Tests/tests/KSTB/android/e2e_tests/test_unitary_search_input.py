from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import pytest
import logging


def select_char_and_check(test, letter, text_to_check=""):
    """
    Select a Letter and check the input text is updated correctly. Assert in case of error.
    :param test:
    :param letter:
    :param text_to_check:
    :return:
    """
    if text_to_check is "":
        text_to_check = letter

    text_to_check += '_'

    # Select the letter
    status = test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "Fail to select character: {}".format(letter))

    # Verify that the letter is set in the input text
    input_text = test.screens.search.get_keyboard_text()
    test.log_assert(input_text == text_to_check, "Bad input text {0} instead of {1}".format(input_text, text_to_check))


def erase_char_and_check(test, text_to_check=""):
    """
    Erase a char and check the input text is updated correctly. Assert in case of error.
    :param test:
    :param letter:
    :param text_to_check:
    :return:
    """
    if text_to_check is not "":
        text_to_check = text_to_check[:-1]

    text_to_check += '_'

    # Select the letter
    status = test.screens.search.search_select_char("<", True)
    test.log_assert(status, "Fail to select Erase character")

    # Verify that the letter is set in the input text
    input_text = test.screens.search.get_keyboard_text()
    test.log_assert(input_text == text_to_check, "Bad input text {0} instead of {1}".format(input_text, text_to_check))


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.dummy
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_nagivation
def test_search_selected_chatest_search_selected_char():
    '''
    Check that the User can select each character
    :return:
    '''
    test = VeTestApi(title="test_search_selected_char")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Check that default focus is on 'A'
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    test.log_assert(selected_char == 'A', "Default focus is NOT on first letter of alphabetical characters but: %s" % selected_char)

    # Navigate from 'A' to 'Z'
    status = test.screens.search.search_select_char('Z', validate=False)
    test.log_assert(status, "Fail to navigate from A to Z")

    # Navigate from 'Z' to 'A'
    status = test.screens.search.search_select_char('A', validate=True)
    test.log_assert(status, "Fail to navigate from Z to A")

    # Select _screens.search
    char = ' '
    status = test.screens.search.search_select_char(char, validate=False)
    test.log_assert(status, "Fail to navigate from A to _")

    # Navigate from '_' to '9'
    char = '9'
    status = test.screens.search.search_select_char(char, validate=False)
    test.log_assert(status, "Fail to navigate from _ to 9")

    # Navigate from '9' to 'A' and validate 'A' to be able to select <
    char = 'A'
    status = test.screens.search.search_select_char(char, validate=True)
    test.log_assert(status, "Fail to navigate from 9 to A")
    # Navigate from 'A' to '<'
    char = '<'
    status = test.screens.search.search_select_char(char, validate=False)
    test.log_assert(status, "Fail to navigate from A to <")

    test.end()
    logging.info("##### End test_search_selected_char #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L2
def test_search_input_string():
    '''
    Check that the User can type a search string
    :return:
    '''
    test = VeTestApi("test_search_input_string")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Enter the string 'A'
    logging.info("Search the string: THE")
    letter = 'T'
    string_search = letter
    status = test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "Fail to selected character: %s" % letter)
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == letter + '_', "Fail to have %s in the input text" % letter)

    letter = 'H'
    string_search = string_search + letter
    status = test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "Fail to selected character: %s" % letter)
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == string_search + '_', "Fail to have %s in the input text" % string_search)

    letter = 'E'
    string_search = string_search + letter
    status = test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "Fail to selected character: %s" % letter)
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == string_search + '_', "Fail to have %s in the input text"  % string_search)

    test.end()
    logging.info("##### End test_search_input_string #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L2
@pytest.mark.QA
@pytest.mark.QA_search
@pytest.mark.QA_search_selection
def test_search_erase_char():
    '''
    Check that the User can type a search string
    :return:
    '''
    test = VeTestApi(title="test_search_erase_char")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    status = test.screens.search.search_select_char('A', True)
    test.log_assert(status, "Fail to selected character: A")
    status = test.screens.search.search_select_char('N', True)
    test.log_assert(status, "Fail to selected character: N")
    status = test.screens.search.search_select_char('D', True)
    test.log_assert(status, "Fail to selected character: D")
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == 'AND'+'_', "Fail to have AND in the input text")

    # Press <
    status = test.screens.search.search_select_char('<', True)
    test.log_assert(status, "Fail to selected character: <")
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == 'AN'+'_', "Fail to erase D")

    # Press <
    status = test.screens.search.search_select_char('<', True)
    test.log_assert(status, "Fail to selected character: <")
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == 'A'+'_', "Fail to erase N")

    # Press <
    status = test.screens.search.search_select_char('<', True)
    test.log_assert(status, "Fail to selected character: <")
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == '_', "Fail to erase A")

    # Verify that < is no more accessible
    status = test.screens.search.search_select_char('<', False)
    test.log_assert(not status, "< is still enable even with text input empty")

    test.end()
    logging.info("##### End test_search_erase_char #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L2
def test_search_numerical_char():
    """
    Check that the User can type a numerical char
    :return:
    """
    test = VeTestApi("test_search_numerical_char")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: {}"
                    .format(test.milestones.get_current_screen()))
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Select a numerical character and verify we can erase it
    select_char_and_check(test,'1')
    erase_char_and_check(test)

    # Get a valid suggestion value with numerical value
    select_char_and_check(test,'B')
    suggestion_list = test.screens.search.get_suggestion_list()
    test.log_assert(suggestion_list is not False, "Fail to retrieve suggestion list")

    # Looking for a valid suggested asset with a digit in it
    # Use reverse list for having a suggestion different from the first shown.
    suggestion_to_find = ""
    for suggestion in reversed(suggestion_list):
        if any(i.isdigit() for i in suggestion.encode('ascii')):
            suggestion_to_find = suggestion.upper()
            logging.info("Suggestion with numerical digit = {}".format(suggestion_to_find))
            break
    else:
        test.log_assert(False, "No suggestion found with a numeric value.")

    # Erase to perform a full selection after
    erase_char_and_check(test)

    # Select the suggested value with a digit.
    input_text = ""
    for letter in suggestion_to_find:
        input_text += letter
        select_char_and_check(test,letter,input_text)

        if letter.isdigit():
            logging.info("input_text = {}".format(input_text))
            break

    suggestion_list = test.screens.search.get_suggestion_list()
    test.log_assert(suggestion_list is not False, "Fail to retrieve suggestion list")

    erase_char_and_check(test,input_text)

    test.end()
    logging.info("##### End test_search_numerical_char #####")


#@pytest.mark.non_regression
#@pytest.mark.FS_Search
#@pytest.mark.LV_L3
@pytest.mark.skipif(True,reason="Skip")
# To be activated when functionality will be implemented (DE5096)
def test_search_numerical_RCU():
    '''
    Check that the User can type a digit on its RCU
    :return:
    '''
    test = VeTestApi(title="test_search_numerical_RCU")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)

    # Press 1 on the RCU
    test.appium.key_event("KEYCODE_1")
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    logging.info("input_text: %s" % input_text)
    test.log_assert(input_text == '1' + '_', "Fail to have 1 in the input text")

    # Press <
    status = test.screens.search.search_select_char('<', True)
    test.log_assert(status, "Fail to selected character: <")
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == '_', "Fail to erase 1 ")

    letter = 'D'
    status = test.screens.search.search_select_char(letter, True)
    test.log_assert(status, "Fail to selected character: D")
    # Press 9 on the RCU
    test.appium.key_event("KEYCODE_9")
    # Verify that the letter is set in the input text
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == letter + '9' + '_', "Fail to have D9 in the input text")

    # Press <
    status = test.screens.search.search_select_char('<', True)
    test.log_assert(status, "Fail to selected character: <")
    milestone = test.milestones.getElements()
    input_text = test.milestones.get_value_by_key(milestone, 'keyboard_text')
    test.log_assert(input_text == 'D' + '_', "Fail to erase 9 ")

    test.end()
    logging.info("##### End test_search_numerical_RCU #####")


@pytest.mark.non_regression
@pytest.mark.FS_Search
@pytest.mark.LV_L3
def test_search_english_german_keyboard():
    '''
    Check that the User can switch to German keyboard
    :return:
    '''
    test = VeTestApi(title="test_search_german_keyboard")
    test.begin(screen=test.screens.fullscreen)
    test.screens.main_hub.navigate()
    # Access to Search from the Hub
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check that default focus is on 'A'
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    test.log_assert(selected_char == 'A', "Default focus is NOT on first letter of alphabetical characters but: %s" % selected_char)
    # Check the English keyboard
    milestone = test.milestones.getElements()
    nb_characters_line1 = test.milestones.get_value_by_key(milestone, 'template_count')

    for i in range(1, nb_characters_line1):
        test.move_towards('right')
        test.wait(1)
        milestone = test.milestones.getElements()
        selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
        test.log_assert(selected_char == CONSTANTS.g_keyboard1_chars[i], "Fail on keyboard character: %s  instead of %s" % (selected_char, CONSTANTS.g_keyboard1_chars[i]))

    # Check there is no second line
    test.move_towards('down')
    milestone = test.milestones.getElements()
    selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
    test.log_assert(selected_char == 'Z', "Focus has been moved")
    nb_characters_line = test.milestones.get_value_by_key(milestone,'template_count')
    test.log_assert(nb_characters_line == len(CONSTANTS.g_keyboard1_chars), "Focus is NOT on English keyboard: %s" % selected_char)
    # Come-back to Main-hub
    status = test.screens.main_hub.navigate()
    test.log_assert(status, "Fail to go to Main Hub from Search. Current screen: %s" % test.milestones.get_current_screen())

    # switch in German
    status = test.screens.main_hub.navigate_to_settings_sub_menu("PREFERENCES")
    test.wait(CONSTANTS.GENERIC_WAIT)
    test.log_assert(status, "Failed to go into Preferences sub-menu")
    status = test.screens.filter.modify_uilanguage(ui_language='DEUTSCH')
    test.log_assert(status, "Failed to switch in DEUTSCH")
    test.wait(CONSTANTS.GENERIC_WAIT)
    logging.info("Switched in German")
    # Update cookie
    test.he_utils.updateCookies()

    # come-back to Search and check the keyboard
    test.go_to_previous_screen()
    test.wait(3)
    status = test.screens.search.navigate()
    test.log_assert(status, "Fail to go to Search from Main Hub. Current screen: %s" % test.milestones.get_current_screen())
    test.wait(3)

    test.wait(CONSTANTS.GENERIC_WAIT)
    # Check the German keyboard
    milestone = test.milestones.getElements()
    nb_characters_line1 = test.milestones.get_value_by_key(milestone,'template_count')
    test.log_assert(nb_characters_line1 == len(CONSTANTS.g_keyboard1_chars_deu), "Fail on keyboard nb character: %s  instead of %s" % (nb_characters_line1, CONSTANTS.g_keyboard1_chars_deu))

    for i in range(1, nb_characters_line1):
        test.move_towards('right')
        test.wait(1)
        milestone = test.milestones.getElements()
        selected_char = test.milestones.get_value_by_key(milestone,'selected_char')
        test.log_assert(selected_char == CONSTANTS.g_keyboard1_chars_deu[i], "Fail on keyboard character: %s  instead of %s" % (selected_char, CONSTANTS.g_keyboard1_chars_deu[i]))

    test.move_towards('down')
    test.wait(1)
    milestone = test.milestones.getElements()
    nb_characters_line2 = test.milestones.get_value_by_key(milestone, 'template_count')
    test.log_assert(nb_characters_line2 == len(CONSTANTS.g_keyboard2_chars_deu), "Fail on keyboard nb character: %s  instead of %s" % (nb_characters_line2, CONSTANTS.g_keyboard1_chars_deu))
    for i in range(1, nb_characters_line2):
        test.move_towards('right')
        test.wait(1)
        milestone = test.milestones.getElements()
        selected_char = test.milestones.get_value_by_key(milestone, 'selected_char')
        test.log_assert(selected_char == CONSTANTS.g_keyboard2_chars_deu[i], "Fail on keyboard character: %s  instead of %s" % (selected_char, CONSTANTS.g_keyboard2_chars_deu[i]))

    test.end()
    logging.info("##### End test_search_german_keyboard #####")
