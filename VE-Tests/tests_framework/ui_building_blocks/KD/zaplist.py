__author__ = 'bwarshaw'

import logging
from time import sleep
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.tests_conf import DeviceType

''' Constants '''
TUNE_TO_CHANNEL_TIMEOUT = 3
TIMEOUT = 2
ZAPLIST_DISMISS_TIMEOUT = 15
BACK_TIMEOUT = 2

class ZapList(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "zap_list")
        self.timeout = ZAPLIST_DISMISS_TIMEOUT
        if self.test.platform == "Android":
            self.scroll_speed = -1
        else:
            self.scroll_speed = -2

    def verifyimages(self):
        self.verify_active()
        """ Todo: Add support for verifying images """

    def navigate(self, swipe_direction=ScreenActions.DOWN):
        logging.info("Navigate to zap list")
        screen = self.test.milestones.get_current_screen()
        if screen == "zap_list":
            return
        if screen != "fullscreen" and  screen != 'infolayer':
            self.test.say('need to navigate to fullscreen')
            self.test.screens.fullscreen.navigate()

        if self.test.project != "KD":
            if self.test.app_mode == "V2":
                self.test.screens.infolayer.show()
                #Tap zaplist button if exists
                self.test.wait(2)
                self.test.ui.tap_element("zaplist")
        else:
            self.test.ui.two_finger_swipe(swipe_direction)
        self.verify_active()

    def get_centered_event_view(self, elements, filter='channel_id'):
        return self.test.ui.get_center_element("event_view", elements, filter)

    def dismiss(self, alternateExit=False):
        logging.info("Dismiss zaplist")
        elements = self.test.milestones.getElements()
        screen = self.test.milestones.get_current_screen(elements)
        if screen != "zap_list":
            return

        if self.test.project != "KD" and self.test.app_mode == "V2":
            if self.test.device_type != DeviceType.TABLET:
                self.test.ui.tap_element("exit")
            else:
                self.test.ui.tap_element("back")
            self.test.wait(BACK_TIMEOUT)
            self.test.screens.infolayer.dismiss(self.test.screens.infolayer.dismissTypes.TAP)
        else:
            "Dismiss zaplist, return to Fullscreen"
            window_width, window_height = self.test.milestones.getWindowSize()
            self.test.appium.tap(window_width/2, window_height/2)
            self.test.screens.fullscreen.verify_active()

    def prepare_for_channel_scrolling(self, direction):
        logging.info("prepare_for_channel_scrolling")
        self.test.say('navigating to zaplist')
        self.navigate()
        elements = self.test.milestones.getElements()
        first_centered_event_view = self.get_centered_event_view(elements)
        self.test.log_assert(first_centered_event_view, "tune_to_channel_by_name building block can't find event view in the center of the screen")

        device_details = self.test.milestones.getDeviceDetails()
        if "touch-slop" in device_details:
            touch_slop = device_details["touch-slop"] + 2 # just a little bit more
        else:
            device_type = self.test.device_type
            if device_type != DeviceType.TABLET:
                touch_slop = first_centered_event_view["height"]* 0.05
            else:
                touch_slop = 0
        self.test.log("touch slop is %s " % touch_slop)
        scroll_distance = first_centered_event_view["height"] + touch_slop

        #check if to use parent height - ios!
        if ('parent-height' in first_centered_event_view) and (first_centered_event_view['parent-height'] > 0):
            scroll_distance = first_centered_event_view['parent-height']
            self.test.log("scroll distance (using parent): " + str(scroll_distance))
        else:
            self.test.log("scroll distance: " + str(scroll_distance))

        events_scroller = self.test.milestones.getElement([("name", "events_scroller", "==")], elements)
        self.test.log_assert(events_scroller, "No events scroller in zaplist Milstones")

        return (first_centered_event_view, scroll_distance, events_scroller)

    def scroll_channels(self, steps):
        logging.info("scrolling %d channels" % steps)
        direction = ScreenActions.UP if steps>0 else ScreenActions.DOWN
        (first_centered_event_view, scroll_distance, events_scroller) = self.prepare_for_channel_scrolling(direction)
        for i in range(0,abs(steps)):
            self.test.appium.scroll_from_element(events_scroller, scroll_distance, direction, self.scroll_speed)
            sleep(0.3)
        logging.info("finished scrolling %d channels" % steps)

    def tune_to_channel_by_sek(self, channel_id, verify_streaming_started=True):
        self.navigate()
        event_view = self.scroll_to_channel_by_sek(channel_id)
        self.test.wait(1)
        logging.info("Tunning to channel %s" % channel_id)
        self.test.appium.tap_element(event_view)
        if verify_streaming_started:
            self.test.screens.playback.verify_streaming_playing()

    def scroll_channel(self, direction, optional, verify_callback, *params):
        ''' tune to channel by channel id  '''
        logging.info("Scrolling to channel matching " + str(*params))
        (first_centered_event_view, scroll_distance, events_scroller) = self.prepare_for_channel_scrolling(direction)
        channel_found = False
        cycle_not_completed = True
        current_centered_event_view = first_centered_event_view
        self.test.log_assert(first_centered_event_view, "Cannot find first centered event view")
        self.test.log_assert('channel_id' in first_centered_event_view, "Cannot find channel id in first centered event view")
        if first_centered_event_view and verify_callback(first_centered_event_view, *params):
            return first_centered_event_view
        event_changed = False
        event_not_first = False
        while cycle_not_completed:
            if current_centered_event_view and verify_callback(current_centered_event_view, *params):
                channel_found = True
                break

            self.verify_active()
            self.test.appium.scroll_from_element(events_scroller, scroll_distance, direction, self.scroll_speed)
            elements = self.test.milestones.getElements()

            current_centered_event_view = self.get_centered_event_view(elements, filter=None)
            self.test.log_assert(current_centered_event_view, "Cannot find current centered event view")
            if 'channel_id' in current_centered_event_view:
                event_not_first = current_centered_event_view["channel_id"] != first_centered_event_view["channel_id"]
                self.test.log("First channel id %s, Current channel id %s" % (first_centered_event_view["channel_id"], current_centered_event_view["channel_id"]))
            if event_not_first:
                if not event_changed:
                    event_changed = True
            elif event_changed:
                cycle_not_completed = False
            sleep(0.1)

        if not optional:
            self.test.log_assert(channel_found, "Could not find matching channel to params: " + str(*params))
        if not channel_found:
            current_centered_event_view = None
        return current_centered_event_view

    def compare_sek(self, current_view, channel_id):
       return 'channel_id' in current_view and current_view['channel_id'] == str(channel_id)

    def get_scroll_direction(self, channel_id):
        scroll_direction = ScreenActions.UP
        elements = self.test.milestones.getElements()
        first_centered_event_view = self.get_centered_event_view(elements)
        if first_centered_event_view and 'channel_id' in first_centered_event_view:
            current_channel_id = first_centered_event_view['channel_id']
            ''' retrieve ctap channel list '''
            ctap_grid_info = self.test.ctap_data_provider.send_request('GRID', None)
            channel_count = ctap_grid_info['total']
            channel_index = self.test.ctap_data_provider.get_channel_index(channel_id, ctap_grid_info)
            current_channel_index = self.test.ctap_data_provider.get_channel_index(current_channel_id, ctap_grid_info)

            self.test.log("channel_count= " + str(channel_count) + ", channel_index=" + str(channel_index) + " , current_channel_index=" + str(current_channel_index))
            if channel_index < current_channel_index:
                scroll_direction = ScreenActions.DOWN
                self.test.log("Scrolling down because target channel is above current channel")
            elif channel_index > current_channel_index:
                up_channel_diff = channel_index - current_channel_index
                down_channel_diff = channel_count - channel_index - current_channel_index
                self.test.log("up_channel_diff=" + str(up_channel_diff) + ", down_channel_diff=" + str(down_channel_diff))
                if down_channel_diff>=0 and up_channel_diff>=0 and down_channel_diff < up_channel_diff:
                #if down_channel_diff < up_channel_diff:
                    scroll_direction = ScreenActions.DOWN
                    self.test.log("Scrolling down because target channel is above current channel")
                else:
                    scroll_direction = ScreenActions.UP
                    self.test.log("Scrolling up because target channel is below current channel")
        return scroll_direction

    def scroll_to_channel_by_sek(self, channel_id, direction=None):
        if direction==None:
            direction = self.get_scroll_direction(channel_id)
        return self.scroll_channel(direction, False, self.compare_sek, channel_id)

    def scroll_from_center(self, duration=0, direction = ScreenActions.UP):
        elements = self.test.milestones.getElements()
        first_centered_event_view = self.get_centered_event_view(elements)
        self.test.log_assert(first_centered_event_view, "can't find event view in the center of zaplist screen")

        scroll_distance = first_centered_event_view["height"]
        events_scroller = self.test.milestones.getElement([("name", "events_scroller", "==")], elements)
        self.test.log_assert(events_scroller, "no event_scroller in zaplist milstones")
        self.test.appium.scroll_from_element(events_scroller, scroll_distance, direction, duration)

    def get_displayed_events(self, elements=None):
        if elements==None:
             elements = self.test.milestones.getElements()
        events = self.test.ui.get_sorted_elements("event_view", 'x_pos', elements, 'channel_id')
        return events

    def get_all_events(self):
        events = []
        self.navigate()
        first_event = self.get_centered_event_view(self.test.milestones.getElements())
        current_event = first_event

        cycle_not_completed = True
        while cycle_not_completed:
            events.append(current_event)
            logging.info("curr channel id = %s", current_event['channel_id'])
            next_event = self.get_next_event(current_event)
            logging.info("next channel id = %s", next_event['channel_id'])
            if first_event['channel_id'] == next_event['channel_id']:
                cycle_not_completed = False
            else:
                current_event = next_event
        return events

    def get_next_event_from_milstone(self, channel_id, swipe_direction = ScreenActions.UP):
        displayed_events = self.get_displayed_events()
        for i in range(0,len(displayed_events)):
            if displayed_events[i]['channel_id'] == channel_id:
                if swipe_direction == ScreenActions.UP:
                    index = i+1
                else:
                    index = i-1
                self.test.log_assert(index>=0 and index<len(displayed_events), "Next event is not in milstone. cur event index=%s nextEventIndex = %s"%(i, index))
                return displayed_events[index]

        self.test.log_assert(False, "channel %s is not in zaplist displayed events" % channel_id)

    def get_event_from_milstones(self, channel_id):
        displayed_events = self.get_displayed_events()
        for i in range(0,len(displayed_events)):
            if displayed_events[i]['channel_id'] == channel_id:
                return  displayed_events[i]
        self.test.log_assert(False, "channel %s is not in zaplist displayed events" % channel_id)

    def get_next_event(self, current_event, swipe_direction=ScreenActions.UP):
        currentEventChId = current_event["channel_id"]

        (first_centered_event_view, scroll_distance, events_scroller) = self.prepare_for_channel_scrolling(swipe_direction)
        self.test.appium.scroll_from_element(events_scroller, scroll_distance, swipe_direction, self.scroll_speed)

        elements = self.test.milestones.getElements()
        next_event = self.get_centered_event_view(elements)
        nextEventChId = next_event["channel_id"]

        self.test.log_assert(currentEventChId != nextEventChId, "Channel should not match, current: " + str(currentEventChId) + " next: " + str(nextEventChId))
        return next_event

    def verify_channels_lineup(self, events):
        channel_numbers = []
        logging.info("verify_channels_lineup")
        lowest_channel = int(events[0]['channel_number'])
        lowest_channel_index = 0
        for i in range(0, len(events)):
            channel_number = int(events[i]['channel_number'])
            if channel_number < lowest_channel:
                lowest_channel = channel_number
                lowest_channel_index = i
            channel_numbers.append(channel_number)

        self.test.log("Lowest channel is " + str(lowest_channel) + " at index " + str(lowest_channel_index) + ", Channel lineup: " + str(channel_numbers))

        #Verify that channels are sorted by logical channel number
        for i in range(0, len(channel_numbers)-1):
            cur_channel = channel_numbers[lowest_channel_index-i]
            next_channel = channel_numbers[lowest_channel_index-i-1]
            if next_channel < cur_channel and next_channel!=lowest_channel:
                self.test.log_assert(False, "ZapList logical channels not in lineup (%d>%d)"%(cur_channel,next_channel))

    def verify_playing_channel_position(self, channel_id):
        self.navigate()
        center_event = self.get_centered_event_view(self.test.milestones.getElements())
        self.test.log_assert(center_event['channel_id'] == channel_id, "zaplist center channel (%s) is not as expected (%s)"%(center_event['channel_id'], channel_id))
        return center_event

    def tap_channel(self,channelIndex):
        self.double_tap_channel(channelIndex)

    def get_tuned_event(self):
        tuned_channel_id = self.test.screens.playback.get_current_tuned()
        tuned_event = self.verify_playing_channel_position(tuned_channel_id)
        return tuned_event

    def tune_to_current_channel(self):
        tuned_channel_id = self.test.screens.playback.get_current_tuned()
        self.tune_to_channel_by_sek(tuned_channel_id)

    def get_non_centered_channel_LCN(self):
        elements = self.test.milestones.getElements()
        element = self.test.milestones.getElementsArray([("id", "LCN", "==")],elements)
        return element[-1]["title_text"]

    def double_tap_channel(self,channelIndex):
        elements = self.test.milestones.getElements()
        event = self.test.ui.get_vertical_element("event_view", elements, channelIndex)
        self.test.log_assert(event, "Cannot find channel " + str(channelIndex) + " to tap")
        self.test.appium.double_tap(event['x_pos'] + event['width']/2 , event['y_pos'] + event['height']/2)
        self.test.wait(3)

    def scroll_multi(self, duration, direction, repeat = 1):
        for index in range(0,repeat):
            self.scroll_from_center(duration, direction)

    def verify_zaplist_showing(self):
        screen = self.test.milestones.get_current_screen()
        self.test.log_assert(screen == "zap_list","ZapList is not on the screen")

    def getSnapshot(self):
        self.infoLayerData = self.test.milestones.getElements()

    def compare_verify(self, current_view, zaplist_events):
        zaplist_events.append(current_view)
        event_progress = float(current_view['progress_bar'])
        if  event_progress  > 0.1 and event_progress < 0.9:
            self.test.ctap_data_provider.compare_event_metadata(current_view)
        else:
            logging.info("Event progress [%f] is close to event boundary, skip ctap compare" % event_progress)

    def verify_metadata(self):
        self.navigate()
        zaplist_events = []
        self.scroll_channel(ScreenActions.DOWN, True, self.compare_verify, zaplist_events)

        ctap_grid_info = self.test.ctap_data_provider.send_request('GRID', None)
        self.test.log_assert(ctap_grid_info['total'] == len(zaplist_events), "Number of channels displayed in zaplist (%d) is different than number of channels got from ctap(%d)"%(len(zaplist_events),ctap_grid_info['total'], ))

        self.verify_channels_lineup(zaplist_events)

