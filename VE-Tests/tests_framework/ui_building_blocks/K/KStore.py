from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ui_building_blocks.universal.store import Store
from tests_framework.ve_tests.tests_conf import DeviceType
import logging
from enum import Enum
import time
from retrying import retry

__author__ = 'zhamilto'

HIDE_KEYBOARD_EVENT = 111
MAX_NUM_OF_SHOPS_IN_SCROLLER = 10
TIMEOUT = 5


class SortType(Enum):
    DATE = "date"
    A_TO_Z = "title"


class KStore(Store):
    def __init__(self, test):
        Store.__init__(self, test, "store_filter")

    def get_shop_name(self):
        ctap_response = self.test.ctap_data_provider.get_categories_by_id(categoryId="")
        for section in ctap_response["categories"]:
            if section["type"] == "category_shops_root":
                return section["name"]

    def print_shops(self, elements):
        self.test.log_assert(elements or len(elements), "No elements passed")
        for element in elements:
            logging.info("Shop name: {} ".format(element["title_text"]))

    def navigate_to_channel_stores_row(self):
        ctap_response = self.test.ctap_data_provider.get_categories_by_id(categoryId="")
        for section in ctap_response["categories"]:
            if section["type"] == "category_shops_root":
                shop_root_name = section["name"]
                break
        # noinspection PyUnboundLocalVariable
        self.test.log_assert(shop_root_name, "Cannot find category shop root in CTAP")
        self.scroll_to_section(shop_root_name)

    def wait_for_events_by_selection_channel_stores(self, name):
        events = None
        for wait in range(0, 30):
            events = self.get_events_by_section_channel_stores(name)
            if events:
                break
            self.test.wait(1)
        self.test.log_assert(events, "Cannot find events for section " + name)
        return events

    def scroll_and_return_elements(self, section):
        all_elements = []
        curr_elements = ""
        sectionsElements = self.wait_for_events_by_selection_channel_stores(section)
        prev_elements = sectionsElements

        while prev_elements != curr_elements:
            all_elements += [sec_elem['title_text'] for sec_elem in sectionsElements]
            prev_elements = curr_elements
            start = [sectionsElements[0]['x_pos'] + sectionsElements[0]['width'], sectionsElements[0]['y_pos'] + sectionsElements[0]['height']/2]
            end = [sectionsElements[0]['x_pos'] - 15, sectionsElements[0]['y_pos']+ sectionsElements[0]['height']/2]
            self.test.appium.scroll(start, end, 3000)
            sectionsElements = self.wait_for_events_by_selection_channel_stores(section)
            curr_elements = sectionsElements
        if len(sectionsElements) > 1:
            all_elements += [sec_elem['title_text'] for sec_elem in sectionsElements]
        return list(set(all_elements))

    def scroll_down_and_return_elements(self):
        all_elements = []
        curr_elements = ""
        elements = self.test.milestones.getElements()
        sectionsElements = self.test.ui.get_sorted_elements('image_view', 'x_pos', elements)
        prev_elements = sectionsElements

        while prev_elements != curr_elements:
            all_elements += [s['title_text'] for s in self.test.milestones.getElementsArray([('section', 'VodChannels', '==')])]
            prev_elements = curr_elements
            start = [sectionsElements[0]['x_pos'], sectionsElements[0]['y_pos'] + sectionsElements[0]['height']]
            end = [sectionsElements[0]['x_pos'], sectionsElements[0]['y_pos']]
            self.test.appium.scroll(start, end, 3000)
            elements = self.test.milestones.getElements()
            sectionsElements = self.test.ui.get_sorted_elements('image_view', 'x_pos', elements)
            curr_elements = sectionsElements
        return list(set(all_elements))

    def get_events_by_section(self, name):
        elements = self.test.milestones.getElements()
        events = self.test.ui.get_sorted_elements("event_view", 'x_pos', elements, "section", name)
        return events

    def get_titles_by_section(self, name):
        titles = []
        prev_elements = None
        first_element = None
        while True:
            elements = self.test.milestones.getElements()
            for element in elements:
                element_keys = element.keys()
                if "name" in element_keys and element["name"] == "text_view" and "section" in element_keys and element["section"] == name:
                    if "title_text" in element and element["title_text"] not in titles:
                        if first_element is None or element["x_pos"] < first_element["x_pos"]:
                            first_element = element
                        titles.append(element["title_text"])

            self.test.appium.swipe_element(first_element, first_element["width"], ScreenActions.LEFT, 3000)
            if elements == prev_elements:
                break
            prev_elements = elements

        # Kind of work around take the titles back
        prev_elements = None
        while True:
            self.test.appium.swipe_element(first_element, first_element["width"]*5, ScreenActions.RIGHT, 2000)
            elements = self.test.milestones.getElements()
            if elements == prev_elements:
                break
            prev_elements = elements
            self.test.wait(0.5)

        return titles

    def get_events_by_section_channel_stores(self, name):
        elements = self.test.milestones.getElements()
        if name == "VodChannels":
            events = self.test.ui.get_sorted_elements("text_view", 'x_pos', elements, "section", name)
        else:
            events = self.test.ui.get_sorted_elements("event_view", 'x_pos', elements, "section", name)
        return events

    def navigate(self):
        if not self.test.screens.header.item_exists("DIC_MAIN_HUB_STORE"):
            self.test.screens.tv_filter.navigate()
        if not self.is_active():
            self.test.screens.header.tap_item("DIC_MAIN_HUB_STORE")
        if self.test.project == "NET":
            self.test.wait(TIMEOUT)
        self.verify_active()

    def extract_shops_from_tree(self, node):
        Shops = []
        shop_root_name = self.get_shop_name()

        for classific1 in node.children:
            if classific1.name == shop_root_name:
                logging.info("extract_shops_from_tree: Found {}".format(shop_root_name))
                for classific2 in classific1.children:
                    Shops.append(classific2)
        return Shops

    def verify_shops(self, ui_shops, ctap_shops):
        self.test.log_assert(len(ui_shops) <= MAX_NUM_OF_SHOPS_IN_SCROLLER, "more than 10 elements in scroller {}".format(ui_shops))

        for shop in ctap_shops[:MAX_NUM_OF_SHOPS_IN_SCROLLER]:
            self.test.log_assert(shop.name in ui_shops, "Shop {} couldn't be found in UI shops".format(shop.name))
            logging.info("Shops from CTAP are: {}".format(shop.name))  # KINDER is only a workaround in KD ingest

        # check SEE ALL
        shop_name = self.get_shop_name()
        if len(ctap_shops) > MAX_NUM_OF_SHOPS_IN_SCROLLER:
            see_all_element = self.test.milestones.getElement([("title_section", shop_name, "=="), ("title_text", "SEE ALL", "==")])
            self.test.log_assert(see_all_element, "SEE ALL not found")
            self.test.appium.tap_element(see_all_element)
            ui_shops_full_screen = self.scroll_down_and_return_elements()
            self.test.log_assert(len(ui_shops_full_screen) == len(ctap_shops), "not the same quantity: in HE {} in application full screen{}"
                                 .format(ctap_shops, ui_shops_full_screen))
            for shop in ctap_shops:
                self.test.log_assert(shop.name in ui_shops_full_screen, "Shop {} couldn't be found in UI shops full screen".format(shop.name))
                logging.info("Shops from CTAP are: {}".format(shop.name))

            # shop selection from full content screen
            self.tap_channel_stores_element()
            self.verify_channel_logo([d for d in ctap_shops[0].branding_media if d['type'] == 'logo_top'][0]['url'])
            self.go_to_previous_screen()
            self.go_to_previous_screen()

    @retry(stop_max_delay=240000, wait_fixed=1000)
    def get_element_retry(self, section, section_name, store):
        try:
            asset_element = self.test.milestones.getElement(section)
        except:
            logging.error("can't send milestone")
            raise AssertionError
        if not asset_element:
            logging.error("can't find asset")
            self.go_to_previous_screen()
            store.navigate_to_channel_stores_row()
            store.tap_channel_stores_element()
            found_section = self.scroll_to_section(section_name)
            self.test.log_assert(found_section, "Section " + str(section_name) + " not found on screen")
            raise AssertionError
        return asset_element

    def verify_content_full_section(self, section, up_section, store):
        section_name = str(section.name).upper()
        up_section_name = '< ' + str(up_section).upper()
        found_section = self.scroll_to_section(section_name)
        self.test.log_assert(found_section, "Section " + str(section_name) + " not found on screen")

        if len(section.content) > MAX_NUM_OF_SHOPS_IN_SCROLLER:  # should see SEE ALL and compare assets in it
            # Workaround until "SEE_ALL" test will be fixed, currently not working in iPhone app.
            if self.test.title == "test_verify_store_row":
                return
            asset_element = self.get_element_retry([("title_section", section.name, "=="), ("title_text", "SEE ALL", "==")], section_name, store)
            self.test.appium.tap_element(asset_element)
            ui_events = self.test.milestones.getElementsArray([("name", "event_view", "==")], self.test.milestones.getElements())
            ui_titles = [x['title_text'] for x in ui_events]
            # verify screen title(top left on the screen) indicates the previous screen ( "Action" in the
            # image seen on the right)
            screen_title = self.test.milestones.getElement(
                [("name", "text_view", "=="), ("title_text", section_name, "==")])
            self.test.log_assert(screen_title, "no indication to screen in see all")
            prev_screen_title = self.test.milestones.getElement(
                [("name", "text_view", "=="), ("title_text", up_section_name, "==")])
            self.test.log_assert(prev_screen_title, "no indication to previous screen in see all")

            # TODO: verify Up / Down scrolling options are available in order to view the rest of the assets
            #       (up down scrolling will be made only if there are more then x assets x = 18?)

            self.go_to_previous_screen()

        else:
            ui_titles = self.scroll_and_return_elements(section_name)
        for ctap_event in section.content:
            if str(ctap_event["title"]).upper() not in ui_titles:
                self.test.log_assert(False, "The asset event '" + str(ctap_event["title"]) + "' is not found in '" + str(section_name) + "' scroller")

        if len(section.content) > 0:
            asset_element = self.test.milestones.getElement([("name", "event_view", "=="), ("section", section_name, "==")])
            self.test.appium.tap_element(asset_element)
            self.test.wait(1)
            self.test.screens.action_menu.verify_active()
            self.go_to_previous_screen()

    def verify_category_list_section(self, section):
        section_name = str(section.name).upper()
        found_section = self.scroll_to_section(section_name)
        self.test.log_assert(found_section, "Section " + str(section_name) + " not found on screen")

        ui_categories = self.get_titles_by_section(section_name)
        for ctap_category in section.children:
            if str(ctap_category.name).upper() not in ui_categories:
                self.test.log_assert(False, "The category '" + str(ctap_category.name).upper() + "' is not found in '" + str(
                    section_name) + "' scroller")

        # verify next screen on tap
        if len(section.children) > 0:
            elements = self.test.milestones.getElements()
            category_element = None
            for element in elements:
                if "section" in element and "title_text" in element and element["name"] == "text_view" and element["section"] == section_name and str(element["title_text"]).upper() == str(section.children[0].name).upper():
                    category_element = element
                    break

            is_leaf_category = None
            for ctap_category in section.children:
                if str(ctap_category.name).upper() == str(category_element["title_text"]).upper():
                    is_leaf_category = ctap_category.leaf
                    break
            self.test.appium.tap_element(category_element)
            self.test.wait(1)
            # noinspection PyUnboundLocalVariable
            if is_leaf_category:
                self.test.screens.full_content_screen.verify_active()
            else:
                self.test.screens.store_filter.verify_active()
            self.go_to_previous_screen()

    def verify_channel_logo_in_asset_action_menu(self):
        elements = self.test.milestones.getElements()
        ui_channel_logo_url = self.test.milestones.get_elements_if_has_key(elements, "logo_bottom_url")
        self.test.log_assert(ui_channel_logo_url, "No channel logo found in UI")
        event_name = ui_channel_logo_url[0]["event_id"][0:ui_channel_logo_url[0]["event_id"].find('~')]
        ctap_channel_logo_url = self.test.ctap_data_provider.server_data_for_event_id(
            ui_channel_logo_url[0]["event_id"])
        self.test.log_assert(ctap_channel_logo_url,
                             "No channel logo found in ctap for event_id {}".format(ui_channel_logo_url[0]["event_id"]))
        ui_channel_logo_url = ui_channel_logo_url[0]["logo_bottom_url"]
        self.test.log_assert(ui_channel_logo_url, "No channel logo URL found in UI")
        ctap_channel_logo_url = ctap_channel_logo_url["branding"]["media"][0]["url"]
        self.test.log_assert(ctap_channel_logo_url, "No channel logo URL found in ctap ")
        self.test.log_assert(ui_channel_logo_url == ctap_channel_logo_url,
                             "CTAP and UI channel logo URL does not match")

        logging.info("Channel logo url was verified and is {}".format(ui_channel_logo_url))
        # Exit the action menu
        self.test.ui.tap_element("exit")

        return event_name

    def verify_channel_logo(self, ctap_channel_logo_url):
        time.sleep(2)
        elements = self.test.milestones.getElements()
        ui_channel_logo_url = self.test.milestones.get_elements_if_has_key(elements, "header_channel_store_logo")[0]['header_channel_store_logo']
        self.test.log_assert(ui_channel_logo_url, "No channel logo found in UI")
        self.test.log_assert(ui_channel_logo_url == ctap_channel_logo_url, "CTAP and UI channel logo URL does not match")
        logging.info("Channel logo url was verified and is {}".format(ui_channel_logo_url))

    def get_top_section_scroller(self, elements=None):
        if not elements:
            elements = self.test.milestones.getElements()
        scrollers = self.test.milestones.get_elements_if_has_key(elements, "section_title_header")
        top_section_scroller = scrollers[-1]
        for scroller in scrollers:
            if scroller["y_pos"] < top_section_scroller["y_pos"]:
                top_section_scroller = scroller

        return top_section_scroller

    def scroll_top_section(self):
        fullscreen = self.test.ui.fullscreen_element()
        top_scroller = self.get_top_section_scroller()
        start = [fullscreen["x_pos"] + (fullscreen["width"] / 2), fullscreen["y_pos"] + (fullscreen["height"] / 2)]
        end = [fullscreen["x_pos"] + (fullscreen["width"] / 2),
               fullscreen["y_pos"] + (fullscreen["height"] / 2) - top_scroller["section_height"]]
        self.test.appium.scroll(start, end)

    def scroll_to_top_of_screen(self):
        # The following scroll to top the store section
        elements = self.test.milestones.getElements()
        fullscreen = self.test.ui.fullscreen_element()
        while True:
            self.test.appium.swipe_element(fullscreen, 150, ScreenActions.DOWN, 500)
            self.test.wait(1)
            elements_after_swipe = self.test.milestones.getElements()
            lists_identical = True
            for elem in elements:
                if elem not in elements_after_swipe:
                    lists_identical = False
            if len(elements_after_swipe) != len(elements):
                lists_identical = False
            if lists_identical:
                break
            else:
                elements = elements_after_swipe

    def scroll_to_section(self, name):
        self.scroll_to_top_of_screen()
        fullscreen = self.test.ui.fullscreen_element()

        feature_poster_event = self.test.milestones.getElement([("name", "event_view", "=="), ("section", "poster", "==")])
        if feature_poster_event:
            self.test.appium.swipe_element(fullscreen, feature_poster_event["height"] + 15, ScreenActions.UP, 2000)

        section_scroller = None
        while True:
            self.test.wait(1)
            section_scroller = self.test.milestones.getElement([("section_title_header", name, "==")])
            if section_scroller:
                if self.test.device_type != DeviceType.TABLET:
                    menu_tab_bar = self.test.milestones.getElement([("name", "menu_tab_bar", "==")])
                    if section_scroller["y_pos"] + section_scroller["section_height"] > fullscreen["height"] - menu_tab_bar["height"]:
                        self.test.appium.swipe_element(fullscreen, section_scroller["section_height"], ScreenActions.UP, 2000)
                else:
                    if section_scroller["y_pos"] + section_scroller["section_height"] > fullscreen["height"]:
                        self.test.appium.swipe_element(fullscreen, section_scroller["y_pos"] + section_scroller["section_height"] - fullscreen["height"], ScreenActions.UP, 2000)
                break
            elements_before_scrolling = self.test.milestones.getElements()
            self.scroll_top_section()
            if elements_before_scrolling == self.test.milestones.getElements():
                break
        return section_scroller

    def get_categories_details_from_server(self):
        ctap_response = self.test.ctap_data_provider.get_categories_by_id(categoryId="")
        sections = []
        for category in ctap_response["categories"]:
            details = {
                "name": category["name"],
                "id": category["id"],
                "type": category["type"]
            }
            sections.append(details)
        return sections

    def tap_channel_stores_element(self):
        asset_elements = self.test.milestones.getElementsArray([("name", "text_view", "=="), ("section", "VodChannels", "==")])
        asset = asset_elements[0]
        for el in asset_elements:
            if asset['x_pos'] > el['x_pos']:
                asset = el
        self.test.appium.tap_element(asset)

    def tap_vod_asset_element(self):
        asset_element = self.test.milestones.getElement([("name", "event_view", "=="), ("event_source", "EVENT_SOURCE_TYPE_VOD", "==")])
        self.test.log_assert(asset_element, "Cannot find VOD Events")
        window_width, window_height = self.test.milestones.getWindowSize()
        if (window_height < asset_element['y_pos']+ asset_element['height']):
            self.test.appium.swipe_element(asset_element, asset_element['height'], ScreenActions.DOWN)
        self.test.appium.tap_element(asset_element)

    def get_title_property(self, isEvent):
        prop = "title_text"
        return prop

    @staticmethod
    def getNearestImage_x(options):
        x_pos = 10000

        for option in options:
            if option['x_pos'] < x_pos:
                returnElement = option
                x_pos = option['x_pos']

        # noinspection PyUnboundLocalVariable
        return returnElement

    def play_vod_content_by_title(self, policyContent, verifyStreaming=True):

        # Updating LCS with the correct ASN
        search = self.test.screens.search
        search.navigate()
        tittle_text = policyContent['title'].replace("\'", "\\\'")
        search.input_event_into_search_filed_and_search(tittle_text)
        if self.test.he_utils.platform.upper() == "ANDROID":
            self.test.appium.key_event(HIDE_KEYBOARD_EVENT)
        self.test.wait(TIMEOUT)
        elements = self.test.milestones.getElementsArray([("event_type", "EVENT_CONTENT_TYPE_STANDALONE", "==")])
        tap_element = self.test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")], elements)
        self.test.appium.tap_element(tap_element)
        self.test.wait(TIMEOUT)

        play_button_options = self.test.milestones.getElementsArray([("name", "image_view", "==")])
        # workaround to get the play label, will be replaced once it gets fixed.
        play_button = self.getNearestImage_x(play_button_options)
        self.test.appium.tap_element(play_button)
        self.test.wait(TIMEOUT)
        if verifyStreaming:
            self.test.screens.fullscreen.verify_active()
