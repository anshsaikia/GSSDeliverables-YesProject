__author__ = 'paln'

import logging
import json
import re
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ui_building_blocks.universal.store import Store
from tests_framework.ui_building_blocks.KD.main_hub import Showcases
from operator import itemgetter
from tests_framework.ui_building_blocks.KD.full_content_screen import SortType
from tests_framework.he_utils.he_utils import VodContentType

''' Constants '''

PILL_BOX_CONTENT = 10
TIMEOUT = 3
FULL_CONTENT_TIMEOUT=4

class KDStore(Store):
    def __init__(self, test):
        Store.__init__(self, test, "menu_store")
        self.PILL_BOX_CONTENT = PILL_BOX_CONTENT
        self.counter = 0

    def navigate(self):
        logging.info("Navigate to menu store")
        if self.is_active():
            return

        self.test.screens.main_hub.navigate()
        is_focused = self.test.screens.main_hub.focus_showcase(Showcases.STORE)
        while (not is_focused):
            self.test.screens.main_hub.navigate()
            is_focused = self.test.screens.main_hub.focus_showcase(Showcases.STORE)

        dic_value = self.test.milestones.get_dic_value_by_key("DIC_MAIN_HUB_STORE","general").upper()
        if self.test.project != "KD":
            store_label = self.test.milestones.getElement([("title_text", dic_value, "==")])
        else:
            store_label = self.test.milestones.getElement([("regular_text", dic_value, "==")])
        self.test.log_assert(store_label, "%s label was not found on main hub screen."%dic_value)

        self.test.appium.tap_element(store_label)

        self.verify_active()

    def navigate_no_tap(self):
        logging.info("Navigate to menu store")
        if self.is_active():
            return

        self.test.screens.main_hub.navigate()
        is_focused = self.test.screens.main_hub.focus_showcase(Showcases.STORE)
        while (not is_focused):
            self.test.screens.main_hub.navigate()
            is_focused = self.test.screens.main_hub.focus_showcase(Showcases.STORE)

        window_width, window_height = self.test.milestones.getWindowSize()
        self.test.appium.swipe_area(window_width / 10 * 8, window_height / 10 * 8, window_width / 10 * 2,
                               window_height / 10 * 8, 0)

    def get_title_property(self, isEvent=True):
        property = None
        if (self.test.project.upper() !="KD" or (self.test.platform == "Android" and isEvent==False)):
            property = "menu_item_title"
        else :
            property = "title_text"
        return property

    def check_scroller_item_by_title(self, title, isEvent=True):
        logging.info("Scroller item title: %s " % title)
        title_property = self.get_title_property(isEvent)
        window_width, window_height = self.test.milestones.getWindowSize()
        y = window_height/2
        left_x = window_width/1.5
        right_x = window_width/4
        self.test.mirror.swipe_area(int(right_x), y, left_x, y, 1000)
        if (self.test.screens.full_content_screen.is_active()):#case of sub classidication
            self.test.screens.full_content_screen.sort(SortType.A_TO_Z)
            self.test.mirror.swipe_area(int(window_width/4), window_height/2,
                    window_width/4, window_height/5, 1000)
        elements = self.test.milestones.getElements()

        scroller_item = self.test.milestones.getElement([(title_property, str(title), "(_")], elements)
        while scroller_item == None or len(scroller_item[title_property]) == 0:
            logging.info("swiping left")
            if (self.test.screens.full_content_screen.is_active()):#case of sub classidication
                 self.test.mirror.swipe_area(int(window_width/4), window_height/2,
                    window_width/4, window_height/5, 1000)
            else:
                self.test.mirror.swipe_area(int(left_x), y, right_x, y, 1000)
            elements_after_swiping = self.test.milestones.getElements()
            if elements == elements_after_swiping:
                logging.info("Reached end.")
                break
            else:
                elements = elements_after_swiping
            scroller_item = self.test.milestones.getElement([(title_property, str(title), "(_")], elements)

        self.test.log_assert(scroller_item and len(scroller_item[title_property]) != 0,"Vod Store scroller_item '%s' not Found. \nevent = %s" % (str(title), scroller_item))
        return scroller_item


    def select_event_by_title(self, title):
        event = self.check_scroller_item_by_title(title, isEvent=True)
        self.test.appium.tap_element(event)
        self.test.wait(TIMEOUT)
        self.test.screens.vod_action_menu.verify_active()

    def check_view_all(self, category, imprintcell =None):
        self.test.log("checking if VIEW ALL is present")
        elements = self.test.milestones.getElements()
        events = self.test.milestones.getElementsArray([("name", "event_view", "==")], elements)
        events = sorted(events, key=itemgetter('x_pos'))
        #View All is first element and has title, event_image_url as category name
        if (imprintcell) or ('title_text' in events[0] and events[0]['title_text'] is None):#when imprintcell is on screen or null event
            view_all_value = events[1]
        else:
            view_all_value = events[0]

        view_all_title = self.test.milestones.get_dic_value_by_key("DIC_VIEW_ALL_TITLE","general").upper()
        self.test.log_assert(view_all_value and 'title_text' in view_all_value, "No title text in view value: " + str(view_all_value))
        self.test.log_assert(view_all_value and 'time_text' in view_all_value, "No time text in view value: " + str(view_all_value))
        if view_all_value['title_text'].upper() == category.upper() and view_all_value['time_text'] == view_all_title:
            return view_all_value
        else:
            return None

    def tap_view_all(self, category,imprintcell= None):
        view_all_value = self.check_view_all(category, imprintcell)
        self.test.appium.tap_element(view_all_value)
        self.test.wait(TIMEOUT)

    def tap_imprint_cell(self):
        elements = self.test.milestones.getElements()
        events = self.test.milestones.getElementsArray([("name", "event_view", "==")], elements)
        events = sorted(events, key=itemgetter('x_pos'))
        self.test.appium.tap_element(events[0])
        self.test.wait(TIMEOUT)

    def tap_verify_imprint(self):
        self.test.log_assert( self.test.milestones.getElement([("is_imprint", "true", "==")]), "imprint view did not appear.")

    def compare_vod_sis_imprint_view_metadata(self,child):
        imprint_view = self.test.milestones.getElement([("is_imprint",True,"==")])
        self.test.ctap_data_provider.compare_imprint(imprint_view, child)

    def navigate_to_vod_asset_by_title(self, title):
        logging.info("Navigate to VOD asset %s" % title)
        asset = self.test.he_utils.getVodContent([VodContentType.TITLE], {'title': title})
        classificationKey = self.get_store_classification_key(asset["classificationKeys"])
        logging.info("classificationKey: " + classificationKey)

        categories = self.test.ctap_data_provider.get_categories_by_id(classificationKey)
        categoryType = categories['type']
        categoryName = self.navigate_to_category(classificationKey)
        self.test.wait(1)

        if categoryType != 'content_full':
            if self.check_view_all(categoryName):
                self.tap_view_all(categoryName)
                self.test.wait(FULL_CONTENT_TIMEOUT)
                self.test.screens.full_content_screen.tap_event_by_title(title)
            else:
                self.select_event_by_title(title)
        else:
            self.test.screens.full_content_screen.tap_event_by_title(title)

    def scroll_related_section(self):
        elements = self.test.milestones.getElements()
        if self.test.platform == "Android":
           events_scroller = self.test.milestones.getElement([("id","related_items_scroll_area", "==")], elements)
        else:
           events_scroller = self.test.milestones.getElement([("id","FullContentScroller", "==")], elements)

        related_elements = self.test.milestones.getElementInBorders(elements, events_scroller)

        window_width, window_height = self.test.milestones.getWindowSize()
        self.test.mirror.swipe_area(int(window_width / 2),
                                    window_height / 1.5, int(window_width / 2),
                                    window_height / 3, 1000)
        elements_after_swiping = ""
        while related_elements != elements_after_swiping:
            related_elements = elements_after_swiping
            self.test.appium.swipe_element(events_scroller, window_width / 5, ScreenActions.LEFT)
            elements_after_swiping = self.test.milestones.getElements()

    def verify_full_content_and_sort(self,categoryId, sort=None):
        full_content_screen = self.test.screens.full_content_screen

        if sort == SortType.EDITORIAL:
            # Sort by editorial and verify
            full_content_screen.sort(SortType.EDITORIAL)
            self.verify_contents(categoryId, SortType.EDITORIAL)

        else:
            # Sort by title and verify
            full_content_screen.sort(SortType.A_TO_Z)
            self.verify_contents(categoryId, SortType.A_TO_Z)

            # Sort by date and verify
            full_content_screen.sort(SortType.DATE)
            self.verify_contents(categoryId, SortType.DATE)

    def verify_contents(ve_test, categoryId, sortBy):
        full_content_screen = ve_test.test.screens.full_content_screen

        response = ve_test.test.ctap_data_provider.get_content_list_for_category(categoryId = categoryId, sortBy = sortBy)
        contents = response['content']
        # Verify sort by comparing first displayed asset to ctap
        first_event = full_content_screen.get_first_event()['title_text'].upper()
        ctap_first_event = contents[0]['content']['title'].upper()
        ve_test.test.log_assert(first_event in ctap_first_event, "Events are not sort by %s. expected first event = '%s' actual first event = '%s'" % (sortBy, ctap_first_event, first_event))

        t = []
        for content in contents:
            t.append(content['content'])
        num_contents = len(t)
        if num_contents > 15 and sortBy != SortType.EDITORIAL:
            num_contents = 15

        # Verify that tapping on a event leads to action-menu screen
        full_content_screen.tap_event_by_title(t[0]['title'].upper())
        action_menu = ve_test.test.screens.vod_action_menu
        action_menu.verify_active()
        full_content_screen.go_to_previous_screen()

        # Verify events
        for i in range(num_contents):
            full_content_screen.is_found_event_by_title(t[i]['title'].upper(), start_from_top=False)

    def traverse_VOD_Store(self, node, shopInShop=False, parentType = None, counter=0,miniTraverse=False):
        self.test.log("traverse_VOD_Store: " + str(node))
        for child in node.children:
            self.test.log(str(child))
            if (child.type == "category_shop" or miniTraverse):# test only two shops
                counter +=1
            if counter>3:
                continue
            if shopInShop:
                if(child.type =="category_list" ):#dont navigate to store when shopInShop navigation, will check leaf on main
                    continue
            elif (child.type == "category_shops_root" or child.type == "category_shop"): #dont navigate to SIS on store navigaton
                continue

            #if(shopInShop and (child.type == "category_shops_root" or child.type == "category_shop" )):
            if(shopInShop and (child.type == "category_shop" )) or (child.type == 'category_list'):
                if (self.test.screens.full_content_screen.is_active()):
                  self.go_to_previous_screen()
                self.select_scroller_item_by_title(child.name)#special case for shop root tap on scroller and not menu item
            elif(child.type == "content_full" and not node.name == "STORE"):
                if (self.test.screens.full_content_screen.is_active()):
                  self.go_to_previous_screen()
                self.select_scroller_item_by_title(child.name)#horizontal
            else:
                self.select_menu_item_by_title(child.name)#all other cases
            screen = self.test.milestones.get_current_screen()
            self.test.log("Navigated to " + screen)
            elements = self.test.milestones.getElements()
            imprint_cell = self.test.milestones.getElement([("id", "KDImprintItemView", "==")], elements)
            imprint_view= self.test.milestones.getElement([("is_imprint", True, "==")], elements)
            if child.leaf == False:
                if (imprint_cell):
                    self.tap_imprint_cell()
                    self.compare_vod_sis_imprint_view_metadata(child.menuScript)
                    self.go_to_previous_screen()
                parentType= child.type # i am a parent
                self.traverse_VOD_Store(child, shopInShop,parentType, counter)
            elif (imprint_view == None):#in that case there is no scroller
                contents = child.content
                contents_size = len(contents)
                #if "VIEW ALL" is present, move to full content, verify content and sort actions
                if (contents_size > self.PILL_BOX_CONTENT and not (child.type == "content_full" and not node.name == "STORE")):
                    self.tap_view_all(child.name,imprint_cell)
                    self.verify_full_content_and_sort(child.id)
                    first_event_title =  self.test.screens.full_content_screen.get_first_event()['title_text']
                    self.go_to_previous_screen()
                else:
                    #Verify store events
                    for i in range(contents_size):
                        self.check_scroller_item_by_title(contents[i]['title'].upper(), isEvent=True)
                    if contents_size > 0:
                        first_event_title = contents[0]['title']

                #Tap event -> check if it leads to action-menu
                if contents_size > 0:
                    window_width, window_height = self.test.milestones.getWindowSize()
                    self.test.mirror.swipe_area(int(window_width/4), window_height/2,
                    window_width/1, window_height/2, 1000)
                    self.select_event_by_title(str(first_event_title.upper()))
                    action_menu = self.test.screens.vod_action_menu
                    action_menu.verify_active()
                    if shopInShop and parentType == "category_shop":
                        action_menu.compare_vod_sis_actionmenu_metadata()
                    self.go_to_previous_screen()

        if not (self.test.milestones.get_current_screen() == "menu_store"):
         self.go_to_previous_screen()
