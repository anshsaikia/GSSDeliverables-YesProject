__author__ = 'callix'

from tests_framework.ui_building_blocks.screen import Screen
import logging, re
from time import time, sleep
from datetime import datetime
import datetime
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from datetime import datetime, timedelta
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from pytz import timezone
import pytz

UI_TIMEZONE = 'Europe/Berlin'

class Fullscreen(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "fullscreen")

    def navigate(self, direction='ok', verify_active = True):
        '''
        Go to fullscreen, from any screen
        :return: True when on fullscreen 
        '''
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
            
        if screen == self.screen_name:
            return True

        if screen == "zap_list_tv" or screen == "timeline":
            if direction == 'ok':
                self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            elif direction == 'back':
                self.test.appium.key_event("KEYCODE_BACK")
            else:
                self.test.appium.key_event("KEYCODE_BACK")
            self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
            self.verify_active()
            return True

        if screen == "infolayer":
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
            if not status:
                logging.error("navigate to fullscreen failed")
                return False
            else:
                self.verify_active()
                return True

        if screen == "action_menu":
            self.test.appium.key_event("KEYCODE_BACK")
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
            if not status:
                logging.error("navigate to fullscreen failed")
                return False
            else:
                self.verify_active()
                return True

        if screen != "main_hub":
            status = self.test.screens.main_hub.navigate()
            if not status :
                logging.error("navigate to main_hub failed")
                return False

        self.test.appium.key_event("KEYCODE_BACK")
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
        self.verify_active()
        return status


    def to_nextchannel_in_fullscreen(self, wait_few_seconds):
        '''
        Go to next channel in fullscreen (by pressing "down")
        :param wait_few_seconds: time to wait for the zapping to be performed
        :return: True when on new channel.
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen" )
        if not status:
            logging.error("wait for fullscreen timed out")
            return False
        actualChannelNumber = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "current_channel")
        logging.info("actual channel: %s" %actualChannelNumber)

        self.test.appium.key_event("KEYCODE_DPAD_DOWN")
        self.test.wait(wait_few_seconds)
        nextChannelNumber = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "current_channel")
        logging.info("next channel: %s" %nextChannelNumber)

        return (actualChannelNumber != nextChannelNumber)
        
        
    def to_previouschannel_in_fullscreen(self, wait_few_seconds):
        '''
        Go to next channel in fullscreen (by pressing "up")
        :param wait_few_seconds: time to wait for the zapping to be performed
        :return: True when on new channel.
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen" )
        if not status:
            logging.error("wait for fullscreen timed out")
            return False
        actualChannelNumber = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "current_channel")
        logging.info("actual channel: %s" %actualChannelNumber)

        self.test.appium.key_event("KEYCODE_DPAD_UP")
        self.test.wait(wait_few_seconds)
        nextChannelNumber = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "current_channel")
        logging.info("next channel: %s" %nextChannelNumber)
        if nextChannelNumber is False:
            return False
        return actualChannelNumber != nextChannelNumber
            
    def is_infolayer_shown(self):
        """
        Check if info_layer is shown
        :return: True when info_layer is shown
        """
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "infolayer")
        return status

    def wait_for_infolayer_dismiss(self, wait_in_seconds):
        """
        Check if info_layer is shown
        :return: True when info_layer is shown
        """
        status = self.test.wait_for_screen(wait_in_seconds, "infolayer", compare="!=")
        return status
        
    def get_current_channel(self):
        '''
        Get the current channel number in fullscreen
        :return: channel number.
        '''  
        milestone = self.test.milestones.getElements()
        return int(self.test.milestones.get_value_by_key(milestone, "current_channel"))

    def get_current_event_broadcasting_time(self):
        """
        When you are in full screen in live, retrieve from UI the broadcasting time
        :return: the broadcasting time - start and end
        """
        retries = 0
        start_time = False
        while start_time is False and retries < 10:
            milestones = self.test.milestones.getElements()
            start_time = self.test.milestones.get_value_by_key(milestones, "current_event_start")
            end_time = self.test.milestones.get_value_by_key(milestones, "current_event_end")
            retries += 1
            self.test.wait(1)

        if not start_time:
            logging.info("no valid start time. Milestone: {0}".format(milestones))
            return False
        if not end_time:
            logging.info("no valid end time. Milestone: {0}".format(milestones))
            return False
        start_time /= 1000
        end_time /= 1000
        # logging.info("start_time: %s  end_time: %s" % (start_time, end_time))

        event_start_time = datetime.utcfromtimestamp(start_time)
        event_end_time = datetime.utcfromtimestamp(end_time)
        # logging.info("start: %s       end: %s " % (event_start_time, event_end_time))
        return {"event_start_time": event_start_time, "event_end_time": event_end_time}

    def get_current_event_title(self):
        retries = 0
        live_event_title = False
        while live_event_title is False and retries < 10:
            milestones = self.test.milestones.getElements()
            live_event_title = self.test.milestones.get_value_by_key(milestones, "current_event_title")
            retries += 1
            self.test.wait(1)
        return live_event_title

    def zapping_by_dca_in_fullscreen(self, channel_number):
        """
        Perform a dca in fullscreen and check that the current screen is still fullcreen
        :param channel_number: logical channel number to zap to
        :return: true/false
        """
        logging.info("Zap to channel number %s" % channel_number)
        self.test.screens.playback.dca(channel_number)
        self.test.wait(CONSTANTS.INFOLAYER_TIMEOUT + 1)
        if not self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT+2, 'fullscreen'):
            logging.info("STB is not on fullscreen but %s" + self.test.milestones.get_current_screen())
            return False
        elements = self.test.milestones.getElements()
        # logging.info("elements: \n %s" % elements)
        current_channel = self.test.milestones.get_value_by_key(elements, 'current_channel')
        retries = 0
        while current_channel != channel_number and retries < 10:
            self.wait(1)
            elements = self.test.milestones.getElements()
            logging.info("elements: \n %s" % elements)
            current_channel = self.test.milestones.get_value_by_key(elements, 'current_channel')
            retries += 1

        if current_channel != channel_number:
            logging.info("Current channel is " + str(current_channel) + " instead of " + str(channel_number))
            return False

        return True

    def current_event_remaining_time(self):
        """
        return the broadcasting time from the event in current full screen
        """
        he_current_time = datetime.now(timezone(UI_TIMEZONE))
        logging.info("he_current_time: %s" % he_current_time)

        broadcast_time = self.get_current_event_broadcasting_time()
        if not broadcast_time:
            return False

        event_end = broadcast_time['event_end_time'].replace(tzinfo=pytz.UTC)
        event_broadcast_end = event_end.astimezone(timezone(UI_TIMEZONE))
        logging.info("event_broadcast_end: %s" % event_broadcast_end)

        if int(event_broadcast_end.hour) < int(he_current_time.hour):  # the event will be ended tomorrow
            logging.info("the event will be ended tomorrow")
            event_broadcast_end = event_broadcast_end + timedelta(days=1)

        current_event_remaining_time = event_broadcast_end - he_current_time
        logging.info("Remaining time {}".format(current_event_remaining_time))
        return current_event_remaining_time

    def wait_for_event_with_minimum_time_until_end(self, min_time_in_seconds=80):
        """
        param min_time_in_seconds: minimum weconds we want until the end of event
        Waiting for event which had enough time until the end
        """
        logging.info("@@@@ checking if current event has {} seconds until the end".format(min_time_in_seconds))
        current_event_remaining_time = self.current_event_remaining_time()
        if not current_event_remaining_time:
            return False, "Current event is not correct {}".format(self.get_current_event_title())
        while current_event_remaining_time.total_seconds() < min_time_in_seconds:
            logging.info("@@@@ checking if current event has {} seconds until the end".format(min_time_in_seconds))
            logging.info("Need to wait {} seconds until next event".format(current_event_remaining_time.seconds + 30))
            self.test.wait(current_event_remaining_time.seconds + 30)
            logging.info("launching the action Menu to refresh the data in UI")
            status = self.test.screens.action_menu.navigate()
            if status:
                status = self.test.screens.fullscreen.navigate()

            if not status:
                return False,"Fails to update the event"

            current_event_remaining_time = self.current_event_remaining_time()
            if not current_event_remaining_time:
                return False,"Next event {} is not correct".format(self.get_current_event_title())
        return True, False
