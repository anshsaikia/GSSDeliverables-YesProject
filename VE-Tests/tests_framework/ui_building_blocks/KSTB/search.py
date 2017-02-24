__author__ = 'callix'

from tests_framework.ui_building_blocks.screen import Screen
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from time import time


class Search(Screen):

    def __init__(self, test):
        Screen.__init__(self, test, "search")

    def navigate(self):
        logging.info("Navigate to search")
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)

        if screen == self.screen_name:
            return True

        # Navigate to main_hub :
        status = self.test.screens.main_hub.navigate()
        if status:
             status = self.test.screens.main_hub.focus_search_item_in_hub()
             if not status:
                logging.error("Fail to focus Search item in Hub")
                return False

             self.test.appium.key_event("KEYCODE_DPAD_CENTER")
             self.test.wait(CONSTANTS.GENERIC_WAIT)
             status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "search")
             if not status:
                logging.error("wait for search timed out")
                return False
        logging.info("In search")
        self.verify_active()
        return True

    def to_search_in_store(self):
        """
        Access to Search in Store home
        :return: True / False
        """
        category = "SEARCH"
        sub_category = "BY KEYWORD"

        logging.info("Access to Search in Store home")
        status = self.test.screens.filter.focus_item_in_filterscreen_ux(category)

        if not status:
            return False
        self.test.wait(CONSTANTS.GENERIC_WAIT)

        status = self.test.screens.filter.select_sub_item_in_filterscreen_ux(sub_category)
        if not status:
            return False

        self.test.wait(CONSTANTS.GENERIC_WAIT)
        logging.info("In full_content")
        return True

    def find_keyboard_by_char(self, c):
        '''
        Find in which keyboard the param (c) is included
        :param c:
        :return: keyboard
        '''
        keyboard = None
        if c in CONSTANTS.g_keyboard0_chars_num:
            keyboard = CONSTANTS.g_keyboard0_chars_num
        else:
            cur_keyboard = CONSTANTS.g_keyboard1_chars
            if c in cur_keyboard:
                keyboard = cur_keyboard
        if keyboard is None:
            return False
        return keyboard

    def search_select_char(self, c, validate):
        '''
        Select the letter c in the keyboard and validate it or not according to the validate param
        :param c: letter to select
        :param validate: validate the letter or no
        :return: True if the letter has been found and validate. Return False if the letter has not been found
        '''
        if c in CONSTANTS.g_keyboard0_chars_num:
            c = c.upper()
        src_char = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "selected_char")
        src_keyboard = self.find_keyboard_by_char(src_char)
        if not src_keyboard:
            return False
        # logging.info('---> keyboard source: ' + str(src_keyboard))

        # calculate destination char
        dst_char = c
        # convert space to underline
        if dst_char == ' ':
            dst_char = u'\ue019'
        # convert < to erase
        elif dst_char == '<':
            dst_char = u'\ue00f'
        dst_keyboard = self.find_keyboard_by_char(dst_char)
        if not dst_keyboard:
            return False
        # logging.info('---> keyboard dst: ' + str(dst_keyboard))

        # logging.info("---> Go from " + src_char + " to " + dst_char)

        # switch to correct keyboard
        if dst_keyboard != src_keyboard:
            if dst_keyboard == CONSTANTS.g_keyboard0_chars_num:
                self.test.appium.key_event("KEYCODE_DPAD_UP")
            else:
                self.test.appium.key_event("KEYCODE_DPAD_DOWN")

        # calculate source char again after switching keyboards
        src_char = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "selected_char")
        if not src_char:
            return False
        self.test.wait(1)

        # go to char on keyboard
        num_steps = dst_keyboard.index(dst_char) - dst_keyboard.index(src_char)
        # logging.info("Go " + str(num_steps) + " steps in keyboard")
        # if last charcter was " " then " " is greyed out and the current key is back. As " " is greyed out we need to substract 1
        if dst_keyboard == CONSTANTS.g_keyboard0_chars_num:
            keyboard_text = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "keyboard_text")
            if len(keyboard_text) > 2 and keyboard_text[-2] == " ":
                num_steps = num_steps -1
        for i in range(abs(num_steps)):
            if num_steps > 0:
                self.test.appium.key_event("KEYCODE_DPAD_RIGHT")
            else:
                self.test.appium.key_event("KEYCODE_DPAD_LEFT")
            self.test.wait(1)

        # check that we are on the correct char
        current_key = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "selected_char")
        # logging.info("current_key: %s   validate: %s" % (current_key, validate))
        if current_key != dst_char:
            # logging.info("current_key: %s   dst_char: %s" % (current_key, dst_char))
            return False

        if validate:
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait(1)
        return True

    def wait_for_search_suggestions(self, wait_in_seconds=10):
        '''
        Wait that the suggestion list is no more empty
        :param wait_in_seconds: timeout to the suggestion shall be refresh
        :return: Retur False if suggestion list is still empty after the timeout
        '''
        start_time = time()
        current_time = start_time
        time_out = (current_time - start_time) >= wait_in_seconds
        milestone = self.test.milestones.getElements()
        suggestions_nb = self.test.milestones.get_value_by_key(milestone, 'suggestions_nb')
        # Wait until suggestions are available
        while suggestions_nb == 0 and (not time_out):
            current_time = time()
            time_out = (current_time - start_time) >= wait_in_seconds
            milestone = self.test.milestones.getElements()
            suggestions_nb = self.test.milestones.get_value_by_key(milestone, 'suggestions_nb')
            self.test.wait(0.5)

        if suggestions_nb == 0:
            logging.error("Suggestion field is empty")
            return False
        else:
            return True

    def wait_for_search_suggestions_list_update(self, old_suggestion_list=None, wait_in_seconds=60):
        '''
        Wait that the suggestion list is updated
        :param old_suggestion_list: suggestion list to compare
        :param wait_in_seconds: timeout till refresh shall be done
        :return: True if the suggestion list has been updeted
        '''
        # check every [x] seconds if suggestions have changed
        suggestions_list_changed = False
        timeout = time() + wait_in_seconds   # 1 minutes from now
        while time() < timeout:
            self.test.wait(1)
            # logging.info("Check message text and no suggestion in list")
            milestone = self.test.milestones.getElements()
            new_suggestions_list = self.test.milestones.get_value_by_key(milestone, 'suggestions_list')
            # logging.info("(time %s) New suggestion list = %s" %(str(time()), new_suggestions_list))
            if new_suggestions_list != old_suggestion_list:
                logging.info("---> Suggestion list has changed")
                suggestions_list_changed = True
                break
        return suggestions_list_changed

    def check_suggestions_start_with(self, suggestions_list=None, letter="", reverseOrder=False):
        """
        Check if all the suggestion in the suggestion list has a word started by letter
        :param suggestions_list:
        :param letter:
        :param reverseOrder:
        :return: False in case one suggestion has no word staarted by letter. Return True else.
        """
        if suggestions_list[0] == CONSTANTS.g_no_suggestions_msg_text:
            logging.error("Fail to have suggestion for: %s" % letter)
            return False

        used_suggestions_list = reversed(suggestions_list) if reverseOrder else suggestions_list
        for suggestion in used_suggestions_list:
            # logging.info("----> suggestion: %s" %suggestion)
            suggestion_r = suggestion.replace(':', ' ')
            suggestion_words_list = suggestion_r.split()
            # logging.info("----> suggestion_words_list: %s" %suggestion_words_list)
            status = False
            for word in suggestion_words_list:
                word1 = word.upper()
                # logging.info("---> word1: %s" % word1)
                if word1.startswith(letter) is True:
                    # logging.info("Suggestion %s is beginning by: %s " % (suggestion, letter))
                    status = True
                    break
            if not status:
                # logging.info("Suggestion %s has no word beginning by: %s " % (suggestion, letter))
                return False
        return True

    def scroll_to_suggestion(self, title):
        '''
        Scroll to the first element of the suggestion list
        :return:
        '''
        suggestion_found = False

        milestone = self.test.milestones.getElements()
        suggestions_nb = self.test.milestones.get_value_by_key(milestone, 'suggestions_nb')

        if suggestions_nb == 0:
            logging.error("No suggestion list")
            return False

        current_char = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "selected_char")

        if current_char in CONSTANTS.g_keyboard0_chars_num:
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
            self.test.wait(1)
            current_char = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "selected_char")

        if current_char in CONSTANTS.g_keyboard1_chars:
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
            self.test.wait(1)
            current_char = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), 'selected_char')

        if current_char in CONSTANTS.g_keyboard2_chars_deu:
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
            self.test.wait(1)

        first_search_result = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "search_result")
        logging.info("-->first_search_result %s" % first_search_result)
        if first_search_result == False:
            logging.error("Failed to select the suggestion list")
            return False

        suggestions_nb = self.test.milestones.get_value_by_key(milestone, 'suggestions_nb')
        # Select the title
        for counter in range(suggestions_nb):
            self.test.wait(CONSTANTS.SMALL_WAIT)
            search_result = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "search_result")
            # Ignore any weird characters in the suggestion
            search_result = search_result.encode('ascii', errors='ignore')
            logging.info("Focused on %s. look for %s." % (search_result, title))
            if title.upper() == search_result.upper():
                suggestion_found = True
                break
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
            self.test.wait(1)

        return suggestion_found

    def go_to_search_results(self, suggestion_string):

        # Flag to make sure asset was found in the suggestion, UI scrolled to the suggestion and selected it.
        asset_in_suggestion = False

        # Strip off any extra spaces added to the start and end of the title.
        # This is happening sometimes depending on the asset.
        suggestion_string = suggestion_string.strip().upper()
        logging.info("--> suggestion_string : %s" % suggestion_string)
        milestone = self.test.milestones.getElements()
        nb_suggestions = self.test.milestones.get_value_by_key(milestone, 'suggestions_nb')
        suggestions_list = self.test.milestones.get_value_by_key(milestone, 'suggestions_list')
        if suggestions_list == []:
            suggestions_list = None
        logging.info("suggestions_list: %s" % suggestions_list)
        # Enter characters for search
        logging.info("Searching asset title: {}, length: {} ".format(suggestion_string, str(len(suggestion_string))))
        for i in range(len(suggestion_string)):
            self.search_select_char(suggestion_string[i], True)
            self.wait_for_search_suggestions_list_update(suggestions_list, 60)
            milestone = self.test.milestones.getElements()
            suggestions_list = self.test.milestones.get_value_by_key(milestone, 'suggestions_list')
            suggestion_list_stripped = [suggestion.strip().upper() for suggestion in suggestions_list]
            logging.info("--> suggestion_list_stripped: %s" % suggestion_list_stripped)
            if suggestion_string in suggestion_list_stripped:
                asset_in_suggestion = True
                logging.info("Asset title found in suggestion")
                self.scroll_to_suggestion(suggestion_string)
                self.test.appium.key_event("KEYCODE_DPAD_CENTER")
                self.test.wait(1)
                break

        # Break from test since there must be an inconsistency between the VOD store
        # and the suggestions being provided
        if asset_in_suggestion == False:
            return False

        # Wait for search results and select the first asset which should match the asset that was searched for
        status = self.test.wait_for_screen(wait_in_seconds=10, screen_name='full_content')
        return status

    def find_suggestion_contains(self, suggestion_string):
        '''
        Find the first suggestion containing suggestion string
        :param suggestion_string:
        :return:
        '''
        milestone = self.test.milestones.getElements()
        suggestions_list = self.test.milestones.get_value_by_key(milestone, 'suggestions_list')
        if suggestions_list == False:
            return False
        suggestion_string.upper()
        logging.info("Searching asset title: {}, length: {} ".format(suggestion_string, str(len(suggestion_string))))
        for i in range(len(suggestion_string)):
            self.search_select_char(suggestion_string[i], True)
            self.wait_for_search_suggestions_list_update(suggestions_list, 10)
            milestone = self.test.milestones.getElements()
            suggestions_list = self.test.milestones.get_value_by_key(milestone, 'suggestions_list')
            suggestions_nb = self.test.milestones.get_value_by_key(milestone, 'suggestions_nb')
            if suggestions_list == False:
                return False
            suggestion_list_stripped = [suggestion.strip() for suggestion in suggestions_list]
            # logging.info("--> suggestion_list_stripped: %s" % suggestion_list_stripped)
            for suggestion in suggestion_list_stripped:
                # logging.info("--> suggestion: %s " % suggestion.upper())
                if suggestion_string.upper() in suggestion.upper():
                    logging.info("---> Asset title found in suggestion")
                    self.scroll_to_suggestion(suggestion)
                    self.test.appium.key_event("KEYCODE_DPAD_CENTER")
                    self.test.wait(0.5)
                    return True
            # logging.info("suggestions_nb: %s" % suggestions_nb)
            if suggestions_nb < 2:
                logging.info("---> Asset title NOT found in suggestion")
                return False
        else:
            logging.info("---> Asset title NOT found in suggestion")
            return False

    def get_next_letter(self, suggestions_list, start_string=""):
        '''
        Find the next letter of a suggestion starting by "start_string"
        :param suggestions_list: list of the suggestion available
        :param start_string: beginning of the suggestion
        :return: letter or False/True
        '''
        starts_with_letter = ""
        next_letter = ""
        for suggestion in suggestions_list:
            if suggestion.upper().startswith(start_string):
                starts_with_letter = suggestion
                logging.info("%s starts with letter: %s " % (starts_with_letter, start_string))
                if len(starts_with_letter) != 0:
                    # logging.info("starts_with_letter[len(start_string)]: %s" % starts_with_letter[len(start_string)])
                    if starts_with_letter[len(start_string)] != ' ':
                        next_letter = starts_with_letter[len(start_string)]
                        return next_letter

        if len(starts_with_letter) == 0 or next_letter == "":
            logging.info("Could not find any suggestions starts with %s " % start_string)
            return False

        return True

    def get_suggestion_number(self, milestone=None):
        """
        Return the number of suggestions. Load the milestone if necessary
        :param milestone: where to find suggestion number
        :return: Number of suggestion, 0 in case of error
        """
        if milestone is None:
            milestone = self.test.milestones.getElements()

        suggestions_nb = self.test.milestones.get_value_by_key(milestone,'suggestions_nb')

        if suggestions_nb is False:
            return 0
        else:
            return suggestions_nb

    def get_suggestion_list(self, milestone=None):
        """
        Return the suggestion list. Load the milestone if necessary
        :param milestone: where to find suggestion list
        :return: suggestion list, False in case of error
        """
        if milestone is None:
            milestone = self.test.milestones.getElements()
        suggestion_list = self.test.milestones.get_value_by_key(milestone,'suggestions_list')

        return suggestion_list

    def get_keyboard_text(self, milestone=None):
        """
        Return the keyboard selected text. Load the milestone if necessary
        :param milestone: where to find keyboard selected text.
        :return: Keyboard selected text, False in case of error
        """
        if milestone is None:
            milestone = self.test.milestones.getElements()
        keyboard_text = self.test.milestones.get_value_by_key(milestone,'keyboard_text')

        return keyboard_text
