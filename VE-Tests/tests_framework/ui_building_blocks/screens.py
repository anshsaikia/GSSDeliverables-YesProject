
__author__ = 'bwarshaw'

from tests_framework.ui_building_blocks.screen import Screen

from tests_framework.ui_building_blocks.KD.action_menu import LinearActionMenu
from tests_framework.ui_building_blocks.KD.action_menu import VodActionMenu
from tests_framework.ui_building_blocks.KD.action_menu import PvrActionMenu
from tests_framework.ui_building_blocks.KD.action_menu import ActionMenu
from tests_framework.ui_building_blocks.KD.login_screen import LoginScreen
from tests_framework.ui_building_blocks.KD.pincode import PinCodescreen
from tests_framework.ui_building_blocks.KD.fullscreen import Fullscreen
from tests_framework.ui_building_blocks.KD.infolayer import InfoLayer
from tests_framework.ui_building_blocks.KD.timeline import TimeLine
from tests_framework.ui_building_blocks.KD.settings import Settings
from tests_framework.ui_building_blocks.KD.playback import Playback
from tests_framework.ui_building_blocks.KD.main_hub import MainHub
from tests_framework.ui_building_blocks.KD.zaplist import ZapList
from tests_framework.ui_building_blocks.KD.library import Library
from tests_framework.ui_building_blocks.KD.search import Search
from tests_framework.ui_building_blocks.KD.full_content_screen import FullContentScreen
from tests_framework.ui_building_blocks.K.full_content_screen import KfullContentScreen
from tests_framework.ui_building_blocks.KD.notification import Notification
from tests_framework.ui_building_blocks.KD.boot import Boot
from tests_framework.ui_building_blocks.KD.guide import Guide
from tests_framework.ui_building_blocks.KD.booking_recording import BookingRecording
from tests_framework.ui_building_blocks.KD.KDStore import KDStore
from tests_framework.ui_building_blocks.KD.tips import KDTips

from tests_framework.ui_building_blocks.K.tv_filter import TvFilter
from tests_framework.ui_building_blocks.K.KStore import KStore
from tests_framework.ui_building_blocks.K.library_filter import LibraryFilter
from tests_framework.ui_building_blocks.K.trick_bar import TrickBar
from tests_framework.ui_building_blocks.K.ksettings import kSettings
from tests_framework.ui_building_blocks.K.header import Header
from tests_framework.ui_building_blocks.K.dvb_subtitle import DvbSubtitles
from tests_framework.ui_building_blocks.K.closed_caption import ClosedCaption
from tests_framework.ui_building_blocks.K.KGuide import KGuide
from tests_framework.ui_building_blocks.K.KGuide import KSmartphoneGuide
from tests_framework.ui_building_blocks.K.KGuide import KSmartphoneDatesSelection
from tests_framework.ui_building_blocks.K.KGuide import KSmartphoneChannelsSelection
from tests_framework.ui_building_blocks.K.timeline_catchup import TimeLineCatchup

from tests_framework.ui_building_blocks.KSTB.action_menu import ActionMenu as KSTB_ActionMenu
from tests_framework.ui_building_blocks.KSTB.login_screen import LoginScreen as KSTB_LoginScreen
from tests_framework.ui_building_blocks.KSTB.pincode import PinCodeActionMenu as KSTB_PinCodeActionMenu
from tests_framework.ui_building_blocks.KSTB.fullscreen import Fullscreen as KSTB_Fullscreen
from tests_framework.ui_building_blocks.KSTB.infolayer import InfoLayer as KSTB_InfoLayer
from tests_framework.ui_building_blocks.KSTB.timeline import TimeLine as KSTB_TimeLine
from tests_framework.ui_building_blocks.KSTB.playback import Playback as KSTB_Playback
from tests_framework.ui_building_blocks.KSTB.main_hub import MainHub as KSTB_MainHub
from tests_framework.ui_building_blocks.KSTB.zaplist import ZapList as KSTB_ZapList
from tests_framework.ui_building_blocks.KSTB.search import Search as KSTB_Search
from tests_framework.ui_building_blocks.KSTB.fullcontent import Fullcontent as KSTB_FullContent
from tests_framework.ui_building_blocks.KSTB.notification import Notification as KSTB_Notification
from tests_framework.ui_building_blocks.KSTB.boot import Boot as KSTB_Boot
from tests_framework.ui_building_blocks.KSTB.boot import Boot as KSTB_Boot
from tests_framework.ui_building_blocks.KSTB.guide import Guide as KSTB_Guide
from tests_framework.ui_building_blocks.KSTB.filter import Filter as KSTB_Filter
from tests_framework.ui_building_blocks.KSTB.library import Library as KSTB_Library

class Screens(object):
    def __init__(self, test):
        self.screen_list = {}
        self.test = test
        self.test.screens = self

        #Multi-Project
        if self.test.project_type == 'K' or self.test.project_type == 'KD' :
            self.linear_action_menu = LinearActionMenu(test)
            self.vod_action_menu = VodActionMenu(test)
            self.pvr_action_menu = PvrActionMenu(test)
            self.login_screen = LoginScreen(test)
            self.pincode = PinCodescreen(test)
            self.fullscreen = Fullscreen(test)
            self.infolayer = InfoLayer(test)
            self.timeline = TimeLine(test)
            self.settings = Settings(test)
            self.playback = Playback(test)
            self.main_hub = MainHub(test)
            self.zaplist = ZapList(test)
            self.library = Library(test)
            self.search = Search(test)
            self.notification = Notification(test)
            self.boot = Boot(test)
            self.booking_recording = BookingRecording(test)
            self.store = KDStore(test)
            self.tips = KDTips(test)

            #K Specific
            self.trick_bar = TrickBar(test)
            self.tv_filter = TvFilter(test)
            self.store_filter = KStore(test)
            self.library_filter = LibraryFilter(test)
            self.action_menu = ActionMenu(test)
            self.ksettings = kSettings(test)
            self.header = Header(test)
            self.dvb_subtitle = DvbSubtitles(test)
            self.closed_caption = ClosedCaption(test)
            self.KSmartphoneGuide = KSmartphoneGuide(test)
            self.KSmartphoneDatesSelection = KSmartphoneDatesSelection(test)
            self.KSmartphoneChannelsSelection = KSmartphoneChannelsSelection(test)
            self.timeline_catchup = TimeLineCatchup(test)

            #Project specific
            if test.project != "KD":
                self.full_content_screen = KfullContentScreen(test)
                self.guide = KGuide(test)
            else:
                self.full_content_screen = FullContentScreen(test)
                self.guide = Guide(test)

        elif self.test.project_type == 'KSTB':
            #KSTB Specific
            self.notification = KSTB_Notification(test)
            self.action_menu = KSTB_ActionMenu(test)
            self.login_screen = KSTB_LoginScreen(test)
            self.pincode = KSTB_PinCodeActionMenu(test)
            self.fullscreen = KSTB_Fullscreen(test)
            self.infolayer = KSTB_InfoLayer(test)
            self.timeline = KSTB_TimeLine(test)
            self.playback = KSTB_Playback(test)
            self.main_hub = KSTB_MainHub(test)
            self.zaplist = KSTB_ZapList(test)
            self.filter = KSTB_Filter(test)
            self.fullcontent = KSTB_FullContent(test)
            self.guide = KSTB_Guide(test)
            self.boot = KSTB_Boot(test)
            self.search = KSTB_Search(test)
            self.library = KSTB_Library(test)

    def getCurrentScreen(self):
        screen_name = self.test.get_current_screen()
        return self.getScreenByName(screen_name)

    def getScreenByName(self, name):
        self.test.log_assert(name in self.screen_list, "Screen not supported " + name)
        screen = self.screen_list[name]
        return screen

    def navigateSingle(self, item):
        if isinstance(item, basestring):
            self.test.log("navigating to " + item)
            self.test.log_assert(item in self.screen_list, "Cannot navigate to missing screen " + item)
            screen = self.screen_list[item]
            if hasattr(screen, 'navigate'):
                screen.navigate()
            else:
                self.test.log("Screen " + screen.screen_name + " cannot be navigated to directly")
        elif isinstance(item, Screen):
            screen = item
            self.test.log("navigating to " + screen.screen_name)
            if hasattr(screen, 'navigate'):
                screen.navigate()
            else:
                self.test.log("Screen " + screen.screen_name + " cannot be navigated to directly")
        else:
            self.test.log("navigating to list: " + str(item))
            for subItem in item:
                self.navigateSingle(subItem)

    def navigate(self, *list):
        if list:
            for item in list:
                self.navigateSingle(item)
                self.test.wait(1)

    def wait_for_screen(self, screen_name, is_match=True, retries=10):
        i=0
        while i<retries:
            found = self.test.ui.verify_screen(screen_name)
            if ((found and is_match) or
                (not found and not is_match)):
                return
            i+=1
            self.test.wait(0.5)

        self.test.log_assert(False, "Fail to get to screen! screen_name:{0}, is_match:{1}".format(screen_name, str(is_match)))
