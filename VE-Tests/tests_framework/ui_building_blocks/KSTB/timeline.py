__author__ = 'callix'

from tests_framework.ui_building_blocks.screen import Screen
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from time import sleep, time

''' Constants '''
START_STREAMING_TIMEOUT = 10

class TimeLine(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "timeline")

    def navigate(self, direction="right"):
        logging.info("Navigate to timeline")
        screen = self.test.milestones.get_current_screen()
        if screen == self.screen_name:
            return True

        if screen != "fullscreen":
            self.test.say('need to navigate to fullscreen')
            self.test.screens.fullscreen.navigate()

        if direction == "right" :
            self.test.appium.key_event_adb("KEYCODE_DPAD_RIGHT")
        else :
            self.test.appium.key_event_adb("KEYCODE_DPAD_LEFT")

        self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "timeline")
        self.verify_active()
        return True

    def to_nextchannel(self, direction="up"):
        '''
        Go to next channel in timeline
        :param direction: button to press. "up" or "down"
        :return: True when on new channel. Still on timeline screen
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "timeline" )
        if not status :
            logging.error("wait for timeline timed out")
            return False
        logging.info("In timeline")

        actualFocusedChannelNumber = self.get_focused_channel_number()
        nextFocusedChannelNumber = actualFocusedChannelNumber
        start_time = time()
        current_time = start_time
        if direction == "down" :
            #logging.info("Pressing down key")
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
        else :
            #logging.info("Pressing up key")
            self.test.appium.key_event("KEYCODE_DPAD_UP")

        time_out = ((current_time - start_time) >= CONSTANTS.WAIT_TIMEOUT)
        focused_ok = (nextFocusedChannelNumber == actualFocusedChannelNumber)
        while (not focused_ok) and (not time_out) :
            current_time = time()
            time_out = (current_time - start_time) >= CONSTANTS.WAIT_TIMEOUT
            nextFocusedChannelNumber = self.get_focused_channel_number()
            focused_ok = (nextFocusedChannelNumber == actualFocusedChannelNumber)
            sleep(0.5)

        if time_out:
            logging.error("focused item change timed out in timeline")
            return False
        #logging.info("focused item has changed in timeline")
        return focused_ok

    def is_focused_on_current_event(self):
        '''
        Return True if focused event in timeline is current event,
        and False if not
        '''
        return self.test.milestones.get_value_by_key(self.test.milestones.getElements(),"focus_state_now")

    def to_nextevent(self, starting_from_current_event=False):
        '''
        Go to next event in timeline
        :param direction: button to press. "up" or "down"
        :return: True when focused on next event
        '''
        try:
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "timeline" )
            if not status :
                logging.error("wait for timeline timed out")
                return False
            logging.info("In timeline")
            source_event_name = self.test.milestones.get_value_by_key(self.test.milestones.getElements(),"focused_event_id")
            if starting_from_current_event:
                assert self.is_focused_on_current_event()==True, "We are not focused in current event"
            self.test.appium.key_event("KEYCODE_DPAD_RIGHT")
            destination_event_name = self.test.milestones.get_value_by_key(self.test.milestones.getElements(),"focused_event_id")
            if source_event_name==destination_event_name:
                logging.warn("Please be aware that still same event is focused. Maybe the transition was failed.")
            if starting_from_current_event:
                assert self.is_focused_on_current_event()==False, "We are still focused in current event"
            return True
        except Exception as ex:
            logging.exception("\n\n\n\n --------------------------------------------------- ACTION ABORTED DUE TO : ")
            return {"exception" : ex}

    def tune_to_channel_by_sek(self, channel_id, handle_pincode_screen=True, verify_streaming_started=True, direction="KEYCODE_DPAD_DOWN",verify_infolayer=False):
        '''
        Navigate till the wanted channel number then zap on it by validating it
        :param channel_id: channel number wanted
        :param handle_pincode_screen:
        :param verify_streaming_started:
        :param verify_infolayer:
        :return:
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "timeline" )
        if not status :
            logging.error("wait for timeline timed out")
            logging.error("not in timeline")
            return False
        logging.info("In timeline")
        pin_code = self.test.screens.pincode
        firstFocusedChannelNumber = self.get_focused_channel_number()

        channel_found = False
        cycle_not_completed = True
        actualFocusedChannelNumber = firstFocusedChannelNumber

        while cycle_not_completed:
            if str(actualFocusedChannelNumber) == str(int(channel_id)):
                channel_found = True
                elapse_time = 0
                infolayer = True
                logging.info("Tuning to channel %s" % channel_id)
                self.test.appium.key_event("KEYCODE_DPAD_CENTER")
                sleep(1)

                if self.test.screens.pincode.is_active(1, ignoreNotification=True):
                    if handle_pincode_screen:
                        youth_pincode = self.test.he_utils.getYouthpincode()
                        pin_code.enter_pin(youth_pincode)
                        verify_infolayer = False
                    else:
                        break

                if verify_infolayer :
                    start_time = time()
                    if self.test.wait_for_screen(CONSTANTS.INFOLAYER_TIMEOUT, "infolayer") == False :
                        logging.error(" No InfoLayer display ")
                        logging.info("##################### NO INFO LAYER !!!!!!!!!!!!!!!!!")
                        infolayer = False
                        if not verify_streaming_started :
                            return False
                    else:
                        elapse_time = int(time() - start_time)

                if verify_streaming_started:

                    stream_time_out = int(START_STREAMING_TIMEOUT - elapse_time)
                    if  elapse_time >= START_STREAMING_TIMEOUT :
                        stream_time_out = 1

                    for i in range(stream_time_out):
                        playback_status = self.test.milestones.getPlaybackStatus()
                        state = playback_status["playbackState"]
                        if (not verify_infolayer and state == "PLAYING") or ( infolayer and state == "PLAYING" ):
                            return True
                        sleep(1)
                    elements = self.test.milestones.getElements()
                    error_msg = self.test.milestones.get_value_by_key(elements, "msg_text")
                    logging.error("Playback streaming failed playing : error_msg = " + str(error_msg))
                    return False
                break

            self.test.appium.key_event(direction)
            sleep(1)
            actualFocusedChannelNumber = self.get_focused_channel_number()

            cycle_not_completed = int(actualFocusedChannelNumber) != int(firstFocusedChannelNumber)

        if not channel_found:
            logging.info("Could not find channel_id %s in timeline" % channel_id)
            return False
        else:
            return True
        #self.test.log_assert(channel_found, "Could not find channel_id %s in zaplist" % channel_id)

    def get_focused_channel_number(self, elements=None):
        if elements is None:
            elements = self.test.milestones.getElements()

        channel_info = self.test.milestones.get_value_by_key(elements, 'focused_channel_info')
        if not isinstance(channel_info, bool):
            if 'number' in channel_info:
                return channel_info['number']

        return False
