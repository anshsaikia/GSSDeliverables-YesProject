__author__ = 'paln'


import logging
import json
import re
from tests_framework.ui_building_blocks.screen import Screen, ScreenActions
from tests_framework.ui_building_blocks.KD.main_hub import Showcases
from operator import itemgetter
from tests_framework.ui_building_blocks.KD.full_content_screen import SortType
from tests_framework.he_utils.he_utils import VodContentType

''' Constants '''
TIMEOUT = 4


class CategoryNode(object):
    def __init__(self, id=None, name=None, leaf=None, type=None, media=None, menuScript=None, branding_media=None):
        self.id = id
        self.name = name
        self.leaf = leaf
        self.type = type
        self.media = media
        self.menuScript = menuScript
        self.branding_media = branding_media
        self.content = []
        self.children = []
 
    def __str__(self):
        return "Name " + self.name


class Store(Screen):
    def __init__(self, test, screen_name):
        Screen.__init__(self, test, screen_name)
    
    def create_category_tree(self):
        ctap_response = self.test.ctap_data_provider.get_categories_by_id(categoryId="")
        root = CategoryNode(id = "-1", name="STORE", leaf=False)
        tree = self.build_node(node=root, response=ctap_response)
        return tree
    
    def build_node(self, node, response):
        if node.leaf is False:
            for category in response['categories']:
                if category['type'] == "category_shop":
                    tmpNode = CategoryNode(id=category['id'], name=category['name'], leaf=category['leaf'],
                                           type=category['type'], media=category['media'],
                                           branding_media=category['branding']['media'])
                else:
                    tmpNode = CategoryNode(id=category['id'], name=category['name'], leaf=category['leaf'],
                                               type=category['type'])
                if category['leaf'] is False:
                    data = self.test.ctap_data_provider.get_categories_by_id(category['id'])
                else:
                    data = "Empty"
                                                       
                addData = self.build_node(node=tmpNode, response=data)
                node.children.append(addData)
        else:
            contents_response = self.test.ctap_data_provider.get_content_list_for_category(node.id, sortBy=SortType.DATE)
            contents = contents_response['content']
            for content in contents:
                if 'content' in content:
                    node.content.append(content['content'])
        return node


    def display_tree(self,tree_obj = None):
        logging.info("Tree.id is: %s" %tree_obj.id)
        logging.info("Tree.name is: %s Tree.leaf: %s" %(tree_obj.name, tree_obj.leaf))
        for child in tree_obj.children:
            logging.info("Tree.childrens %s"%child.name)
        for categories in tree_obj.children:
            self.display_tree(categories)

    def select_scroller_item_by_title(self, title):
        window_width, window_height = self.test.milestones.getWindowSize()
        title = title.upper()
        #workaround to handle HE typo
        # if (str(title) == 'KOMDIE'):
        #     title = 'KOMEDIE'

        elements = self.test.milestones.getElements()
        scroller_item = self.test.milestones.getElement([(self.get_title_property(isEvent=False), title, "==")], elements)
        if scroller_item == None or (280+scroller_item["x_pos"]>window_width):
            y = window_height / 2
            left_x = window_width / 1.5
            right_x = 0
            self.test.mirror.swipe_area(left_x, y,int(right_x), y, 1000)
            elements = self.test.milestones.getElements()
            scroller_item = self.test.milestones.getElement([(self.get_title_property(isEvent=False), title, "==")], elements)

        if scroller_item != None and scroller_item['x_pos'] + 280 > window_width:
            y = window_height / 2
            left_x = window_width / 1.5
            right_x = window_width / 4
            self.test.mirror.swipe_area(left_x, y, int(right_x), y, 1000)
            elements = self.test.milestones.getElements()
            scroller_item = self.test.milestones.getElement([(self.get_title_property(isEvent=False), title, "==")], elements)

        while scroller_item is None:
            self.check_scroller_item_by_title(title, isEvent=False)
            elements_after_swiping = self.test.milestones.getElements()
            scroller_item = self.test.milestones.getElement([(self.get_title_property(isEvent=False), title, "==")], elements)
            if elements_after_swiping == elements:
                break
            else:
                elements = elements_after_swiping
        self.test.log_assert(scroller_item,"scroll menu item element [%s] not Found" % title)
        self.test.appium.tap_element(scroller_item)
        self.test.wait(TIMEOUT)

    def select_menu_item_by_title(self, title):
        logging.info("Menu: %s " % title)
        title = title.upper()
        # if (str(title) == 'KOMDIE'):
        #     title = 'KOMEDIE'
        self.test.logCurrentScreen()
        
        elements = self.test.milestones.getElements()
        menu_item = self.test.milestones.getElement([(self.get_title_property(isEvent=False), title, "==")], elements)
        
        #Swiping indefinitely until we find the menu or nothing to swipe
        while menu_item is None:
            window_width, window_height = self.test.milestones.getWindowSize()
            logging.info("swiping up")
            self.test.mirror.swipe_area(window_width/2, window_height-10,
                                        window_width/2, int(window_height/1.25), 1000)
            elements_after_swiping = self.test.milestones.getElements()
            menu_item = self.test.milestones.getElement([(self.get_title_property(isEvent=False), title, "==")], elements_after_swiping)
            if elements_after_swiping == elements:
                logging.info("Reached end.")
                break
            else:
                elements = elements_after_swiping
        self.test.log_assert(menu_item,"Vod Store menu element [%s] not Found" % title)
        logging.info("Tapping Element Name is: %s " % title)
        self.test.appium.tap_element(menu_item)
        self.test.wait(TIMEOUT)


    def get_classification_type(self, classificationKey, classificationName):
        classificationId1= classificationKey[:classificationKey.index(classificationName) + len(classificationName)]
        classificationId2= classificationId1.replace("TERM", "node")
        classificationPath = classificationId2 + '~' + classificationId1
        categories = self.test.ctap_data_provider.get_categories_by_id(classificationPath)
        return categories['type']

    def get_category_path(self, classificationKey):
        first_index = classificationKey.find("store")
        self.test.log_assert(first_index >= 0,"'store' is not in categoryId. Invalid categoryId [%s]" % classificationKey)
        path = classificationKey[first_index:]
        path = path.split(':')
        last_category = path[len(path) -1]
        i = re.search("\d", last_category)
        #ignoring digits in last category
        if i:
            path[len(path) -1] = last_category[:i.start()]
        
        logging.info("category path:  %s" % path)
        return path

    def navigate_to_category(self, classificationKey):
        self.navigate()
        categories = self.test.ctap_data_provider.get_categories_by_id(classificationKey)
        categoryName = categories['name']
        categoryType = categories['type']
        logging.info("Navigate to VOD category %s" % categoryName)
        logging.info("VOD category type %s" % categoryType)
        category_path = self.get_category_path(classificationKey)
        self.navigate()
        for i in range(1, len(category_path)):
            #on the first level in store its always vertical menu
            if i == 1:
                self.select_menu_item_by_title(category_path[i])
            else:
                classificationType = self.get_classification_type(classificationKey, category_path[i-1])
                if classificationType == 'category_list':
                    if i+1 == len(category_path):
                        self.select_scroller_item_by_title(categoryName)
                    else:
                        self.select_scroller_item_by_title(category_path[i])
                else:
                    if i+1 == len(category_path):
                        self.select_menu_item_by_title(categoryName)
                    else:
                        self.select_menu_item_by_title(category_path[i])
        return categoryName



    def get_store_classification_key(self, classificationKeys, searchTerm="store"):
        for key in classificationKeys:
            first_index = key.find(searchTerm)
            if first_index >= 0:
                return key
        self.test.log_assert(False, "Cannot find " + searchTerm + " in classification keys: " + str(classificationKeys))
        return None


    def navigate_to_vod_asset_by_title_same_screen(self,title):
        logging.info("Navigate to VOD asset %s" % title)
        asset = self.test.he_utils.getVodContent([VodContentType.TITLE], {'title': title})
        classificationKey = self.get_store_classification_key(asset["classificationKeys"])
        categoryName = self.navigate_to_category(classificationKey)
        channel = self.test.milestones.getElement([("title_text", title.upper(), "==")])
        
        for loop in range(0, 30):
            #Swipe row up:
            elements = self.test.milestones.getElements()
            row_element = self.test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")])
            self.test.log_assert(row_element, "Cannot find event with source of EVENT_SOURCE_TYPE_VOD")
            start_x = row_element['x_pos'] + row_element['width']/2
            start_y = row_element['y_pos'] + row_element['height']/2
            stop_x = start_x
            stop_y = row_element['y_pos'] - row_element['height']
            self.test.appium.swipe_area(start_x,start_y,stop_x,stop_y)
            self.test.appium.swipe_element(row_element, row_element["height"], ScreenActions.UP)
            self.test.wait(TIMEOUT)
            channel = self.test.milestones.getElement([("title_text", title.upper(), "==")])
            if channel:
                break
        self.test.log_assert(channel, "Cannot find channel of title: " + title)

        logging.info("%s channel found",title)
        channels = self.test.milestones.getElementsArray([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")])
        self.test.appium.tap_element(channel)

    def play_vod_by_title(self, title, verify_streaming=True, trailer=False):
        if self.test.project.upper() != "KD":
            self.navigate_to_vod_asset_by_title_same_screen(title)
            elements = self.test.milestones.getElements()
            self.test.wait(TIMEOUT)
            required_channel = self.test.milestones.getElement([("title_text", title.upper(), "==")])
            self.test.appium.tap_element(required_channel)
            self.test.wait(TIMEOUT)
            play_button = self.test.milestones.getElement([("id", "play", "==")])
            self.test.appium.tap_element(play_button)
            self.test.wait(TIMEOUT)
            if verify_streaming:
                self.test.screens.playback.verify_streaming_playing()
                self.test.screens.fullscreen.verify_active()
        else:
            self.navigate_to_vod_asset_by_title(title)
            if (trailer):
                self.test.screens.vod_action_menu.play_trailer()
            else:
                self.test.screens.vod_action_menu.verify_play_menu(present=True)
                self.test.screens.vod_action_menu.play_asset(verify_streaming=verify_streaming)

