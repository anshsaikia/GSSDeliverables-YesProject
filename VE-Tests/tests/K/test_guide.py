import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.K.KGuide import kGuideScreenSection
from vgw_test_utils.IHmarks import IHmark
from tests_framework.ve_tests.tests_conf import DeviceType
__author__ = 'nahassan'
#@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2057
def test_guide_compare_data():
    my_test = VeTestApi("Guide:test_guide_data")
    my_test.begin()
    my_test.appium.launch_app()
    if my_test.device_type != DeviceType.TABLET:
        guide = my_test.screens.KSmartphoneGuide
        guide.navigate()
        guide.verify_data_cell_on_screen()

    my_test.end()
@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF2057
@IHmark.US28912


def test_guide_basic_functionality():
    my_test = VeTestApi("Guide:test_guide_basic_functionality")
    my_test.begin()
    if my_test.device_type == DeviceType.TABLET:
        guide = my_test.screens.guide
        guide.navigate()
        guide.verify_data()
        guide.showAndVerifyActionMenu()
        # my_test.screens.linear_action_menu.dismiss()
        guide.scrollTo(kGuideScreenSection.GRID)
        guide.tap_grid_event()
        guide.select_day(day_number=1)
        guide.scroll_next_channel()
        guide.select_day(day_number=2)
        guide.verify_grid_data()
        guide.select_first_day()
        guide.verify_grid_data()
        guide.tap_grid_event()
        guide.swipe_in_grid_actions()
        guide.verify_grid_data()
        guide.tap_grid_event()
    else:
        guide = my_test.screens.KSmartphoneGuide
        guide.navigate()

        guide.verify_data()
        guide.showAndVerifyActionMenu()
        my_test.screens.linear_action_menu.dismiss()
        guide.navigate()
        guide.verify_data()
        guide.actionMenuBookEvent()
        guide.navigate()
        guide.verifyRecordIcon()
        i = 1
        while i < 7:
         guide.select_day(day_number=i)
         i+=1
        guide.select_day(day_number=1)
        guide.navigate()
        guide.verifyEpisodeTextExists()
    my_test.end()


@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
def test_guide_channels_scrolling():
    my_test = VeTestApi("Guide:test_guide_channels_scrolling")
    my_test.begin(skipdevice=DeviceType.TABLET)
    guide = my_test.screens.KSmartphoneGuide
    guide.navigate()
    guide.verify_data()

    can_move_forward = True
    i = 0
    while ((can_move_forward == True) & (i < 3)):#increase this number for a better coverage
        can_move_forward = guide.scroll_next_channel()
        i+=1

    my_test.end()


@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
def test_guide_hour_selection():
    my_test = VeTestApi("Guide:test_guide_hour_selection")
    my_test.begin(skipdevice=DeviceType.TABLET)
    guide = my_test.screens.KSmartphoneGuide
    guide.navigate()
    guide.verify_data()
    guide.select_day(day_number=1)
    can_move_forward = True
    i = 0
    while ((can_move_forward == True) & (i < 3)):#increase this number for a better coverage
        can_move_forward = guide.select_next_hour()
        i+=1

    can_move_backward = True
    i = 0
    while ((can_move_backward == True) & (i < 6)):#increase this number for a better coverage
        can_move_backward = guide.select_previous_hour()
        i+=1

    my_test.end()


@IHmark.LV_L2
@IHmark.O_iOS
def test_guide_channel_selection():

    my_test = VeTestApi("Guide:test_guide_channel_selection")
    my_test.begin(skipdevice=DeviceType.TABLET)

    ''' Go to guide and verify data '''
    guide = my_test.screens.KSmartphoneGuide
    guide.navigate()
    guide.verify_data()

    ''' Go to channels selection and verify that channels are presented correctly '''
    channels_selection = my_test.screens.KSmartphoneChannelsSelection
    channels_selection.navigate(guide)
    channels_selection.verify_data()

    ''' Scroll down the table and verify that channels are presented correctly '''
    window_width, window_height = my_test.milestones.getWindowSize()
    my_test.mirror.swipe_area(0.5*window_width, 0.75*window_height, 0.5*window_width, 0.25*window_height, 200)
    channels_selection.verify_data()

    ''' Tap on # in the indexer and verify that channels are presented correctly '''
    my_test.mirror.tap(window_width-10, window_height-20)
    channels_selection.verify_data(False)
    my_test.wait(2)

    ''' Scroll up the table, tap on a channel and verify that this channel is displayed first '''
    my_test.mirror.swipe_area(0.5*window_width, 0.25*window_height, 0.5*window_width, 0.75*window_height, 200)
    channel_name = channels_selection.test.milestones.getElement([("id", "CHANNEL_NAME", "==")], channels_selection.test.milestones.getElements())
    my_test.appium.tap_element(channel_name)
    guide.verify_data(start_channel_id=channel_name['CHANNEL_ID'])

    my_test.end()
