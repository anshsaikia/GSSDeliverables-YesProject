from tests_framework.ve_tests.tests_conf import DeviceType

__author__ = 'dpedro'

from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.KD.main_hub import Showcases
import logging
from tests_framework.ui_building_blocks.screen import ScreenActions
import re

'''Constants'''
OPEN_GUIDE_TIMEOUT = 3


class Guide(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "guide")
        self.maxChannelsToCycle = 500

    def navigate(self):
        logging.info("Navigate to guide")

        screen = self.test.milestones.get_current_screen()
        if screen == "guide":
            return

        if self.test.project != "KD":
            if self.test.app_mode == "V2":
                if not self.test.screens.header.item_exists("DIC_MAIN_HUB_GUIDE"):
                    self.test.screens.tv_filter.navigate()
                self.test.screens.header.tap_item("DIC_MAIN_HUB_GUIDE")
            else:
                self.test.screens.main_hub.navigate()
                Television_dic = self.test.milestones.get_dic_value_by_key("DIC_MAIN_HUB_TV", "general")
                Television_button = self.test.milestones.getElementContains(self.test.milestones.getElements(), Television_dic)
                self.test.appium.tap_element(Television_button)
                Guide_dic = self.test.milestones.get_dic_value_by_key("DIC_GUIDE_GUIDE", "general")
                Guide_button = self.test.milestones.getElement([("title_text", Guide_dic.upper(), "==")])
                self.test.appium.tap_element(Guide_button)
        else:
            self.test.screens.main_hub.navigate()
            live_dic_value = self.test.milestones.get_dic_value_by_key("DIC_MAIN_HUB_PROGRAM","general")
            Live_button = self.test.milestones.getElement([("regular_text", live_dic_value, "==")])
            self.test.log_assert(Live_button, "Failed selecting LIVE panel")

            self.test.appium.tap_element(Live_button)
        self.verify_active()

    def tune_to_channel_by_sek(self, channel_id, verify_streaming_started=True):
        channel_view = self.scroll_to_channel_by_sek(channel_id)
        self.playCurrentCenteredChannel(verify_streaming_started)

    def scroll_to_channel_by_sek(self, channel_id):
        ''' tune to channel by channel id  '''
        foundChannel = False
        #Storing the first channel for comparison
        self.storeCurrentChannel()
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

    def scroll_to_event(self, event_id, channel_id):
        self.scroll_to_channel_by_sek(channel_id)
        logging.info("event_id: %s channel_id: %s" % (event_id, channel_id))
        window_width, window_height = self.test.milestones.getWindowSize()
        y = window_height / 2
        left_x = window_width / 1.5
        right_x = window_width / 4

        self.test.wait(5) #Make sure all events information refreshed
        elements = self.test.milestones.getElements()
        event = self.test.milestones.getElement([("event_id", event_id, "==")], elements)
        while event == None:
            logging.info("swiping left")
            self.test.mirror.swipe_area(int(left_x), y, right_x, y, 1000)
            self.test.wait(5)
            elements_after_swiping = self.test.milestones.getElements()
            if elements == elements_after_swiping:
                logging.info("Reached end")
                break
            else:
                elements = elements_after_swiping
            event = self.test.milestones.getElement([("event_id", event_id, "==")], elements)

        self.test.log_assert(event,"event_id '%s' not Found in Grid" % event_id)
        return event

    def tap_event(self, event_id, channel_id):
        event = self.scroll_to_event(event_id, channel_id)
        self.test.appium.tap_element(event)
        self.test.wait(2)

    def get_centered_channel_view(self, elements):
        '''getting the current channel in the event grid'''
        if self.test.device_type == DeviceType.TABLET:
            return self.test.ui.get_center_element("event_view", elements)
        else :
            return self.test.ui.get_center_element("cell_view", elements)

    def get_centered_current_event_view(self, elements):
        '''getting the current event in the event grid'''
        cell_elements = self.test.ui.get_center_elements("cell_view", elements)
        for cell in cell_elements:
            if cell["is_current"] == False:
                continue
            self.test.log("found event: " + str(cell))
            return cell
        self.test.log_assert(False, "Cannot get the current event in the grid")



    def getCurrentTime(self, elements):
        '''Getting the current time in the Top Left of the Guide screen'''

        timeView = self.test.milestones.getElement([("id", "now","==" )],elements)
        self.test.log_assert(timeView, "No time at the top left corner of the screen")
        self.test.log("found time: " + str(timeView))
        return timeView

    def getEndTime(self, elements):
        '''Getting the end time time in the Top Right of the Guide screen detailing the end of the DISPLAYED time of the current shown events in the GRID'''
        for element in elements:
            if "end_time" in element:
                end_time = element["end_time"]
                self.test.log("end_time: " + str(end_time))
                results = re.compile('\d{2}:\d{2}').split(end_time)
                self.test.log_assert(results, "Cannot parse " + str(end_time))
                hourMin = results[1]
                self.test.log("found time: " + str(hourMin))
                self.test.log_assert(hourMin, "Invalid time: " + str(end_time))
                return hourMin
        self.test.log_assert(False, "No end time at the top Right corner of the screen")

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

    def scrollEventFromCenter(self,  direction, duration=0):
        #Scrolling in Event grid
        elements = self.test.milestones.getElements()
        first_centered_event_view = self.get_centered_current_event_view(elements)
        self.test.log_assert(first_centered_event_view, "can't find the centered event in the event grid")
        scroll_distance = first_centered_event_view["width"]
        self.test.appium.swipe_element(first_centered_event_view, scroll_distance, direction, duration)

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

    def checkCyclicChannelList(self, direction):
        '''Scroll through the channel list and compare the first event to make sure the list is cyclic'''
        foundChannel = False
        #Storing the first channel for comparison
        self.storeCurrentChannel()
        #setting a limit of channel changes in the channel list
        for channelIndex in range (0, self.maxChannelsToCycle):
            self.scrollChannelFromCenter(direction)
            if self.isCurrentStoredChannel():
                foundChannel = True
                return
        self.test.log_assert(foundChannel, 'Could not find the first channel')


    def checkCyclicEventList(self, direction):
        '''Scroll through the event list and compare the first event to make sure the list is cyclic'''
        foundChannel = False
        #Storing the first channel for comparison
        self.storeCurrentChannel()
        #setting a limit of channel changes in the channel list
        for channelIndex in range (0, self.maxChannelsToCycle):
            self.scrollEventFromCenter(direction)
            if self.isCurrentStoredChannel():
                foundChannel = True
                return
        self.test.log_assert(foundChannel, 'Could not find the first channel')


    def playCurrentCenteredEvent(self):
        '''Find the centered EVENT in the channel list and tap twice to play with verification of the playback status'''
        elements = self.test.milestones.getElements(update=True)
        CurrentCenteredEvent = self.get_centered_current_event_view(elements)
        #Shorten width because of overlapping events
        CurrentCenteredEvent["width"] = 2
        self.test.appium.double_tap_element(CurrentCenteredEvent)
        self.test.wait(3)
        state = self.test.milestones.getPlaybackStatus("playbackState")
        self.test.log_assert(state == "PLAYING", "Failed playing the Event from the EVENT list! playback state:" + state)

    def playCurrentCenteredChannel(self, verify_streaming_started=True):
        '''Find the centered CHANNEL in the event list and tap twice to play with verification of the playback status'''
        elements = self.test.milestones.getElements(update=True)
        CurrentCenteredChannel = self.get_centered_channel_view(elements)
        self.test.appium.double_tap_element(CurrentCenteredChannel)
        if verify_streaming_started:
            self.test.screens.playback.verify_streaming_playing()

    def CurrentCenteredChannelActionMenu(self):
        '''Find the centered CHANNEL in the channel list and tap ONCE to open Action Menu'''
        elements = self.test.milestones.getElements()
        CurrentCenteredChannel = self.get_centered_channel_view(elements)
        self.test.appium.tap_element(CurrentCenteredChannel)
        self.test.screens.linear_action_menu.verify_active()
        return CurrentCenteredChannel

    def showAndVerifyActionMenu(self):
        elements = self.test.milestones.getElements(update=True)
        cell_elements = self.test.milestones.getElementsArray([("name", "cell_view", "==")],elements)

        '''Find first not current event'''
        not_current_event = None
        for element in cell_elements:
            if element['is_current'] == False:
                not_current_event = element
                break

        #Shorten width because of overlapping events
        not_current_event["width"] = 2
        self.test.appium.tap_element(not_current_event)
        self.test.screens.linear_action_menu.verify_active()

    def isDatesVisible(self, elements=None):
        '''Getting the current header state to see whether it's in time\hours or in days'''
        if(elements == None):
            elements = self.test.milestones.getElements()

        for i in range(0, len(elements)):
            element = elements[ i ]
            if 'name' in element and element['name'] == 'text_view' and element['id'] == u'DATE':
                del elements[ i ]
                break

        headerCurrentView = self.test.milestones.getElement([("id", "date_","(_" )],elements)
        if headerCurrentView:
            return True
        else:
            return False

    def getDayView(self, index, elements):
        '''retrieve day view'''
        dayView = self.test.milestones.getElement([("id", "day_"+ str(index),"==" )], elements)
        self.test.log_assert(dayView, "Can't find the %d day in the header, days %s" %(index, str(self.getDisplayedDays(elements))))
        return dayView

    def scrollDay(self, fromDayIndex, toDayIndex, duration=0):
        '''scrolling in the header to a specific day'''
        elements = self.test.milestones.getElements()
        fromDayView = self.getDayView(fromDayIndex, elements)
        toDayView = self.getDayView(toDayIndex, elements)
        if fromDayIndex == toDayIndex:
            return
        elementToSwipe = None
        distance = 0
        if fromDayIndex < toDayIndex:
            elementToSwipe = toDayView
            distance = toDayView["x_pos"] - fromDayView["x_pos"]
            direction = ScreenActions.LEFT
        else:
            elementToSwipe = fromDayView
            distance = fromDayView["x_pos"] - toDayView["x_pos"]
            direction = ScreenActions.RIGHT
        self.test.appium.swipe_element(elementToSwipe,distance, direction, duration)


    def switchToDayView(self):
        elements = self.test.milestones.getElements()
        '''Switching the current header state to days by tapping on the TODAY button'''
        if self.isDatesVisible(elements) == False:
            todayView = self.test.milestones.getElement([("id", "currentDay","==" )],elements)
            self.test.log_assert(todayView, "Failed switching to date view in the header, cannot find the TODAY button!")
            self.test.appium.tap_element(todayView)

    def storeCurrentTime(self):
        #Storing the current time when entering the screen.
        elements = self.test.milestones.getElements()
        current_time = self.getCurrentTime(elements)
        self.test.log_assert(current_time, "can't find the time in the top left of guide screen")
        self.storedTime = current_time

    def getDisplayedDays(self, elements):
        days = self.test.milestones.getElementsArray([("id", "day_","_)" )],elements)
        return days

    def jumpToDay(self, day):
        '''Switch to day view and scroll in the header to a specified day'''
        self.switchToDayView()
        elements = self.test.milestones.getElements()
        todayView = self.test.milestones.getElement([("id", "currentDay","==" )],elements)
        for dayIndex in range(0, day-1):
            self.scrollDay(dayIndex, dayIndex+1)
        elements = self.test.milestones.getElements()
        selectedDayView = self.test.milestones.getElement([("id", "day_"+ str(day-1),"==" )],elements)
        self.test.log_assert(selectedDayView, "Failed to scroll to the correct day %s in the header %s" % (str(day), str(self.getDisplayedDays(elements))))
        self.test.appium.tap_element(selectedDayView)
        elements = self.test.milestones.getElements()
        todayView = self.test.milestones.getElement([("id", "currentDay","==" )],elements)
        self.test.log_assert(todayView, "Cannot find the TODAY button!")
        self.test.log_assert(todayView["title_text"] == selectedDayView["title_text"] , "Failed to selected the desired day in the header!, todayView %s selectedDayView %s" % (todayView, selectedDayView))


    def scrollEventsToEnd(self,direction=ScreenActions.RIGHT, duration=0):
        '''Scroll in the grid to the last events'''
        foundTime = False
        for channelIndex in range (0, self.maxChannelsToCycle):
            self.scrollEventFromCenter(direction)
            elements = self.test.milestones.getElements()
            if self.getEndTime(elements) != "00:00":
                foundTime = True
                break
            self.test.log_assert(foundTime, 'Could not find the End time of 00:00 at the top right corner of the Header')

    def checkAllEventsAreNotCurrent(self):
         elements = self.test.milestones.getElements()
         cell_elements = self.test.milestones.getElementsArray([("name", "cell_view", "==")],elements)
         for element in cell_elements:
             if element['is_current'] == True:
                 return False
         return True

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