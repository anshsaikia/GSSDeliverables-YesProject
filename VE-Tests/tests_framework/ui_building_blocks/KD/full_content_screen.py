
__author__ = 'paln'

from tests_framework.ui_building_blocks.screen import Screen, ScreenActions
from tests_framework.ui_building_blocks.KD.library import FilterType
from tests_framework.ui_building_blocks.K.library_filter import FilterType as K_filterType
import logging
from enum import Enum
from retrying import retry

'''Constants'''
TIMEOUT = 2
PILL_BOX_CONTENT = 10

class SortType(Enum):
    EDITORIAL = "editorial"
    DATE = "date"
    A_TO_Z = "title"



class FullContentScreen(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "full_content_screen")
        if self.test.project_type == "KD":
            self.filter_type = FilterType
        else:
            self.filter_type = K_filterType

    def is_found_event_by_title(self, title, start_from_top=True):
        logging.info("Event: %s " % title)

        if start_from_top:
            self.scroll_to_edge(direction = ScreenActions.DOWN)

        screen_elements = self.test.milestones.getElements()
        title_element = self.test.milestones.getElement([("title_text", str(title).upper(), "(_")], screen_elements)
        #Swiping indefinitely until we find the event or nothing to swipe
        while title_element == None or len(title_element['title_text']) == 0:
            event_view = self.test.ui.get_center_element("event_view", screen_elements)
            scroll_distance = event_view['height']
            self.test.appium.swipe_element(event_view, scroll_distance, ScreenActions.UP)
            logging.info("Swiping up")
            screen_elements_after_swiping = self.test.milestones.getElements()
            if screen_elements == screen_elements_after_swiping:
                logging.info("Reached end.")
                break
            else:
                screen_elements = screen_elements_after_swiping
            title_element = self.test.milestones.getElement([("title_text",str(title).upper(), "(_")], screen_elements)
        self.test.log_assert(title_element and len(title_element['title_text']) != 0,"Event '%s' not Found" % title)
        return title_element

    def is_found_event_by_event_id(self, event_id, start_from_top=True):
        logging.info("Event: %s " % event_id)

        if start_from_top:
            self.scroll_to_edge(direction = ScreenActions.DOWN)

        screen_elements = self.test.milestones.getElements()
        title_element = self.test.milestones.getElement([("event_id", str(event_id).upper(), "in")], screen_elements)
        #Swiping indefinitely until we find the event or nothing to swipe
        while title_element == None or len(title_element['event_id']) == 0:
            event_view = self.test.ui.get_center_element("event_view", screen_elements)
            scroll_distance = event_view['height']
            self.test.appium.swipe_element(event_view, scroll_distance, ScreenActions.UP)
            logging.info("Swiping up")
            screen_elements_after_swiping = self.test.milestones.getElements()
            if screen_elements == screen_elements_after_swiping:
                logging.info("Reached end.")
                break
            else:
                screen_elements = screen_elements_after_swiping
            title_element = self.test.milestones.getElement([("event_id",str(event_id).upper(), "(_")], screen_elements)
        self.test.log_assert(title_element and len(title_element['event_id']) != 0,"Event '%s' not Found" % event_id)
        return title_element

    def do_swipe(self, direction):
        screen_elements = self.test.milestones.getElements()
        window_width, window_height = self.test.milestones.getWindowSize()
        element = {
            "x_pos": window_width / 2,
            "y_pos": window_height / 2,
            "width": window_width / 2,
            "height": window_height / 2
        }
        # Swiping indefinitely until no more swiping (edge of content)
        event_view = self.test.milestones.getElement([("name", "event_view", "==")], screen_elements)
        if event_view is not None:
            scroll_distance = event_view['height']
            #self.test.appium.swipe_element(event_view, scroll_distance, direction)
            self.test.mirror.swipe_area(element['x_pos'],element['y_pos'] + element['height'], element['x_pos'], element['y_pos'])
            logging.info("Swiping %s" % direction.value)
        else:
            logging.info("There are no events on the screen. No need to swipe")

        @retry(stop_max_attempt_number=10, wait_fixed=500)
        def check_reached_end():
            screen_elements_after_swiping = self.test.milestones.getElements()
            assert screen_elements != screen_elements_after_swiping
            return screen_elements_after_swiping
        try:
            return check_reached_end()
        except:
            logging.info("Reached Edge.")
            return None


    def tap_event_by_title(self, title):
        title_element = self.is_found_event_by_title(title)
        self.test.appium.tap_element(title_element)
        self.test.wait(TIMEOUT)

    def tap_event_by_event_id(self, event_id):
        title_element = self.is_found_event_by_event_id(event_id)
        self.test.appium.tap_element(title_element)
        self.test.wait(TIMEOUT)

    def scroll_to_edge(self, direction = ScreenActions.UP):
        screen_elements = self.test.milestones.getElements()
        window_width, window_height = self.test.milestones.getWindowSize()
        element = {
            "x_pos": window_width/2,
            "y_pos": window_height/2,
            "width": window_width/2,
            "height": window_height/2
        }
        #Swiping indefinitely until no more swiping (edge of content)
        while True:
            event_view = self.test.milestones.getElement([("name", "event_view", "==")], screen_elements)
            if event_view is not None:
                scroll_distance = event_view['height']
                self.test.appium.swipe_element(element, scroll_distance, direction)
                logging.info("Swiping %s" % direction.value)
            else:
                logging.info("There are no events on the screen. No need to swipe")

            screen_elements_after_swiping = self.test.milestones.getElements()
            if screen_elements == screen_elements_after_swiping:
                logging.info("Reached Edge.")
                break
            else:
                screen_elements = screen_elements_after_swiping


    def select_menu_item(self, menu_title):
        screen_elements = self.test.milestones.getElements()
        test_element = self.test.milestones.getElement([("title_text", str(menu_title).upper(), "==")], screen_elements)
        self.test.log_assert(test_element,"Menu element %s not Found" % menu_title)
        logging.info("Selecting  %s" % menu_title)
        self.test.appium.tap_element(test_element)
        self.test.wait(TIMEOUT)

    def get_first_event(self, asset_type="vod"):
        self.verify_active()
        self.scroll_to_edge(direction = ScreenActions.DOWN)
        elements = self.test.milestones.getElements()
        first_event = None

        if asset_type == "vod":
            event_type = "EVENT_TYPE_VOD_ASSET"
            event_source = "EVENT_SOURCE_TYPE_VOD"
        elif asset_type == "pvr":
            event_type = "EVENT_TYPE_PVR_ASSET"
            event_source = "EVENT_SOURCE_TYPE_PVR"

        for i in range(len(elements)):
            element = elements[i]
            if "name" in  element and element["name"] == "event_view" and (("event_type" in element and (element["event_type"] == event_type) or ("event_source" in element and element["event_source"] == event_source))):
                first_event = element
                break
        self.test.log_assert(first_event!=None, "No VOD asset events on full content screen")
        return first_event

    def screen_empty(self):
        message_text = None
        self.verify_active()
        elements = self.test.milestones.getElements()
        event_view = self.test.milestones.getElement([("name", "event_view", "==")], elements)

        return event_view is None

    def get_all_assets_in_full_content_screen(self, event_type):
        self.verify_active()

        allAssetsInFullContentScreen = []
        endOfScreen = False

        while endOfScreen == False:
            elements = self.test.milestones.getElements()
            for pos, curr in enumerate(reversed(elements)):
                if "event_type" in curr and curr["event_type"] == event_type:
                    lastElement = curr
                    break

            if any(lastElement["event_id"] == asset["event_id"] for asset in allAssetsInFullContentScreen):
                endOfScreen = True
                break

            for indexElement in elements:
                if ("event_type" in indexElement and indexElement["event_type"] == event_type):
                    if not any(indexElement["event_id"] == asset["event_id"] for asset in allAssetsInFullContentScreen):
                        allAssetsInFullContentScreen.append(indexElement)

            self.test.ui.swipe_element("up")

        return allAssetsInFullContentScreen

    def sort(self, sort_type = SortType.A_TO_Z):
        self.test.log_assert(sort_type in [SortType.A_TO_Z, SortType.DATE, SortType.EDITORIAL], "Undefined sort type '%s'" % sort_type)

        self.scroll_to_edge(direction = ScreenActions.DOWN)
        if sort_type == SortType.A_TO_Z:
            title_menu = self.test.milestones.get_dic_value_by_key('DIC_MENU_SORT_BY_TITLE', 'general')
        elif sort_type == SortType.DATE:
            title_menu = self.test.milestones.get_dic_value_by_key('DIC_MENU_SORT_BY_DATE', 'general')
        elif sort_type == SortType.EDITORIAL:
            title_menu = self.test.milestones.get_dic_value_by_key('DIC_MENU_SORT_BY_EDITORIAL', 'general')
        self.select_menu_item(title_menu)

    def verify_full_content_and_sort(self, filterType):
        # Sort by title and verify
        self.sort(SortType.A_TO_Z)
        self.verify_contents(filterType, SortType.A_TO_Z)
        # Sort by date and verify
        self.sort(SortType.DATE)
        self.verify_contents(filterType, SortType.DATE)

    def verify_contents(self, filterby, sortBy):
        from vgw_test_utils.headend_util import get_all_catalog

        titles = self.get_all_events()

        if sortBy == SortType.A_TO_Z:
            self.test.log_assert(sorted(titles) == titles, "Events are not sort by %s" % (sortBy))
        elif sortBy == SortType.DATE:
            if filterby ==  self.filter_type.SCHEDULED:
                catalog = get_all_catalog(filter_to_use="state=BOOKED", sort_to_use="-created")
            elif filterby == self.filter_type.RECORDINGS:
                catalog = get_all_catalog(filter_to_use="state=RECORDING&filter:state=RECORDED",
                                          sort_to_use="-startTime")
            self.test.log_assert (len(catalog) == len(titles), "events from pps does not match events displayed")
            sorted_assets = [x['content']['title'].upper() for x in catalog]
            self.test.log_assert(sorted_assets == titles,
                               "Events are not sort by %s" % (sortBy))


    def get_all_events(self):
        dvr_elements = self.test.milestones.getElementsArray([('event_source', 'EVENT_SOURCE_TYPE_PVR', '==')])
        total_event_names = [x["title_text"] for x in dvr_elements]

        while self.do_swipe(ScreenActions.UP) != None:
            dvr_elements = self.test.milestones.getElementsArray([('event_source', 'EVENT_SOURCE_TYPE_PVR', '==')])
            screen_event_names = [x["title_text"] for x in dvr_elements]
            for event in screen_event_names:
                if event not in total_event_names:
                    total_event_names.append(event)

        return total_event_names

