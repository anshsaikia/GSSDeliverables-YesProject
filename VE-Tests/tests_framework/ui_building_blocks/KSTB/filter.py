__author__ = 'bngo'

import collections
from tests_framework.ui_building_blocks.screen import Screen
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS


def getIterable(element):
    if isinstance(element, collections.Iterable) and not isinstance(element, basestring):
        return element
        
    else:
        return element
        

class Filter(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "filter")
        
    def focus_menu_item_by_id_in_filter(self, crumbtrail, menu_id, expected_pos=10, check_pos=False):
        """
        in filter screen, move focus to menu which id in the ctap response is [menu_id]. Position of [menu_id] can be checked, with respect to current position 
        :param crumbtrail: filter sub type : "TELEVISION" "STORE" "LIBRARY" etc ...
        :param menu_id: id of the menu to be focused. In dummy mode menu_id == menu_title. This can make the test language independant
        :param expected_pos:         
        :param check_pos: st to True if position of [menu_title] is to be checked        
        :return: True when focus is on [menu_id], and that it is at position [expected_pos] with respect to current position
        """
        if self.test.is_dummy:
            menu_title = menu_id
        else:        
            menu_title = self.test.he_utils.get_filter_menuitem_title_by_item_id(crumbtrail, menu_id)
        
        if len(menu_title) == 0:
            logging.error("Cant find menu title for menu id %s " % menu_id)
            return False
        
        status = self.test.screens.main_hub.move_to_menu_from_basepos(menu_title=menu_title, expected_pos=expected_pos, check_pos=check_pos)
        if not status:
            logging.error("moving to %s failed" % menu_title)
            return False
            
        return True   
        
    def focus_filter_category(self, filter_path=('GENRES', 'ACTION')):
        """
        In filter screen, focus a category (leaf item)
        :param filter_path: path to go through in the tree to reach the category. This is the ID of the items to go through. In dummy, id == title
        :return: True when on category 
        :return: Classification id from the ctap for the focused category (or leaf item)
        """
        classId = ""
        catalogId = ""
        if filter_path:
            focused_milestone = "focused_item"
            direction = "vertical"
            
            filter_path_iter = getIterable(filter_path)

            if not self.test.is_dummy:
                catalogId = self.test.he_utils.getCatalogueId(self.test.he_utils.platform)
                classId = self.test.he_utils.get_rootClassificationID_from_catalogId(catalogId)
                last_direction = "vertical"

            for categoryId in filter_path_iter:

                if self.test.is_dummy:
                    title = categoryId
                else:
                    title, classId = self.test.he_utils.get_category_title_from_class_id(catalogId, classId, categoryId)
                status = self.test.screens.main_hub.move_to_menu_from_basepos(menu_title=title, direction=direction, focused_milestone=focused_milestone)
                if not status:
                    logging.error("moving to %s failed" % title)
                    return False, classId

                hasShowcase = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "hasShowcase")
                # logging.info("selected_object_count: %s" %selected_object_count)
                if hasShowcase:  # we have more than 1 selected items = assets are available and we are on a leaf
                    if direction != "horizontal":
                        direction = "horizontal"
                        focused_milestone = "focused_asset"
                else:
                    # logging.info("categoryId: %s   filter_path_iter[-1]: %s " % (categoryId, filter_path_iter[-1]))
                    if categoryId != filter_path_iter[-1]:  # only if we are not on a leaf
                        logging.info("going into %s " % title)
                        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
                        self.test.wait(CONSTANTS.GENERIC_WAIT)

            # at the end on the for loop, we should be on focused on a leaf item
        return True, classId

    def get_classification_id(self, filter_path=('GENRES', 'ACTION')):
        """
        In filter screen, get the classification id of a specific category
        :param filter_path: path to go through in the tree to reach the category. This is the ID of the items to go through. In dummy, id == title
        :return: Classification id from the ctap for the focused category (or leaf item)
        """
        classId = ""
        catalogId = ""
        if filter_path:

            filter_path_iter = getIterable(filter_path)

            if not self.test.is_dummy:
                catalogId = self.test.he_utils.getCatalogueId(self.test.he_utils.platform)
                classId = self.test.he_utils.get_rootClassificationID_from_catalogId(catalogId)

            for categoryId in filter_path_iter:

                if self.test.is_dummy:
                    title = categoryId
                else:
                    title, classId = self.test.he_utils.get_category_title_from_class_id(catalogId, classId, categoryId)

        return classId

    def get_root_classification_id(self, filter_path='RECOMMENDED'):
        """
        In filter screen, get the classification id of a specific category
        :param filter_path: path to go through in the tree to reach the category. This is the ID of the items to go through. In dummy, id == title
        :return: Classification id from the ctap for the focused category (or leaf item)
        """
        classId = ""
        catalogId = ""
        if filter_path:

            if not self.test.is_dummy:
                catalogId = self.test.he_utils.getCatalogueId(self.test.he_utils.platform)
                classId = self.test.he_utils.get_rootClassificationID_from_catalogId(catalogId)

                if self.test.is_dummy:
                    title = filter_path
                else:
                    title, classId = self.test.he_utils.get_category_title_from_class_id(catalogId, classId, filter_path)

        return classId


    def to_filter_leaf_from_filter(self, filter_path=('FILMS', 'RECOMMENDED')):
        """
        Same as focus_filter_category + check we are in filter screen 
        :param filter_path: path to go through in the tree to reach the category. This is the ID of the items to go through. In dummy, id == title
        :return: True when on category 
        :return: Classification id from the ctap for the focused category (or leaf item)
        """
        classification_id = ""

        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status:
            logging.error("wait for filter timed out")
            return False, classification_id

        status, classification_id = self.focus_filter_category(filter_path=filter_path)

        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status:
            logging.error("wait for filter timed out")
            return False, classification_id

        return True, classification_id
        
    def to_fullcontent_from_filter(self, filter_path = ('GENRES', 'ACTION')):
        """
        In filter screen, go the the full content of a category (or leaf item)
        :param filter_path: path to go through in the tree to reach the category. This is the ID of the items to go through. In dummy, id == title
        :return: True when in category fullcontent
        :return: Classification id from the ctap for the category (or leaf item)
        """
        classification_id = ""
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status :
            logging.error("wait for filter timed out")
            return False, classification_id
        
        status, classification_id = self.focus_filter_category(filter_path=filter_path)
        
        logging.info("Going into Fullcontent")
        self.test.appium.key_event("KEYCODE_DPAD_LEFT")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "full_content")
        if not status:
            logging.error("wait for full_content timed out")
            return False, classification_id

        return True, classification_id

    def get_day_in_tvfilter(self):
        """
        Return the day focused in tv_filter
        :return: day as a string
        """
        return self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_day")

    def get_month_in_tvfilter(self):
        """
        Return the month focused in tv_filter
        :return: month as a string
        """
        
        return self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_month")

    def focus_item_in_filterscreen_ux(self, item):
        """
        focus a specific item in filterscreen
        :param item: item to be focused
        :return: True when item is focused
        """
        milestone = self.test.milestones.getElements()
        itemsList = self.test.milestones.get_value_by_key(milestone, "item_list")
        if itemsList == False:
            return False
        
        l_itemsList = [x.lower() for x in itemsList]    # to be upper/lower case agnostic
        if item.lower() not in l_itemsList:
            logging.info("item " + item.lower() + " is not in: " + l_itemsList)
            return False
        
        focused_item = self.test.milestones.get_value_by_key(milestone, "focused_item").lower() # where we are
        nb_moves = l_itemsList.index(focused_item) - l_itemsList.index(item.lower())    

        if not nb_moves:                            # on the good item
            logging.info("item " + item + " is focused")
            return True
        
        if nb_moves < 0:
            key_dir = "KEYCODE_DPAD_UP"
            nb_moves = 0- nb_moves                  # == abs(nb_moves) without math lib
        else:
            key_dir = "KEYCODE_DPAD_DOWN"
        
        for _i in range(nb_moves):
            self.test.appium.key_event(key_dir)     # move to the desired item
        
        logging.info("item " + item + " is focused (" + str(nb_moves) + " move)")
        return True

    def select_item_in_filterscreen_ux(self, item):
        """
        validate the selected item in filter screen
        :param item: item to be selected
        :return: True when item is validated
        """
        if self.focus_item_in_filterscreen_ux(item):
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            return True
        else:
            return False

    def focus_sub_item_in_filterscreen_ux(self, sub_item):
        """
        focus a specific item in filterscreen
        :param sub_item: item to be focused
        :return: True when item is focused
        """
        milestone = self.test.milestones.getElements()
        sub_items_list = self.test.milestones.get_value_by_key(milestone, "sub_items")
        if not sub_items_list:
            return False

        for i in range(len(sub_items_list)):
            self.test.appium.key_event("KEYCODE_DPAD_LEFT")
        has_item = False
        logging.info(sub_item)

        for i in range(len(sub_items_list)):
            if sub_items_list[i].lower() == sub_item.lower():
                has_item = True
                break
            else:
                self.test.appium.key_event("KEYCODE_DPAD_RIGHT")

        if not has_item:
            logging.error("Could not find item " + sub_item + " in filter screen")
            return False
        else:
            logging.info("item " + sub_item + " is focused")
            return True

    def select_sub_item_in_filterscreen_ux(self, sub_item):
        """
        validate the selected item in filter screen
        :param item: item to be selected
        :return: True when item is validated
        """
        if self.focus_sub_item_in_filterscreen_ux(sub_item):
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            return True
        else:
            return False

    def focus_asset_in_filterscreen_ux(self, asset):
        """
        focus a specific asset in filterscreen
        :param asset: asset to be focused
        :return: True when asset is focused
        """
        milestone = self.test.milestones.getElements()
        assetList = self.test.milestones.get_value_by_key(milestone, "asset_list")
        focused_asset = self.test.milestones.get_value_by_key(milestone, "focused_asset")
        if assetList == None :
            logging.error("There is no asset associated to this filter item")
            return False

        focused_index = 0
        asset_index = 0
        for i in range(len(assetList)):
            if focused_asset == assetList[i]:
                focused_index = i
            if asset == assetList[i]:
                asset_index = i
        for i in range(abs(focused_index - asset_index)):
            if focused_index > asset_index:
                self.test.appium.key_event("KEYCODE_DPAD_LEFT")
            elif focused_index < asset_index :
                self.test.appium.key_event("KEYCODE_DPAD_RIGHT")

        if asset.__eq__(self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_asset")):
            logging.info("asset " + asset + " is focused")
            return True
        else :
            logging.error("asset : " + asset + " - focused_asset : " + self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_asset"))
            return False

    def select_asset_in_filterscreen_ux(self, asset):
        """
        validate the selected asset in filter screen
        :param asset: asset to be selected
        :return: True when asset is validated
        """
        if not self.focus_asset_in_filterscreen_ux(asset):
            return False
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        return True

    def search_keyword_typing(self, phrase, max_list_size=0):
        """
        Type phrase in the search field 
        :param phrase:
        :return:
        """
        alpha_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        # check that the focus is on a letter
        selected_char = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), 'selected_char')
        if selected_char == '<':
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
            self.test.wait(0.5)
            selected_char = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), 'selected_char')
        if selected_char not in alpha_list:
            logging.info("Focus is not on the Alphabetical line")
            return False
        
        list_updated = False
        for char in phrase:
            milest = self.test.milestones.getElements()
            selected_char = self.test.milestones.get_value_by_key(milest, 'selected_char')
            #logging.info("char: %s  selected: %s "%(char,selected_char))
            if max_list_size and list_updated:  # if the list size is bordered
                list_size = self.test.milestones.get_value_by_key(milest, "suggestions_nb")
                #logging.info("check the list size: %s"%(list_size))
                if list_size <= max_list_size:  # the list is small enough
                    #logging.info("size ok -> finish")
                    break                       # we can exit
                else:
                    logging.info("size too great %s"%(list_size))    
            
            if selected_char == '<':
                logging.info("No result Found. Focus is on Erase")
                return False
            else:                               # go on the next char of the phrase
                logging.info("move to next char")
                if char > selected_char:
                    moving = "KEYCODE_DPAD_RIGHT"
                else:
                    moving = "KEYCODE_DPAD_LEFT"
                    
                nbmovs = ord(char) - ord(selected_char)      # quick move to next char
                if nbmovs < 0:
                    nbmovs = -nbmovs
                if nbmovs > 3 and nbmovs < len(alpha_list):
                    nbmovs -= 2                              # nearest one
                    while nbmovs:
                        self.test.appium.key_event(moving)   # move without wait
                        nbmovs -= 1
                        
                for _i in alpha_list:
                    self.test.appium.key_event(moving)      # normally last move
                    self.test.wait(0.5)
                    selected_char = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), 'selected_char')
                    if char == selected_char:
                        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
                        self.test.wait(1)    # wait a few to let the list to be upgraded
                        list_updated = True
                        break
                
        return True

    def to_uilanguage_from_preferences(self, expected_pos=0, check_pos=False):
        """
        Modify the uilanguage to the one specify in parameter
        :param expected_pos:
        :param check_pos:
        :return: True/False
        """
        logging.info("--> to_uilanguage_from_preferences")

        href_uilanguage = "setUserProfilePreference?key=uiLanguage"
        uilanguage_title = self.test.he_utils.get_preferences_menuitem_title_by_item_href(href_uilanguage)

        logging.info("Moving focus to: %s" % uilanguage_title)

        if len(uilanguage_title) == 0:
            logging.error("Can not find %s" % uilanguage_title)
            return False

        status = self.test.screens.main_hub.move_to_menu_from_basepos(menu_title=uilanguage_title, direction="vertical",
                                                     expected_pos=expected_pos, check_pos=check_pos)

        if not status:
            logging.error("Fail to move focus on: %s" % uilanguage_title)
            return False

        return True

    def modify_uilanguage(self, ui_language='ENGLISH', expected_pos=0, check_pos=False):
        """
        Modify the uilanguage to the one specify in parameter
        :param ui_language: wanted uilanguage
        :param expected_pos:
        :param check_pos:
        :return: True/False
        """
        logging.info("--> modify_uilanguage")

        status = self.to_uilanguage_from_preferences()
        logging.info("Focus is on LANGUAGE")

        status = self.test.screens.main_hub.move_to_menu_from_basepos(menu_title=ui_language, direction="horizontal",
                                                     expected_pos=expected_pos, check_pos=check_pos,
                                                     focused_milestone="focused_asset")
        if not status:
            logging.error("Fail to move focus on: %s" % ui_language)
            return False
        else:
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait(CONSTANTS.GENERIC_WAIT)
            if not self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "isSelected"):
                logging.error("Failed to validate the ui language %s" % ui_language)
                return False

        return True
