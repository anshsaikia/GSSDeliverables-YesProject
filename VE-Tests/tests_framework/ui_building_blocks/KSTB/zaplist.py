__author__ = 'callix'

from tests_framework.ui_building_blocks.screen import Screen
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
from time import sleep,time

''' Constants '''
START_STREAMING_TIMEOUT = 10

class ZapList(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "zap_list_tv")

    def navigate(self, direction = "up"):
        logging.info("Navigate to zap list")
        screen = self.test.milestones.get_current_screen()
        if screen == self.screen_name:
            return True

        if screen != "fullscreen":
            self.test.say('need to navigate to fullscreen')
            self.test.screens.fullscreen.navigate()

        logging.info("Navigating to zaplist, current step : fullscreen")
        if direction == "down":
            logging.info("pressing down key")
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
            self.test.wait(2)
            self.test.appium.key_event("KEYCODE_DPAD_UP")
        else:
            logging.info("pressing up key")
            self.test.appium.key_event("KEYCODE_DPAD_UP")
            self.test.wait(2)
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")

        self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "zap_list_tv")
        self.verify_active()
        return True

    def verify_zaplist_showing(self, elements=None):
        if elements is None:
            elements = self.test.milestones.getElements()

        screen = self.test.milestones.get_value_by_key(elements, "screen")
        if screen == "zap_list_tv":
            return True
        else:
            logging.error("ZapList is not displayed on the screen but {0}".format(screen))
        return False

    def zaplist_timeout_to_fullscreen(self):
        '''
        Go to fullscreen from zaplist by waiting for SCREEN_TIMEOUT duration
        :return: True when on fullscreen after SCREEN_TIMEOUT seconds
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "zap_list_tv")
        if not status:
            logging.error("Not in zaplist")
            return False
        logging.info("In zaplist")
        status = self.test.wait_for_screen(CONSTANTS.SCREEN_TIMEOUT + 1, "zap_list_tv", "!=" )
        if not status:
            logging.error("wait for zaplist to timeout failed")
            return False
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "fullscreen")
        if not status:
            logging.error("wait for fullscreen timed out")
            return False
        logging.info("In fullscreen")
        return status



    def to_nextchannel(self, direction="up"):
        '''
        Go to next channel in zaplist
        :param direction: button to press. "up" or "down"
        :return: True when on new channel. Still on zaplist screen
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "zap_list_tv")
        if not status:
            logging.error("wait for zaplist timed out")
            return False
        logging.info("In zaplist")

        actualFocusedChannelNumber = self.test.milestones.get_value_by_key(self.test.milestones.getElements(),"focused_channel_number")
        start_time = time()
        current_time = start_time
        if direction == "down":
            # logging.info("Pressing down key")
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
        else:
            # logging.info("Pressing up key")
            self.test.appium.key_event("KEYCODE_DPAD_UP")

        nextFocusedChannelNumber = actualFocusedChannelNumber
        time_out = (current_time - start_time) >= CONSTANTS.WAIT_TIMEOUT
        focused_ok = nextFocusedChannelNumber == actualFocusedChannelNumber
        while (not focused_ok) and (not time_out):
            current_time = time()
            time_out = (current_time - start_time) >= CONSTANTS.WAIT_TIMEOUT
            nextFocusedChannelNumber = self.test.milestones.get_value_by_key(self.test.milestones.getElements(),"focused_channel_number")
            focused_ok = nextFocusedChannelNumber == actualFocusedChannelNumber
            sleep(0.2)

        if time_out:
            logging.error("focused item change timed out in zaplist")
            return False
        # logging.info("focused item has changed in zaplist")
        return focused_ok    

    def tune_to_channel_by_sek(self, channel_id, handle_pincode_screen=True, verify_streaming_started=True):
        '''
        Navigate till the wanted channel number then zap on it by validating it
        :param channel_id:
        :param handle_pincode_screen:
        :param verify_streaming_started:
        :return:
        '''
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "zap_list_tv")
        if not status:
            logging.error("wait for zap_list_tv timed out")
            logging.error("not in zap_list_tv")
            return False
        logging.info("In zap_list_tv")
        pin_code = self.test.screens.pincode
        elements = self.test.milestones.getElements()
        
        firstFocusedChannelNumber = self.test.milestones.get_value_by_key(elements, "focused_channel_number")
        
        channel_found = False
        cycle_not_completed = True
        actualFocusedChannelNumber = firstFocusedChannelNumber

        while cycle_not_completed:
            if str(actualFocusedChannelNumber) == str(int(channel_id)):
                channel_found = True
                # print ("Tuning to channel %s" % channel_id)
                self.test.appium.key_event("KEYCODE_DPAD_CENTER")
                sleep(1)

                if self.test.screens.pincode.is_active(1, ignoreNotification=True):
                    if handle_pincode_screen:
                        youth_pincode = self.test.he_utils.getYouthpincode()
                        pin_code.enter_pin(youth_pincode)
                    else:
                        break
                if verify_streaming_started:
                    for i in range(START_STREAMING_TIMEOUT):
                        playback_status = self.test.milestones.getPlaybackStatus()
                        state = playback_status["playbackState"]
                        if state == "PLAYING":
                            return True
                        sleep(1)
                    elements = self.test.milestones.getElements()
                    error_msg = self.test.milestones.get_value_by_key(elements, "msg_text")
                    logging.error("Playback streaming failed playing : error_msg = " + str(error_msg))
                    return False
                break

            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
            sleep(1)
            elements = self.test.milestones.getElements()
            actualFocusedChannelNumber = self.test.milestones.get_value_by_key(elements, "focused_channel_number")

            cycle_not_completed = int(actualFocusedChannelNumber) != int(firstFocusedChannelNumber)

        if not channel_found:
            logging.info("Could not find channel_id %s in zaplist" % channel_id)
            return False
        else:
            return True
        # self.test.log_assert(channel_found, "Could not find channel_id %s in zaplist" % channel_id)


