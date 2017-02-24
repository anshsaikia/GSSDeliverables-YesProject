__author__ = 'bwarshaw'

from time import sleep
from operator import itemgetter
from tests_framework.ve_tests.tests_conf import DeviceType
from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.ui_building_blocks.screen import ScreenDismiss

import logging

''' Constants '''
OPEN_TIMELINE_FROM_FULLSCREEN_TIMEOUT = 4
TIMEOUT = 2
TIME_LINE_DISMISS_TIMEOUT = 15


class TimeLine(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "timeline")
        self.timeout = TIME_LINE_DISMISS_TIMEOUT
        self.maxChannelsToCycle = 500

    def navigate(self, swipe_direction=Screen.actionTypes.LEFT):
        logging.info("Navigate to timeline")
        screen = self.test.milestones.get_current_screen()
        if screen == "timeline":
            return

        if self.test.project != "KD" and self.test.app_mode == "V2":
            if screen != 'infolayer':
                self.test.say('need to navigate to info layer')
                self.test.screens.infolayer.show()
            self.test.ui.tap_center_element("timeLine")
            self.test.wait(OPEN_TIMELINE_FROM_FULLSCREEN_TIMEOUT)
            self.verify_active()
            return

        self.test.screens.fullscreen.navigate()
        window_width, window_height = self.test.milestones.getWindowSize()
        y = window_height/2
        left_x = window_width*0.1
        right_x = window_width*0.75

        if swipe_direction == Screen.actionTypes.LEFT:
            self.test.mirror.swipe_area(right_x, y, left_x, y)
        else:
            self.test.mirror.swipe_area(left_x, y, right_x, y)

        self.test.wait(OPEN_TIMELINE_FROM_FULLSCREEN_TIMEOUT)

        self.verify_active()

    def scroll_direction(self, from_channel, to_channel):
        if from_channel and to_channel and from_channel['y_pos'] < to_channel['y_pos']:
            direction = Screen.actionTypes.UP
        else:
            direction = Screen.actionTypes.DOWN
        return direction


    def tune_to_channel_by_sek(self, channel_id, verify_streaming_started=True):
        channel = self.scroll_to_channel_by_sek(channel_id)
        self.test.appium.tap_element(channel)
        if verify_streaming_started:
            self.test.screens.playback.verify_streaming_playing()

    def scroll_to_channel_by_sek(self, channel_id):
        ''' tune to channel by channel id  '''
        channelFound = False
        direction = Screen.actionTypes.DOWN
        for cycleIndex in range(0, self.maxChannelsToCycle):
            elements = self.test.milestones.getElements()
            channels = self.test.ui.get_sorted_elements('event_view', 'y_pos', elements, 'channel_id')
            channel = self.test.ui.get_element_by_value(channels, 'channel_id', str(channel_id))
            if channel:
                current_channel = self.get_current_channel(elements)
                if current_channel and current_channel['channel_id'] == channel['channel_id']:
                    channelFound = True
                    channel = current_channel
                    break
                direction = self.scroll_direction(channel, current_channel)
            self.swipe_channel(direction)
            elements = self.test.milestones.getElements()
        self.test.log_assert(channelFound, "Cannot find channel: " + str(channel_id))
        self.test.log_assert(channel['channel_id'] == channel_id, "Channel %s does not match %s " % (channel['channel_id'], str(channel_id)))
        return channel

    def check_first_element_and_order(self, mainHubSelectedEventView, serverData):

        clientData = self.test.milestones.getElements()

        #Looking for index of current channel
        index = 0
        currentChannelIndex = self.find_current_channel_index_by_eventId(mainHubSelectedEventView['event_id'], serverData)

        horizontalAssetsScroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], clientData)
        horizontalChannelItems = self.test.milestones.getElementInBorders(clientData, horizontalAssetsScroller)
        #Filtering empty and vertical items
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)

        "Checking items increasing timewise"
        currentChannelAssets = serverData['channels'][currentChannelIndex]['schedule']
        prevAssetId = horizontalChannelItems[ 0 ]['event_id']
        prevAsset = self.test.milestones.getElement([("id", prevAssetId, "==")], currentChannelAssets)
        self.test.log_assert(prevAsset, "Can't find asset in horizontal scroller")
        prevViewAsset = horizontalChannelItems[ 0 ]
        for view in horizontalChannelItems:
            if view['event_id'] == prevAsset['id'] or view['event_id'] == u'null':
                continue
            asset = self.test.milestones.getElement([("id", view['event_id'], "==")], serverData['channels'][currentChannelIndex]['schedule'])
            self.test.wait(2)
            self.test.log_assert( asset, "no asset in items")

            if asset['startTime'] > prevAsset['startTime']:
                self.test.log_assert(view['x_pos'] > prevViewAsset['x_pos'])
            else:
                self.test.log_assert(view['x_pos'] < prevViewAsset['x_pos'])
            prevAsset = asset
            prevViewAsset = view

    def get_current_channel(self, elements):
        current_channel = None
        horizontalAssetsScroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)
        if len(horizontalChannelItems) > 0:
            current_channel = horizontalChannelItems[0]
        return current_channel

    def swipe_channel(self, swipe_direction):
        window_width, window_height = self.test.milestones.getWindowSize()
        if swipe_direction == Screen.actionTypes.UP:
            self.test.mirror.swipe_area(window_width / 2, window_height / 4, window_width / 2, window_height / 4 * 3, 0)
        elif swipe_direction == Screen.actionTypes.DOWN:
            self.test.mirror.swipe_area(window_width / 2, window_height / 10 * 8, window_width / 2, window_height / 10 , 0)

    def swipe_and_verify_channel(self, horizontalAssetsScroller, serverData, channelIndex, swipe_direction):
        self.swipe_channel(swipe_direction)

        elements = self.test.milestones.getElements()
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)
        serverChannelEventId = serverData['channels'][channelIndex]['schedule'][0]['id']
        eventId = horizontalChannelItems[0]['event_id']
        self.test.log_assert(serverChannelEventId == eventId, "Wrong current event " + str(eventId) + " on channel " + str(channelIndex) + " compared with server event " + str(serverChannelEventId))


    def check_swipe_global_area(self, serverData):
        elements = self.test.milestones.getElements()

        horizontalAssetsScroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        #Filtering empty and vertical items
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)
        currentChannelIndex = self.find_current_channel_index_by_eventId(horizontalChannelItems[0]['event_id'], serverData)

        "Swipe up/down on clean area changes to next/previous channel"

        self.swipe_and_verify_channel(horizontalAssetsScroller, serverData, currentChannelIndex + 1, Screen.actionTypes.DOWN)
        self.swipe_and_verify_channel(horizontalAssetsScroller, serverData, currentChannelIndex + 2, Screen.actionTypes.DOWN)
        self.swipe_and_verify_channel(horizontalAssetsScroller, serverData, currentChannelIndex + 1, Screen.actionTypes.UP)

    def check_open_action_menu_not_current_channel(self, serverData):
        "Open ActionMenu when tapping on non-current event on any channel"
        elements = self.test.milestones.getElements()
        horizontalAssetsScroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        #Filtering empty and vertical items
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)
        #Not current channel
        self.test.appium.tap(horizontalChannelItems[1]["x_pos"] + horizontalChannelItems[1]["width"] / 2 , horizontalChannelItems[1]["y_pos"] + horizontalChannelItems[1]["height"] / 2)
        sleep(TIMEOUT)

        self.test.screens.linear_action_menu.verify_active()

        #Back to timeline screen
        self.test.screens.timeline.navigate()

    def check_tap_other_channel_align(self, serverData):

        "Tap on other channel aligns it to the channel list"

        elements = self.test.milestones.getElements()
        lowerScroller = self.test.milestones.getElement([("id", "ChannelScrollerLower", "==")], elements)
        self.test.log_assert(lowerScroller, "no ChannelScrollerLower")

        horizontalAssetsScroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        #Filtering empty and vertical items
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)
        currentChannelIndex = self.find_current_channel_index_by_eventId(horizontalChannelItems[0]['event_id'], serverData)

        lowerScrollerViews = self.test.milestones.getElementInBorders(elements, lowerScroller)
        self.test.log_assert(len(lowerScrollerViews) > 0, "len(lowerScrollerViews) %d"%len(lowerScrollerViews))

        self.test.appium.tap(lowerScrollerViews[1]["x_pos"] + lowerScrollerViews[1]["width"] / 2 , lowerScrollerViews[1]["y_pos"] + lowerScrollerViews[1]["height"] / 2)
        sleep(0.5)

        elements = self.test.milestones.getElements()
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)

        channelIndexDelta = 2
        self.test.log_assert(serverData['channels'][currentChannelIndex + channelIndexDelta]['schedule'][0]['id'] == horizontalChannelItems[0]['event_id'])

    def check_scroll_channel_area(self, serverData):
        elements = self.test.milestones.getElements()
        horizontalAssetsScroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        #Filtering empty and vertical items
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)
        currentChannelIndex = self.find_current_channel_index_by_eventId(horizontalChannelItems[0]['event_id'], serverData)
        self.test.log("CurrentChannelIndex: " + str(currentChannelIndex))
        self.test.log("FullContentScroller: " + str(horizontalAssetsScroller))

        channelScrollerUpper = self.test.milestones.getElement([("id", "ChannelScrollerUpper", "==")], elements)
        upperScrollerViews = self.test.milestones.getElementInBorders(elements, channelScrollerUpper)
        self.test.log("ChannelScrollerUpper: " + str(channelScrollerUpper))

        channelsToScroll = maxChannelsToScroll = channelsLeftToScroll = 4
        upperScrollerViewsCount = len(upperScrollerViews)
        self.test.log("UpperScrollerViews count: " + str(upperScrollerViewsCount) + " content:" + str(upperScrollerViews))

        '''Scroll visible views untill maximum channels to scroll reached'''
        while channelsLeftToScroll > 0:
            if upperScrollerViewsCount < channelsToScroll:
                channelsToScroll = upperScrollerViewsCount
            if channelsToScroll > channelsLeftToScroll:
                channelsToScroll = channelsLeftToScroll
            channelsLeftToScroll -= channelsToScroll
            self.test.log("Scrolling " + str(channelsToScroll) + " channels, channels left: " + str(channelsLeftToScroll))

            "Scroll in channels area"
            #check if to use parent height
            event_view = upperScrollerViews[ 0 ]
            scroll_distance = event_view['height'] * channelsToScroll
            if ('parent-height' in event_view) and (event_view['parent-height'] > 0):
                scroll_distance = event_view['parent-height'] * channelsToScroll
                self.test.log("scroll distance (using parent): " + str(scroll_distance))
            else:
                self.test.log("scroll distance: " + str(scroll_distance))
            self.test.appium.swipe_area(channelScrollerUpper["x_pos"] + channelScrollerUpper["width"] / 2, channelScrollerUpper["y_pos"] + scroll_distance, channelScrollerUpper["x_pos"] + channelScrollerUpper["width"] / 2, channelScrollerUpper["y_pos"])
        self.test.wait(3)

        elements = self.test.milestones.getElements()
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)

        currentRowIndex = (currentChannelIndex + maxChannelsToScroll) % len(serverData['channels'])

        eventId = horizontalChannelItems[0]['event_id']
        channelId = horizontalChannelItems[0]['channel_id']
        self.compare_item_id(serverData, currentRowIndex, channelId, eventId)

        self.test.wait(2)

    def compare_item_id(self, serverData, index, channelId, eventId):
        serverEventId = serverData['channels'][index]['schedule'][0]['id']
        serverChannelId = serverData['channels'][index]['logicalChannelNumber']
        row = serverEventId == eventId
        self.test.log_assert(row, "Row " + str(index) + " does not match, server: " + str(serverChannelId) + "/" + str(serverEventId) + " client: " + str(channelId) + "/" + str(eventId))

    def tap_on_element(self, event):
        elements = self.test.milestones.getElements()
        horizontalAssetsScroller = self.test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
        horizontalChannelItems = self.test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
        horizontalChannelItems = self.filterViewsResult(horizontalChannelItems)
        self.test.appium.tap(event ["x_pos"] + event ["width"] / 2 ,event ["y_pos"] + event ["height"] / 2)

    def filterViewsResult(self, views):
        filterResult = list()
        for view in views:
             if "title_text" in view and view['title_text'] != None and "channel_name" in view and view['channel_name'] != 'null':
                 filterResult.append(view)
        filterResult = sorted(filterResult, key=itemgetter('x_pos'))

        return filterResult

    def find_current_channel_index_by_eventId(self, eventId, serverData):
        #Looking for index of current channel
        index = 0
        currentChannelIndex = -1
        for channel in serverData['channels']:
            if 'schedule' in channel and channel['schedule'][ 0 ]['id'] == eventId:
                currentChannelIndex = index
                break
            index += 1
        self.test.log_assert(currentChannelIndex != -1, "Can't find current channel index")
        return currentChannelIndex

    def find_channel_index_by_channelId(self, channelId, serverData):
        # Looking for index of channel
        index = 0
        channelIndex = -1
        for channel in serverData['channels']:
            if channel['id'] == channelId:
                channelIndex = index
                break
            index += 1
        self.test.log_assert(channelIndex != -1, "Can't find channel index")
        return channelIndex

    def find_next_channel_index(self, current_channel_index, server_data):
        if current_channel_index == server_data["count"] - 1:
            return 0
        else:
            return current_channel_index+1

    def find_prev_channel_index(self, current_channel_index, server_data):
        if current_channel_index == 0:
            return server_data["count"]-1
        else:
            return current_channel_index-1

    def find_next_channel_id(self, current_channel_id, server_data):
        current_channel_index = self.find_channel_index_by_channelId(current_channel_id, server_data)
        next_channel_index = self.find_next_channel_index(current_channel_index, server_data)
        return server_data["channels"][next_channel_index]["id"]

    def find_prev_channel_id(self, current_channel_id, server_data):
        current_channel_index = self.find_channel_index_by_channelId(current_channel_id, server_data)
        prev_channel_index = self.find_prev_channel_index(current_channel_index, server_data)
        return server_data["channels"][prev_channel_index]["id"]

    def side_bar_tap(self):
        elements = self.test.milestones.getElements()
        up_arrow = self.test.milestones.getElement([("id", "upImageView", "==")], elements)
        down_arrow = self.test.milestones.getElement([("id", "downImageView", "==")], elements)
        self.test.log_assert(up_arrow, "Cannot find up arrow")
        self.test.log_assert(down_arrow, "Cannot find down arrow")
        top = (int(down_arrow['y_pos']) - int(up_arrow['y_pos'])) / 2

        left = self.test.mirror.bar(up_arrow['x_pos'], 2)

        element = {
            "name" : "side bar tap",
            "x_pos": left,
            "y_pos": top,
            "width": 0,
            "height": 0
        }

        self.test.appium.tap_element(element)

    "dismiss can occur by tap on video or after timeout or after tap on exit button or after tap on more info button"
    def dismiss(self, action = ScreenDismiss.TAP):
        self.test.log_assert(action in [ScreenDismiss.TAP, ScreenDismiss.TIMEOUT, ScreenDismiss.CLOSE_BUTTON, ScreenDismiss.BACK_BUTTON, ScreenDismiss.TAP_ON_EVENT], "Unknown action  %s in dismiss timeline" % action)
        logging.info("Dismiss timeline by %s" % action.value)

        if action == ScreenDismiss.TAP:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                self.side_bar_tap()
                self.test.screens.infolayer.verify_active()
                self.test.screens.infolayer.dismiss(action = self.test.screens.infolayer.dismissTypes.TAP)
            else:
                self.tap_background()
                self.test.screens.fullscreen.verify_active()
            return
        if action == ScreenDismiss.CLOSE_BUTTON:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                self.test.ui.tap_element("exit")
                self.test.screens.infolayer.verify_active()
            return
        if action == ScreenDismiss.BACK_BUTTON:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                self.test.ui.tap_element("back")
                self.test.screens.linear_action_menu.verify_active()
            return
        if action == ScreenDismiss.TAP_ON_EVENT:
            if self.test.project != "KD" and self.test.app_mode == "V2":
                event = self.test.milestones.getElement([("name", "event_view", "==")])
                self.test.appium.tap_element(event)
                self.test.screens.linear_action_menu.verify_active()
            return
        elif action == ScreenDismiss.TIMEOUT:
            for i in range(1, self.timeout):
                sleep(1)
                screen = self.test.milestones.get_current_screen()
                if screen != 'timeline':
                    break
            self.test.log_assert(screen!='timeline', "Timeline not dismiss after timeout (%d seconds)" % self.timeout)
            self.test.log_assert(screen=='fullscreen', "Not switching to fullscreen after timeline dismiss. screen=%s "% screen)
            return

    def tap_background(self):
        window_width, window_height = self.test.milestones.getWindowSize()

        screen = self.test.milestones.get_current_screen()
        if screen != "timeline":
            logging.warn("Not in timeline screen. screen=%s" % screen)
            return

        logging.info("Tapping timeline background")
        self.test.appium.tap(window_width / 2 , window_height / 3)

    def compare_events_metadata(self, server_data, elements, focused_channel_id, is_current):
        focused_channel_index = self.find_channel_index_by_channelId(focused_channel_id, server_data)
        if is_current:
            first_event_index = 1
        else:
            first_event_index = 0
        first_event_data = server_data["channels"][focused_channel_index]["schedule"][first_event_index]
        second_event_data = server_data["channels"][focused_channel_index]["schedule"][first_event_index+1]
        first_event_view = self.test.milestones.getElement([("event_id", first_event_data["id"], "==")], elements)
        second_event_view = self.test.milestones.getElement([("event_id", second_event_data["id"], "==")], elements)
        self.test.ctap_data_provider.compare_event_metadata(first_event_view, server_data["channels"][focused_channel_index], first_event_index, False)
        self.test.ctap_data_provider.compare_event_metadata(second_event_view, server_data["channels"][focused_channel_index], first_event_index+1, False)

    def compare_channels_logos(self, server_data, elements, focused_channel_id):
        focused_channel_index = self.find_channel_index_by_channelId(focused_channel_id, server_data)
        channels_panel = self.test.milestones.getElement([("name", "channels_panel", "==")], elements)
        channels_urls = [channels_panel["upper_channel_logo_url"], channels_panel["focused_channel_logo_url"], channels_panel["lower_channel_logo_url"]]
        upper_channel_index = self.find_prev_channel_index(focused_channel_index, server_data)
        lower_channel_index = self.find_next_channel_index(focused_channel_index, server_data)
        indexes = [upper_channel_index, focused_channel_index, lower_channel_index]
        j = 0
        for i in indexes:
            ctap_channel_logo = None
            channel = server_data["channels"][i]
            if 'media' not in channel and ctap_channel_logo == None:
                j += 1
                continue
            self.test.log_assert('media' in channel, "Cannot find media in ctap channel " + str(i) + " where image should have been " + str(ctap_channel_logo))
            media = channel['media']
            for logo in media:
                if logo['type'] == "regular" and 'url' in logo:
                    ctap_channel_logo = logo['url']
            self.test.log_assert(channels_urls[j] == ctap_channel_logo, "Channel logo (%s) doesn't match ctap channel logo (%s)"%(channels_urls[j],ctap_channel_logo))
            j += 1
