import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition
from tests_framework.ui_building_blocks.screen import ScreenActions
import logging

__author__ = 'gmaman'


@pytest.mark.events_updates_stability
def test_events_updates_stability():
    my_test = VeTestApi("test_events_updates_stability")
    my_test.begin()

    main_hub = my_test.screens.main_hub
    zaplist = my_test.screens.zaplist
    fullscreen = my_test.screens.fullscreen

    #9 hours playback and data verification upon screens
    for i in range(2):
        main_hub.navigate()
        main_hub_linear_events = main_hub.get_events_by_type("EVENT_CONTENT_TYPE_STANDALONE")
        channel_1_lcn = my_test.milestones.get_value(main_hub_linear_events, 0, 'channel_number')
        channel_2_lcn = my_test.milestones.get_value(main_hub_linear_events, 1, 'channel_number')
        channel_3_lcn = my_test.milestones.get_value(main_hub_linear_events, 2, 'channel_number')

        logging.info("Tunning from main hub")
        main_hub.tune_to_linear_channel_by_position(EventViewPosition.left_event, verify_streaming=False)
        verify_screens_data(my_test, channel_1_lcn)

        #play for 90 min
        my_test.wait(5400)
        logging.info("Channel change")
        fullscreen.channel_change(ScreenActions.DOWN,  verify_playing=False)
        verify_screens_data(my_test, channel_2_lcn)

        #play for 90 min
        my_test.wait(5400)
        logging.info("Tunnig from zaplist")
        channel_3_id = main_hub_linear_events[2]['channel_id']
        zaplist.tune_to_channel_by_sek(channel_3_id, verify_streaming_started=False)
        verify_screens_data(my_test, channel_3_lcn)

        #play for 90 min
        my_test.wait(5400)

    my_test.end()

#only for demo- show navigations between screens for a long time
def test_demo_stability():
    my_test = VeTestApi("test_demo_stability")
    my_test.begin()

    main_hub = my_test.screens.main_hub
    zaplist = my_test.screens.zaplist
    fullscreen = my_test.screens.fullscreen
    timeline = my_test.screens.timeline

    #9 hours playback and data verification upon screens
    for i in range(1000):
        main_hub.navigate()
        main_hub_linear_events = main_hub.get_events_by_type("EVENT_CONTENT_TYPE_STANDALONE")
        channel_1_lcn = my_test.milestones.get_value(main_hub_linear_events, 0, 'channel_number')
        channel_2_lcn = my_test.milestones.get_value(main_hub_linear_events, 1, 'channel_number')
        channel_3_lcn = my_test.milestones.get_value(main_hub_linear_events, 2, 'channel_number')

        logging.info("Zoom main hub")
        main_hub.zoom()
        my_test.wait(3)
        main_hub.zoom()

        my_test.wait(3)

        logging.info("Channel change")
        fullscreen.channel_change(ScreenActions.DOWN,  verify_playing=False)
        my_test.wait(5)
        fullscreen.channel_change(ScreenActions.UP,  verify_playing=False)
        my_test.wait(5)

        logging.info("Tunnig from zaplist")
        channel_2_id = main_hub_linear_events[1]['channel_id']
        zaplist.tune_to_channel_by_sek(channel_2_id, verify_streaming_started=False)

        my_test.wait(5)
        fullscreen.channel_change(ScreenActions.UP,  verify_playing=False)
        my_test.wait(5)

        timeline.navigate()
        my_test.wait(5)

    my_test.end()

def verify_screens_data(test, current_channel_lcn, verify_info_layer = True):

    infoLayer = test.screens.infolayer
    linear_action_menu = test.screens.linear_action_menu
    zaplist = test.screens.zaplist
    main_hub = test.screens.main_hub

    if verify_info_layer:
        #verify info layer metadata
        infoLayer.verify_data(current_channel_lcn)
        infoLayer.dismiss()

    #verify action menu metadata
    linear_action_menu.navigate()
    linear_action_menu.verify_data()
    linear_action_menu.dismiss()

    #verify zaplist metadata
    zaplist.verify_metadata()
    zaplist.dismiss()

    #verify main hub metadata.
    #currently verify only 3 first events, due to appium issue (timeout 60 seconds after any operation. this case - zoom)
    main_hub.navigate()
    ctap_grid_info =  test.ctap_data_provider.send_request('GRID', None)
    events = main_hub.get_events_by_type("EVENT_CONTENT_TYPE_STANDALONE")
    for event in events:
        ctap_channel = test.ctap_data_provider.get_channel_info(event['channel_id'], ctap_grid_info)
        test.ctap_data_provider.compare_event_metadata(event, ctap_channel)
    main_hub.dismiss()

    test.screens.playback.verify_streaming_playing()

