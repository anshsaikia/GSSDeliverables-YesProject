__author__ = 'callix'

from time import sleep
from tests_framework.ui_building_blocks.screen import Screen
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS

class MainHub(Screen):

    def __init__(self, test):
        Screen.__init__(self, test, "main_hub")

    def navigate(self):
        '''
        Go to main_hub screen, from any screen
        :return: True when on main_hub screen
        '''
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)

        if screen == self.screen_name:
            return True

        if screen == "infolayer":
            self.test.wait(CONSTANTS.INFOLAYER_TIMEOUT)
        self.pop_stack_to_hub()
        self.verify_active()
        return True

    def long_back_press_to_hub(self):
        '''
        Long pressing BACK key to go back to main_hub screen
        :return: True when on main_hub, False otherwise
        currently not working
        '''
        logging.error("DO NOT USE")
        logging.info("Longpressing back key")
        self.test.long_key_press("KEYCODE_BACK")
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if(status) :
            logging.info("back to main hub screen")
        else :
            logging.error("cannot get back to main hub screen")
            #sometimes, long keypress back is not taken into account, try again
            logging.info("2nd try")
            self.test.long_key_press("KEYCODE_BACK")
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT*2, "main_hub")
            if(status) :
                logging.info("back to main hub screen")
            else :
                logging.error("still cannot get back to main hub screen")

        return status

    def pop_stack_to_hub(self, iteration=10):
        '''
        :return: True when on main_hub, False otherwise
        '''
        if self.test.wait_for_screen(0, "main_hub"):
            return True

        for _ in range(0, iteration):
            if self.test.wait_for_screen(CONSTANTS.GENERIC_WAIT, "main_hub"):
                return True
            self.test.key_press("KEYCODE_BACK", 0)

        return False
        

    def focus_default_menuitem_in_hub(self):
        '''
        in MainHub, move the focus to the first item of the menu
        :return:
        '''
    
        if self.test.is_dummy:
            default_title = CONSTANTS.HUB_TV
        else:
            default_title = self.test.he_utils.get_hub_default_menu_title()
        
        # logging.info("default_title %s"%default_title)
        
        
        if len(default_title) == 0 :
            logging.error("SHOWCASE item not found")
            return False
        
        current_focused = self.test.milestones.get_value_by_key(self.test.milestones.getElements(),"focused_item")
        old_focused = ""
        stop = False
        isDefaultMenuItemFocused = (current_focused == default_title)
        
        nb_actions = 0
        
        key_event = "KEYCODE_DPAD_UP"
        while (nb_actions < CONSTANTS.MAX_ACTIONS) and (not stop) and (not isDefaultMenuItemFocused) :
            self.test.appium.key_event(key_event)
            nb_actions = nb_actions + 1
            sleep(0.5)
            old_focused = current_focused
            current_focused = self.test.milestones.get_value_by_key(self.test.milestones.getElements(),"focused_item")
            isDefaultMenuItemFocused = (current_focused == default_title)
            if current_focused == old_focused :
                if key_event != "KEYCODE_DPAD_DOWN" :
                    key_event = "KEYCODE_DPAD_DOWN"
                    nb_actions = 0;
                else :
                    stop = True
            

        if not isDefaultMenuItemFocused :
            return False
        
            
        # for i in hub_horizontal_menuitem_list:
            # self.test.appium.key_event("KEYCODE_DPAD_LEFT")
            # sleep(0.5)
            
        return True
        
    def to_menu_in_hub(self, menuid = CONSTANTS.HUB_TV, menu_type = "vertical", expected_pos = 10, check_pos = False):
        '''
        in main_hub screen, move focus to menu which id in the ctap response is [menuid]. Position of [menuid] can be checked, with respect to current position 
        :param menuid: id of the menu to be focused. In dummy mode menuid == menu_title. This can make the test language independant. 
        Can be "fullscreen" "libraryMenu" "storeMenu" "preferencesMenu" "search" 
        :param menu_type: "vertical" or "horizontal" menu
        :param expected_pos:         
        :param check_pos: st to True if position of [menuid] is to be checked        
        :return: True when focus is on [menuid], and that it is at position [expected_pos] with respect to current position
        '''
        
        if not self.focus_default_menuitem_in_hub():
            logging.error("SHOWCASE item cant be focused")
            return False

        logging.info("Moving focus to menu id : %s" %menuid)
        
        if self.test.is_dummy:
            menu_title = menuid
        else:
            menu_title = self.test.he_utils.get_hub_menuitem_title_by_item_id(menuid)
            
        
        status = self.move_to_menu_from_basepos(menu_title = menu_title, direction=menu_type, expected_pos = expected_pos, check_pos = check_pos)
        if not status :
            logging.error("moving to %s failed"%menu_title)
            return False

        logging.info("Going into %s" %menu_title)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(CONSTANTS.GENERIC_WAIT)

        return True             
        
    def to_hub_root_showcase_in_hub(self):
        '''
        in MainHub, move the focus to the first asset on the showcase
         ie: focus is on the first thumbnail
        :return:
        '''
        status = self.focus_default_menuitem_in_hub()
        if not status :
            logging.error("cant focus SHOWCASE in hub")
            return False
            
        # self.test.appium.key_event("KEYCODE_DPAD_DOWN")

        return True

    def focus_item_in_hub(self, item_title, expected_pos=10, check_pos=False):
        '''
        Focus an item in Hub. Position can be checked, with respect to current position
        :param item_title: item title to focus
        :param expected_pos: Position of the item (vertical one)
        :param check_pos: set to True if position is to be checked
        :return: True/False
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if not status:
            logging.error("wait for main_hub timed out")
            return False
        logging.info("In main_hub")

        if check_pos:
            if not self.focus_default_menuitem_in_hub():
                logging.error("SHOWCASE item cant be focused")
                return False

        logging.info("Moving focus to %s" % item_title)

        status = self.move_to_menu_from_basepos(menu_title=item_title, direction="vertical", expected_pos=expected_pos, check_pos=check_pos)

        if not status:
            logging.error("moving to %s failed" % item_title)
            return False

        return True

    def focus_store_item_in_hub(self, expected_pos=2, check_pos=False):
        '''
        Focus the Store item in Hub. Position of Store menu_item can be checked, with respect to current position
        :param expected_pos: Position of the item (vertical one)
        :param check_pos: set to True if position is to be checked
        :return: True/False
        '''
        logging.info("--> focus_store_item_in_hub")
        if self.test.is_dummy:
            store_title = "ON DEMAND"
        else:
            store_title = self.test.he_utils.get_hub_menuitem_title_by_item_id("STORE")
        logging.info("Moving focus to: %s" % store_title)

        if len(store_title) == 0:
            logging.error("Can not find Store menu name")
            return False

        status = self.focus_item_in_hub(item_title=store_title, expected_pos=expected_pos, check_pos=check_pos)
        if not status:
            logging.error("Fail to move focus on: %s" % store_title)
            return False

        return True

    def navigate_to_store(self, expected_pos=2, check_pos=False):
        '''
        Access to the Store from Hub
        :param expected_pos: Position of the item (horizontal one)
        :param check_pos: does the position shall be checked
        :return: True/False
        '''
    
        #The commented code should be the real function, below is a workaround waiting for the hub to be converted to the new template mmodel
        
        # status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        # if not status :
            # logging.error("Not in main hub screen")
            # return False
        # self.to_menu_in_hub(menuid = "ON DEMAND", menu_type = "horizontal", expected_pos = expected_pos, check_pos = check_pos)

        # status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter" )
        # if not status :
            # logging.error("wait for store_filter timed out")
            # return False
        # logging.info("in Store")
        # return True

        self.navigate()
        status = self.focus_store_item_in_hub(expected_pos=expected_pos, check_pos=check_pos)
        if not status:
            logging.error("Fail to focus Store item in Hub")
            return False

        logging.info("Going into Store")
        self.test.appium.key_event("KEYCODE_DPAD_LEFT")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(CONSTANTS.GENERIC_WAIT)

        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status:
            logging.error("wait for store_filter timed out")
            return False
        logging.info("in Store")
        return True
    

    def to_hub_from_store(self):
        '''
        Come-back to Hub from the Store
        :return: True/False
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status:
            logging.error("wait for store_filter timed out")
            return False
        logging.info("in Store")
        self.test.appium.key_event("KEYCODE_BACK")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if not status:
            logging.error("wait for main_hub timed out")
            return False
        logging.info("In main_hub")
        return status

    def focus_search_item_in_hub(self, expected_pos=3, check_pos=False):
        '''
        Focus the Search item in Hub. Position of search menu_item can be checked, with respect to current position
        :param expected_pos: Position of the item (vertical one)
        :param check_pos: set to True if position is to be checked
        :return: True/False
        '''
        logging.info("--> focus_search_item_in_hub")
        if self.test.is_dummy:
            search_title = "SEARCH"
        else:
            search_title = self.test.he_utils.get_hub_menuitem_title_by_item_id("SEARCH")
        logging.info("Moving focus to: %s" % search_title)

        if len(search_title) == 0:
            logging.error("Can not find Search menu name")
            return False

        status = self.focus_item_in_hub(search_title, expected_pos, check_pos)
        if not status:
            logging.error("Fail to move focus on: %s" % search_title)
            return False

        return True
        


    def focus_settings_item_in_hub(self, expected_pos=4, check_pos=False):
        '''
        Focus the Settings item in Hub. Position can be checked, with respect to current position
        :param expected_pos: Position of the item (vertical one)
        :param check_pos: set to True if position is to be checked
        :return: True/False
        '''
        logging.info("--> focus_settings_item_in_hub")

        if self.test.is_dummy:
            settings_title = "SETTINGS"
        else:
            settings_title = self.test.he_utils.get_hub_menuitem_title_by_item_id("SETTINGS")
        logging.info("Moving focus to: %s" % settings_title)

        if len(settings_title) == 0:
            logging.error("Can not find Settings menu name")
            return False

        status = self.focus_item_in_hub(item_title=settings_title, expected_pos=expected_pos, check_pos=check_pos)
        if not status:
            logging.error("Fail to move focus on: %s" % settings_title)
            return False
        logging.info("<-- focus_settings_item_in_hub")

        return True
    
    def navigate_to_settings_sub_menu(self, sub_menu_href, expected_pos=10, check_pos=False):
        '''
        To settings screen from hub screen. Position of settings menu_item can be checked, with respect to current position
        :param sub_menu_href: sub menu href : PREFERENCES PARENTAL or SYSTEM_INFORMATION
        :param expected_pos:         
        :param check_pos: set to True if position of settings menu_item is to be checked        
        :return: True when in settings screen and position of menu_item is in the expected position. Otherwise returns False
        '''
        logging.info("--> navigate_to_settings_sub_menu sub_menu="+str(sub_menu_href))

        status = self.focus_settings_item_in_hub(expected_pos=expected_pos, check_pos=check_pos)
        if not status:
            logging.error("Fail to focus Settings item in Hub")
            return False

        logging.info("Focus is on Settings : sub_menu_href="+sub_menu_href)
        
        if self.test.is_dummy:
            sub_menu_title = sub_menu_href
        else:
            sub_menu_title = self.test.he_utils.get_hub_sub_menuitem_title_by_item_href(sub_menu_href)

        status = self.move_to_menu_from_basepos(sub_menu_title, direction="horizontal", focused_milestone="focused_asset")
        if status:
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            self.test.wait(CONSTANTS.GENERIC_WAIT)
        
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
            if not status:
                logging.error("wait for settings timed out")
                return False
        else:
            return False

        logging.info("In %s" % sub_menu_title)
        
        return True

    def focus_settings_sub_sub_menu(self, setting):
        setting = setting.lower()

        settings_list = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "item_list")
        settings_list = map(lambda x : x.lower(), settings_list)
        if setting not in settings_list:
            logging.error("couldn't find %s in %s" % (setting, settings_list))
            return False

        for _ in settings_list:
            focused_item = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_item")
            if focused_item.lower() == setting:
                return True
            self.test.appium.key_event("KEYCODE_DPAD_UP")
            self.test.wait(CONSTANTS.GENERIC_WAIT)

        logging.error("couldn't select %s in %s ..." % (setting, settings_list))
        return False

    def select_settings_sub_sub_menu(self, setting, value, check_selected_asset=True):
        # start by focusing on the setting
        if not self.focus_settings_sub_sub_menu(setting):
            return False

        value = value.lower()
        values_list = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "sub_items")
        values_list = map(lambda x : x.lower(), values_list)
        if value not in values_list:
            logging.error("couldn't find %s in %s" % (value, values_list))
            return False

        selected_asset = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "selected_asset")
        if selected_asset is not False and selected_asset.lower() == value:
            return True

        for _ in values_list:
            focused_asset = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_asset")
            if focused_asset.lower() == value:
                self.test.appium.key_event("KEYCODE_DPAD_CENTER")
                self.test.wait(CONSTANTS.GENERIC_WAIT)
                # double check it was selected
                if check_selected_asset is True:
                    selected_asset = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "selected_asset")
                    if selected_asset.lower() != value:
                        logging.error("%s was not selected ! (still %s)" % (value, selected_asset))
                        return False
                return True
            self.test.appium.key_event("KEYCODE_DPAD_RIGHT")
            self.test.wait(CONSTANTS.GENERIC_WAIT)

        logging.error("couldn't select %s in %s ..." % (value, values_list))
        return False




    def focus_tvfilter_item_in_hub(self, expected_pos=5, check_pos=False):
        '''
        Focus the Settings item in Hub. Position can be checked, with respect to current position
        :param expected_pos: Position of the item (vertical one)
        :param check_pos: set to True if position is to be checked
        :return: True/False
        '''
        logging.info("--> focus_tvfilter_item_in_hub")
        if self.test.is_dummy:
            tvfilter_title = "LIVE TV"
        else:
            tvfilter_title = self.test.he_utils.get_hub_default_menu_title()
        logging.info("Moving focus to: %s" % tvfilter_title)

        if len(tvfilter_title) == 0:
            logging.error("Can not find TvFilter menu name")
            return False

        status = self.focus_item_in_hub(item_title=tvfilter_title, expected_pos=expected_pos, check_pos=check_pos)
        if not status:
            logging.error("Fail to move focus on: %s" % tvfilter_title)
            return False

        return True

    def to_tvfilter_from_hub(self, expected_pos=10, check_pos=False):
        '''
        To tvfilter screen from hub screen. Position of tvfilter menu_item can be checked, with respect to current position
        :param expected_pos:         
        :param check_pos: set to True if position of tvfilter menu_item is to be checked        
        :return: True when in tvfilter screen and position of menu_item is in the expected position. Otherwise returns False
        '''
        status = self.focus_tvfilter_item_in_hub(expected_pos=expected_pos, check_pos=check_pos)
        if not status:
            logging.error("Fail to focus TvFilter item in Hub")
            return False

        logging.info("Moving focus to %s" % CONSTANTS.HUB_TV)
        
        if self.test.is_dummy:
            tvfilter_title = CONSTANTS.HUB_TV
        else:
            tvfilter_title = self.test.he_utils.get_hub_default_menu_title()
        
        status = self.move_to_menu_from_basepos(menu_title = tvfilter_title, expected_pos = expected_pos, check_pos = check_pos)
        if not status :
            logging.error("moving to %s failed"%tvfilter_title)
            return False

        logging.info("Going into %s" % CONSTANTS.HUB_TV)

        self.test.appium.key_event("KEYCODE_DPAD_LEFT")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(CONSTANTS.GENERIC_WAIT)

        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status:
            logging.error("wait for tv_filter timed out")
            return False

        logging.info("in %s" % CONSTANTS.HUB_TV)
        return True

    def to_programme_from_hub(self, expected_pos = 10, check_pos = False):
        '''
        To programme screen from hub screen. Position of programme menu_item can be checked, with respect to current position
        :param expected_pos:         
        :param check_pos: set to True if position of programme menu_item is to be checked        
        :return: True when in programme screen and position of menu_item is in the expected position. Otherwise returns False
        '''

        #new hub v2 : cant access directly to the grid from hub
        return self.to_guide_from_hub()
        
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub" )
        if not status :
            logging.error("wait for main_hub timed out")
            return False
        logging.info("In main_hub")

        status = self.focus_default_menuitem_in_hub()
        if not status :
            logging.error("cant focus SHOWCASE in hub")
            return False

        if self.test.is_dummy:
            guide_title = "Programme"
        else:
            guide_title = self.test.he_utils.get_hub_menuitem_title_by_target("KGrid")

        if len(guide_title) == 0 :
            logging.error("cant find KGRID menu name")
            return False

        status = self.move_to_menu_from_basepos(menu_title = guide_title, expected_pos = expected_pos, check_pos = check_pos)
        if not status :
            logging.error("cant focus %s in hub" % guide_title)
            return False

        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "guide")
        if not status:
            logging.error("wait for guide timed out")
            return False

        logging.info("In guide")
        return True
        
    def to_hub_from_programme(self):
        '''
        To main_hub from programme screen 
        :return: True when in main_hub
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "guide")
        if not status:
            logging.error("wait for guide timed out")
            return False
        logging.info("in guide")
        self.test.appium.key_event("KEYCODE_BACK")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if not status:
            logging.error("wait for main_hub timed out")
            return False
        logging.info("In main_hub")
        return status
        
    def verify_main_hub_item_focused(self, sub_item):
        '''
        Verify the sub-item focused in Main Hub.
        :return: True when in focus is on the sub_item
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if not status:
            logging.error("wait for main_hub timed out")
            return False
        logging.info("In main_hub")

        elements = self.test.milestones.getElements()
        focused_item = self.test.milestones.get_value_by_key(elements, "focused_item")
        if focused_item is False:
            logging.info("Failure to retrieve a focus item.\n{0}".format(elements))
            return False

        if str(focused_item).upper() != str(sub_item).upper():
            logging.error("The focused item({0}) is not the expected one ({1})"
                          .format(focused_item.upper(), sub_item.upper()))
            return False

        return True

    def get_day_in_main_hub(self):
        '''
        Return the day focused in main_hub
        :return: day as a string
        '''
        return self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_day")

    def get_month_in_main_hub(self):
        '''
        Return the month focused in main_hub
        :return: month as a string
        '''

        return self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_month")

    def focus_library_item_in_hub(self, expected_pos=4, check_pos=False):
        '''
        Focus the Library item in Hub. Position of library menu_item can be checked, with respect to current position
        :param expected_pos: Position of the item (vertical one)
        :param check_pos: set to True if position is to be checked
        :return: True/False
        '''
        logging.info("--> focus_library_item_in_hub")

        if self.test.is_dummy:
            library_title = "LIBRARY"
        else:
            library_title = self.test.he_utils.get_hub_menuitem_title_by_item_id("LIBRARY")
        logging.info("Moving focus to: %s" % library_title)

        if len(library_title) == 0:
            logging.error("Can not find LIBRARY menu name")
            return False

        status = self.focus_item_in_hub(library_title, expected_pos, check_pos)
        if not status:
                logging.error("Fail to move focus on: %s" % library_title)
                return False

        return True

    def to_library_from_hub(self, expected_pos = 10, check_pos = False):
        '''
        To library screen from hub screen. Position of library menu_item can be checked, with respect to current position
        :param expected_pos:
        :param check_pos: set to True if position of search menu_item is to be checked
        :return: True when in search screen and position of menu_item is in the expected position. Otherwise returns False
        '''
        status = self.focus_library_item_in_hub(expected_pos=expected_pos, check_pos=check_pos)
        if not status:
            logging.error("Fail to focus Library item in Hub")
            return False

        self.test.appium.key_event("KEYCODE_DPAD_LEFT")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        self.test.appium.key_event("KEYCODE_DPAD_CENTER")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status:
            logging.error("wait for filter timed out")
            return False

        logging.info("In library")
        return True

    def to_hub_from_library(self):
        '''
        To main_hub from library screen
        :return: True when in main_hub
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status :
            logging.error("wait for library timed out")
            return False
        logging.info("In library")
        self.test.appium.key_event("KEYCODE_BACK")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if not status :
            logging.error("wait for main_hub timed out")
            return False
        logging.info("In main_hub")
        return status

    def move_to_menu_from_basepos(self, menu_title, direction="vertical", expected_pos=10, check_pos=False, focused_milestone="focused_item"):
        '''
        move to a [menu_title] from current position. Position of [menu_title] can be checked, with respect to current position
        :param menu_title:
        :param direction: "vertical" or "horizontal" menu
        :param expected_pos:
        :param check_pos: st to True if position of [menu_title] is to be checked
        :param focused_milestone: label of the milestone to get the menu_tilite being focused
        :return: True when focus is on [menu_title], and that it is at position [expected_pos] with respect to current position
        '''
        status = True
        logging.info("--> move_to_menu_from_basepos menu_title="+str(menu_title))

        if direction == "vertical":
            key_event = "KEYCODE_DPAD_UP"
        else:
            key_event = "KEYCODE_DPAD_RIGHT"

        milestone = self.test.milestones.getElements()
        current_focused = self.test.milestones.get_value_by_key(milestone, focused_milestone)

        if not current_focused:
            return False

        if current_focused.upper() == menu_title.upper():
            i = 0
        else:
            if not check_pos:
                expected_pos = CONSTANTS.MAX_ACTIONS
            for i in range(0, expected_pos):
                self.test.appium.key_event(key_event)
                self.test.wait(CONSTANTS.SMALL_WAIT)
                milestone = self.test.milestones.getElements()
                current_focused = self.test.milestones.get_value_by_key(milestone, focused_milestone)
                print "current focused = -"+ str(current_focused) +"- menu_title="+str(menu_title.upper())
                if not current_focused:
                    return False
                #logging.info("milestone -------------> %s "%milestone)
                if current_focused and current_focused.upper() == menu_title.upper():
                    i = i + 1
                    break

        if check_pos:
            if i != expected_pos:
                logging.error("%s is not on the expected position %d but %d instead of" % (menu_title, i, expected_pos))
                status = False

        if current_focused == False or current_focused.upper() != menu_title.upper():
            logging.error("%s is not the focused item" % str(menu_title))
            status = False

        return status

    def dismiss(self):
        self.test.appium.key_event("KEYCODE_BACK")
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
        if not status:
            logging.error("navigate to fullscreen failed")
        else :
            logging.info(" main_hub dismiss correctly")
        return