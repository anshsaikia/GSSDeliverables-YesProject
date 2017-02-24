__author__ = 'ravnon'

import logging
import operator
import datetime
import random
import time
from dateutil import tz
import calendar

from enum import Enum
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenActions
from tests_framework.ve_tests.tests_conf import DeviceType
'''Globals'''
EVENT_VIEW_TIME_FORMAT = "%I.%M %p"
HOUR_VIEW_TIME_FORMAT = "%I %p"
DATE_LONG_FORMAT = "%a, %B %-d"
DATE_SHORT_FORMAT = "%a, %b %-d"


class kGuideScreenSection(Enum):
    PREVIEW = "preview"
    GRID = "grid"

class KGuide(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "guide")
        self.maxChannelsToCycle = 500

    def navigate(self):
        logging.info("Navigate to guide")

        screen = self.test.milestones.get_current_screen()
        if screen == "guide":
            return
        if not self.test.screens.header.item_exists("DIC_MAIN_HUB_GUIDE"):
            self.test.screens.tv_filter.navigate()
        self.test.screens.header.tap_item("DIC_MAIN_HUB_GUIDE")
        self.verify_active()

    # TODO: duplicate from smartphones
    def get_current_screen_data(self,elements = None):
        if elements is None:
            elements = self.test.milestones.getElements(update=True)

        channels = self.get_channels(elements)
        self.test.log_assert(channels,"No channels found on screen")

        current_hour = self.get_current_selected_hour_window(elements)
        current_day = self.get_current_selected_day()
        current_channel_id = channels[0]['channel_id']
        server_channel_index = self.test.ctap_data_provider.get_channel_index(current_channel_id)
        return { 'hour' : current_hour,
                 'day' : current_day,
                 'channel_id':current_channel_id,
                 'channel_offset': server_channel_index}

    # TODO: duplicated from smartphones
    def scroll_next_channel(self):
        #WARNING: since we are scrolling one channel, it might happen that for some channels that are already displayed,the events list
        #might not be updated
        elements = self.test.milestones.getElements()
        channels = self.get_channels(elements)

        channels = self.get_channels(elements)
        self.test.log_assert(channels,"No channels found on screen")

        current_data = self.get_current_screen_data(elements)

        self.test.appium.swipe_element(channels[1], channels[1]['x_pos'],ScreenActions.UP)
        self.test.wait(0.5,log=False)

        # get updated channles
        channels = self.get_channels()
        if channels[0]['channel_id'] == current_data['channel_id']:#reach end of horizontal list,cannot scroll further
            return False

        #TODO: verify data only works on preview screen
        # self.verify_data()
        return True

    #internal
    def should_add_day_to_calc(self, time_elements, curr_time_x_pos):

        headerElement = self.test.ui.get_localized_label("DIC_GUIDE_GRID")
        grid_start_x_pos = headerElement["x_pos"]

        for time_element in time_elements:
            time_header = time_element['title_text']
            time_header = self.test.ui.remove_special_chars(time_header)
            time_header_x_pos = time_element['x_pos']
            if self.test.mirror.in_edge_of_screen(time_element):
                continue
            self.test.log_assert(':' in time_header, "time_header does not contain colon: " + str(time_header) + " element: " + str(time_element))
            time_header_hour, time_header_minute = time_header.split(':')
            time_header_minute, time_header_ampm = time_header_minute.split(' ')
            time_header_hour = int(time_header_hour)
            time_header_minute = int(time_header_minute)

            if time_header_ampm == "PM":
                time_header_hour += 12

            if time_header_hour ==0 and time_header_minute == 0 and grid_start_x_pos < time_header_x_pos and time_header_x_pos <= curr_time_x_pos:
                return 1
            elif time_header_hour == 23 and time_header_minute == 30 and time_header_x_pos < grid_start_x_pos and curr_time_x_pos <= time_header_x_pos:
                return -1

        return 0

    #event extract times
    def extract_event_times_grid(self, event):
        self.test.log_assert(event is not None, "Event is empty! could not parse this event.")
        time_text = self.test.ui.remove_special_chars(event["time_text"])
        time_text = self.test.milestones.replace_date_names(time_text)
        if len(time_text.split(' ')) > 3:
            return self.extract_event_times_grid_full_time(time_text)
        else:
            return self.extract_event_times(time_text)

    def get_month_as_number(self, monthname):
        mlist=list(calendar.month_abbr)
        mlist=filter(None, mlist)
        if monthname in mlist:
            result = mlist.index(monthname) + 1
        else:
            result = -1
        self.test.log("Month: " + str(monthname) + " = " + str(result) + " in list: " + str(mlist))
        return result

    def extract_event_times_grid_full_time(self, time_text):
        device_details = self.test.milestones.getDeviceDetails()

        day, day_in_month, month_name, times, am_pm = time_text.split()
        start_time , end_time = times.split(u'\u2014')

        month_num = self.get_month_as_number(month_name)
        self.test.log("time_text: " + str(time_text) + " day: " + day + " day_in_month: "  + str(day_in_month) + " month_num: " + str(month_num) + " month name: " + str(month_name) + " times: " + str(times) + " am_pm: " + str(am_pm))
        return self.calc_am_pm(start_time, end_time, am_pm, int(day_in_month), month_num)

    def calc_am_pm(self, start_time, end_time, end_am_pm, day_in_month=-1, month_num=-1):
        device_details = self.test.milestones.getDeviceDetails()

        start_h, start_m = start_time.split(':')
        end_h, end_m = end_time.split(':')

        startTimeHR = int(start_h)
        endTimeHR = int(end_h)
        day_offset = 0
        start_ampm = end_am_pm
        #Set to 0 for calculations if 12
        if startTimeHR == 12:
            startTimeHR = 0
        if endTimeHR == 12:
            endTimeHR = 0
        #set am/pm indictator
        if startTimeHR > endTimeHR:
            if end_am_pm == 'AM':
                start_ampm = 'PM'
            else:
                start_ampm = 'AM'
        #set 12 to 24 hour
        if start_ampm == 'PM':
            startTimeHR += 12
        if end_am_pm == 'PM':
            endTimeHR += 12
        if end_am_pm == 'AM':
            if startTimeHR > endTimeHR:
                day_offset = 1

        self.test.log("start-time: " + str(start_time) + " start_ampm: " + (start_ampm) + " end-time: " + str(end_time) + " end_am_pm: " + str(end_am_pm))

        startTime = datetime.datetime.now().replace(hour=startTimeHR,
                                                    minute=int(start_m), second=0,
                                                    microsecond=0).replace(tzinfo=tz.gettz(device_details['timezone']))
        endTime = datetime.datetime.now().replace(hour=endTimeHR,
                                                  minute=int(end_m), second=0,
                                                  microsecond=0).replace(tzinfo=tz.gettz(device_details['timezone']))

        if day_in_month != -1:
            startTime = startTime.replace(day = day_in_month)
            endTime = endTime.replace(day = day_in_month)
            self.test.log("replacing day_in_month: " + str(day_in_month) + " startTime: " + str(startTime) + " endTime: " + str(endTime))
        if month_num != -1:
            startTime = startTime.replace(month = month_num)
            endTime = endTime.replace(month = month_num)
            self.test.log("replacing month_num: " + str(month_num) + " startTime: " + str(startTime) + " endTime: " + str(endTime))

        day_in_month = endTime.day + day_offset
        if day_in_month > 31:
            endTime = endTime.replace(day=0)
            endTime = endTime.replace(month=endTime.month + 1)
        if endTime.month > 12:
            endTime = endTime.replace(month=0)
            endTime = endTime.replace(year=endTime.year + 1)

        self.test.log_assert(day_in_month >= 1 and day_in_month <= 31, "day in month not valid (1-31) day_in_month:" + str(day_in_month) + " endTime.day: " + str(endTime.day) + " day_offset: " + str(day_offset))
        self.test.log("replacing day in month from " + str(endTime.day) + " to " + str(day_in_month))
        endTime = endTime.replace(day = day_in_month)
        return startTime, endTime

    def extract_event_times(self, time_text):
        times, end_am_pm = time_text.split()
        start_time, end_time = times.split(u'\u2014')

        return self.calc_am_pm(start_time, end_time, end_am_pm)

    def verify_grid_data(self):
        channels = self.get_grid_channels()
        device_details = self.test.milestones.getDeviceDetails(update=True)

        headerElement = self.test.ui.get_localized_label("DIC_GUIDE_GRID")
        grid_x_pos = self.test.mirror.get_x(headerElement)
        self.test.log("grid_x_pos: " + str(grid_x_pos))

        time_elements = self.test.milestones.getElementsArray([("id", "guide_time", "==")])
        current_day_element = self.get_current_selected_day()
        current_day = self.test.ui.remove_special_chars(current_day_element['title_text'])
        day_in_mounth = filter(type(current_day).isdigit, current_day)

        for time_element in time_elements:
            time_header = time_element['title_text']
            time_header = self.test.ui.remove_special_chars(time_header)
            time_header_x_pos = self.test.mirror.get_x(time_element)
            if self.test.mirror.in_edge_of_screen(time_element):
                self.test.log("Skipping time: " + str(time_element) + " because it is at the edge of the screen")
                continue
            if not self.test.mirror.element_after_element(time_element, headerElement):
                self.test.log("Skipping time: " + str(time_element) + ":" + str(time_header_x_pos) + " because it is before grid start point: " + str(grid_x_pos))
                continue
            self.test.log_assert(':' in time_header, "time_header does not contain colon: " + str(time_header) + " element: " + str(time_element))
            time_header_hour, time_header_minute = time_header.split(':')
            time_header_minute, time_header_ampm = time_header_minute.split(' ')
            time_header_hour = int(time_header_hour)
            time_header_minute = int(time_header_minute)

            if time_header_ampm == "PM" and time_header_hour != 12:
                time_header_hour += 12
            elif time_header_ampm == "AM" and time_header_hour == 12:
                time_header_hour = 0

            dayOffset = self.should_add_day_to_calc(time_elements, time_header_x_pos)

            time_header_date = datetime.datetime.now().replace(day = int(day_in_mounth) + dayOffset, hour=int(time_header_hour), minute=int(time_header_minute), second=0,
                                            microsecond=0).replace(tzinfo=tz.gettz(device_details['timezone']))

            self.test.log("verifying events in grid date: " + str(time_header_date) + " time_header_x_pos:" + str(time_header_x_pos) + " day_in_month: " + str(day_in_mounth) + " time_header_hour: " + str(time_header_hour) + " time_header_minute: " + str(time_header_minute))

            for channel in channels:
                if channel == None:
                    continue
                for event in channel:
                    if "time_text" not in event:
                        continue

                    (startTime, endTime) = self.extract_event_times_grid(event)

                    within_pos_window = self.test.mirror.element_within_column(event, time_element)
                    in_time_window = startTime <= time_header_date < endTime
                    logMessage = "within_pos_window: " + str(within_pos_window)
                    logMessage += " in_time_window: " + str(in_time_window)
                    logMessage += " event: " + str(event['title_text'])
                    logMessage += " left: " + str(event['x_pos'])
                    logMessage += " right: " + str(event['x_pos'] + event['width'])
                    logMessage += " startTime: " + str(startTime)
                    logMessage += " endTime: " + str(endTime)
                    logMessage += " time_header_date: " + str(time_header_date)
                    logMessage += " time_header_x_pos: " + str(time_header_x_pos)
                    logMessage += " time_element: " + str(time_element['title_text'])
                    logMessage += " left: " + str(time_element['x_pos'])
                    logMessage += " right: " + str(time_element['x_pos'] + time_element['width'])
                    self.test.log_assert(in_time_window == within_pos_window, "event not correctly mapped into time window " + logMessage)
                    self.test.log("assessment of event alignment: " + logMessage)

    def get_grid_channels(self):
        headerElement = self.test.ui.get_localized_label("DIC_GUIDE_GRID")
        grid_events = self.test.milestones.getElements()
        grid_events = self.test.ui.get_sorted_elements('event_view', 'y_pos', grid_events)
        self.test.log_assert(grid_events, "Cannot find grid events")

        grid_channels = self.get_channels()
        self.test.log_assert(grid_channels, "Cannot find grid channels")
        self.test.log("number of channels found: " + str(len(grid_channels)) + " channels: " + str(grid_channels))
        channels = [None] * len(grid_channels)
        found_channel = False
        for grid_event in grid_events:
            if not self.test.mirror.element_after_element(grid_event, headerElement, no_overlap=False):
                continue
            found_event = False
            channel_index = 0
            self.test.log("searching for channel " + str(grid_event['channel_id']))
            for grid_channel in grid_channels:
                if grid_event['channel_id'] == grid_channel['channel_id']:
                    if channels[channel_index] == None:
                        channels[channel_index] = []
                    channels[channel_index].append(grid_event)
                    self.test.log("Found a grid event: " + str(grid_event))
                    found_channel = True
                    found_event = True
                    break
                channel_index+=1
            self.test.log_assert(found_event, "Cannot find matching channel for event: " + str(grid_event))
        self.test.log_assert(found_channel, "Cannot find grid events from left position " + str(headerElement['x_pos']))
        return channels

    def get_current_selected_day(self):
        date_elements = self.test.milestones.getElementsArray([("id","guide_date","==")])
        selected_date_element = self.test.milestones.getElement([("is_selected", True,"==")])
        return selected_date_element

    def get_current_selected_hour_window(self, elements=None):
        time_elements = self.test.milestones.getElementsArray([("id", "guide_time", "==")])
        time_elements = self.test.ui.get_sorted_elements('text_view', 'x_pos', time_elements)
        startTime = time_elements[0]['title_text']
        endTime = time_elements[-1]['title_text']
        return (startTime, endTime)

    def get_channels(self, elements = None):
        channels = sorted(self.test.milestones.getElementsArray([("id", "channel_logo", "==")], elements), key=operator.itemgetter('y_pos'))
        return channels

    def verify_data(self):
        device_details = self.test.milestones.getDeviceDetails()
        localTime = self.test.milestones.getLocalTime()

        '''Verify NOW string exist
           Verify all events under Now column are in the expected time range'''
        nowElement = self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_NOW", "general").upper(), "==")])
        self.test.log_assert(nowElement,"NOW Element is not exist")
        nowEventsElements = self.test.ui.get_column_events("event_view", 0)
        for nowEventElement in nowEventsElements:
            if "time_text" in nowEventElement:
                (startTime, endTime) = self.extract_event_times_grid(nowEventElement)
                logging.info("NowEvent: startTime = %s endTime = %s localTime = %s", str(startTime), str(endTime), str(localTime))
                self.test.log_assert((startTime <= localTime) and (endTime >= localTime), "Now Event Element time is not in the expected time range, startTime: " + str(startTime) + ", endTime: " + str(endTime) + ", localTime: " + str(localTime))

        '''Verify NEXT string exist
            Verify all events under Next column are in the expected time range'''
        nextElement = self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_NEXT", "general").upper(), "==")])
        self.test.log_assert(nextElement,"NEXT Element is not exist")
        nextEventsElements = self.test.ui.get_column_events("event_view", 1)
        for nextEventElement in nextEventsElements:
            if "time_text" in nextEventElement:
                (startTime, endTime) = self.extract_event_times_grid(nextEventElement)
                logging.info("NextEvent: startTime = %s endTime = %s localTime = %s", str(startTime), str(endTime), str(localTime))
                self.test.log_assert(startTime > localTime, "Next Event Element time is not in the expected time range, startTime: " + str(startTime) + ", endTime: " + str(endTime) + ", localTime: " + str(localTime))

        '''Verify NOW, NEXT strings exist'''
        self.test.log_assert(self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_NOW", "general").upper(), "==")]),"NOW Element is not exist")
        self.test.log_assert(self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_NEXT", "general").upper(), "==")]),"NEXT Element is not exist")

        '''Verify if earlier than 20:00Pm TONIGHT string will exist, otherwise LATER string should exist'''
        today8pm = datetime.datetime.now().replace(hour=20, minute=0, second=0, microsecond=0).replace(tzinfo=tz.gettz(device_details['timezone']))
        if (localTime > today8pm):
            self.test.log_assert(self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_LATER", "general").upper(), "==")]),"LATER Element is not exist")
        else:
            self.test.log_assert(self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_TONIGHT", "general").upper(), "==")]),"TONIGHT Element is not exist")

    def showAndVerifyActionMenu(self):
        elements = self.test.milestones.getElements()
        '''Verify Action Menu on current event'''
        elements = self.test.milestones.getElements()
        nowElement = self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_NOW", "general").upper(), "==")])
        self.test.log_assert(nowElement,"NOW Element is not exist")
        nowEventsElements = self.test.ui.get_column_events("event_view", 0)
        if "time_text" in nowEventsElements[0]:
            self.test.appium.tap_element(nowEventsElements[0])
            self.test.screens.linear_action_menu.verify_active()
            self.test.wait(2)
            self.test.screens.linear_action_menu.verify_data()
            self.test.screens.linear_action_menu.dismiss()
            self.test.wait(2)
        '''Verify Action Menu on next event'''
        elements = self.test.milestones.getElements()
        nextElement = self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_NEXT", "general").upper(), "==")])
        self.test.log_assert(nextElement,"NEXT Element is not exist")
        nextEventsElements = self.test.ui.get_column_events("event_view", 1)
        if "time_text" in nextEventsElements[0]:
            self.test.appium.tap_element(nextEventsElements[0])
            self.test.screens.linear_action_menu.verify_active()
            self.test.wait(2)
            self.test.screens.linear_action_menu.verify_data()
            self.test.screens.linear_action_menu.dismiss()
            self.test.wait(2)
        #TODO: ask rama - was pointing to a grid event view
        # cell_elements = self.test.ui.get_sorted_events("event_view", 'y_pos', elements)
        # element = cell_elements[0]
        # self.test.appium.tap_center_element(element)
        # self.test.screens.linear_action_menu.verify_active()

    def get_current_screen_section(self):
        element = self.test.milestones.getElement([("title_text", self.test.milestones.get_dic_value_by_key("DIC_GUIDE_NOW", "general").upper(), "==")])
        if element:
            return kGuideScreenSection.PREVIEW
        else:
            return kGuideScreenSection.GRID

    def scrollTo(self, section = kGuideScreenSection.PREVIEW):
        self.test.log("Scrolling to section: " + str(section))
        current_section = self.get_current_screen_section()
        if current_section == section:
            logging.info("Already been in this section" + str(section))
            return

        if section == kGuideScreenSection.PREVIEW:
            self.test.ui.side_bar_swipe("left")
        else:
            self.test.ui.side_bar_swipe("right")

        current_section = self.get_current_screen_section()
        self.test.log_assert(current_section == section, "Was not able to move from section " + str(current_section) + " to section " + str(section))

    def tap_grid_event(self):
        # TODO: add grid in content transition
        self.test.wait(5, True)
        event = self.get_grid_first_event()
        self.test.log_assert(event, "No events in the grid!")
        # element width can be very big, even outside screen so we have to tap near it's x,y
        self.test.appium.tap(int(event['x_pos']) + 24, int(event["y_pos"]) + int(event["height"])/2)
        self.test.screens.linear_action_menu.verify_active()
        self.test.screens.action_menu.dismiss()

    def get_grid_first_event(self):
        channels = self.get_grid_channels()
        fullscreen = self.test.ui.fullscreen_element()

        first = False

        self.test.log_assert(channels, "No grid channels")
        self.test.log("grid channels: \n" + str(channels))
        for channel in channels:
            #tapping on first line might tap on date since event is cutting from top edge
            if not first:
                first = True
                continue

            if channel == None:
                continue
            for event in channel:
                # defend from getting events that are out of the screen, event width might be big
                if event['x_pos'] > fullscreen['width'] - 24:
                    self.test.log("event skipped: " + str(event))
                    continue

                return event
        return None


    def select_first_day(self):
       for i in range(0,3):
           date_elements = self.test.milestones.getElementsArray([("id", "guide_date", "==")])
           date_elements = self.test.ui.get_sorted_elements('text_view', 'x_pos', date_elements)
           second_element = date_elements[1]
           self.test.appium.tap_element(second_element)
           self.test.wait(5)

       first_element = date_elements[0]
       self.test.appium.tap_element(first_element)

    def select_day(self, day_number):
        date_elements = self.test.milestones.getElementsArray([("id", "guide_date", "==")])
        self.test.log_assert(date_elements, "Cannot find date elements")
        selected_date_element = self.test.milestones.getElement([("is_selected", True, "==")], date_elements)
        self.test.log_assert(selected_date_element, "Cannot find selected date element")
        goto_date_element = date_elements[day_number]
        self.test.log_assert(goto_date_element, "Cannot find day number " + str(day_number) + " in day elements: " + str(date_elements))

        if (selected_date_element["title_text"] == goto_date_element["title_text"]):
            return

        self.test.appium.tap_element(goto_date_element)
        self.test.wait(5)

    def get_selected_date(self):
        date_elements = self.test.milestones.getElementsArray([("id","guide_date","==")])
        selected_date_element = self.test.milestones.getElement([("is_selected","True","==")])
        return selected_date_element

    def swipe_in_grid_actions(self):
        self.swipe_in_grid(ScreenActions.LEFT, 3)
        self.swipe_in_grid(ScreenActions.RIGHT,2)

    def swipe_in_grid(self, direction = ScreenActions.LEFT, count = 1):
        direction = self.test.mirror.direction(direction)
        for x in range(count):
            time_elements = self.test.milestones.getElementsArray([("id","guide_time","==")])
            time_elements = self.test.ui.get_sorted_elements('text_view', 'x_pos', time_elements)
            time_element = time_elements[1]
            self.test.appium.swipe_element(time_element, 1000, direction)
            self.test.wait(2)

    #We assume that an hour is selected and visible on screen
    def get_current_selected_hour(self,elements = None):
        if elements is None:
            elements = self.test.milestones.getElements()
        hour_element = self.test.milestones.getElement([("name","guide_date", "=="),("is_selected",True,"==")], elements)
        hour = None
        if hour_element:
            hour = datetime.datetime.strptime(hour_element['hour'],HOUR_VIEW_TIME_FORMAT).hour
        else:
            self.test.log_assert(hour_element,"No selected hour visible")

        return hour

    def navigateToCurrentEventOnChannel(self, channel):
        target_channel_id = channel
        target_channel = None
        abr_channels = self.test.he_utils.abr_services
        for ch in abr_channels:
            if abr_channels[ch]['logicalChannelNumber'] == target_channel_id:
                target_channel = abr_channels[ch]
        self.test.log_assert(target_channel, "Target channel not found!")
        logging.info("Scroll to channel:%s through Guide screen",str(target_channel['logicalChannelNumber']))
        self.navigate()
        self.scroll_to_channel_by_sek(target_channel['serviceEquivalenceKey'])
        current_event = self.CurrentCenteredChannelActionMenu()
        return current_event['title_text']

    def scroll_to_channel_by_sek(self, channel_id):
        ''' tune to channel by channel id  '''
        foundChannel = False
        #Storing the first channel for comparison
        self.storeCurrentChannel()
        print "self.storedChannel[channel_id]: " + self.storedChannel["channel_id"]
        print "int(channel_id): " + channel_id
        if int(self.storedChannel["channel_id"]) > int(channel_id):
            direction = ScreenActions.DOWN
        else:
            direction = ScreenActions.UP

        # setting a limit of channel changes in the channel list
        for channelIndex in range (0, self.maxChannelsToCycle):
            channel_view = self.getCurrentChannel()
            logging.info("channel: " + channel_view['channel_id'])
            if channel_view['channel_id'] == str(channel_id):
                foundChannel = True
                break
            if channelIndex > 0 and cmp(channel_view['channel_id'],self.storedChannel['channel_id']) == 0:
                break
            self.scrollChannelFromCenter(direction)
        self.test.log_assert(foundChannel, 'Could not find the channel: ' + str(channel_id))

    def getCurrentChannel(self):
        elements = self.test.milestones.getElements()
        first_centered_event_view = self.get_centered_channel_view(elements)
        self.test.log_assert(first_centered_event_view, "can't find event view in the center of guide screen")
        return first_centered_event_view

    def storeCurrentChannel(self):
        first_centered_event_view = self.getCurrentChannel()
        #Storing the first channel when entering the screen.
        self.storedChannel = first_centered_event_view

    def isCurrentStoredChannel(self):
        #Compare the current event to the first channel when entered the screen
        first_centered_event_view = self.getCurrentChannel()
        return cmp(first_centered_event_view,self.storedChannel)

    def get_centered_channel_view(self, elements):
        '''getting the current channel in the event grid'''
        if self.test.device_type == DeviceType.TABLET:
            return self.test.ui.get_center_element("event_view", elements)
        else :
            return self.test.ui.get_center_element("cell_view", elements)

    def scrollChannelFromCenter(self,  direction, duration=0):
        #Scrolling in Channel list
        elements = self.test.milestones.getElements()
        first_centered_channel_view = self.get_centered_channel_view(elements)
        self.test.log_assert(first_centered_channel_view, "can't find channel view in the channel list")

        scroll_distance = first_centered_channel_view['height']
        #check if to use parent height - ios!
        if ('parent-height' in first_centered_channel_view) and (first_centered_channel_view['parent-height'] > 0):
            scroll_distance = first_centered_channel_view['parent-height']
        self.test.log("scrolling channel: " + first_centered_channel_view["channel_name"])
        self.test.appium.scroll_from_element(first_centered_channel_view, scroll_distance, direction, duration)

    def CurrentCenteredChannelActionMenu(self):
        '''Find the centered CHANNEL in the channel list and tap ONCE to open Action Menu'''
        elements = self.test.milestones.getElements()
        CurrentCenteredChannel = self.get_centered_channel_view(elements)
        self.test.appium.tap_element(CurrentCenteredChannel)
        self.test.screens.linear_action_menu.verify_active()
        return CurrentCenteredChannel


class KSmartphoneDatesSelection(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "dates_selection_view")


class KSmartphoneGuide(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "guide")

    def navigate(self):
        logging.info("Navigate to guide")

        screen = self.test.milestones.get_current_screen()
        if screen == "guide":
            return
        if not self.test.screens.header.item_exists("DIC_MAIN_HUB_GUIDE"):
            self.test.screens.tv_filter.navigate()
        self.test.screens.header.tap_item("DIC_MAIN_HUB_GUIDE")
        self.verify_active()

    def get_channels(self, elements = None):
        channels = sorted(self.test.milestones.getElementsArray([("id", "channel_logo", "==")], elements), key=operator.itemgetter('x_pos'), reverse=self.test.mirror.is_sort_reverse('x_pos'))
        return channels

    def verifyEpisodeTextExists(self):
        grid_info = self.test.ctap_data_provider.send_request('GRID', None)
        found = 0
        episode_logical_number = None
        Title = None

        for channel in grid_info['channels']:
            if found:
                break;
            logical_number = channel["logicalChannelNumber"]
            channel_events = channel["schedule"]

            for i in range(0, len(channel_events)):
                content = channel_events[i]["content"]

                if "episodeNumber" in content:
                    wrap_logical_number = str(logical_number).zfill(3)
                    Title = content["title"].upper()
                    while (1):
                        events_scroller = self.test.milestones.getElementsArray([("channel_number", wrap_logical_number, "==")])
                        if len(events_scroller):
                            events_scroller = self.test.milestones.getElementsArray(
                                [("channel_number", logical_number, "==")])
                            if len(events_scroller) > 1:
                                self.test.appium.swipe_element(events_scroller[1], events_scroller[1]["height"] * 100, ScreenActions.DOWN)
                            while (1):
                                events_scroller = self.test.milestones.getElementsArray([("channel_number", logical_number, "==")])
                                episode_element = self.test.milestones.getElement([("title_text", Title , "==")], events_scroller)
                                if episode_element != None:
                                    break
                                elif len(events_scroller) <= 1:
                                    break
                                else:
                                    self.test.appium.swipe_element(events_scroller[1], events_scroller[1]["height"] * 2,
                                                                   ScreenActions.UP)

                            self.test.log_assert((("episode_text" in episode_element) and episode_element["episode_text"]), "episode text is missing")
                            return
                        self.test.log_assert(self.scroll_next_channel(),"Failed to find episode event")

    def showAndVerifyActionMenu(self):
        elements = self.test.milestones.getElements()
        cell_elements = self.test.ui.get_sorted_events("event_view", 'y_pos', elements)
        element = cell_elements[0]
        self.test.appium.tap_center_element(element)
        self.test.screens.linear_action_menu.verify_active()

    def actionMenuBookEvent(self, tap_record=False):

        self.showAndVerifyActionMenu()
        elements = self.test.milestones.getElements()
        record_this_event = self.test.milestones.get_dic_value_by_key("DIC_ACTION_MENU_ACTION_RECORD").upper()
        self.test.ui.verify_and_press_button_by_title(record_this_event)
        self.test.wait(2)

    def verifyRecordIcon(self):
        elements = self.test.milestones.getElements()
        cell_elements = self.test.ui.get_sorted_events("event_view", 'y_pos', elements)
        is_record_button = cell_elements[0]['record_button']
        self.test.log_assert(is_record_button == True, "Failed reason: No record button")

    #To be modified once date format returns only the day in the week
    def get_day_str(self,day_number,date_format=DATE_LONG_FORMAT):
        if day_number == 0:
            return self.test.milestones.get_dic_value_by_key("DIC_TODAY").upper()
        if day_number == 1:
            return self.test.milestones.get_dic_value_by_key("DIC_TOMORROW").upper()
        day_date = datetime.date.today() + datetime.timedelta(days=day_number)
        return day_date.strftime(date_format).upper()

    #We assume that an hour is selected and visible on screen
    def get_current_selected_hour(self,elements = None):
        if elements is None:
            elements = self.test.milestones.getElements()
        hour_element = self.test.milestones.getElement([("id","hour_view", "=="),("is_selected",True,"==")], elements)
        hour = None
        if hour_element:
            hourText = hour_element['title_text'].strip()
            hourText = self.test.ui.remove_special_chars(hourText)
            hour = datetime.datetime.strptime(hourText,HOUR_VIEW_TIME_FORMAT).hour
            self.test.log("Converted " + hourText + " to: " + str(hour))
        else:
            self.test.log_assert(hour_element,"No selected hour visible")

        return hour

    #Consider moving this method to a deeper building block
    #Warning:this method assumes en_US locale, maybe we should add (if not exist)a milestone to get the app locale
    def get_current_selected_day(self,elements = None):
        if elements is None:
            elements = self.test.milestones.getElements()
        day_element = self.test.milestones.getElement([("id","guide_date","==")],elements)

        if not day_element:
            return None
        #WARNING:Modify this method,if displayed date is reflecting the weekday only
        if day_element['title_text'] == self.test.milestones.get_dic_value_by_key("DIC_TODAY").upper():
            return 0
        elif day_element['title_text'] == self.test.milestones.get_dic_value_by_key("DIC_TOMORROW").upper():
            return 1
        else:
            #date = datetime.datetime.strptime(day_element['title_text'],DATE_SHORT_FORMAT) #parsing raises exception, opt for brute force approach
            i = 2
            found = False
            while i <= 14:
                date_str = self.get_day_str(day_number=i,date_format=DATE_SHORT_FORMAT).upper()
                if date_str == day_element['title_text']:
                    found = True
                    return i
                i+=1

            self.test.log_assert(found,"Could not retrieve day in focus, day_element:" + day_element['title_text'])
            return -1

    #Check if the events list first cell displayed time is before or equal to selected hour and that second cell time is after that selected hour
    #NOTE: channel number should not be zero padded
    def is_events_list_focus_selected_hour(self,channelnumber,elements=None):
        if elements is None:
            elements = self.test.milestones.getElements()
        selected_hour = self.get_current_selected_hour(elements)
        if selected_hour is None:
            return False
        selected_hour = datetime.time(hour = selected_hour)
        event_cells = self.test.ui.get_sorted_events("event_view", 'y_pos', elements, "channel_number", channelnumber)
        if not event_cells:
            return True
        first_cell = event_cells[0]
        time_text = first_cell['time_text'].strip()
        self.test.log_assert(time_text, "Cannot find time text for channel: " + str(channelnumber))
        first_start_time = self.get_start_time(time_text)
        if first_start_time > selected_hour:
            #Swipe down to check if there are cells above
            self.test.appium.swipe_element(event_cells[0], event_cells[0]["height"],ScreenActions.DOWN)
            elements = self.test.milestones.getElements()
            updated_cells = self.test.ui.get_sorted_events("event_view", 'y_pos', elements, "channel_number",channelnumber)
            return self.get_start_time(updated_cells[0]['time_text']) == first_start_time


        if len(event_cells) == 1:
            return True

        second_start_time = self.get_start_time(event_cells[1]['time_text'])
        return first_start_time<=selected_hour<second_start_time

    def get_start_time(self, time_text):
        time_text = self.test.ui.remove_special_chars(time_text)
        return datetime.datetime.strptime(time_text,EVENT_VIEW_TIME_FORMAT).time()

    def get_hours_array(self):
        hours = ['12 AM','2 AM','4 AM','6 AM','8 AM','10 AM','12 PM','2 PM','4 PM','6 PM','8 PM','10 PM']
        return hours

    def verify_hour_focus(self,elements = None):
        if elements is None:
            elements = self.test.milestones.getElements()
        channels = self.get_channels(elements)
        selected_hour = self.get_current_selected_hour(elements)
        self.test.log_assert(channels,"No channels found on screen")
        for channel_element in channels:
            channel_number = (int)(str(channel_element['channel_number']))
            event_cells = self.test.ui.get_sorted_elements("event_view", 'y_pos', elements, "channel_number",(channel_number))
            if len(event_cells) > 0:
                self.test.log_assert(self.is_events_list_focus_selected_hour(channel_number,elements),"Channel" + str(channel_element['channel_number']) + "events list not focusing around " + str(selected_hour))


    # verify_data checks that desired day, hour in arguments are selected
    # Events list start around the focus hour, the last event is before midnight of the selected day
    # Fast check that number of events displayed is not greater than the returned response from CTAP
    # Check cell by event against HE response is not part of this building block
    def verify_data(self,hour=datetime.datetime.now().hour-datetime.datetime.now().hour%2,start_channel_id=None, day_number=0):
        self.test.log_assert(((hour >= 0) & (hour <= 23) & (hour%2 == 0)),"Invalid hour"+str(hour))

        start_time = datetime.date.today() + datetime.timedelta(days=day_number)
        duration = 86400
        if day_number == 0:
            start_time = datetime.datetime.now()
            #could not find a quicker way to compute time interval between now and today midnight
            duration = 86400 - (start_time.hour * 3600 + start_time.minute*60 + start_time.second)

        server_data = self.test.ctap_data_provider.send_request('GRID', payload={'start_time': start_time,
                                                                                 'duration': str(duration)})
        elements = self.test.milestones.getElements()

        #Retrieve channels logos currently visible on screen
        channels = self.get_channels(elements)
        self.test.log_assert(channels,"No channels found on screen")

        #Verify that channels order is compatible with the HE order

        #check selected hour
        selected_hour = self.get_current_selected_hour(elements)
        self.test.log_assert(hour == selected_hour,"The selected hour: "+ str(selected_hour) + " is different than the desired one: "+str(hour))

        #check selected day
        selected_day = self.get_current_selected_day(elements)
        self.test.log_assert(selected_day == day_number,"The selected day: "+ str(selected_day) + " is different than the desired one: "+str(day_number))

        # Get starting channel id
        if not start_channel_id:
            hhId = self.test.he_utils.get_default_credentials()[0]
            start_channel_id = str(self.test.he_utils.get_last_tuned_channel_for_device(hhId))
            self.test.log_assert(start_channel_id, "Cannot find playing channel")

        if server_data:
            self.test.wait(1, log=False)#wait for guide columns to load("help" exit content transition)
            i = self.test.ctap_data_provider.get_channel_index(start_channel_id, server_data)
            self.test.log("Starting from server channel #" + str(i) + " : " + str(start_channel_id) + " device channels:" + str(self.test.ui.get_property_list(channels, "channel_id")))
            #Match channels
            for channel_element in channels:
                self.test.log_assert(i < server_data['count'], "Channel #" + str(i) + ": " + str(channel_element['channel_number']) + " does not exist in the server data, count: " + str(server_data['count']))
                server_channel = server_data['channels'][i]
                i+=1
                channel_number = (int)(str(channel_element['channel_number']))
                self.test.log_assert(server_channel['logicalChannelNumber'] == channel_number,"Channels order different than HE order, server : " + str(server_channel['logicalChannelNumber']) + " = " + str(server_channel['id']) + " local: " + str(channel_number) + " : " + str(channel_element['channel_name']))
                if len(server_channel['schedule'])>0:
                    logging.info("Found events for channel " + str(channel_element['channel_number']))
                    event_cells = self.test.ui.get_sorted_events("event_view", 'y_pos', elements, "channel_number", channel_number)
                    #Check cells are displayed for this channel
                    self.test.log_assert(len(event_cells) > 0,"No cells are displayed for channel: "+ str(channel_element['channel_number'])+" whereas " + str(len(server_channel['schedule'])) +" events are returned from HE")
                    #Check number of displayed cells is not greater than number of events returned from HE
                    self.test.log_assert((len(event_cells) <= len(server_channel['schedule'])),"More cells (" + str(len(server_channel['schedule'])) + ") are displayed than returned from HE for channel: "+ str(channel_element['channel_number']))
                    #Check cells are respecting the focus hour
                    self.test.log_assert(self.is_events_list_focus_selected_hour(channel_number,elements),"Channel" + str(channel_element['channel_number']) + "events list not focusing around " + str(selected_hour))
                    #TODO:check that cells correspond to real events returned from HE

    def verify_data_cell_on_screen(self):
        events = []
        elements = self.test.milestones.getElements()
        #events = sorted(self.test.milestones.getElementsArray([("event_source","EVENT_SOURCE_TYPE_LINEAR","==")],elements),key=operator.itemgetter('y_pos'))
        events = self.test.milestones.getElementsArray([("event_source", "EVENT_SOURCE_TYPE_LINEAR", "==")], elements)

        dictlist = []
        for i in range(len(events)):
            dictlist.append(events[i])
        for info in events:
            event_id = self.test.ctap_data_provider.get_event_id([info])
            server_data = self.test.ctap_data_provider.server_data_for_event_id(event_id)
            server_title = server_data['content']['title']
            self.test.log_assert(server_title.upper() == info['title_text'],
                             "Title doesn't match ctap")
            serverDate = datetime.datetime.strptime(server_data['startDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if (server_data['content']['duration']) / 60000 > 60 or serverDate <= datetime.datetime.utcnow():
                self.test.log_assert(server_data['content']['media'][0]['url'] == info['event_image_url'],
                                     "image on grid cell doesn't match ctap")



    def select_day(self,day_number):
        elements = self.test.milestones.getElements()
        current_hour = self.get_current_selected_hour(elements)
        date_element = self.test.milestones.getElement([("id","guide_date","==")],elements)
        self.test.appium.tap_element(date_element)
        dates_selection = self.test.screens.KSmartphoneDatesSelection
        dates_selection.verify_active()

        day_string = self.get_day_str(day_number)
        day_element = self.test.milestones.getElement([("title_text",day_string,"==")])
        self.test.log_assert(day_element,"Could not find " + day_string + " option in dates list")
        self.test.appium.tap_element(day_element)
        self.verify_active()
        self.verify_data(hour=current_hour,day_number=day_number)

    def get_current_screen_data(self,elements = None):
        if elements is None:
            elements = self.test.milestones.getElements()

        channels = self.get_channels(elements)
        self.test.log_assert(channels,"No channels found on screen")

        current_hour = self.get_current_selected_hour(elements)
        current_day = self.get_current_selected_day(elements)
        current_channel_id = channels[0]['channel_id']
        next_channel_id = channels[1]['channel_id']
        return { 'hour' : current_hour,
                 'day' : current_day,
                 'channel_id':current_channel_id,
                 'next_channel_id': next_channel_id}


    def scroll_next_channel(self):
        #WARNING: since we are scrolling one channel, it might happen that for some channels that are already displayed,the events list
        #might not be updated
        elements = self.test.milestones.getElements()
        channels = self.get_channels(elements)
        self.test.log_assert(channels,"No channels found on screen")

        current_data = self.get_current_screen_data(elements)

        direction = self.test.mirror.direction(ScreenActions.LEFT)
        self.test.appium.swipe_element(channels[1], channels[1]['x_pos'],direction)
        self.test.wait(0.5,log=False)

        updated_elements = self.test.milestones.getElements()
        channels = self.get_channels(elements)
        if channels[0]['channel_id'] == current_data['channel_id']:#reach end of horizontal list,cannot scroll further
            return False

        self.verify_data(day_number=current_data['day'],hour=current_data['hour'],start_channel_id=current_data['next_channel_id'])
        return True

    def select_next_hour(self):
        elements = self.test.milestones.getElements()
        current_data = self.get_current_screen_data(elements)
        current_hour = current_data['hour']
        if current_hour == 22:
            return False
        next_hour = current_hour + 2
        next_hour_str = self.get_hours_array()[next_hour/2]
        hour_element = self.test.milestones.getElement([("id","hour_view", "=="),("title_text",next_hour_str,"===")], elements)
        self.test.log_assert(hour_element, "Cannot find hour element for '" + next_hour_str + "'")
        if hour_element['is_enabled'] == False:
            return False
        self.test.appium.tap_element(hour_element)
        self.test.wait(0.5,log=False)
        self.test.log_assert(self.get_current_selected_hour()==next_hour,"Wrong hour in focus, current_hour: " + str(self.get_current_selected_hour()) + " next hour: " + str(next_hour))
        self.verify_hour_focus()

        return True


    def select_previous_hour(self):
        elements = self.test.milestones.getElements()
        current_data = self.get_current_screen_data(elements)
        current_hour = current_data['hour']
        if current_hour <= 2:
            return False
        previous_hour = current_hour - 2
        previous_hour_str = self.get_hours_array()[previous_hour/2]
        hour_element = self.test.milestones.getElement([("id","hour_view", "=="),("title_text",previous_hour_str,"===")], elements)
        if hour_element['is_enabled'] == False:
            return False
        self.test.appium.tap_element(hour_element)
        self.test.wait(0.5,log=False)#Wait for the slide animation
        self.test.log_assert(self.get_current_selected_hour()==previous_hour,"Wrong hour in focus, current_hour: " + str(self.get_current_selected_hour()) + " previous hour: " + str(previous_hour))
        self.verify_hour_focus()


        return True


class KSmartphoneChannelsSelection(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "channels_selection_view")

    def navigate(self, guide):
        if self.test.platform == "Android":
            self.test.skip("Channel selection not currently implemented on Android")
        logging.info("Navigate from guide to channels selection")
        channels_element = guide.test.milestones.getElement([("id","CHANNELS","==")], guide.test.milestones.getElements())
        guide.test.appium.tap_element(channels_element)
        self.verify_active()

    def verify_data(self, check_sort=True):
        elements = self.test.milestones.getElements()
        channel_names = self.test.milestones.getElementsArray([("id", "CHANNEL_NAME", "==")], elements)
        for channel_name in channel_names:
            name = channel_name["title_text"]
            section_title = channel_name["SECTION_TITLE"]
            if ord(name[0]) in range(ord('A'), ord('Z') + 1):
                self.test.log_assert(section_title == name[0], "Channel name (" + name + ") should start with " + section_title)
            else:
                self.test.log_assert(section_title == "#", "Channel name (" + name + ") should be under section #")
        if check_sort:
            sorted_channel_by_names = self.test.ui.get_sorted_elements('text_view', 'title_text', channel_names)
            sorted_channels_by_y_pos = self.test.ui.get_sorted_elements('text_view', 'y_pos', channel_names)
            self.test.log_assert(sorted_channel_by_names == sorted_channels_by_y_pos, "Channels are not sorted alphabetically")
