__author__ = 'bwarshaw'

from tests_framework.ui_building_blocks.screen import Screen
from datetime import datetime, timedelta
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from pytz import timezone
import pytz
import json
import requests



class ActionMenu(Screen):


    def __init__(self, test):
        Screen.__init__(self, test, "action_menu")

    def navigate(self, verify_active = True):
        logging.info("Navigate to action menu")
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
        if screen == "action_menu":
            return True
        if screen == "infolayer":
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
            screen = "fullscreen"
        if screen == "trickmode":
            self.test.appium.key_event("KEYCODE_BACK")
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
            screen = "fullscreen"

        if screen == "fullscreen":
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
            self.verify_active()
            return True
        if screen == "main_hub":
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
            self.verify_active()
            return True
        if screen == "full_content":
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
            self.verify_active()
            return True
        if screen == "filter":
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
            self.verify_active()
            return True
        if screen == "timeline":
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
            self.verify_active()
            return True
        if screen == "guide":
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "action_menu")
            self.verify_active()
            return True

        self.verify_active()
        assert False, "Navigation not implemented in this screen : " + screen


    def get_value_by_key(self, key, elements=None):
        if elements is None:
            elements = self.test.milestones.getElements()
        return self.test.milestones.get_value_by_key(elements, key)

    def get_focused_item(self, elements=None):
        return self.get_value_by_key("focused_item", elements)

    def get_focused_asset(self, elements=None):
        return self.get_value_by_key("focused_asset", elements)
    
    def str_like_list_2_list(self,input_list):
        '''
        return a true list from a string looking like a list
        example: input: '[menu, volume, datas]'
                 output: [menu,volume,datas]
        '''
        input2list = input_list.split(",")
        for item_id in range(len(input2list)):
            item = input2list[item_id].strip().replace("[","").replace("]","")
            input2list[item_id]= item
        
        return input2list
    
    def get_menu_nb_audio(self):
        """
        Retrieve the number of audio items in language menu
        return : the number of audio items in language menu
        """
        return int(self.get_value_by_key("nbAudios"))

    def get_menu_audio_items(self):
        """
        Retrieve the list of audio items strings in language menu
        return : the list of audio items strings in language menu
        """
        return self.str_like_list_2_list(self.get_value_by_key("audioItems"))

    def get_menu_audio_item_selected(self):
        """
        Retrieve the audio item selected string in language menu
        return : the audio item selected string in language menu
        """
        return self.get_value_by_key("audioItemSelected")


    def get_actions_from_current_actionmenu(self):
        """
        retrieve the actions which are in action menu
        return : list of the actions in action menu
        """
        
        str_items_list = self.get_value_by_key("titleItems") # string like: '[SUMMARY, PLAY, WATCH LIST, LIKE]'
        list_items = self.str_like_list_2_list(str_items_list)
        
        return list_items

    def get_audio_languages_from_current_actionmenu(self):
        """
        retrieve the actions which are in action menu
        return : list of the actions in action menu
        """
        return self.str_like_list_2_list(self.get_value_by_key("audioTitles"))

    def get_subtitles_languages(self):
        subtitles = self.get_value_by_key("SUBTITLES")
        if subtitles is not None:
            return subtitles.get("items", [])
        else:
            return None

    def get_subtitles_selected(self):
        subtitles = self.get_value_by_key("SUBTITLES")
        if subtitles:
            return subtitles.get("items", [])[subtitles.get("selected", 0)]
        else:
            return None

    def select_subtitles(self, lang):
        if not self.navigate_to_action("SUBTITLES"):
            return False
        lang_list = self.get_subtitles_languages()
        selected =  self.get_subtitles_selected()
        if lang not in lang_list:
            return False

        if selected == lang:
            return True

        for (i, _) in enumerate(lang):
            focus = self.get_value_by_key("focused_asset")

            if focus == lang:
                self.test.validate_focused_item()
                return True
            else:
                self.test.move_towards("right")


        return False

    def get_summary(self):
        """
        Get the summary from the summary item in action menu
        :return: summary as String
        """
        return self.get_value_by_key("summary")

    def scroll_in_action_menu(self, direction="UP"):
        """
        scrolling once action menu
        param direction : the direction of scrolling
        return: True when located on requsted action
        """
        try:
            start_action = self.get_focused_item()
            assert direction in ("UP", "DOWN")
            keyevent = "KEYCODE_DPAD_"+direction
            self.test.appium.key_event(keyevent)
            self.test.wait(0.75)
            assert self.get_focused_item()!=start_action, "We are still in the same action"
            return True
        except Exception as ex:
            self.test.log_assert(False,"{}".format( ex))
            return {"exception" : ex}

    def navigate_to_action(self, action):
        '''
        navigating to specific action in action menu
        '''
        try:
            assert self.test.milestones.get_current_screen()=="action_menu", "We excpected to be on action_menu screen but we are in {}".format(self.test.milestones.get_current_screen())
            actions_in_actionmenu = self.get_actions_from_current_actionmenu()
            assert action in actions_in_actionmenu, "The requested action does not appear in this action menu\nCurrent actions in this action menu are {}".format(actions_in_actionmenu)
            focused_action = self.get_focused_item()
            steps = actions_in_actionmenu.index(action)-actions_in_actionmenu.index(focused_action)
            direction = None
            if steps >0:
                direction = "UP"
            else:
                direction = "DOWN"
            for step in range(0, steps):
                self.scroll_in_action_menu(direction)
            assert self.get_focused_item()==action
            return True
        except Exception as ex:
            self.test.log_assert(False,"{}".format( ex))
            return {"exception" : ex}

    def get_event_title(self, elements=None):
        return self.get_value_by_key("prog_title", elements)

    def get_channel_logo(self, elements=None):
        return self.get_value_by_key("prog_channel_logo", elements)

    def get_languages(self, iso_codes):
        """
        Allow to convert the iso code language list into a list of titles
        :param isoCodes: The list of iso codes languages given by the player
        :return: The corresponding list of titles expected from the CTAP
        """
        langList = []
        for isoCode in iso_codes:
            if CONSTANTS.dico_languages.has_key(isoCode):
                langList.append(CONSTANTS.dico_languages[isoCode])
            else:
                logging.error("get_languages has not key %s" % (isoCode))
        return langList

    def get_action_menu_url(self, json_response):
        """
        Retrieve the url for the action menu content.
        It will return json[links]["ok"][href]
        :param json_response:
        :return:
        """
        for i in json_response:
            if i == "links":
                for k in json_response[i]:
                    if k["event"] == "ok":
                        logging.info("action %s " % k["href"])
                        return k["href"]

    def get_action_menu_content_by_href(self, actionmenu_url):
        if not len(actionmenu_url):
            return False
        if 'http://localhost:8081/ctap' in actionmenu_url:
            # CTAP by SGW
            new_url = actionmenu_url.replace('http://localhost:8081/ctap/', self.test.he_utils.ctapUrl)
        else:
            return False

        r = requests.get(new_url, headers=self.test.he_utils.session_guard_header, cookies=self.test.he_utils.r_cookie)
        response = json.loads(r.text)
        #logging.info("response : %s" % response)

        return response

    def check_action_list(self, action_item_list):
        """
        Check the action list for the current action menu screen
        :param action_item_list: The expected action titles list
        """
        # Check the first item
        focused_item = self.get_focused_item()
        expected_item = action_item_list[0]
        status = focused_item == expected_item
        if not status:
            logging.error("First focused item is %s, expected %s" % (focused_item, expected_item))
            return False

        # Check the remaining items
        for nb in range(1, len(action_item_list)):
            self.test.appium.key_event("KEYCODE_DPAD_UP")
            self.test.wait(CONSTANTS.SMALL_WAIT)
            focused_item = self.get_focused_item()
            expected_item = action_item_list[nb]
            logging.info("expected_item is %s" % expected_item)
            logging.info("selected_item is %s" % focused_item)
            if focused_item not in action_item_list:
                logging.error("Found focused item %s, expected %s" % (focused_item, expected_item));
                return False
            else:
                # Check the selected sub-item in case of an optional action item (item with a selectable list of items)
                if expected_item in CONSTANTS.actionlist_optional_item:
                    if self.test.is_dummy:
                        expected_sub_item = CONSTANTS.dummy_sublist_optional_item[expected_item][0]
                    else :
                        # FIXME retrieve the selected language - Here we consider the first one
                        # In case of live, retrieve the selected audio language
                        audio_languages = self.retrieve_audio_languages()
                        logging.info("audio_languages %s " % audio_languages)
                        audio_string = self.convert_languages_to_id_isocode_string(audio_languages)
                        logging.info("audio_string %s " % audio_string)
                        languages_expected = self.get_languages(audio_languages)

                        #Use retrieve_selected_audio_track_id
                        audioId = self.retrieve_selected_audio_track_id()
                        if not audioId:
                            logging.error("No audio available (audioId is null) ")
                            return False

                        expected_sub_item = languages_expected[int(audioId)]

                        #check nb audio corresponds to expeced audio languages number
                        if len(audio_languages) != self.get_menu_nb_audio():
                            logging.error("Number of audio language: %s, found: %s" % (len(audio_languages), self.get_menu_nb_audio()))
                            return False

                        #Check the focused audio item
                        focused_value = self.get_focused_asset()
                        if languages_expected[int(audioId)] != focused_value:
                            logging.error("Found focused language: %s, expected: %s" % (focused_value, languages_expected[0]))
                            return False

                        #Check the selected audio item
                        selected_value = self.get_menu_audio_item_selected()
                        if expected_sub_item != selected_value:
                            logging.error("Found selected language: %s, expected %s" % (selected_value, expected_sub_item))
                            return False


        # Check that next selected item will be the first one
        self.test.appium.key_event("KEYCODE_DPAD_UP")
        self.test.wait(CONSTANTS.SMALL_WAIT)
        focused_item = self.get_focused_item()
        logging.info("focused_item %s " % focused_item)
        if focused_item != action_item_list[0]:
            logging.error("No loop on first item %s, found %s" % (action_item_list[0],focused_item))
            return False
        return True


    def retrieve_action_list_from_content(self, action_menu_content):
        """
        Extract the titles of the actions from the JSON action menu response
        :param test: Test instance
        :param action_menu_content: The CTAP JSON response for the action menu
        :return: The list of action titles
        """
        ctap_action_list = self.test.he_utils.get_action_menu_actions_list(action_menu_content)
        ctap_action_titles_list = []
        for k in ctap_action_list:
            ctap_action_titles_list.append(k['title'])
        logging.info(ctap_action_titles_list)
        return ctap_action_titles_list

    def retrieve_audio_languages(self):
        """
        Allow to retrieve the current available audio languages as a list of iso codes
        :return: The formated audio languages as a list of iso codes
        """
        languages = []
        playbackStatusInfo = self.test.milestones.getPlaybackStatus()
        streams = playbackStatusInfo["allPlaybackStreams"]
        for stream in streams:
            if stream["type"] == "AUDIO":
                languages.append(stream["language"])
        logging.info("retrieve_audio_languages %s" % str(languages))
        return languages

    def retrieve_selected_audio_track_id(self):
        """
        Allow to retrieve the current selected audio language index
        :return: The index of the selected audio track
        """
        playbackStatusInfo = self.test.milestones.getPlaybackStatus()
        audioTrackId = playbackStatusInfo["selectedAudioTrackId"]
        logging.info("audioTrackId %s" % audioTrackId)
        return audioTrackId

    def convert_languages_to_id_isocode_string(self,languages):
        str = ""
        first = True
        for language in languages:
            if first:
                str = language
                first = False
            else:
                str = str + "," + language
        logging.info("convert_languages_to_id_isocode_string %s" % str)
        return str

    def retrieve_action_list(self, action_menu_url):
        """
        Request the action menu content from the CTAP and return the list the action items
        :param test:  Test instance
        :param action_menu_url: action menu URL with the parameters to replace
        :return: The list of action items available
        """
        audio_languages = self.retrieve_audio_languages()
        logging.info("audio_languages %s " % str(audio_languages))
        id_selected_track = self.retrieve_selected_audio_track_id()
        logging.info("id_selected_track %s " % str(id_selected_track))
        audio_string = self.convert_languages_to_id_isocode_string(audio_languages)
        action_menu_url = action_menu_url.replace("{audioTracks}",audio_string)
        action_menu_url = action_menu_url.replace("{activeAudioTrackId}",id_selected_track)
        action_menu_content = self.get_action_menu_content_by_href(action_menu_url)
        return self.retrieve_action_list_from_content(action_menu_content)

    def check_action_menu_logo_title(self, expected_channel_logo, expected_event_title) :
        """
        Check validity of the logo URL and the event title displayed in the current action menu screen
        :param expected_channel_logo: The expected logo URL
        :param expected_event_title: The expected event title
        :return: True only if the logo URL and the event title in the action menu are the expected ones
        """
        elements = self.test.milestones.getElements()
        channel_info = self.test.milestones.get_value_by_key(elements, "prog_channel_info")
        am_channel_logo = ""
        if not channel_info:
            logging.info("no channel_info milestone")
        else:
            if 'logo' in channel_info:
                logging.info("logo found item")
                if channel_info['logo'] != "" and channel_info['logo'] != None and channel_info['logo'] != False:
                    logging.info("logo present")
                    am_channel_logo = channel_info['logo']

        am_event_title = self.test.milestones.get_value_by_key(elements, "prog_title")
        if am_channel_logo != expected_channel_logo :
            logging.error("Failure on channel. Expected: %s, found: %s" % (expected_channel_logo, am_channel_logo))
            return False
        if am_event_title != expected_event_title :
            logging.error("Failure on event title. Expected: %s, found: %s" % (expected_event_title, am_event_title))
            return False
        return True

    def check_if_action_in_action_menu(self, action):
        if self.test.milestones.get_current_screen()=="action_menu":
            actions_in_actionmenu = self.get_actions_from_current_actionmenu()
            return action in actions_in_actionmenu
        else:
            return False



