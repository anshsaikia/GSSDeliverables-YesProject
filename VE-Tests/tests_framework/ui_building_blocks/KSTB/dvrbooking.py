from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ve_tests.ve_test import VeTestApi
import logging

FULL_SCREEN_NAME = "fullscreen"

class DVRBooking():

    def __init__(self, ve_test = None, title = "Tests_ui_i_dont_have_a_name"):
        if ve_test is None :
            self.ve_test = VeTestApi(title)
        else :
            self.ve_test = ve_test

        self.record_action = "RECORD"
        self.acknowledgment_message = "THIS SHOW WILL BE RECORDED"
        self.time_to_wait_for_acknowledgment_message = 5

    def start_record(self,test_flag=True):
        '''
        Start recording event when action menu was already raised
        '''

        try:
            self.ve_test.screens.action_menu.navigate_to_action(self.record_action)
            self.choose_record()
            if test_flag:
                self.ve_test.wait(2)
                for i in range (0,self.time_to_wait_for_acknowledgment_message*10):
                    self.ve_test.wait(1)
                    elements = self.ve_test.milestones.getElements()
                    for elm in elements:
                        if 'message' in elm:
                            actual_message = elm['message']
                            if actual_message==self.acknowledgment_message:
                                logging.info("We got the correct acknowledgment message {}".format(actual_message))
                                return True
                            else:
                                raise AssertionError, "We expected to get the message {}, but we got the message {}".format(self.acknowledgment_message, actual_message)

                raise AssertionError, "We did not recieve aknowledgemnt message after {} seconds".format(self.time_to_wait_for_acknowledgment_message)
            return True
        except Exception as ex:
            logging.exception("\n\n ---------------------------------------------------\n         ACTION ABORTED DUE TO : \n")
            return {"exception" : ex}

    def choose_record(self):
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")

    def verify_recordings_in_hub(self):
        '''
        verify that hub library is not empty
        '''
        try:
            assert self.ve_test.wait_for_screen(10,'main_hub'),"We excpected to be on main_hub screen but we are in {}".format(self.ve_test.milestones.get_current_screen())
            for step in range(0, 10):
                elements = self.ve_test.milestones.getElements()
                focused_item = self.ve_test.milestones.get_value_by_key(elements, "focused_item")
                if focused_item == 'LIBRARY':
                    break
                self.ve_test.appium.key_event("KEYCODE_DPAD_UP")
            assert focused_item=='LIBRARY'
            if self.ve_test.is_dummy:
                assert 'I0705S51E087:LONG:eng' == elements[2]['focused_asset']
                assert 'REC on Tue 5. Jul' == elements[2]['focused_asset_info']
                assert 'file:///android_asset/dummy_images/dummy_logo_1.png' == elements[2]['focused_asset_logo']
                assert '0.0' == elements[2]['focused_asset_pb_start']
                assert 'file:///android_asset/dummy_images/dummy_thumbnail_1.jpg' == elements[2]['focused_asset_container']
                logging.info("We got asset {} in library ".format(elements[2]['focused_asset']))
            else:
                assert elements[2]['focused_asset'],"Missing asset name"
                assert elements[2]['focused_asset_info'],"Missing info"
                assert elements[2]['focused_asset_logo'],"Missing logo"
                assert elements[2]['focused_asset_pb_start'],"Missing progressbar"
                assert elements[2]['focused_asset_container'],"Missing thumbnail"
                logging.info("We got asset {} in library ".format(elements[2]['focused_asset']))
            return True
        except Exception as ex:
            logging.exception("\n\n ---------------------------------------------------\n         ACTION ABORTED DUE TO : \n")
            return {"exception" : ex}

    def start_playback_of_focused_asset_in_hub_library_action_menu(self):
        '''
        Start playback of recording event
        '''
        try:
            assert self.ve_test.wait_for_screen(10,'main_hub'),"We excpected to be on main_hub screen but we are in {}".format(self.ve_test.milestones.get_current_screen())
            elements = self.ve_test.milestones.getElements()
            focused_item = self.ve_test.milestones.get_value_by_key(elements, "focused_item")
            assert focused_item == 'LIBRARY'
            focused_asset = elements[2]['focused_asset']
            self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
            assert self.ve_test.wait_for_screen(10,'action_menu'),"We excpected to be on action_menu screen but we are in {}".format(self.ve_test.milestones.get_current_screen())
            self.ve_test.screens.action_menu.navigate_to_action('PLAY')
            self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
            assert self.ve_test.wait_for_screen(10,'trickmode'),"We excpected to be on trickmode screen but we are in {}".format(self.ve_test.milestones.get_current_screen())
            assert self.ve_test.wait_for_screen(10,'fullscreen'),"We excpected to be on fullscreen screen but we are in {}".format(self.ve_test.milestones.get_current_screen())
            elements = self.ve_test.milestones.getElements()
            cur_event_title = self.ve_test.milestones.get_value_by_key(elements, "cur_event_title")
            assert focused_asset == cur_event_title,"Playing asset name ({}) is wrong, expecting {}".format(cur_event_title,focused_asset)
            logging.info("Playback of asset {} has started".format(cur_event_title))
            return True
        except Exception as ex:
            logging.exception("\n\n ---------------------------------------------------\n         ACTION ABORTED DUE TO : \n")
            return {"exception" : ex} 

    def stop_playback_of_playing_asset(self,return_screen='main_hub'):
        '''
        Stop playback of recording event
        '''
        try:
            assert self.ve_test.wait_for_screen(10,'fullscreen'),"We excpected to be on fullscreen screen but we are in {}".format(self.ve_test.milestones.get_current_screen())
            self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
            assert self.ve_test.wait_for_screen(10,'action_menu'),"We excpected to be on action_menu screen but we are in {}".format(self.ve_test.milestones.get_current_screen())
            self.ve_test.screens.action_menu.navigate_to_action('STOP')
            self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
            assert self.ve_test.wait_for_screen(10,return_screen),"We excpected to return to {} but we are in {}".format(return_screen,self.ve_test.milestones.get_current_screen())
            logging.info("Playback of has been stoped")
            return True
        except Exception as ex:
            logging.exception("\n\n ---------------------------------------------------\n         ACTION ABORTED DUE TO : \n")
            return {"exception" : ex} 
                

class DVRSeriesBooking(DVRBooking):

    def __init__(self, ve_test = None, title = "Tests_ui_i_dont_have_a_name"):
        #super(DVRSeriesBooking, self).__init__(ve_test, title)
        DVRBooking.__init__(self, ve_test, title)
        self.acknowledgment_message = "THIS SEASON WILL BE RECORDED"

 
    def choose_record(self):
        self.ve_test.appium.key_event("KEYCODE_DPAD_RIGHT")
        self.ve_test.appium.key_event("KEYCODE_DPAD_CENTER")
