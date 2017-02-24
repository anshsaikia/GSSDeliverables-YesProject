
from tests_framework.ui_building_blocks.screen import Screen
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from math import ceil
from time import sleep


class Fullcontent(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "full_content")

    def navigate(self, filter_path = ('GENRES', 'ACTION')):
        logging.info("Navigate to fullcontent")
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
        if screen == "full_content":
            return True

        if screen == "action_menu":
            '''
            Dismiss the action menu by the Back key
            :return:
            '''
            self.test.appium.key_event("KEYCODE_BACK")
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "full_content")
            self.verify_active()
            return status

        if screen == "filter":
            """
                In filter screen, go the the full content of a category (or leaf item)
                :param filter_path: path to go through in the tree to reach the category. This is the ID of the items to go through. In dummy, id == title
                :return: True when in category fullcontent
                :return: Classification id from the ctap for the category (or leaf item)
            """
            status, classification_id = self.screens.filter.focus_filter_category(filter_path=filter_path)

            logging.info("Going into Fullcontent")
            self.test.appium.key_event("KEYCODE_DPAD_LEFT")
            self.test.wait(CONSTANTS.GENERIC_WAIT)
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait(CONSTANTS.GENERIC_WAIT)

            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "full_content")
            if not status:
                logging.error("wait for full_content timed out")
                return False, classification_id

            self.verify_active()
            return True, classification_id

        self.verify_active()
        assert True, "Navigation not implementted in this screen : " + screen



    def focus_sort_in_fullcontent(self):
        """
        focus sort options in fullcontent
        :return: True when sort is focused
        """
        key_event = "KEYCODE_DPAD_UP"

        isSortFocused = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "isSortFocused")
        stop = False

        count_actions = 0
        while (not isSortFocused) and (not stop):
            self.test.appium.key_event(key_event)
            sleep(0.5)
            count_actions = count_actions + 1
            isSortFocused = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "isSortFocused")
            if count_actions == CONSTANTS.MAX_ACTIONS:
                if key_event != "KEYCODE_DPAD_DOWN" :
                    key_event = "KEYCODE_DPAD_DOWN"
                    count_actions = 0
                else:
                    stop = True

        if stop:
            return False

        return True
        
    def fullcontent_check_sorting_categories_ux(self):    
        """
        Check sorting items order
        :return: True/False
        """
        if not self.focus_sorting_item_in_fullcontent():
            return False
        milestone = self.test.milestones.getElements()
        sortingList = self.fullcontent_get_sorting_list(milestone)
        for sorting in sortingList:
            if not sorting == self.test.milestones.get_value_by_key(milestone, "selected_sort"):
                logging.error("" + self.test.milestones.get_value_by_key(milestone, "selected_sort") + " is focused instead of " + sorting)
                return False
            else :
                logging.info(self.test.milestones.get_value_by_key(milestone, "selected_sort") + "is focused")
                self.test.appium.key_event("KEYCODE_DPAD_RIGHT")
        return True

    def fullcontent_select_alphabetical_order(self):
        return self.fullcontent_select_item("ALPHABETICAL")

    def fullcontent_select_item(self, item):    
        """
        Select an item from the sorting menu
        :param item: item to be selected
        :return: True/False
        """
        status = self.fullcontent_focus_item(item)
        if not status:
            return False
        # logging.info(self.test.milestones.getElements())
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        sleep(0.5)
        # logging.info(self.test.milestones.getElements())
        return True

    def focus_sorting_item_in_fullcontent(self):
        """
        Focus sorting menu in fullcontent
        :return: True/False
        """
        milestone = self.test.milestones.getElements()
        if not isinstance(self.fullcontent_get_asset_list(milestone), list):
            return False
        if self.test.milestones.get_value_by_key(milestone, "selected_type") == "2_by_3":
            max_number_of_lines = ceil(float(len(self.fullcontent_get_asset_list(milestone)))/6)
        else :
            max_number_of_lines = ceil(float(len(self.fullcontent_get_asset_list(milestone)))/3)
        index = 0
        while self.test.milestones.get_value_by_key(milestone, "selected_type") != "category" and index < max_number_of_lines:
            self.test.appium.key_event("KEYCODE_DPAD_UP")
            index += 1
            sleep(0.5)
            milestone = self.test.milestones.getElements()

        if self.test.milestones.get_value_by_key(milestone, "selected_type") != "category":
            logging.error("Could not focus sorting list: %s " % self.test.milestones.get_value_by_key(milestone, "selected_type") )
            return False
        logging.info("Focus is now on sorting items")
        return True

    def fullcontent_focus_item(self, item):
        """
        Focus an item from the sorting menu
        :param item: item to be focused
        :return: True/False
        """
        # Set the focus in the Category List part
        milestone = self.test.milestones.getElements()
        if self.test.milestones.get_value_by_key(milestone, "selected_type") != "category":
            logging.info("Move to Sorting Category")
            if not self.focus_sorting_item_in_fullcontent():
                return False
        # Select the wanted Category
        milestone = self.test.milestones.getElements()
        current_sort = self.test.milestones.get_value_by_key(milestone, "current_category")
        sorting_list = self.fullcontent_get_sorting_list(milestone)
        current_sort_location = sorting_list.index(current_sort)
        go_to_sort_location = sorting_list.index(item)
        logging.info("Going to sort: " + item)

        if current_sort_location > go_to_sort_location:
            for i in range(go_to_sort_location, current_sort_location):
                self.test.appium.key_event("KEYCODE_DPAD_LEFT")
                sleep(0.5)
        else:
            for i in range(current_sort_location, go_to_sort_location):
                self.test.appium.key_event("KEYCODE_DPAD_RIGHT")
                sleep(0.5)

        milestone = self.test.milestones.getElements()
        if self.test.milestones.get_value_by_key(milestone, "selected_item") == item:
            return True

        logging.error("Could not focus item " + item + " in fullcontent")
        return False

    def fullcontent_check_sort_source(self, assets_arr, source_sort_order):
        """
        Checking the sort order according to assets type
        :param assets_arr: the full list of results assets
        :param source_sort_order: the expected order of assets. options: 'linear', 'pvr', 'vod'
        :returns: True if order as expected
        """
        logging.info("Expected sort order: %s" % source_sort_order)
        for asset in assets_arr:
            logging.info("--> asset: %s " % asset)

        linear_assets = [asset for asset in assets_arr if asset['source'] == 'broadcastTv']
        pvr_assets = [asset for asset in assets_arr if asset['source'] == 'recording']
        vod_assets = [asset for asset in assets_arr if
                      asset['source'] == 'vodUnEntitled' or asset['source'] == 'vodEntitled']

        linear_num = len(linear_assets)
        pvr_num = len(pvr_assets)
        vod_num = len(vod_assets)

        logging.info("Num of linear assets:" + str(linear_num))
        logging.info("Num of pvr assets:" + str(pvr_num))
        logging.info("Num of vod assets:" + str(vod_num))

        sorting_order_dict = {}
        internal_dict = {}
        i = 0
        for sort in source_sort_order:
            if sort == "linear":
                internal_dict["name"] = "LINEAR"
                internal_dict["num"] = linear_num
                internal_dict["assets"] = linear_assets
            if sort == "pvr":
                internal_dict["name"] = "PVR"
                internal_dict["num"] = pvr_num
                internal_dict["assets"] = pvr_assets
            if sort == "vod":
                internal_dict["name"] = "VOD"
                internal_dict["num"] = vod_num
                internal_dict["assets"] = vod_assets
            sorting_order_dict[i] = internal_dict
            i = i + 1
            internal_dict = {}

        sort_num1 = sorting_order_dict.get(0).get('num')
        sort_num2 = sorting_order_dict.get(1).get('num')
        sort_num3 = sorting_order_dict.get(2).get('num')
        if assets_arr[0:sort_num1] != sorting_order_dict.get(0).get('assets'):
            logging.info(
                "Sort by Source failed: " + sorting_order_dict.get(0).get('name') + " assets not in order expectation!")
            return False
        if assets_arr[sort_num1:sort_num1 + sort_num2] != sorting_order_dict.get(1).get('assets'):
            logging.info(
                "Sort by Source failed: " + sorting_order_dict.get(1).get('name') + " assets not in order expectation!")
            return False
        if assets_arr[sort_num1 + sort_num2:sort_num1 + sort_num2 + sort_num3] != sorting_order_dict.get(2).get(
                'assets'):
            logging.info(
                "Sort by Source failed: " + sorting_order_dict.get(2).get('name') + " assets not in order expectation!")
            return False

        return True

    def fullcontent_get_asset_list(self, milestone=None):
        """
        get list of asset in full content
        :param milestone: milestone used. If None, a resquest to the app will be made to get one
        :return: True/False
        """
        if milestone == None :
            return self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "asset_list")
        return self.test.milestones.get_value_by_key(milestone, "asset_list")

    def fullcontent_get_sorting_list(self, milestone=None):
        """
        get list of sorting option in fullcontent
        :param milestone: milestone used. If None, a resquest to the app will be made to get one
        :return: True/False
        """
        if milestone == None:
            return self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "sorting_category_list")
        return self.test.milestones.get_value_by_key(milestone, "sorting_category_list")

    def fullcontent_check_assets_are_focused(self, milestone=None):
        """
        Check that the asset part in fullcontent is focused
        :param milestone: milestone used. If None, a resquest to the app will be made to get one
        :return: True/False
        """
        if milestone == None:
            milestone = self.test.milestones.getElements()
        selected_type = self.test.milestones.get_value_by_key(milestone, "selected_type")
        # logging.info("selected_type: %s" %selected_type)
        if selected_type == "category":
            logging.error("Focus is not (or not only) on assets")
            return False
        else:
            logging.info("Focus is on Assets part")
            return True

    def fullcontent_check_focused_asset(self, asset, milestone=None):           
        """
        Check that [asset] in fullcontent is focused
        :param asset: asset to be focused
        :param milestone: milestone used. If None, a resquest to the app will be made to get one
        :return: True/False
        """
        if milestone == None:
            milestone = self.test.milestones.getElements()
        if not self.fullcontent_check_assets_are_focused(milestone):
            return False
        focused_asset = self.test.milestones.get_value_by_key(milestone, "selected_item")
        # logging.info("focused_asset: %s      asset['title']: %s" % (focused_asset, asset['title']))
        if not focused_asset == asset['title']:
            logging.error("focus is on asset " + focused_asset + " instead of " + asset['title'])
            return False
        return True

    def fullcontent_check_asset_n_is_focused(self, n, milestone=None):           
        """
        Check that focused asset is the nth one of the list
        :param n: position of the focused asset
        :param milestone: milestone used. If None, a resquest to the app will be made to get one
        :return: True/False
        """
        if milestone == None:
            milestone = self.test.milestones.getElements()

        expected_asset_list = self.test.milestones.get_value_by_key(milestone, "asset_list")
        if expected_asset_list == False:
            logging.error("No asset list")
            return False

        self.test.log_assert(expected_asset_list.__len__() > n , "There is not enough asset in the asset list :" + str(expected_asset_list))

        expected_asset = expected_asset_list[n]
        if expected_asset == None :
            logging.error("There is no asset number " + n + " defined in the model:   %s" %expected_asset)
        return self.fullcontent_check_focused_asset(expected_asset, milestone)

    def fullcontent_check_assets_displayed_respect_model(self, fullcontent_type):           
        """
        Check that all assets displayed are from the same type
        and that the number of asset per line is respected
        :param fullcontent_type: Type of the fullcontent : '2_by_3', '16_by_9', 'mixed'
        :return: True/False
        """
        if fullcontent_type not in ('2_by_3', '16_by_9', 'mixed') :
            logging.error("Invalid argument. Fullcontent type must be either 2_by_3, 16_by_9 or mixed")
            return False
        self.test.wait(2)
        milestone = self.test.milestones.getElements()
        asset_list = self.fullcontent_get_asset_list(milestone)
        selected_asset = self.test.milestones.get_value_by_key(milestone,"selected_item")
        selected_type = self.test.milestones.get_value_by_key(milestone,"selected_type")

        if not self.fullcontent_check_asset_n_is_focused(0, milestone):
            logging.error("Focus is not on the first asset")
            return False
        
        # Navigate through all the asset in order to check their type
        assets_by_line = 0      # nb of asset or sum of the weight of each asset
        tab_assets_byline=[]
        logging.info("going to verify %d assets"%(len(asset_list)))
        wait_time = 4           # time to wait before going to the next asset. for the 1st line, 
        MAX_LINES = 5           # max lines to verify. must be limited, if too much assets test can takes hours
        for i in range(0, len(asset_list)):
            # verify the current asset is ok in the list
            current_asset = None
            if asset_list[i]['title'] == selected_asset:        # must be in the same order (list / screen )
                current_asset = asset_list[i]
                if fullcontent_type in ('2_by_3', '16_by_9'):
                    assets_by_line += 1                         # num of assets by line
                else:                                           # in mixed mode it's the weight of assets
                    if selected_type == 'mixed_16_by_9' :
                        assets_by_line += 16                    # weight of this type of asset
                    else:
                        assets_by_line += 6                     # weight of mixed 2_3 type
                #logging.info("%d {%d} '%s': %s"%(i,assets_by_line,selected_asset,selected_type))
            else:                                               # may be at the end of the line 
                logging.info("new line: %d  '%s' != '%s'"%(i,asset_list[i]['title'] , selected_asset))
                tab_assets_byline.append(assets_by_line)        # collect all the lines sizes
                if len(tab_assets_byline) == MAX_LINES:          # not too much tests, limit is x lines
                    logging.info("max nb lines to test reached: end")
                    break
                elif len(tab_assets_byline) == 1:
                    wait_time -= 2                              # after the first line, it can be faster (why 1st line so slow ?)
                self.test.appium.key_event("KEYCODE_DPAD_DOWN") # at the beginning of the below line
                self.test.wait(2)
                milestone = self.test.milestones.getElements()
                selected_asset = self.test.milestones.get_value_by_key(milestone,"selected_item")
                if asset_list[i]['title'] == selected_asset:    # must be in the same order
                    current_asset = asset_list[i] 
                    assets_by_line = 1                          # first of the line
                    logging.info("%d {%d} '%s': %s"%(i,assets_by_line,selected_asset,current_asset['type']))
                    
            # Check that the asset type is the expected one
            if current_asset != None:
                if current_asset['type'] != fullcontent_type:   # the type in the list
                    logging.error("Asset type in list is not correct: %s" %(current_asset['type']))
                    return False
                if selected_type != fullcontent_type:   # the type of the asset on the screen
                    logging.error("Asset type focused is not correct: %s" %(selected_type))
                    return False
            else:
                logging.error("Asset '%s' is not in the asset list" % selected_asset)
                return False

            self.test.appium.key_event("KEYCODE_DPAD_RIGHT") # next asset is on the right
            self.test.wait(wait_time)
            milestone = self.test.milestones.getElements()
            selected_asset = self.test.milestones.get_value_by_key(milestone,"selected_item")
            selected_type = self.test.milestones.get_value_by_key(milestone,"selected_type")

        # must verify that the number/weight of asset by line is good            
        if fullcontent_type in ('2_by_3', '16_by_9'):
            ref = -1
            for nb in tab_assets_byline:
                logging.info("verifying nb assets/ln: %d"%(nb))
                if ref == -1:
                    ref = nb        # the nb of assets on the first line is the ref
                elif (nb != ref):
                    logging.error("the assets strike the line %d / %d" %(nb,ref)) 
        else:
            for nb in tab_assets_byline:
                logging.info("verifying weight of assets: %d"%(nb))
                if nb > CONSTANTS.FULLCONTENT_MIXED_ASSETS_LINE_WIDTH: # reached the max weight per line
                    logging.error("the assets overload the line %d / %d" %(nb,CONSTANTS.FULLCONTENT_MIXED_ASSETS_LINE_WIDTH))
        return True

    def is_in_full_content(self):
        """
        Test wheter we are in fullcontent
        :return: True/False
        """
        sleep(1)
        milestone = self.test.milestones.getElements()
        return self.test.milestones.get_value_by_key(milestone, "screen") == "full_content"

    def fullcontent_assets_are_in_alphabetical_order(self):      
        """
        Test wheter the assets are in alphabetical order
        :return: True/False
        """
        asset_list = self.fullcontent_get_asset_list()
        asset_list_title = []
        for asset in asset_list:
            asset_list_title.append(asset['title'])
        asset_list_title_sort_alpha = sorted(asset_list_title, key=lambda s: s.lower())

        if asset_list_title_sort_alpha != asset_list_title:
            logging.error("Assets in datamodel are not in alphabetical order:\n python sort: %s"
                          % asset_list_title_sort_alpha + "\n asset_list:  %s " % asset_list_title)
            return False

        return True

    def fullcontent_check_poster_format_by_source(self, assets_arr):
        """
        Checking the poster format associated to each source
        :param assets_arr: the full list of results assets
        :returns: True if format as expected
        """
        logging.info("fullcontent_check_poster_format_by_source")
        for asset in assets_arr:
            logging.info("--> asset: %s " % asset)

        linear_assets = [asset for asset in assets_arr if asset['source'] == 'broadcastTv']
        pvr_assets = [asset for asset in assets_arr if asset['source'] == 'recording']
        vod_assets = [asset for asset in assets_arr if
                      asset['source'] == 'vodUnEntitled' or asset['source'] == 'vodEntitled']

        linear_num = len(linear_assets)
        pvr_num = len(pvr_assets)
        vod_num = len(vod_assets)

        logging.info("Num of linear assets:" + str(linear_num))
        logging.info("Num of pvr assets:" + str(pvr_num))
        logging.info("Num of vod assets:" + str(vod_num))

        for asset in linear_assets:
            if asset['type'] == "16_by_9" or asset['type'] == "mixed_16_by_9":
                logging.info("Success on Linear poster format for asset: %s" % asset)
            else:
                logging.error("Failure on Linear poster format displayed: %s" % asset['type'])
                return False

        for asset in pvr_assets:
            if asset['type'] == "16_by_9" or asset['type'] == "mixed_16_by_9":
                logging.info("Success on Linear poster format for asset: %s" % asset)
            else:
                logging.error("Failure on PVR poster format displayed: %s" % asset['type'])
                return False

        for asset in vod_assets:
            if asset['type'] == "2_by_3" or asset['type'] == "mixed_2_by_3":
                logging.info("Success on Linear poster format for asset: %s" % asset)
            else:
                logging.error("Failure of VOD poster format displayed: %s" % asset['type'])
                return False

        return True

