__author__ = 'oaharoni'

from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenActions
from time import sleep
import logging

class Search(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "tv_search")

    def navigate(self):
        logging.info("Navigate to search")
        elements = self.test.milestones.getElements()
        screen_name = self.test.milestones.get_current_screen(elements)
        if not screen_name:
            self.test.logging.info("the view does not contains screen name, navigation not performed")
            return

        if screen_name == self.screen_name:
            return

        if self.test.project != "KD":
            if screen_name == "action_menu" or screen_name == "settings" or screen_name == "trick_bar":
                self.test.ui.tap_element("exit")
            if screen_name == "fullscreen":
                self.test.ui.top_tap()
                self.test.ui.tap_element("exit")
            elements = self.test.milestones.getElements()
            if not self.is_active():
                self.test.ui.tap_element("search", elements)
        else:
            if screen_name == "fullscreen":
                self.test.screens.linear_action_menu.navigate()
                screen_name = self.test.milestones.get_current_screen()
            if screen_name == "action_menu":
                self.go_to_previous_screen()
                screen_name = self.test.milestones.get_current_screen()
            if screen_name == "full_content_screen":
                self.go_to_previous_screen()
            elements = self.test.milestones.getElements()
            if not self.test.milestones.get_current_screen(elements) == self.screen_name:
                search_dic_value = self.test.milestones.get_dic_value_by_key("DIC_SEARCH_SEARCH","general").upper()

                search_button = self.test.milestones.getElement([("title_text", search_dic_value, "==")], elements)
                if not search_button:
                    self.test.screens.main_hub.navigate()
                    search_button = self.test.milestones.getElement([("title_text", search_dic_value, "==")])
                self.test.log_assert(search_button, "Search button not found")
                self.test.appium.tap_element(search_button)
        self.verify_active()

    def input_event_into_search_filed_and_search(self, search_string):
        search_string = str(search_string)
        self.test.appium.type_keyboard(search_string)
        self.test.wait(1)
        self.test.appium.send_enter()

    def input_text_into_search_field(self, searchText):
        self.test.appium.type_keyboard(searchText)

    def verify_no_suggestions(self):
        suggestions = self.wait_for_suggestions()

        if suggestions is not None: #KD
            self.test.log_assert( len(suggestions) == 1, "Too many suggestions for gibrish search key")
            milestones = self.test.milestones

            no_suggestion_available_string_dic_value = milestones.get_dic_value_by_key("DIC_SEARCH_NO_SUGGESTIONS")
            no_results_label = milestones.getElementContains(suggestions, no_suggestion_available_string_dic_value)
            self.test.log_assert(no_results_label, \
                           "No Suggestions availbale text is missing")


    def wait_for_suggestions(self, timeout=5):
        msec = 0.4
        count = int(timeout/msec)
        for i in range(count):
            self.test.log("waiting for suggestions")
            self.test.wait(msec)
            suggestions = self.get_suggestions()
            if suggestions:
                return suggestions
        return None

    def get_suggestions(self):
        elements = self.test.milestones.getElements()
        suggestions = self.test.milestones.getElementsArray([("id", "suggestions", "==")], elements)
        return suggestions


    #results
    def verify_no_results(self):
        milestones = self.test.milestones

        elements = milestones.getElements()

        if self.test.project != "KD":
            no_suggestion_available_string_dic_value = milestones.get_dic_value_by_key("DIC_SEARCH_NO_RESULTS_AVAILABLE")
        else:
            no_suggestion_available_string_dic_value = milestones.get_dic_value_by_key("DIC_SEARCH_NO_RESULTS")

        self.test.log_assert(milestones.getElementContains(elements, no_suggestion_available_string_dic_value), \
                       "No Results available text is missing")

        elements = self.test.milestones.getElements()
        sugg_results = self.test.milestones.getElementsArray([("id","CTLabel","==")], elements)
        return sugg_results

    def tap_on_the_first_result(self):
        suggestions = self.wait_for_suggestions()
        self.test.log_assert(suggestions != None, "No suggestions text")
        self.test.appium.tap_element(suggestions[0])

    def scroll_suggestions(self,swipe_direction=ScreenActions.DOWN, msec=2):
        suggestions = self.wait_for_suggestions()
        self.test.log_assert( suggestions != None, "No suggestions text")
        steps = 1
        first_entry = suggestions[0]
        direction = swipe_direction
        scroll_distance = first_entry['height'] * 4
        # ['y_pos']
        for i in range(0,abs(steps)):
            self.test.appium.swipe_element(first_entry, scroll_distance, direction)
            sleep(0.3)


    def get_all_suggestions(self):
        suggestions = self.wait_for_suggestions()
        after = None
        all_suggestion = suggestions
        before = suggestions[0]['title_text']

        while after == None or after != before:
            suggestions = self.wait_for_suggestions()
            before = suggestions[0]['title_text']

            self.scroll_suggestions(ScreenActions.UP)

            suggestions = self.wait_for_suggestions()
            after = suggestions[0]['title_text']

            for i in range(0, len(suggestions)):
                if all_suggestion[-1]['title_text'] == suggestions[i]['title_text']:
                    break

            all_suggestion.extend(suggestions[i + 1:])

        return all_suggestion

    def navigate_to_action_menu_by_event_title(self, asset_title):
        #select the suggestion by title
        suggestion = self.test.milestones.getElement([("title_text", asset_title.upper(), "=="), ("name", "text_view", "==")])
        self.test.appium.tap_element(suggestion)
        self.test.wait(2)

        #tap on the event to navigate to action menu
        event = self.test.milestones.getElement([("title_text", asset_title.upper(), "(_"), ("name", "event_view", "==")])
        self.test.appium.tap_element(event)

    def clear_search_text_line(self):
        clear_text = self.test.milestones.get_dic_value_by_key("DIC_SEARCH_CLEAR")
        self.test.log_assert(clear_text is not None, "could not find clear button dic")
        clear_button = self.test.milestones.getElement([("title_text", clear_text.upper(), "=="), ("name", "button_view", "==")])
        if clear_button is None:
            logging.info("Clear Button is not avaliable, moving on")
            return
        self.test.appium.tap_element(clear_button)

    def search_and_try_to_open_action_menu_of_first_suggestion(self, search_text):
        self.navigate()
        logging.info('Search for event "{}"'.format(search_text))
        self.input_text_into_search_field(search_text)
        suggestions = self.wait_for_suggestions()
        if (suggestions == None):
            logging.info('No suggestions for event "{}"'.format(search_text))
            elements = self.test.milestones.getElements()
            cancel_button = self.test.milestones.getElement([('id', 'CANCEL', '==')], elements)
            self.test.appium.tap_element(cancel_button)
            return False
        else:
            self.test.appium.tap_element(suggestions[0])
            self.test.wait(2)
            elements = self.test.milestones.getElements()
            tap_event = self.test.milestones.getElementsArray([("name", "event_view", "_)")], elements)
            if (tap_event and len(tap_event) > 0):
                logging.info('"{}" found!'.format(search_text))
                self.test.appium.tap_element(tap_event[0])
                self.test.wait(2)
                return True
            else:
                logging.info('No event view for event "{}"'.format(search_text))
                cancel_button = self.test.milestones.getElement([('id', 'CANCEL', '==')], elements)
                self.test.appium.tap_element(cancel_button)
                return False
