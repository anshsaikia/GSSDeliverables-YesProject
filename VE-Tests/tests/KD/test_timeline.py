__author__ = 'isinitsi'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

from tests_framework.ve_tests.tests_conf import DeviceType
from vgw_test_utils.IHmarks import IHmark

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
@pytest.mark.regression
def test_first_element_and_order():
    ve_test = VeTestApi("timeline:test_check_first_element_and_order")
    ve_test.begin()

    server_data = ve_test.ctap_data_provider.send_request('GRID', payload={'duration':'50000'})

    ve_test.screens.timeline.navigate()
    elements = ve_test.milestones.getElements()
    tuned_linear_event, channel_prop = ve_test.he_utils.getLinearContentABR('clear')
    ve_test.screens.zaplist.tune_to_channel_by_sek(tuned_linear_event, verify_streaming_started =False)
    playback_channel = ve_test.screens.playback.get_playback_status();

    #Looking for index of current channel
    ve_test.log_assert(playback_channel, "Cannot find playback channel")
    currentChannelIndex = ve_test.screens.timeline.find_current_channel_index_by_eventId(playback_channel['currentEventId'], server_data)

    ve_test.log_assert(currentChannelIndex > -1, "Can't find current channel index")
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems =  ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    #Filtering empty and vertical items
    horizontalChannelItems = ve_test.screens.timeline.filterViewsResult(horizontalChannelItems)

    "Checking items increasing timewise"
    currentChannelAssets = server_data['channels'][currentChannelIndex]['schedule']
    prevAssetId = horizontalChannelItems[0]['event_id']
    prevAsset = ve_test.milestones.getElement([("id", prevAssetId, "==")], currentChannelAssets)
    ve_test.log_assert(prevAsset, "Can't find asset in horizontal scroller")
    prevViewAsset = horizontalChannelItems[ 0 ]
    for view in horizontalChannelItems:
        if view['event_id'] == prevAsset['id'] or view['event_id'] == u'null':
            continue
        asset = ve_test.milestones.getElement([("id", view['event_id'], "==")], server_data['channels'][currentChannelIndex]['schedule'])
        ve_test.wait(2)
        ve_test.log_assert( asset, "no asset in items")
        if asset['startDateTime'] > prevAsset['startDateTime']:
            ve_test.log_assert(view['x_pos'] > prevViewAsset['x_pos'])
        else:
            ve_test.log_assert(view['x_pos'] < prevViewAsset['x_pos'])
        prevAsset = asset
        prevViewAsset = view

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
def test_swipe_global_area():
    ve_test = VeTestApi("timeline:test_swipe_global_area")
    ve_test.begin()
    server_data = ve_test.ctap_data_provider.send_request('GRID', payload={'duration':'50000'})

    ve_test.screens.timeline.navigate()
    ve_test.screens.timeline.check_swipe_global_area(server_data)

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
@pytest.mark.commit
@pytest.mark.ios_regression
def test_open_action_menu_not_current_event():
    ve_test = VeTestApi("timeline:test_open_action_menu_not_current_channel")
    ve_test.begin()
    ve_test.screens.timeline.navigate()

    "Open ActionMenu when tapping on non-current event on any channel"
    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    #Filtering empty and vertical items
    horizontalChannelItems = ve_test.screens.timeline.filterViewsResult(horizontalChannelItems)
    #Not current channel
    ve_test.log_assert(horizontalChannelItems, "Cannot find items in timeline")
    ve_test.log_assert(len(horizontalChannelItems) >= 2, "not enough items in timeline, expected 2, actual %d" % len(horizontalChannelItems))
    ve_test.appium.tap_element(horizontalChannelItems[1])
    ve_test.screens.linear_action_menu.verify_active()

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
def test_tap_other_channel_align():

    ve_test = VeTestApi("timeline:check_tap_other_channel_align")
    ve_test.begin()

    device_type = ve_test.device_type
    server_data = ve_test.ctap_data_provider.send_request('GRID', payload={'duration':'50000'})

    ve_test.screens.timeline.navigate()

    "Tap on other channel aligns it to the channel list"
    elements = ve_test.milestones.getElements()
    lowerScroller = ve_test.milestones.getElement([("id", "ChannelScrollerLower", "==")], elements)
    ve_test.log_assert(lowerScroller, "no ChannelScrollerLower")

    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    #Filtering empty and vertical items
    horizontalChannelItems = ve_test.screens.timeline.filterViewsResult(horizontalChannelItems)
    currentChannelIndex = ve_test.screens.timeline.find_current_channel_index_by_eventId(horizontalChannelItems[0]['event_id'], server_data)
    ve_test.log_assert(currentChannelIndex > -1, "Can't find current channel index")

    lowerScrollerViews = ve_test.milestones.getElementInBorders(elements, lowerScroller)
    ve_test.log_assert(len(lowerScrollerViews) > 0, "len(lowerScrollerViews) %d"%len(lowerScrollerViews))
    if device_type == DeviceType.TABLET :
     ve_test.appium.tap(lowerScrollerViews[1]["x_pos"] + lowerScrollerViews[1]["width"] / 2 , lowerScrollerViews[1]["y_pos"] + lowerScrollerViews[1]["height"] / 2)
    else:
        ve_test.appium.tap(lowerScrollerViews[0]["x_pos"] + lowerScrollerViews[0]["width"] / 2 , lowerScrollerViews[0]["y_pos"] + lowerScrollerViews[0]["height"] / 2)

    ve_test.wait(2.5)

    elements = ve_test.milestones.getElements()
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    horizontalChannelItems = ve_test.screens.timeline.filterViewsResult(horizontalChannelItems)

    if device_type == DeviceType.TABLET :
        channelIndexDelta = 2
    else:
        channelIndexDelta = 1
    ve_test.log_assert(server_data['channels'][currentChannelIndex + channelIndexDelta]['schedule'][0]['id'] == horizontalChannelItems[0]['event_id'])

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
def test_tap_item_not_current_channel():
    ve_test = VeTestApi("timeline:test_tap_item_not_current_channel")
    ve_test.begin()

    ve_test.screens.timeline.navigate()
    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    #Filtering empty and vertical items
    horizontalChannelItems = ve_test.screens.timeline.filterViewsResult(horizontalChannelItems)
    ve_test.appium.tap(horizontalChannelItems[1]["x_pos"] + horizontalChannelItems[1]["width"] / 2 ,horizontalChannelItems[1]["y_pos"] + horizontalChannelItems[1]["height"] / 2)
    ve_test.wait(2)

    elements = ve_test.milestones.getElements()
    ve_test.log_assert(ve_test.milestones.getElement([("screen", "action_menu", "==")], elements) or ve_test.milestones.getElement([("screen", "KDActionMenuPane", "==")], elements) , "no action_menu")
    #Back to timeline screen
    ve_test.screens.timeline.navigate()

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
@pytest.mark.export_regression_MF956_channel_timeline
@pytest.mark.level2
@IHmark.LV_L2
def test_scroll_channel_area_switch_channel():
    ve_test = VeTestApi("timeline:test_scroll_channel_area_switch")
    ve_test.begin()

    server_data = ve_test.ctap_data_provider.send_request('GRID', payload={'duration':'50000'})
    ve_test.screens.timeline.navigate()
    ve_test.screens.timeline.check_scroll_channel_area(server_data)
    ve_test.screens.timeline.navigate()
    elements = ve_test.milestones.getElements()
    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    #Filtering empty and vertical items
    horizontalChannelItems = ve_test.screens.timeline.filterViewsResult(horizontalChannelItems)

    ve_test.appium.tap(horizontalChannelItems[1]["x_pos"] + horizontalChannelItems[1]["width"] / 2 ,horizontalChannelItems[1]["y_pos"] + horizontalChannelItems[1]["height"] / 2)
    ve_test.wait(5)

    elements = ve_test.milestones.getElements()

    ve_test.log_assert(ve_test.milestones.getElement([("screen", "action_menu", "==")], elements) or ve_test.milestones.getElement([("screen", "KDActionMenuPane", "==")], elements) , "no action_menu")

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
def test_no_tuning_to_current_event():
    ve_test = VeTestApi("timeline:test_no_tuning_to_current_event")
    ve_test.begin()

    playback = ve_test.screens.playback
    oldPlaybackUrl = playback.get_streaming_session_id()
    ve_test.screens.timeline.navigate()
    elements = ve_test.milestones.getElements()

    horizontalAssetsScroller = ve_test.milestones.getElement([("id", "FullContentScroller", "==")], elements)
    ve_test.log_assert(horizontalAssetsScroller, "No FullContentScroller in timeline")
    horizontalChannelItems = ve_test.milestones.getElementInBorders(elements, horizontalAssetsScroller)
    horizontalChannelItems = ve_test.screens.timeline.filterViewsResult(horizontalChannelItems)
    ve_test.appium.tap(horizontalChannelItems[ 0 ]["x_pos"] + horizontalChannelItems[ 0 ]["width"] / 2 ,horizontalChannelItems[ 0 ]["y_pos"] + horizontalChannelItems[ 0 ]["height"] / 2)
    ve_test.wait(4)

    after_streaming_session_id = playback.get_streaming_session_id()
    ve_test.log_assert(oldPlaybackUrl == after_streaming_session_id,"sessionPlaybackUrl != oldPlaybackUrl")

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
def test_tap_back():
    ve_test = VeTestApi("timeline:test_tap_back")
    ve_test.begin()

    fullscreen = ve_test.screens.fullscreen
    ve_test.screens.timeline.navigate()

    ve_test.screens.timeline.go_to_previous_screen()
    ve_test.wait(1)
    fullscreen.verify_active()

    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF956
@pytest.mark.MF956_channel_timeline
def test_timeout():
    ve_test = VeTestApi("timeline:test_timeout")
    ve_test.begin()

    fullscreen = ve_test.screens.fullscreen
    ve_test.screens.timeline.navigate()
    ve_test.wait(ve_test.screens.timeline.timeout - 8)
    ve_test.screens.timeline.verify_active()
    ve_test.wait(4)
    fullscreen.verify_active()

    ve_test.end()

