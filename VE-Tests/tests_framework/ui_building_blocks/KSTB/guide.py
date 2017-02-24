
from tests_framework.ui_building_blocks.screen import Screen
import logging
import tests_framework.ui_building_blocks.KSTB.constants as CONSTANTS
import time


class Guide(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "guide")


    def navigate(self, directly=False):
        logging.info("Navigate to guide")

        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)

        if screen == self.screen_name:
            return True

        if screen == "fullscreen":
            self.test.screens.main_hub.navigate()
            screen = "main_hub"

        if screen == "main_hub":
            status = self.test.screens.main_hub.focus_item_in_hub(item_title='GRID')
            logging.info("Going into GRID")
            self.test.appium.key_event("KEYCODE_DPAD_CENTER")
            status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "guide")
            if not status:
                logging.error("to_guide_from_hub failed")
                return False
            self.verify_active()
            return True

        self.verify_active()
        assert True, "Navigation not implemented in this screen : " + screen



    def to_tvfilter_from_guide(self):
        """
        To tvfilter from guide screen 
        :return: True when in tvfilter
        """
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "guide")
        if not status:
            logging.error("wait for guide timed out")
            return False
        logging.info("In guide")
        self.test.appium.key_event("KEYCODE_BACK")
        self.test.wait(CONSTANTS.GENERIC_WAIT)
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "filter")
        if not status:
            logging.error("wait for tv_filter timed out")
            return False
        logging.info("In tv_filter")
        return True

    def to_grid_days_filter_from_fullscreen(self):
        """
        To grid days filter from fullscreen.
        :return: True when in filter
        """

        status = self.test.screens.main_hub.navigate()
        if not status:
            logging.error("to_hub_from_fullscreen failed")
            return False

        status = self.test.screens.main_hub.focus_item_in_hub(item_title='GRID')
        if not status:
            logging.error("Fail to move focus on GRID")
            return False

        self.test.wait(CONSTANTS.GENERIC_WAIT)
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "main_hub")
        if not status:
            logging.error("wait for main_hub timed out")
            return False

        logging.info("In main_hub")
        return True

    def to_nextchannel_in_guide(self, direction="up"):
        """
        Go to next channel in guide
        :param direction: button to press. "up" or "down"
        :return: True when on new channel. Still on guide screen
        """
        status = self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "guide")
        if not status:
            logging.error("wait for guide timed out")
            return False
        logging.info("In guide")

        actual_focused_channel_number = self.test.milestones.get_value_by_key(self.test.milestones.getElements(),
                                                                                "focused_channel_number")

        if direction == "down":
            logging.info("Pressing down key")
            self.test.appium.key_event("KEYCODE_DPAD_DOWN")
        else:
            logging.info("Pressing up key")
            self.test.appium.key_event("KEYCODE_DPAD_UP")

        next_focused_channel_number = self.test.milestones.get_value_by_key(self.test.milestones.getElements(),
                                                                              "focused_channel_number")

        return actual_focused_channel_number != next_focused_channel_number

    def get_focused_channel_number(self, elements=None):
        """
        return the focused channel as int
        based on the pattern of events now
        """
        if elements is None:
            elements = self.test.milestones.getElements()

        channel_info = self.test.milestones.get_value_by_key(elements, 'focused_channel_info')
        if not isinstance(channel_info, bool):
            if 'number' in channel_info:
                return channel_info['number']

        return False

    def get_focused_event_title(self, elements=None):
        """
              return the focused event title
        """
        if elements is None:
            elements = self.test.milestones.getElements()

        focused_event_title = self.test.milestones.get_value_by_key(elements, 'focused_event_title')

        return focused_event_title

    def get_focused_event_start_time(self, elements=None):
        """
              return the focused event start time
        """
        if elements is None:
            elements = self.test.milestones.getElements()

        event_start_time = self.test.milestones.get_value_by_key(elements, 'start_time')

        return event_start_time

    def get_focused_event_end_time(self, elements=None):
        """
              return the focused event start time
        """
        if elements is None:
            elements = self.test.milestones.getElements()

        event_start_time = self.test.milestones.get_value_by_key(elements, 'start_time')
        event_duration = self.test.milestones.get_value_by_key(elements, 'duration')
        if event_start_time is not False and event_duration is not False:
            event_end_time = event_start_time + event_duration
            return event_end_time

        return False

    def to_specific_channel_in_guide(self, specific_channel, direction="up", timeout=300):
        """
        Go to specific channel in guide
        param specific_channel: destination channel
        :param specific_channel: channel to go
        :param direction: button to press. "up" or "down"
        :param timeout: in seconds
        :return: True when on destination channel. Still on guide screen
        """

        try:
            assert self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "guide"), "Not located GUIDE TV"

            actual_focused_channel_number = self.get_focused_channel_number()
            
            start_time = time.time()
            
            while actual_focused_channel_number != specific_channel:
                logging.info("actual_focused_channel_number is %s" % actual_focused_channel_number)
                #pdb.set_trace()
                self.to_nextchannel_in_guide("down")
                actual_focused_channel_number = self.get_focused_channel_number()
                assert time.time()-start_time < timeout, "{} seconds passed and we did not get to requsted channel, current variabales are {}".format(seconds, locals)
            
            return specific_channel == self.get_focused_channel_number()
        except Exception as ex:
            logging.exception("\n\n ---------------------------------------------------\n         ACTION ABORTED DUE TO : \n")
            return {"exception": ex}
     
    def to_nextevent_in_guide(self):
        """
        Moving to next event in guide
        return : True when located on next event
        """
        try:
            assert self.test.wait_for_screen(CONSTANTS.WAIT_TIMEOUT, "guide"), "Not located GUIDETV"
            src_event_title = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_event_title")
            self.test.appium.key_event("KEYCODE_DPAD_RIGHT")
            dst_event_title = self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "focused_event_title")
            if src_event_title == dst_event_title:
                logging.warn("The name of focused event was not changed after the action of pressing right.\nMaybe an error has occured.\nPrevious focused event name is {}, current focused event name is {}".format(src_event_title, dst_event_title))
            return True
        except Exception as ex:
            logging.exception("\n\n ---------------------------------------------------\n         ACTION ABORTED DUE TO : \n")
            return {"exception": ex}

    def guide_scroll_channellineup(self, direction='down'):
        """
        In Guide, scroll through the channels
        :param direction: direction of the scrolling (up/down)
        :return: new channel_number focussed
        """
        if direction == 'down':
            self.test.appium.key_event("KEYCODE_DPAD_DOWN" )
        else:
            self.test.appium.key_event("KEYCODE_DPAD_UP" )
        self.test.wait(0.5)

        for retries in range(5, 0, -1):
            elements = self.test.milestones.getElements()
            current_channel = self.test.milestones.get_value_by_key(elements, "focused_channel_number")
            logging.info("current_channel: {0}".format(current_channel))
            if current_channel is not False:
                return current_channel
            self.test.wait(0.5)

        return False

    def get_dayOffset_in_guide(self):
        """
        Return dayOffset in guide
        :return: dayOffset as a string
        """
        
        return self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "day_offset")

    def get_overview_title_in_guide(self):
        """
        Return the text in the overview field of the Guide
        :return: string
        """

        return self.test.milestones.get_value_by_key(self.test.milestones.getElements(), "overview_title")

    def get_guide_focus_state(self):
        elements = self.test.milestones.getElements()
        focus_state = self.test.milestones.get_value_by_key(elements, "focus_state")
        return focus_state

    def guide_find_channel_with_events(self, direction='down', max_channels_to_search=40):
        for i in range(max_channels_to_search):
            current_event = self.get_focused_event_title()
            if current_event is not None and current_event is not False:
                logging.info("guide_find_channel_with_events: lcn: {0}  found event:{1}"
                             .format(self.get_focused_channel_number(), current_event))
                return True
            if direction == 'down':
                self.test.appium.key_event("KEYCODE_DPAD_DOWN" )
                self.test.wait(1)
            else:
                self.test.appium.key_event("KEYCODE_DPAD_UP" )
                self.test.wait(1)
        else:
            logging.error("Did not find any channel with events")
            return False

    def guide_goto_next_event(self, direction='right', validation_check=False):
        """
        Select the next/previous event in the Guide
        :param direction: (right/left)
        :param validation_check: check the start next event time
        :return: False is not able to retrieve and event
                 True is a new event is select
                 Last is same event is still selected
        """
        elements = self.test.milestones.getElements()
        previous_event_title = self.get_focused_event_title(elements)
        previous_event_end_time = self.get_focused_event_end_time(elements)
        previous_event_start_time = self.get_focused_event_start_time(elements)

        if previous_event_title is False or previous_event_end_time is False or previous_event_start_time is False:
            logging.info("Failure to retrieve valid event informations. title: {} end_time: {}"
                          .format(previous_event_title, previous_event_end_time))
            return False

        if direction == 'right':
            self.test.appium.key_event("KEYCODE_DPAD_RIGHT" )
        else:
            self.test.appium.key_event("KEYCODE_DPAD_LEFT" )
        self.test.wait(1)

        elements = self.test.milestones.getElements()
        current_event_title = self.get_focused_event_title(elements)
        current_event_start_time = self.get_focused_event_start_time(elements)
        current_event_end_time = self.get_focused_event_end_time(elements)

        if current_event_title is False or current_event_start_time is False or current_event_end_time is False:
            logging.info("Failure to retrieve valid event informations after selected next one. title: {} end_time: {}"
                          .format(current_event_title, current_event_start_time))
            return False

        if current_event_start_time == previous_event_start_time:
            logging.info("Previous event and current have same start time. It seems that there is no more next event")
            return 'Last'

        if validation_check:
            if direction == 'right':
                return previous_event_end_time <= current_event_start_time
            else:
                return current_event_end_time <= previous_event_start_time
        return True
