import json

__author__ = 'gmaman'

import os.path
import pytest

from lib import set_mock_data_and_begin_test
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions

'''Globals'''
ZAPLIST_TIMEOUT=15
SWIPE_SLOW_DURATION=3000
SWIPE_FAST_DURATION=200
#Use only for generating snapshot files. Should never be committed while "True"
UPDATING_SNAPSHOTS_MODE = True
COMPARE_DATA_PATH="KD/android/DummyData/compare_data/"

'''Local Functions'''
def compare_events_by_milstones(ve_test, fileNamePrefix):
    elements = ve_test.milestones.getElements()

    model = ve_test.milestones.getDeviceDetails()['device-model']

    compareFilePath = COMPARE_DATA_PATH + fileNamePrefix + '_' + model +".json"
    if (UPDATING_SNAPSHOTS_MODE ):
         ve_test.android_mock_server.saveMilestonesToFile(elements, compareFilePath)
    ve_test.log_assert(os.path.isfile(compareFilePath), "File %s does not exsists" % compareFilePath)

    with open(compareFilePath) as milstones_file:
        comparedMilstones = json.load(milstones_file)

    displayedEvents = ve_test.screens.zaplist.get_displayed_events(elements)
    snapshotEvents =  ve_test.screens.zaplist.get_displayed_events(comparedMilstones['elements'])

    ve_test.log_assert(len(displayedEvents)==len(snapshotEvents), "Number of events in diplayed zaplist (%d) is different than events number in Snapshot zaplist (%d)" %(len(displayedEvents),len(snapshotEvents)))
    for displayItem, snapshotItem in zip(displayedEvents, snapshotEvents):
         ve_test.log_assert(displayItem["title_text"]==snapshotItem["title_text"], "Displayed events and snapshot events are different [%s != %s]" %(displayItem["title_text"],snapshotItem["title_text"]))

'''----------------------------------------------------------------------------------------Tests-------------------------------------------------------------'''

'''
Navigate to zaplist through full screen (Long swipe up/Down)
Navigate from zaplist to full screen (Tap background)
'''
@pytest.mark.dummy_MF969_Linear_zaplist
def test_zaplist_navigation():
    ve_test = VeTestApi("test_zaplist_navigation")
    ve_test.begin(login=ve_test.login_types.none)
    ve_test.screens.zaplist.navigate(swipe_direction=ScreenActions.DOWN)
    ve_test.screens.zaplist.dismiss()
    ve_test.screens.zaplist.navigate(swipe_direction=ScreenActions.UP)
    ve_test.wait(5)
    ve_test.end()

'''
scroll slow/fast, and verify zaplist events
'''
@pytest.mark.dummy_MF969_Linear_zaplist
def test_zaplist_scrolling():
    ve_test = VeTestApi("test_zaplist_scrolling")
    ve_test.begin(login=ve_test.login_types.none)

    zaplist = ve_test.screens.zaplist
    zaplist.navigate()

    'scroll slow'
    zaplist.scroll_from_center(duration=SWIPE_SLOW_DURATION, direction=ScreenActions.UP)
    compare_events_by_milstones(ve_test, "screen_data_zaplist_scrolling_0")

    'scroll fast'
    zaplist.scroll_from_center(duration=SWIPE_FAST_DURATION, direction=ScreenActions.DOWN)
    compare_events_by_milstones(ve_test, "screen_data_zaplist_scrolling_1")

    ve_test.end()

'''
channel lineup: scroll 1 channel
'''
@pytest.mark.dummy_MF969_Linear_zaplist
def test_zaplist_channellineup_1():
    ve_test = VeTestApi("test_zaplist_event_elements")

    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_zap_list_1_channels.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)
    zaplist = ve_test.screens.zaplist

    'validate 1 channel in lineup'
    events = zaplist.get_all_events()
    ve_test.log_assert(len(events) == 1, "No 1 channel in zaplist. channels num = %d" % len(events))

    'validate channels are displayed in cyclic manner'
    zaplist.verify_channels_lineup(events)

    ve_test.end()

'''
verify display of zap list event elements
channel logo / channel number / event thumbnail / event name / short synopsis / progress bar / start and end times
channel icons (locked/favorite) to be covered by a separate MF
'''
@pytest.mark.ui_regression
@pytest.mark.dummy_MF969_Linear_zaplist
def test_zaplist_event_elements():
    ve_test = VeTestApi("test_zaplist_event_elements")
    ve_test.begin(login=ve_test.login_types.none)

    ve_test.screens.zaplist.navigate()
    #compare_screen_by_milestones(ve_test.milestones, "zaplist_event_items")
    ve_test.android_mock_server.compare_milestones_to_reference("zaplist_event_items")

    ve_test.wait(10)
    ve_test.end()

'''
verify display of zap list event elements with incomplete data
event thumbnail - if missing display placeholder
event name - if missing display "No title available"
other items - will not be dipslayed
'''
@pytest.mark.dummy_MF969_Linear_zaplist
def test_zaplist_event_elements_missing():
    ve_test = VeTestApi("test_zaplist_event_elements_missing")

    mock_server_bundle_path = ve_test.android_mock_server.get_mock_address_data("bundle_l30_current_events_missing_data2.json")
    set_mock_data_and_begin_test(ve_test, "agg_grid_current_events", mock_server_bundle_path)

    ve_test.screens.zaplist.navigate()
    #compare_screen_by_milestones(ve_test.milestones, "zaplist_event_items_partial_data")
    ve_test.android_mock_server.compare_milestones_to_reference("zaplist_event_items_partial_data")

    ve_test.wait(60)
    ve_test.end()



