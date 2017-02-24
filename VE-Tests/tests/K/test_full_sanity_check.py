from tests_framework.ve_tests import ve_test
from vgw_test_utils.IHmarks import IHmark
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions, Screen, ScreenDismiss
import traceback
import pytest
import time
import logging
import requests

logger = logging.getLogger(__name__)
GENERIC_WAIT = 2


def internal_test_zaplist(ve_test):
  '''
    Sanity check of zaplist
    - launch zaplist
    - zap to channel 1 and 3 .Check for video playback
    - select next channel in channel list 2 times
    '''
  try:
      start_time = time.time()
      ve_test.log(
          "************************************* internal_test_zaplist ****************************************************")
      zap_list = ve_test.screens.zaplist
      infolayer = ve_test.screens.infolayer
      fullscreen = ve_test.screens.fullscreen
      '''
      1 st Step : Navigate to fullscreen
      '''
      fullscreen.navigate()
      ve_test.wait(GENERIC_WAIT)
      status = fullscreen.is_active(timeout=5)
      ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 1, status,
                              "Failed to go to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())

      '''
       2nd Step : Zap to first channel
       '''

      # Channels are present in ascending order of channel number. So ,it zaps  default to channel 1 (whichever is first)
      # if first channel has notification error then dismiss it so script can continue
      current_screen = ve_test.milestones.get_current_screen()
      if current_screen == "notification":
          message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
          ve_test.log("Closing notification screen")
          ve_test.appium.tap_element(message_element)

      '''
      3rd Step : check live video playback
      '''
      wait_for_streaming(ve_test)

      ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 2,
                              (ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
                              "video playback not working  (url = %s - current screen=%s ) " % (
                                  ve_test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl'],
                                  ve_test.milestones.get_current_screen()))

      '''
      4th Step:display ChannelList (via TAP on LCN from InfoLayer)
      '''
      zap_list.navigate()
      ve_test.wait(GENERIC_WAIT)
      status = zap_list.is_active()
      ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 3, status,
                              "channel list not displayed . Current screen: %s" % ve_test.milestones.get_current_screen())
      '''
      5th Step : zap to channel  channel 3
      '''
      channel_to_tune = ve_test.milestones.getElement([("channel_number", "3", "==")])
      # if channel 3 is not present then zapping to next channel
      if channel_to_tune is None:
          ve_test.log("channel 3 not found in channel list so tuning to some other channel")
          elements = ve_test.milestones.getElements()
          current_event = zap_list.get_centered_event_view(elements)
          ve_test.log("Current centered event in zaplist is :channel number " + str(current_event['channel_number']))
          ve_test.wait(GENERIC_WAIT)
          channel_to_tune = zap_list.get_next_event(current_event,ScreenActions.DOWN)
          ve_test.log("Next  event in zaplist to tune  :channel number " + str(channel_to_tune['channel_number']))
      ve_test.log("Zapping  on channel  " + str(channel_to_tune['channel_number']))
      ve_test.appium.tap_element(channel_to_tune)
      zapping_start_time = time.time()
      Flag = True
      # Waiting untill we get infolayer screen and if notification is found tune to next channel
      while Flag:
          wait_count = 1
          current_screen = ve_test.milestones.get_current_screen()
          if current_screen == "notification":
              message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
              ve_test.log("Issue in zapping the current channel")
              ve_test.log("Closing notification screen")
              ve_test.appium.tap_element(message_element)
              ve_test.wait(0.3)
              ve_test.log("Zapping to next channel")
              ve_test.ui.one_finger_swipe(ScreenActions.UP)
              ve_test.wait(0.3)
          else:
              if infolayer.is_active(timeout=0.3):
                  Flag = False
              if wait_count > 20:
                  Flag = False
          wait_count = wait_count + 1

      wait_for_streaming(ve_test)
      ve_test.log("Time taken to zap  :" + str(time.time() - zapping_start_time) + " seconds")
      ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 4,
                              (ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
                              "video playback not working  (url = %s - current screen=%s ) " % (
                                  ve_test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl'],
                                  ve_test.milestones.get_current_screen()))
      '''
      Step 6 : check infolayer is present ,then dismiss it
      '''
      status = infolayer.is_active()
      ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 5, status,
                              "Infolayer screen is not present . Current screen: %s" % ve_test.milestones.get_current_screen())
      ve_test.log("Infolayer is displayed for the current channel")
      ve_test.ui.tap_element("exit")
      ve_test.log("Infolayer is dismissed")
      ve_test.wait(0.5)
      if not infolayer.is_active():
          status = True
      else:
          status = False
      ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 6, status,
                              "Infolayer screen is not dismissed")

      '''
      Step 7: display channel list and select next channel 2 times
      '''
      channel_count = 1
      # To open infolayer
      infolayer.show()
      infolayer.is_active(timeout=10)
      current_screen = ve_test.milestones.get_current_screen()
      # If notification is present then dismiss it
      if current_screen == "notification":
          message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
          ve_test.log("Closing notification screen")
          ve_test.appium.tap_element(message_element)
      # Selecting next channel 2 times
      ve_test.log("Selecting next channel in channel list 2 times")
      while channel_count <= 2:
          ve_test.log("Current ilteration is  " + str(channel_count))
          ve_test.log("Checking infolayer is active")
          ve_test.log("Current screen is " + ve_test.milestones.get_current_screen())
          ve_test.wait(1)
          status = infolayer.is_active(timeout=10)
          ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 7, status,
                                  "Infolayer screen is not present. Current screen: %s" % ve_test.milestones.get_current_screen())
          ve_test.log("Current screen is " + ve_test.milestones.get_current_screen())
          element = ve_test.milestones.getElement([("name", "event_view", "==")])
          if element is None:
              for counter in range(20):  # wait for events to load in infolayer
                  ve_test.log("waiting for events to be loaded")
                  ve_test.wait(GENERIC_WAIT)
                  element = ve_test.milestones.getElement([("name", "event_view", "==")])
                  if element is not None:
                      break

          ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 8, element is not None,
                                                  "event_view not present in infolayer screen")
          channel_number = ve_test.milestones.get_value(element, "channel_number")
          ve_test.log("Current channel is " + str(channel_number))
          ve_test.log("infolayer is active and tapping on zaplist")
          ve_test.ui.tap_element("zaplist")
          ve_test.log("Waiting for zaplist")
          status = zap_list.is_active(timeout=10)
          ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 9, status,
                                  "channel list not displayed. Current screen: %s" % ve_test.milestones.get_current_screen())
          ve_test.log("Current screen is " + ve_test.milestones.get_current_screen())
          elements = ve_test.milestones.getElements()
          current_event = zap_list.get_centered_event_view(elements)
          status = current_event is not None
          ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 10, status,
                                  "Current event returned is none")
          ve_test.log("Current centered event in zaplist is :channel number " + str(current_event['channel_number']))
          ve_test.wait(GENERIC_WAIT)
          non_current_event = zap_list.get_next_event(current_event,ScreenActions.DOWN)
          status = non_current_event is not None
          ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 11, status,
                                  "Next event to tune  is none")
          ve_test.log("Next  event in zaplist to tune  :channel number " + str(non_current_event['channel_number']))
          ve_test.appium.tap_element(non_current_event)
          zapping_start_time = time.time()
          for counter in range(40):
              ve_test.wait(1)
              current_screen = ve_test.milestones.get_current_screen()
              # dismiss notification screen
              if current_screen == "notification":
                  message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
                  ve_test.log("Closing notification screen")
                  ve_test.appium.tap_element(message_element)
                  break
              ve_test.log("waiting for the video to start streaming")
              # Wait for infolayer screen to load
              status = infolayer.is_active(timeout=0.3)
              if status:
                  playback_buffer_curr = ve_test.milestones.getPlaybackStatus("playbackBufferCurrent")
                  # Wait for video to start streaming
                  if playback_buffer_curr > 0:
                      ve_test.log("Video is streaming successfully")
                      break
          ve_test.log("Time taken to zap  :" + str(time.time() - zapping_start_time) + " seconds")
          ve_test.log("Current screen is " + ve_test.milestones.get_current_screen())
          ve_test.log("End of ilteration " + str(channel_count))
          channel_count = channel_count + 1
          status = infolayer.is_active(timeout=0.3)
          ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 12, status,
                                  "Infolayer screen is not present. Current screen: %s" % ve_test.milestones.get_current_screen())
      '''
      Step 8 : Exit from channel list via back button (note close button not present)
      '''
      ve_test.log("Exiting from channel list")
      ve_test.ui.center_tap()
      ve_test.wait(0.5)
      ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 13, zap_list.is_active() == False,
                              "Channel list is not dismissed. Current screen: %s" % ve_test.milestones.get_current_screen())
      total_time_duration['internal_test_zaplist'] = str(time.time() - start_time)
      ve_test.log("Time taken to execute internal_test_zaplist :" + str(time.time() - start_time) + " seconds")

  except:
      traceback.print_exc()
      formatted_lines = traceback.format_exc().splitlines()
      message = formatted_lines[-1]
      ve_test.assertmgr.addCheckPoint("internal_test_zaplist", 14, False, message)



def internal_zapping_video_swipe(ve_test):
  '''
    sanity check of zapping video via swipe
    '''

  try:
    start_time = time.time()
    ve_test.log(
        "************************************* internal_zapping_video_swipe ****************************************************")
    '''
    Step 1:
    Navigate to fullscreen
    '''

    fullscreen = ve_test.screens.fullscreen

    # navigating to fullscreen
    fullscreen.navigate()
    ve_test.wait(GENERIC_WAIT)
    status = fullscreen.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_zapping_video_swipe", 1,
                            status,
                            "Fullscreen not found . current screen=%s" % (
                                ve_test.milestones.get_current_screen()))

    '''
    Step 2:
    Milestone pending
    '''
    '''
    Step 3:
    Store current live video url
    '''
    # storing the play back url
    urlBeforeZapping = ve_test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl']
    '''
    Step 4:
    Check for live video playback status
    '''
    # checking playback status
    wait_for_streaming(ve_test)
    unlock_program_if_locked(ve_test)
    ve_test.assertmgr.addCheckPoint("internal_zapping_video_swipe", 2,
                            (ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
                            " The video before the 1st zapping is not playing .current state=%s" % (
                                ve_test.milestones.getPlaybackStatus()["playbackState"]))

    '''
    Step 5:
    Check for no error notification
    '''
    elements = ve_test.milestones.getElements()
    ve_test.assertmgr.addCheckPoint("internal_zapping_video_swipe", 3, check_notification(ve_test) == False,
                            "A notification is shown with msg_error=%s, msg_text=%s" % (
                            str(ve_test.milestones.get_element_by_key(elements, "msg_error")),
                            str(ve_test.milestones.get_element_by_key(elements, "msg_text"))))

    '''
    Step 6:
    Zap to next channel
    '''

    # tune to next channel by SWIPE UP
    ve_test.log("Zapping to next channel by Swipe UP")
    ve_test.ui.one_finger_swipe(ScreenActions.UP)
    ve_test.wait(GENERIC_WAIT)
    '''
    Step 7:
    Milestone pending
    '''
    '''
    Step 8:
    Check for live video playback status
    '''
    unlock_program_if_locked(ve_test)
    wait_for_streaming(ve_test)
    # checking playback status
    ve_test.assertmgr.addCheckPoint("internal_zapping_video_swipe", 4,
                            (ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
                            " The video for next channel  is not playing .current screen=%s" % (
                            ve_test.milestones.get_current_screen()))
    '''
    Step 12:
    Zap to previous channel
    '''

    # tune to previous channel by SWIPE Down
    ve_test.log("Zapping to previous channel by Swipe Down")
    ve_test.ui.one_finger_swipe(ScreenActions.DOWN)
    ve_test.wait(GENERIC_WAIT)

    '''
    Step 13:
    check current live video Url is original one
    '''
    # verifying the current live video url
    ve_test.assertmgr.addCheckPoint("internal_zapping_video_swipe", 5,
                            (urlBeforeZapping == ve_test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl']),
                            "The url is not the expected one")
    total_time_duration['internal_zapping_video_swipe'] = str(time.time() - start_time)
    ve_test.log("Time taken to execute internal_zapping_video_swipe :" + str(time.time() - start_time) + " seconds")

  except:
      traceback.print_exc()
      formatted_lines = traceback.format_exc().splitlines()
      message = formatted_lines[-1]
      ve_test.assertmgr.addCheckPoint("internal_zapping_video_swipe", 6, False, message)


def internal_zapping_video(ve_test):
  '''
    sanity check of zapping video
    '''

  try:
    start_time = time.time()
    ve_test.log(
        "************************************* internal_zapping_video ****************************************************")
    '''
    Step 1:
    Navigate to fullscreen
    '''

    fullscreen = ve_test.screens.fullscreen
    zap_list = ve_test.screens.zaplist
    # navigating to fullscreen
    fullscreen.navigate()
    ve_test.wait(GENERIC_WAIT)
    status = fullscreen.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_zapping_video", 1,
                            status,
                            "Fullscreen not found . current screen=%s" % (
                                ve_test.milestones.get_current_screen()))

    # getting device details
    device_details = ve_test.milestones.getDeviceDetails()

    '''
    Step 2:
    Milestone pending
    '''
    '''
    Step 3:
    Store current live video url
    '''
    # storing the play back url
    urlBeforeZapping = ve_test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl']
    '''
    Step 4:
    Check for live video playback status
    '''
    # checking playback status
    wait_for_streaming(ve_test)
    ve_test.assertmgr.addCheckPoint("internal_zapping_video", 2,
                            (ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
                            " The video before the 1st zapping is not playing .current screen=%s" % (
                            ve_test.milestones.get_current_screen()))

    '''
    Step 5:
    Check for no error notification
    '''
    elements = ve_test.milestones.getElements()
    ve_test.assertmgr.addCheckPoint("internal_zapping_video", 3, check_notification(ve_test) == False,
                            "A notification is shown with msg_error=%s, msg_text=%s" % (
                            str(ve_test.milestones.get_element_by_key(elements, "msg_error")),
                            str(ve_test.milestones.get_element_by_key(elements, "msg_text"))))

    '''
    Step 6:
    Zap to next channel
    '''
    # storing current channel id
    current_channel_id = ve_test.milestones.getPlaybackStatus()['currentChannelId']
    # tune to next channel by TAP down
    ve_test.log("Zapping to next channel by TAP Down")
    # tapping to open infolayer screen
    ve_test.appium.tap(device_details["screen-width"] / 2, device_details["screen-height"] / 2)
    ve_test.wait(GENERIC_WAIT)
    # opening channel list
    ve_test.ui.tap_element("zaplist")
    ve_test.wait(GENERIC_WAIT)
    status = zap_list.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_zapping_video", 4, status,
                            "channel list not displayed. Current screen: %s" % ve_test.milestones.get_current_screen())
    # Getting next event to zap
    next_event = zap_list.get_next_event_from_milstone(current_channel_id)
    ve_test.appium.tap_element(next_event)
    zapping_start_time = time.time()
    ve_test.wait(GENERIC_WAIT)
    '''
    Step 7:
    Milestone pending
    '''
    '''
    Step 8:
    Check for live video playback status
    '''
    # checking playback status
    wait_for_streaming(ve_test)
    ve_test.log("Time taken to zap  :" + str(time.time() - zapping_start_time) + " seconds")
    ve_test.assertmgr.addCheckPoint("internal_zapping_video", 5,
                            (ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
                            " The video for next channel  is not playing .current screen=%s" % (
                            ve_test.milestones.get_current_screen()))
    # storing current channel id
    current_channel_id = ve_test.milestones.getPlaybackStatus()['currentChannelId']
    '''
    Step 12:
    Zap to previous channel
    '''
    # tune to previous channel by TAP Up
    ve_test.log("Zapping to previous channel by TAP Up")
    ve_test.ui.tap_element("zaplist")
    ve_test.wait(GENERIC_WAIT)
    status = zap_list.is_active()
    ve_test.assertmgr.addCheckPoint("internal_zapping_video", 6, status,
                            "channel list not displayed. Current screen: %s" % ve_test.milestones.get_current_screen())
    # to get the previous event
    next_event = ve_test.screens.zaplist.get_next_event_from_milstone(current_channel_id, ScreenActions.DOWN)
    ve_test.appium.tap_element(next_event)
    ve_test.wait(GENERIC_WAIT)
    '''
    Step 13:
    check current live video Url is original one
    '''
    # verifying the current live video url
    ve_test.assertmgr.addCheckPoint("internal_zapping_video", 7,
                            (urlBeforeZapping == ve_test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl']),
                            "The url is not the expected one")
    total_time_duration['internal_zapping_video'] = str(time.time() - start_time)
    ve_test.log("Time taken to execute internal_zapping_video :" + str(time.time() - start_time) + " seconds")

  except:
      traceback.print_exc()
      formatted_lines = traceback.format_exc().splitlines()
      message = formatted_lines[-1]
      ve_test.assertmgr.addCheckPoint("internal_zapping_video", 8, False, message)


wait_time_during_VOD_PLB = 10
wait_time_after_screen_transition = 4
wait_time_for_streaming = 10


def internal_test_vod(ve_test):
    """
      Step 1 : Navigate from Main Hub to Store
      :param ve_test:
      :param assertmgr:
      :return:
      """
    start_time = time.time()
    try:
        ve_test.log(
            "************************************* internal_test_vod ****************************************************")
        store = ve_test.screens.store_filter
        fullcontentscreen = ve_test.screens.full_content_screen
        fullscreen = ve_test.screens.fullscreen
        vod_actionmenu = ve_test.screens.vod_action_menu
        playback = ve_test.screens.playback

        # Verify navigation from Main Hub to Store
        ve_test.log("Navigating to VOD screen from Main hub")
        store.navigate()
        ve_test.wait(wait_time_after_screen_transition)
        store_detail = ve_test.milestones.getElements()
        ve_test.log("navigation to Store is successfull")
        ve_test.assertmgr.addCheckPoint("internal_test_vod", 1, str(ve_test.milestones.get_current_screen()) == "store_filter",
                                "Cannot navigate from MainHub to Store")

        '''
        Step 2 : Select a VOD asset given its classification
        Step 3 : Start playback
        '''
        # Select a VOD asset given its classification.
        device_details = ve_test.milestones.getDeviceDetails()
        x = device_details["screen-width"] / 2
        up_y = device_details["screen-height"] * 0.1
        down_y = device_details["screen-height"] * 0.75

        #env = device_details["build-lab-config"]
        #substrng = 'net'

        flag = True
        if 'net' in ve_test.project:
            while flag:
                var = ve_test.milestones.getElement([("title_text", "RETROSPECTIVA SPORTV", "==")])
                # ve_test.wait(GENERIC_WAIT)
                if var is None:
                    ve_test.appium.swipe_area(x, down_y, x, up_y)
                    ve_test.wait(0.5)
                else:
                    ve_test.log("Asset is :" + str(var))
                    ve_test.appium.tap_element(var)
                    ve_test.wait(GENERIC_WAIT)
                    flag = False
        else:
            selectedAsset = select_vod_free_asset(ve_test)
            ve_test.log("Asset is :" + str(selectedAsset))
            ve_test.wait(0.5)
            if selectedAsset:
                ve_test.appium.tap_element(selectedAsset)
                ve_test.wait(GENERIC_WAIT)
            else:
                ve_test.assertmgr.addCheckPoint("internal_test_vod", 2, selectedAsset is not None,
                                        "No VOD asset are found in Store")
                ve_test.assertmgr.addCheckPoint("internal_test_vod", 3, selectedAsset is not None,
                                        "Playback is not possible as no VOD asset is available")
                # ve_test.log_assert(selectedAsset, "Terminating the VOD test as VOD Store is empty")

        if ve_test.milestones.getElement([("name", "full_content_screen", "==")]):
            ve_test.log("Now selecting the first available VOD asset for playback  ")
            fullcontentscreen.verify_active(timeout=5)
            vod_asset_to_play = ve_test.milestones.getElement([("name", "event_view", "==")])
            ve_test.appium.tap_element(vod_asset_to_play)
            ve_test.wait(wait_time_after_screen_transition)
            play_button = vod_actionmenu.is_active(timeout=2)
            ve_test.assertmgr.addCheckPoint("internal_test_vod", 2, play_button, "Not able to select VOD asset")

            # Start asset playback
            ve_test.log("Starting playback...")
            play_button = verify_play_button(ve_test)
            if play_button:
                ve_test.appium.tap_element(play_button)
            else:
                ve_test.log("Play button not found in the action menu. The selected asset is not FREE asset")
            ve_test.wait(6)
            currentscreen = ve_test.milestones.get_current_screen()
            print currentscreen
            if currentscreen == "pincode":
                hhId = ve_test.configuration["he"]["generated_household"]
                youthpin = str(ve_test.he_utils.getParentalRatingPin(hhId))
                elements = ve_test.milestones.getElements()
                parental_text = ve_test.milestones.getElement([("title_text", "PLEASE ENTER YOUR PIN CODE", "==")],
                                                          elements)
                ve_test.log(str(parental_text))
                x_pos_parental_text = parental_text['x_pos']
                for digit in youthpin:
                    element = ve_test.milestones.getElement(
                        [("title_text", digit, "=="), ("x_pos", x_pos_parental_text, ">")],
                        elements)
                    ve_test.log_assert(element, "Key %s not found in milestone" % digit)
                    ve_test.appium.tap_element(element)
                    ve_test.wait(2)

            vod_streaming_status = wait_for_vodstreaming(ve_test)

            if vod_streaming_status:
                ve_test.log("Time taken to start VOD video streaming is SECS = %s" % str(vod_streaming_status))
            elif vod_streaming_status is None:
                ve_test.ui.center_tap()
                ve_test.wait(0.3)
                ve_test.ui.tap_element("exit")
                ve_test.wait(0.3)
                ve_test.assertmgr.addCheckPoint("internal_test_vod", 3, vod_streaming_status is None,
                                        "VOD  playback did not start for SECS = %s" % TIME_THRESHOLD_FOR_VOD_PLAYING)
                ve_test.log_assert(vod_streaming_status,
                                   " Terminating VOD playback checking as the playback didn't start till SECS = %s" % TIME_THRESHOLD_FOR_VOD_PLAYING)
            playback_status = ve_test.milestones.getPlaybackStatus()
            state = playback_status["playbackState"]

            ve_test.assertmgr.addCheckPoint("internal_test_vod", 3, state == "PLAYING",
                                    "VOD playback has not started. Current state is %s" % state)

        elif ve_test.milestones.getElement([("name", "action_menu", "==")]):
            ve_test.log("Selecting the first available VOD asset in the STORE for playback")
            vodactionmenu = vod_actionmenu.is_active(timeout=5)
            ve_test.assertmgr.addCheckPoint("internal_test_vod", 2, vodactionmenu, "Not able to select VOD asset.")
            ve_test.wait(wait_time_after_screen_transition)
            ve_test.log("Starting playback...")
            ve_test.log(str(ve_test.milestones.get_current_screen()))
            ve_test.wait(GENERIC_WAIT)
            play_button = verify_play_button(ve_test)
            if play_button:
                ve_test.appium.tap_element(play_button)
            else:
                ve_test.log("Play button not found in the action menu")
            ve_test.wait(GENERIC_WAIT)
            notifcationstatus = check_notification(ve_test, dismiss_notification=True)
            if notifcationstatus:
                ve_test.ui.center_tap()
                ve_test.wait(0.3)
                ve_test.ui.tap_element("exit")
                ve_test.wait(0.3)
                ve_test.assertmgr.addCheckPoint("internal_test_vod", 3, notifcationstatus,
                                        "A notification is shown with msg_error=%s, msg_text=%s" % (
                                            str(ve_test.milestones.get_element_by_key(ve_test.milestones.getElements(),
                                                                                      "msg_error")),
                                            str(ve_test.milestones.get_element_by_key(ve_test.milestones.getElements(),
                                                                                      "msg_text"))))
                ve_test.log_assert(notifcationstatus,
                                   "Terminating VOD playback as error notification is thrown when the user tries to playback the asset")
            else:

                vod_streaming_status = wait_for_vodstreaming(ve_test)
                if vod_streaming_status is None:
                    ve_test.assertmgr.addCheckPoint("internal_test_vod", 3, vod_streaming_status is None,
                                            "VOD  playback did not start for SECS = %s" % TIME_THRESHOLD_FOR_VOD_PLAYING)
                    ve_test.log_assert(vod_streaming_status,
                                       " Terminating VOD playback checking as the playback didn't start till SECS = %s" % TIME_THRESHOLD_FOR_VOD_PLAYING)
                playback_status = ve_test.milestones.getPlaybackStatus()
                state = playback_status["playbackState"]
                sessiontime = playback_status["sso"]["sessionStartTime"]
                ve_test.assertmgr.addCheckPoint("internal_test_vod", 3, state == "PLAYING",
                                        "Audio-video of the VOD playback asset is not rendered.Current screen is : %s" % ve_test.milestones.get_current_screen())

            ve_test.wait(GENERIC_WAIT)

        '''
        Step 4 : Check for playback status and current playback position
        '''
        # Check playback status and current playback position.
        playback = ve_test.milestones.getPlaybackStatus()

        playbackCurPos = playback['playbackBufferCurrent']
        # playbackDuration = playback['playbackBufferEnd']-playback['playbackBufferStart']
        if playbackCurPos == 0:
            ve_test.wait(10)
        playback = ve_test.milestones.getPlaybackStatus()
        playbackstatus = playback['playbackState']
        playbackPos = playback['playbackBufferCurrent']
        status = fullscreen.is_active(timeout=5)
        ve_test.assertmgr.addCheckPoint("internal_test_vod", 4, playbackstatus == "PLAYING",
                                "VOD Playback status is not changed to PLAYING. Current state is : %s" %
                                playback["playbackState"])
        ve_test.assertmgr.addCheckPoint("internal_test_vod", 5, (playbackPos > playback['playbackBufferStart']),
                                "Current playback position is not correct")

        # wait time during playback
        ve_test.log("Wait time during playback is set to SECS = %s" % str(wait_time_during_VOD_PLB))
        ve_test.wait(wait_time_during_VOD_PLB)
        '''
        Step 5 : Stop the VOD asset playback
        '''
        # Stop the VOD asset Playback via TAP on video and then "CROSS" on the top right corner
        ve_test.log("Now stopping the VOD playback via TAP in VIDEO and then CROSS on top right corner")

        curscreen = ve_test.milestones.getElement([("name", "fullscreen", "==")])
        if curscreen:
            ve_test.ui.center_tap()
            ve_test.wait(1)
            elements = ve_test.milestones.getElements()
            exit1 = ve_test.milestones.getElement([("id", "exit", "==")])
            ve_test.appium.tap_element(exit1)
            ve_test.wait(1)
        else:
            ve_test.wait(1)
            ve_test.ui.tap_element("exit")
            ve_test.wait(1)

        ve_test.assertmgr.addCheckPoint("internal_test_vod", 6,
                                ve_test.milestones.getPlaybackStatus()["playbackState"] == "STOPPED",
                                "VOD playback is not stopped")

        '''
        Step 6 : Check user goes back to the previous store menu after stopping the playback
        '''
        # Check the user goes back to previous store menu after stopping the playback.
        ve_test.log("Checking whether the user goes back to previous store menu after stopping the playback")
        curscr = ve_test.milestones.get_current_screen()
        if curscr == "full_content_screen":
            status = fullcontentscreen.is_active(timeout=5)
        else:
            status = store.is_active(timeout=5)
        ve_test.assertmgr.addCheckPoint("internal_test_vod", 7, status,
                                "Incorrect screen transition on stopping VOD playback. Current screen is : %s" %
                                ve_test.milestones.get_current_screen())
        back_button = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
        if back_button:
            ve_test.appium.tap_element(back_button)
        ve_test.wait(GENERIC_WAIT)
        total_time_duration['internal_test_vod'] = str(time.time() - start_time)
        ve_test.log("Time taken to execute internal_test_vod :" + str(time.time() - start_time) + " seconds")

    except:
        traceback.print_exc()
        formatted_lines = traceback.format_exc().splitlines()
        message = formatted_lines[-1]
        ve_test.assertmgr.addCheckPoint("internal_test_vod", 8, False, message)


def internal_test_hub_navigation(ve_test):
  '''
  navigate in the main categories of the HUB (LIVE, LIBRARY, STORE, GUIDE, SETTINGS ) and their
   proposed sub-categories and go back to the mainHub
    '''

  try:
      start_time = time.time()
      ve_test.log(
          "************************************* internal_test_hub_navigation ****************************************************")
      # store the starting screen
      main_hub = ve_test.screens.tv_filter
      screens = ve_test.screens
      # Storing the screens in order of navigation
      mainScreens = [
              screens.settings,
              screens.guide,
              screens.store_filter,
              screens.library_filter,
              main_hub
          ]

      count = 0
      # Go to mainhub(tv_filter screen) before starting the test case
      screens.navigateSingle(main_hub)
      status = main_hub.is_active(timeout=5)
      ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 1, status,
                              "Initial mainhub screen expected is   %s but current  screen is %s" % (
                              main_hub.screen_name,
                              ve_test.milestones.get_current_screen()))
      # Navigate to each screen one by one
      for items in mainScreens:
          screens.navigateSingle(items)
          # To check if current screen is setting screen
          if count == 0:
              status = items.is_active(timeout=5)
              ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 2, status,
                                      "Navigation failed current screen is %s but expected screen is % s" % (
                                          ve_test.milestones.get_current_screen(), items.screen_name))
              elements = ve_test.milestones.getElements()
              # Extract sub-screen  present in setting screen
              preferences_label = ve_test.milestones.getElementContains(elements, "PREFERENCES")
              device_management_label = ve_test.milestones.getElementContains(elements, "DEVICE MANAGEMENT")
              logout_label = ve_test.milestones.getElementContains(elements, "SIGN OUT")
              ve_test.appium.tap_element(preferences_label)
              ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 3, (preferences_label is not None),
                                      "Preferences label not present in setting screen")
              ve_test.wait(0.3)
              ve_test.appium.tap_element(device_management_label)
              ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 4, (device_management_label is not None),
                                      "Device management label not present in setting screen")
              ve_test.wait(0.3)
              ve_test.appium.tap_element(logout_label)
              ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 5, (logout_label is not None),
                                      "Logout label not present in setting screen")
              ve_test.wait(0.3)
              elements = ve_test.milestones.getElements()
              cancel_label = ve_test.milestones.getElementContains(elements, "CANCEL")
              ve_test.appium.tap_element(cancel_label)
              ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 6, (cancel_label is not None),
                                      "Cancel label not present in setting screen inside sign out sub-screen")
              elements = ve_test.milestones.getElements()
              back_button = ve_test.milestones.getElement([("id", "back", "==")], elements)
              ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 7, (back_button is not None),
                                      "Back button not present  in setting screen")
              ve_test.appium.tap_element(back_button)
              ve_test.wait(GENERIC_WAIT)
              status = main_hub.is_active(timeout=5)
              ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 8, status,
                                      "Failed to go back to  %s screen . Current  screen is % s" % (
                                      main_hub.screen_name,
                                      ve_test.milestones.get_current_screen()))

          # for screens other than settings
          else:
              status = items.is_active(timeout=5)
              ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 8 + count, status,
                                      "Navigation failed current screen is %s but expected screen is % s" % (
                                          ve_test.milestones.get_current_screen(), items.screen_name))
          count = count + 1

      total_time_duration['internal_test_hub_navigation'] = str(time.time() - start_time)
      ve_test.log("Time taken to execute internal_test_hub_navigation :" + str(time.time() - start_time) + " seconds")


  except:
      traceback.print_exc()
      formatted_lines = traceback.format_exc().splitlines()
      message = formatted_lines[-1]
      ve_test.assertmgr.addCheckPoint("internal_test_hub_navigation", 13, False, message)

def internal_test_actionmenu_ltv_fullscreen(ve_test):
  '''
    Sanity check for action menu full screen
  '''


  try:
    start_time = time.time()
    ve_test.log(
        "************************************* internal_test_actionmenu_ltv_fullscreen ****************************************************")
    fullscreen = ve_test.screens.fullscreen
    infolayer = ve_test.screens.infolayer
    actionmenu = ve_test.screens.action_menu

    '''
    Step 1: Navigate to fullscreen if not already done
    '''
    ve_test.log("Navigating to full-screen")
    fullscreen.navigate()
    status = fullscreen.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_test_actionmenu_ltv_fullscreen", 1, status,
                            "Failed to go to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())

    '''
    Step 2: select channel 1 and check live video playback
    '''
    # zapping to first channel
    device_details = ve_test.milestones.getDeviceDetails()
    ve_test.appium.tap(device_details["screen-width"] / 2, device_details["screen-height"] / 2)
    ve_test.wait(GENERIC_WAIT)

    ve_test.log("Zapped to Channel 1. Now checking live video playback")
    #ve_test.wait(GENERIC_WAIT)
    unlock_program_if_locked(ve_test)
    playbackStatusInfo = ve_test.milestones.getPlaybackStatus()
    ve_test.assertmgr.addCheckPoint("internal_test_actionmenu_ltv_fullscreen", 2,
                            playbackStatusInfo["playbackState"] == "PLAYING",
                            " The video for 1st channel is not playing . Current state is : %s" %
                            playbackStatusInfo["playbackState"])
    ve_test.log("Playback status of current channel is " + playbackStatusInfo["playbackState"])
    #ve_test.wait(GENERIC_WAIT)

    '''
    Step 3: store channel data (logo / event)
    '''
    ve_test.ui.one_finger_swipe(ScreenActions.UP)
    ve_test.wait(5)
    ve_test.log("Storing current channel data")
    ve_test.wait(5)
    elements = ve_test.milestones.getElements()
    #channel_logo_list = ve_test.milestones.get_elements_if_has_key(elements, "image_url")
    playbackStatusInfo = ve_test.milestones.getPlaybackStatus()
    #channel_logo_dict = channel_logo_list[0]

    #channel_logo = channel_logo_dict.get('image_url')
    channel_logo = ve_test.milestones.get_value_by_key(elements,'channel_logo_url')
    '''event_text_list = ve_test.milestones.get_elements_if_has_key(elements, "title_text")
    event_text_dict = event_text_list[1]
    event_text = event_text_dict.get('title_text')'''
    event_text_dict = ve_test.milestones.getElement([("id", "info_title", "==")], elements)
    event_text = event_text_dict.get('title_text')

    pip = playbackStatusInfo['sso']['sessionKeepAliveUrl']
    ve_test.wait(GENERIC_WAIT)
    ve_test.log("Channel logo from infolayer: "+str(channel_logo))
    ve_test.log("Event text from infolayer : "+str(event_text))

    '''
    Step 4: display action menu and compare previously stored data (logo and title) with action menu data
    '''
    # displaying action menu
    ve_test.log("Displaying action menu")
    action_menu_info = ve_test.milestones.getElement([("id", "actionmenu", "==")], elements)
    ve_test.appium.tap_element(action_menu_info)
    ve_test.wait(GENERIC_WAIT)
    status = actionmenu.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_test_actionmenu_ltv_fullscreen", 3, status,
                            "Failed to go to action menu screen. Current screen: %s" % ve_test.milestones.get_current_screen())

    # storing action menu data
    ve_test.log("Storing action menu data")
    ve_test.wait(5)
    actionmenu_playbackStatusInfo = ve_test.milestones.getPlaybackStatus()
    elements = ve_test.milestones.getElements()
    actionmenu_channel_logo_list = ve_test.milestones.get_elements_if_has_key(elements, "logoUrl")
    actionmenu_channel_logo_dict = actionmenu_channel_logo_list[0]
    actionmenu_channel_logo = actionmenu_channel_logo_dict.get('logoUrl')
    actionmenu_event_text_list = ve_test.milestones.get_elements_if_has_key(elements, "title_text")
    for items in actionmenu_event_text_list:
        if items != "" or None:
            actionmenu_event_text_dict = items
            break

    actionmenu_event_text = actionmenu_event_text_dict.get('title_text')

    actionmenu_pip = actionmenu_playbackStatusInfo['sso']['sessionKeepAliveUrl']
    #ve_test.wait(GENERIC_WAIT)

    ve_test.log("Channel logo from actionmenu : "+str(actionmenu_channel_logo))
    ve_test.log("Event text from actionmenu : "+str(actionmenu_event_text))

    # comparing action menu data with previously stored data
    ve_test.assertmgr.addCheckPoint("internal_test_actionmenu_ltv_fullscreen", 4, channel_logo == actionmenu_channel_logo,
                            " Channel logo of current channel and that of action menu is not matching")

    ve_test.assertmgr.addCheckPoint("internal_test_actionmenu_ltv_fullscreen", 5,
                            event_text.lower() == actionmenu_event_text.lower(),
                            " Event text of current channel and that of action menu is not matching")

    '''
    Step 5: check the information are correctly displayed Logo, PIP or Poster , Program Title, synopsis , program info and Actions list
    '''
    ve_test.assertmgr.addCheckPoint("internal_test_actionmenu_ltv_fullscreen", 6, pip == actionmenu_pip,
                            " Event PIP of current channel and that of action menu is not matching")

    # action list verification is not done

    ve_test.log("Previously stored data of channel is matching with action menu data")
    #ve_test.wait(GENERIC_WAIT)

    # action list related verification is left as the feature is not developed in app

    '''
    Step 6: go back to fullscreen with TAP on PIP
    '''
    ve_test.log("Tapping on PIP to go back to fullscreen")
    elements = ve_test.milestones.getElements()
    pip_view = ve_test.milestones.getElement([("id", "fullscreen", "==")], elements)
    if pip_view == None:
        ve_test.log("Pip element is not found. The current element list is :"+str(elements))
        pip_view = ve_test.milestones.getElement([("id", "DraggablePaneView", "==")], elements)
    ve_test.appium.tap_element(pip_view)
    ve_test.wait(GENERIC_WAIT)
    status = fullscreen.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_test_actionmenu_ltv_fullscreen", 7, status,
                            "Failed to go to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())
    total_time_duration['internal_test_actionmenu_ltv_fullscreen'] = str(time.time() - start_time)
    ve_test.log("Time taken to execute internal_test_actionmenu_ltv_fullscreen :" + str(time.time() - start_time) + " seconds")

  except:
    traceback.print_exc()
    formatted_lines = traceback.format_exc().splitlines()
    message = formatted_lines[-1]
    ve_test.assertmgr.addCheckPoint("internal_test_actionmenu_ltv_fullscreen", 8, False, message)


def internal_boot_with_drm(ve_test):
  '''
    Step 1: Check the  is HUB displayed after EPG start
    '''

  try:
    start_time = time.time()
    ve_test.log(
        "************************************* internal_boot_with_drm ****************************************************")
    mainhub = ve_test.screens.tv_filter
    status = mainhub.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_boot_with_drm", 1, status,
                            "Failed to go to mainhub. Current screen: %s" % ve_test.milestones.get_current_screen())

    ve_test.log("Mainhub is sucessfully displayed")
    total_time_duration['internal_boot_with_drm'] = str(time.time()-start_time )
    ve_test.log("Time taken to execute internal_boot_with_drm :"+ str(time.time()-start_time ) +" seconds")

  except:
      traceback.print_exc()
      formatted_lines = traceback.format_exc().splitlines()
      message = formatted_lines[-1]
      ve_test.assertmgr.addCheckPoint("internal_boot_with_drm", 2, False, message)


def internal_test_timeline(ve_test):
  """
    Sanity check of Timeline
        - to display the Timeline from the full screen via swipe left
        - to navigate in the Timeline via swipe left
        - to dismiss the timeline via the CLOSE button
    """

  try:
    start_time = time.time()
    ve_test.log(
        "************************************* internal_test_timeline ****************************************************")
    fullscreen = ve_test.screens.fullscreen
    infolayer = ve_test.screens.infolayer
    timeline = ve_test.screens.timeline
    playback = ve_test.screens.playback
    actionmenu = ve_test.screens.linear_action_menu

    '''
    Step 1: navigate to fullscreen if not already done
    '''
    # Navigate to fullscreen if not already done
    fullscreen.navigate()
    ve_test.wait(GENERIC_WAIT)
    unlock_program_if_locked(ve_test)

    if not fullscreen.is_active(timeout=3) and ve_test.milestones.get_current_screen() == 'infolayer':
        ve_test.ui.center_tap()
        ve_test.wait(GENERIC_WAIT)

    status1 = fullscreen.is_active(timeout=3)
    ve_test.assertmgr.addCheckPoint("internal_test_timeline", 1, status1, "Failed to go to fullscreen. Current screen: %s" % ve_test.milestones.get_current_screen())
    tuned_channel_id = playback.get_current_tuned()
    ve_test.wait(GENERIC_WAIT)

    '''
    Step 2: Check live video playback on tuned channel
    '''
    ve_test.log("Checking live video playback on tuned channel")
    Flag = True
    # Waiting until we get infolayer screen and if notification is found on tuned channel
    for conter in range(20):
            current_screen = ve_test.milestones.get_current_screen()
            if current_screen == "notification":
                message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
                ve_test.log("Issue in zapping the current channel")
                ve_test.log("Closing notification screen")
                ve_test.appium.tap_element(message_element)
                ve_test.wait(0.3)
                ve_test.log("Zapping to next channel")
                ve_test.ui.one_finger_swipe(ScreenActions.UP)
                ve_test.wait(0.3)

            else:
                ve_test.ui.center_tap()
                ve_test.wait(GENERIC_WAIT)
                if infolayer.is_active(timeout=0.3):
                    break

    wait_for_streaming(ve_test)
    unlock_program_if_locked(ve_test)
    ve_test.assertmgr.addCheckPoint("internal_test_timeline", 2, ve_test.milestones.getPlaybackStatus()['playbackState'] == "PLAYING", "Initials Conditions: Zapping on channel id : %s, the video is not playing" % tuned_channel_id)

    '''
    Step 3: navigate to timeline with Swipe "left" and check display
    '''
    # navigate to timeLine with Swipe "left" and check display
    ve_test.log("navigating to timeline with Swipe Left")
    flag = True
    wait_counter = 0
    while flag:
        ve_test.log(str(ve_test.milestones.get_current_screen()))
        #timeline.navigate()
        device_details = ve_test.milestones.getDeviceDetails()
        y = device_details["screen-height"]/2
        left_x = device_details["screen-width"]*0.1
        right_x = device_details["screen-width"]*0.75
        ve_test.appium.swipe_area(right_x, y, left_x, y)
        ve_test.wait(GENERIC_WAIT)
        ve_test.log(str(ve_test.milestones.get_current_screen()))
        if timeline.is_active(timeout=0.03) or wait_counter == 20:
            flag = False
        wait_counter = wait_counter + 1
    screenElement = ve_test.milestones.getElements()
    ve_test.assertmgr.addCheckPoint("internal_test_timeline", 3, str(ve_test.milestones.get_current_screen()) == "timeline", "Failed to go to timeline. Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(GENERIC_WAIT)

    '''
    Step 4; navigate to channel 3 (or next first  channel viewable) via the timeline
    '''
    # navigate to channel 3 (or next first  channel viewable) via the timeline
    elements = ve_test.milestones.getElements()
    tap_label = ve_test.milestones.get_elements_if_has_key(elements, "image_url")
    element_to_tap = tap_label[2]
    ve_test.appium.tap_element(element_to_tap)
    #ve_test.ui.tap_element
    ve_test.wait(GENERIC_WAIT)
    elements=ve_test.milestones.getElements()
    eventIdEle = ve_test.milestones.verify_element_by_key(elements, 'event_id')
    if eventIdEle is False:
        ve_test.wait(10)

    elements = ve_test.milestones.getElements()
    tap_on_next_channel = ve_test.milestones.get_elements_if_has_key(elements, "title_text")
    #tap_on_next_channel = ve_test.milestones.getElement([("title_text", "MORE INFO", "==")])
    ve_test.appium.tap_element(tap_on_next_channel[0])
    ve_test.wait(GENERIC_WAIT)

    '''
    Step 5: Check ACTION MENU is displayed , TAP on the PIP to access fullscreen and check live video playback
    '''
    # Check ACTION MENU is displayed , TAP on the PIP to access fullscreen and check live video playback
    status1 = actionmenu.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_test_timeline", 4, status1,
                            "Action Menu is not displayed. Current screen is : %s" % ve_test.milestones.get_current_screen())
    play_button = verify_play_button(ve_test)
    ve_test.log("Object for play button"+ str(play_button))
    if play_button:
        ve_test.appium.tap_element(play_button)
    else:
        ve_test.log("Play button not found in the action menu")

    wait_for_streaming(ve_test)
    playbackstatus = fullscreen.is_active(timeout=5)
    ve_test.wait(GENERIC_WAIT)
    ve_test.assertmgr.addCheckPoint("internal_test_timeline", 5,
                            (ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING"),
                            "Failed to tune to channel to the next viewable channel from timeline. video playback not working  (url = %s - current screen=%s ) " % (
                                ve_test.milestones.getPlaybackStatus()['sso']['sessionPlaybackUrl'],
                                ve_test.milestones.get_current_screen()))

    '''
    Step 6: navigate to timeline with SWIPE "left" and check display
    '''
    # navigate to timeLine with SWIPE " left" and check display
    ve_test.log("Navigating to timeline of the viewing channel with Swipe Left")
    # timeline.navigate()
    flag = True
    wait_counter = 0
    while flag:
        ve_test.log(str(ve_test.milestones.get_current_screen()))
        # timeline.navigate()
        device_details = ve_test.milestones.getDeviceDetails()
        y = device_details["screen-height"] / 2
        left_x = device_details["screen-width"] * 0.1
        right_x = device_details["screen-width"] * 0.75
        ve_test.appium.swipe_area(right_x, y, left_x, y)
        ve_test.wait(GENERIC_WAIT)
        if timeline.is_active(timeout=0.03) or wait_counter == 20:
            flag = False
        wait_counter = wait_counter + 1
    ve_test.wait(GENERIC_WAIT)
    status1 = timeline.is_active(timeout=0.3)
    ve_test.assertmgr.addCheckPoint("internal_test_timeline", 6, status1,
                            "Failed to go to timeline screen. Current screen: %s" % ve_test.milestones.get_current_screen())
    flg = True
    eventCount = 0
    while flg:
        elements = ve_test.milestones.getElements()
        timelinelist = ve_test.milestones.get_elements_if_has_key(elements, "event_id")
        length = len(timelinelist)

        if length >= 2:
            device_details = ve_test.milestones.getDeviceDetails()
            y = device_details["screen-height"] / 2
            left_x = device_details["screen-width"] * 0.1
            right_x = device_details["screen-width"] * 0.75
            ve_test.appium.swipe_area(right_x, y, left_x, y)
            #ve_test.appium.swipe_area(1526, 732, 494, 732)
            eventCount += length
            if eventCount >= 10:
                break

            flg = True
    ve_test.assertmgr.addCheckPoint("internal_test_timeline", 7, (eventCount >= 10),
                            "Number of events while doing horizontal navigation is not 10")
    '''
    Step 7: select channels in timeline 8 times
    '''
    # selecting next channel in the timeline with TAP Down
    ve_test.log("Performing timeline navigation in UP direction")
    elements = ve_test.milestones.getElements()

    flag = True
    while (flag):
        for count in range(0, 2):
            ve_test.wait(GENERIC_WAIT)
            tap_label = ve_test.milestones.get_elements_if_has_key(elements, "image_url")
            element_to_tap = tap_label[2]
            ve_test.log("Navigating to the next channel")
            ve_test.appium.tap_element(element_to_tap)
            status = timeline.is_active(timeout=3)
            ve_test.assertmgr.addCheckPoint("internal_test_timeline", 8 + count, status,
                                    "Failed to get the focus to the next channel")
            #ve_test.wait(GENERIC_WAIT)

            for counter in range(20):
                current_screen = ve_test.milestones.get_current_screen()
                # dismiss notification screen
                if current_screen == "notification":
                    message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
                    ve_test.log("Closing notification screen")
                    ve_test.appium.tap_element(message_element)
                    break

            flag = True
        else:
            flag = False
            break

    '''
    Step 8: return to full screen with TAP on CLOSE button and check display
    '''
    # Returning to full screen from timeline
    fg = True
    while fg:
        for counter in range(20):
            current_screen = ve_test.milestones.get_current_screen()
            # dismiss notification screen
            if current_screen == "notification":
                message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
                ve_test.log("Closing notification screen")
                ve_test.appium.tap_element(message_element)
                break
            else:
                ve_test.log("Returning to full screen with TAP on CROSS top right corner ")
                action = ScreenDismiss.CLOSE_BUTTON
                timeline.dismiss(action)
                ve_test.wait(0.5)
                action = ScreenDismiss.TAP
                infolayer.dismiss(action)
                ve_test.wait(0.5)
                fg = False
                break


    status = fullscreen.is_active(timeout=5)
    ve_test.assertmgr.addCheckPoint("internal_test_timeline", 16, status, "Failed to go back to fullscreen. "
                                                              "Current screen: %s" % ve_test.milestones.get_current_screen())
    ve_test.wait(GENERIC_WAIT)
    total_time_duration['internal_test_timeline'] = str(time.time() - start_time)
    ve_test.log("Time taken to execute internal_test_timeline :" + str(time.time() - start_time) + " seconds")

  except:
      traceback.print_exc()
      formatted_lines = traceback.format_exc().splitlines()
      message = formatted_lines[-1]
      ve_test.assertmgr.addCheckPoint("internal_test_timeline", 17, False, message)

INITIAL_PARENTAL_PIN = '1111'
INITIAL_THRESHOLD = '30'
WRONG_PIN = '0110'
NEW_PIN = '1234'
NEW_THRESHOLD = 'C7+'

def internal_test_parental_control(ve_test):
  '''
      Sanity check for parental control
      '''

  try:
      start_time = time.time()
      ve_test.log("**********************************************internal_test_parental_control********************************************")
      ############
      ''' First step : init Parental Limits on UPM
          Action
          - set PIN code to 1111 and ThresHold to OFF on UPM
          Checkup
          - check PIN code to 1111 and ThresHold to OFF on UPM
      '''
      fullscreen = ve_test.screens.fullscreen

      hhId = ve_test.configuration["he"]["generated_household"]
      ve_test.he_utils.setTenantValue(hhId, 'k')
      ve_test.he_utils.generate_credentials(True)

      # init PIN code to 1111
      ve_test.he_utils.setParentalRatingPin(hhId, INITIAL_PARENTAL_PIN)
      ve_test.wait(2)

      # init parental ThresHold to OFF
      ve_test.log("set parental ThresHold to " + INITIAL_THRESHOLD)
      ve_test.he_utils.setParentalRatingThreshold(hhId, int(INITIAL_THRESHOLD))
      ve_test.log("Parental Rating Threshold Has Been Set")
      ve_test.wait(2)

      preferences = ve_test.he_utils.getUserprofilePreferences(hhId)
      preferences['parentalRatingThreshold'] = INITIAL_THRESHOLD
      ve_test.he_utils.updateUserprofilePreferences(hhId, preferences)
      ve_test.wait(2)

      # control PIN value on UPM
      currentParentalpincode = str(ve_test.he_utils.getParentalRatingPin(hhId))
      ve_test.log("currentParentalpincode :"+currentParentalpincode)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 1, currentParentalpincode == INITIAL_PARENTAL_PIN,
                              "UPM PIN code init with value " + INITIAL_PARENTAL_PIN + " failed ! current PIN code is : " + currentParentalpincode)

      ve_test.log("Controlled PIN code on UPM " + currentParentalpincode)

      # control THRESHOLD value on UPM
      currentParentalThreshold = str(ve_test.he_utils.getParentalRatingThreshold(hhId))
      ve_test.log("currentParentalThreshold :"+currentParentalThreshold)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 2, currentParentalThreshold == INITIAL_THRESHOLD,
                              "UPM THRESHOLD init with value " + INITIAL_THRESHOLD + " failed ! current THRESHOLD is : " + currentParentalThreshold)

      ve_test.log("Controlled THRESHOLD on UPM " + currentParentalThreshold)

      ############
      ''' Second step : go to PIN code setting screen
          Action
          - enter in PIN code setting menu
          Checkup
          - check PIN code screen is displayed
      '''
      # enter in setting menu to change PIN code
      ve_test.log("navigate_to_settings_screen")
      ve_test.screens.settings.navigate()
      status = ve_test.screens.settings.is_active()
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 3, status, "Fail to go to settings screen. "
                                                                    "Current screen: %s" % ve_test.milestones.get_current_screen())

      elements = ve_test.milestones.getElements()
      parental_control_label= ve_test.milestones.getElementContains(elements, "CHANGE PIN CODE")
      #parental_control_label = ve_test.milestones.getElement([("title_text", "CHANGE PIN CODE", "==")], elements)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 4, parental_control_label, "No button parental control in milestone of current screen")
      #ve_test.wait(3)

      ############
      ''' 3rd step : change Parental PIN code from settings
          Action
          - enter current PIN code (1111)
          - update current PIN code with new PIN code (1234)
          Checkup
          - check PIN code value on UPM matches with changed value from setting
      '''
      # enter current pincode 1111
      count = 0
      ve_test.log("Select Change Pin Code in setting menu")
      ve_test.appium.tap_element(parental_control_label)
      ve_test.wait(2)
      elements = ve_test.milestones.getElements()
      textToVerify = str(ve_test.milestones.get_value_by_key(elements, "PincodeUpdateState"))
      while textToVerify == 'CURRENT_PINCODE' and count < 3:
          ve_test.log("entering current PIN code" + INITIAL_PARENTAL_PIN)
          ve_test.wait(2)
          ve_test.screens.pincode.enter_pin(INITIAL_PARENTAL_PIN)
          elements = ve_test.milestones.getElements()
          count = count + 1
          textToVerify = str(ve_test.milestones.get_value_by_key(elements, "PincodeUpdateState"))
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 5, textToVerify == "NEW_PINCODE",
                              "check new PIN code entry screen is displayed failed, current state is " + textToVerify)
      if textToVerify != "NEW_PINCODE":

          ve_test.log_assert(False,"check new PIN code entry screen is displayed failed")
      ve_test.log("Current Pin code state is " + textToVerify)

      # update current pincode to 1234
      ve_test.log("entering new PIN Code " + NEW_PIN)
      ve_test.wait(2)
      ve_test.screens.pincode.enter_pin(NEW_PIN)
      elements = ve_test.milestones.getElements()
      textToVerify = str(ve_test.milestones.get_value_by_key(elements, "PincodeUpdateState"))
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 6, textToVerify == "CONFIRM_NEW_PINCODE",
                              "check new PIN code confirmation screen is displayed failed, current state is " + textToVerify)
      ve_test.log("Current Pin code state is " + textToVerify)

      ve_test.log("confirming new PIN Code " + NEW_PIN)
      ve_test.wait(2)
      ve_test.screens.pincode.enter_pin(NEW_PIN)
      elements = ve_test.milestones.getElements()
      textToVerify = str(ve_test.milestones.get_value_by_key(elements, "PincodeUpdateState"))
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 7, textToVerify == 'False',
                              "check new PIN code confirmation screen is displayed failed, current state is " + textToVerify)
      ve_test.log("Pincode updated to " + NEW_PIN)

      # check new PIN code value on UPM
      currentParentalpincode = str(ve_test.he_utils.getParentalRatingPin(hhId))
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 8, currentParentalpincode == NEW_PIN,
                              "UPM PIN code update with value " + NEW_PIN + " failed ! current PIN is : " + currentParentalpincode)
      ve_test.log("UPM PIN code update with value " + currentParentalpincode)

      ############
      ''' 4th step : change Parental threshold from settings
          Action
          - enter in Parental threshold screen
          - update current threshold from OFF to 7
          Checkup
          - check threshold value on UPM matches with changed value from setting
      '''
      ve_test.log("check still present in setting screen")
      elements = ve_test.milestones.getElements()
      parental_control_lock_unlock_button = ve_test.milestones.getElement(
          [("name", "parental_control_lock_unlock_button", "==")], elements)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 9, parental_control_label,
                              "No button parental control lock-unlock in milestone of current screen")
      elements = ve_test.milestones.getElements()

      thresholdDict = ve_test.he_utils.getParentalPolicies(hhId)
      for i in thresholdDict:
          value = str(i['category'])
          if (value == "YOUNG_ADULTS"):
              value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_YOUNG_ADULTS")
          elif (value == "TEENS"):
              value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_TEENS")
          elif (value == "CHILDRENS"):
              value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_CHILDRENS")
              category_to_choose = value
          elif (value == "OFF"):
              value = ve_test.milestones.get_dic_value_by_key("DIC_SETTINGS_PARENTAL_CONTROLS_RATING_OFF")

      test_label = ve_test.milestones.getElement([("title_text", value, "==")], elements)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 10, test_label,
                              "No button %s control in milestone of current screen" % value)


      # Tap to New Threshold from UI by unlocking threshold
      ve_test.appium.tap_element(parental_control_lock_unlock_button)
      ve_test.wait(2)
      ve_test.log("entering current PIN code" + NEW_PIN)
      ve_test.wait(2)
      ve_test.screens.pincode.enter_pin(NEW_PIN)
      elements = ve_test.milestones.getElements()
      textToVerify = str(ve_test.milestones.get_value_by_key(elements, "PincodeUpdateState"))
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 11, textToVerify == 'False',
                              "PIN entered screen is displayed failed, current state is " + textToVerify)
      ve_test.log("Threshold is unlocked...")
      ve_test.wait(2)

      yaTapElement = ve_test.milestones.getElement([("title_text", NEW_THRESHOLD, "==")], elements)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 12, yaTapElement,
                              "No button " + NEW_THRESHOLD + " control in milestone of current screen")
      ve_test.wait(2)
      ve_test.appium.tap_element(yaTapElement)
      ve_test.wait(10)

      # control THRESHOLD value on UPM
      currentParentalThreshold = str(ve_test.he_utils.getParentalRatingThreshold(hhId))
      elements = ve_test.milestones.getElements()
      parentalControlSeekBar = ve_test.milestones.getElement([("name", "parental_control_seek_bar", "==")], elements)
      uiSelectedThreshold = parentalControlSeekBar['selected-threshold']
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 13, uiSelectedThreshold == int(currentParentalThreshold),
                              "Mismatch of Parental Threshold")
      ve_test.log("THRESHOLD on screen updated with : " + str(uiSelectedThreshold))
      ve_test.wait(GENERIC_WAIT)

      #going back to fullscreen and relaunching the app
      ve_test.log("Going back to TV-screen")
      ve_test.wait(GENERIC_WAIT)
      elements = ve_test.milestones.getElements()
      back_button = ve_test.milestones.getElement([("id", "back", "==")], elements)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 14, (back_button is not None),
                            "Back button not present  in setting screen")
      ve_test.appium.tap_element(back_button)
      ve_test.wait(GENERIC_WAIT)

      ve_test.log(" relaunch app so new parental threshold will be cached")
      ve_test.appium.restart_app()

      ve_test.wait(2)
      curscreen = ve_test.milestones.get_current_screen()
      if curscreen == "login":
          login_screen = ve_test.screens.login_screen
          login_screen.auto_sign_in()


      # finding a locked program
      fullscreen.navigate()
      status = fullscreen.is_active(timeout=5)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 15, status,
                              "Fail to go to  fullscreen.Current screen: %s" % ve_test.milestones.get_current_screen())
      device_details = ve_test.milestones.getDeviceDetails()
      ve_test.appium.tap(device_details['screen-width']/2,device_details['screen-height']/2)
      ve_test.wait(2)
      unlock_button = is_program_locked(ve_test)
      ve_test.wait(2)
      loop_count = 0
      while unlock_button == False or loop_count == 40:
          # zap to next channel by swipe UP
          loop_count = loop_count + 1
          current_screen = ve_test.milestones.get_current_screen()
          if current_screen == "notification":
              message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
              ve_test.log("Closing notification screen")
              ve_test.appium.tap_element(message_element)
              ve_test.wait(GENERIC_WAIT)
          ve_test.log("Current program is already unlocked. Zapping to next channel by Swipe UP to find locked program")
          ve_test.ui.one_finger_swipe(ScreenActions.UP)
          ve_test.wait(2)
          unlock_button = is_program_locked(ve_test)

      ve_test.log("Found a locked event")
      playback_status = ve_test.milestones.getPlaybackStatus()
      ve_test.log(
          "video locked= " + str(playback_status["hiddenVideo"]) + " audio locked=" + str(playback_status["muted"]))
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 16, playback_status["hiddenVideo"] == True and playback_status["muted"] == True,
                              "video and audio not locked.")
      ve_test.log("video and audio are locked")
      ve_test.appium.tap_element(unlock_button)
      ve_test.wait(2)
      youthpin = NEW_PIN
      elements = ve_test.milestones.getElements()
      parental_text = ve_test.milestones.getElement([("title_text", "PLEASE ENTER YOUR PIN CODE", "==")], elements)
      ve_test.log(str(parental_text))
      x_pos_parental_text = parental_text['x_pos']
      for digit in youthpin:
            element = ve_test.milestones.getElement([("title_text", digit, "=="), ("x_pos",x_pos_parental_text,">")], elements)
            ve_test.log_assert(element, "Key %s not found in milestone" % digit)
            ve_test.appium.tap_element(element)
            ve_test.wait(2)

      current_screen = ve_test.milestones.get_current_screen()
      if current_screen == "notification":
          message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
          ve_test.log("Closing notification screen")
          ve_test.appium.tap_element(message_element)
          ve_test.wait(GENERIC_WAIT)
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 17, is_program_locked(ve_test) == False,
                              "Program still unlocked")
      ve_test.log("Program is unlocked successfully")

      playback_status = ve_test.milestones.getPlaybackStatus()
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 18, playback_status["hiddenVideo"] == False and playback_status["muted"] == False,
                              "video and audio still locked.")
      ve_test.log("video and audio unlocked successfully")
      ve_test.wait(2)

      # checking playback status
      flag = wait_for_streaming(ve_test,time=20)
      if flag == False:
          check_notification(ve_test,True)


      # set Threshold OFF on UPM
      ve_test.log("Reset parental ThresHold to " + INITIAL_THRESHOLD)
      ve_test.he_utils.setParentalRatingThreshold(hhId, int(INITIAL_THRESHOLD))
      ve_test.wait(5)
      total_time_duration['internal_test_parental_control'] = str(time.time() - start_time)
      ve_test.log("Time taken to execute internal_test_parental_control :" + str(time.time() - start_time) + " seconds")


  except:
      ve_test.log("Reset parental ThresHold to " + INITIAL_THRESHOLD)
      ve_test.he_utils.setParentalRatingThreshold(hhId, int(INITIAL_THRESHOLD))
      ve_test.wait(5)
      traceback.print_exc()
      formatted_lines = traceback.format_exc().splitlines()
      message = formatted_lines[-1]
      ve_test.assertmgr.addCheckPoint("internal_test_parental_control", 19, False, message)


def check_notification(ve_test,dismiss_notification = False):
    curscreen = ve_test.milestones.get_current_screen()
    if curscreen == "notification":
        if dismiss_notification:
            message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
            ve_test.appium.tap_element(message_element)
            ve_test.wait(0.5)
        return True
    else:
        return False

def is_program_locked(ve_test):

    elements = ve_test.milestones.getElements()
    unlock_button = ve_test.milestones.getElement([("title_text", "UNLOCK", "==")], elements)
    if unlock_button:
        return unlock_button
    return False

def unlock_program_if_locked(ve_test):

    #ve_test.log("Checking for locked channels if any...")
    ve_test.screens.fullscreen.navigate()
    device_details = ve_test.milestones.getDeviceDetails()
    ve_test.appium.tap(device_details["screen-width"] / 2, device_details["screen-height"] / 2)
    ve_test.wait(2)
    unlock_button = is_program_locked(ve_test)

    if unlock_button != False:
        hhId = ve_test.configuration["he"]["generated_household"]
        ve_test.appium.tap_element(unlock_button)
        ve_test.wait(2)
        youthpin = str(ve_test.he_utils.getParentalRatingPin(hhId))
        elements = ve_test.milestones.getElements()
        parental_text = ve_test.milestones.getElement([("title_text", "PLEASE ENTER YOUR PIN CODE", "==")], elements)
        ve_test.log(str(parental_text))
        x_pos_parental_text = parental_text['x_pos']
        for digit in youthpin:
            element = ve_test.milestones.getElement([("title_text", digit, "=="), ("x_pos", x_pos_parental_text, ">")],
                                                elements)
            ve_test.log_assert(element, "Key %s not found in milestone" % digit)
            ve_test.appium.tap_element(element)
            ve_test.wait(2)

        current_screen = ve_test.milestones.get_current_screen()
        if current_screen == "notification":
            message_element = ve_test.milestones.getElement([("name", "text_view", "=="), ("id", "back", "==")])
            ve_test.log("Closing notification screen")
            ve_test.appium.tap_element(message_element)
            ve_test.wait(GENERIC_WAIT)
        if is_program_locked(ve_test) != False:
            ve_test.log("Program is still locked ")

def select_vod_free_asset(ve_test):

    Flag =True
    while Flag:
        elements = ve_test.milestones.getElements()
        assetlist = ve_test.milestones.get_elements_if_has_key(elements, "event_id")
        lastVODeventdetails = elements[-8]
        if assetlist:
            for count in range(len(assetlist)):
               ve_test.appium.tap_element(assetlist[count])
               ve_test.wait(GENERIC_WAIT)
               elements =ve_test.milestones.getElements()
               button = ve_test.milestones.getElement([("name", "play", "==")], elements)
               if button is None:
                  ve_test.ui.tap_element("exit")
               else:
                  ve_test.ui.tap_element("exit")
                  return  assetlist[count]
                  Flag = False
        else:
            device_details = ve_test.milestones.getDeviceDetails()
            x = device_details["screen-width"] / 2
            up_y = device_details["screen-height"] * 0.1
            down_y = device_details["screen-height"] * 0.75
            ve_test.appium.swipe_area(x, down_y, x, up_y)
            ve_test.wait(GENERIC_WAIT)
            elements1 = ve_test.milestones.getElements()
            ve_test.milestones.get_elements_if_has_key(elements1, "event_id")
            lastVODeventdetails1 = elements1[-8]
            if lastVODeventdetails == lastVODeventdetails1:
                ve_test.log(" Searched VOD asset is not found in the VOD list")
                return None
                break
            Flag = True

def verify_play_button(ve_test):
    Flag = True
    button = None
    wait_count = 1
    while Flag:
        milestones = ve_test.milestones
        elements = milestones.getElements()
        button = ve_test.milestones.getElement([("id", "play", "==")], elements)
        if button :
            Flag = False
        elif wait_count > 20:
            Flag = False
        ve_test.wait(1)
        wait_count = wait_count + 1
    return button

def wait_for_streaming(ve_test,time = 15):
    for i in range(time):
        playback_buffer_curr = ve_test.milestones.getPlaybackStatus("playbackBufferCurrent")
        # Wait for video to start streaming
        if playback_buffer_curr > 0 and ve_test.milestones.getPlaybackStatus()["playbackState"] == "PLAYING":
            ve_test.log("Video is streaming successfully")
            return  True
        ve_test.wait(1)
    return  False


TIME_THRESHOLD_FOR_VOD_PLAYING = 60
def wait_for_vodstreaming(ve_test):
    count = 0
    flag = True
    time_recorded_before_wait = time.time()
    while flag:
        playback_buffer_curr = ve_test.milestones.getPlaybackStatus("playbackBufferCurrent")
        # Wait for video to start streaming
        check_notification(ve_test, dismiss_notification=True)
        if playback_buffer_curr > 0:
            ve_test.log("Video is streaming successfully")
            flag = False
        else:
            count += 1
            if count == TIME_THRESHOLD_FOR_VOD_PLAYING:
                ve_test.log("Video playback did not happen till threshold value of SECS= %s " % str(TIME_THRESHOLD_FOR_VOD_PLAYING))
                return None
                flag = False
            else:
                ve_test.wait(1)
                flag = True
    time_recorded_after_wait = time.time()
    timeDiff = time_recorded_after_wait - time_recorded_before_wait
    return timeDiff


total_time_duration = {}

def each_case_time(ve_test):
    for key,value in total_time_duration.iteritems():
        ve_test.log("Time to execute "+key+" : "+value)

@pytest.mark.level1
def test_full_sanity():
    start_time = time.time()
    ve_test = VeTestApi("Sanity", useAssertMgr=True)
    ve_test.log("Last updated on 30-01-2017 for 2.171.1/AC17.1.1/3febfea version")
    ve_test.begin()
    ve_test.log("Time taken to complete the initialization process : "+str(time.time()-start_time) +"seconds")
    internal_boot_with_drm(ve_test)
    internal_zapping_video(ve_test)
    internal_zapping_video_swipe(ve_test)
    internal_test_hub_navigation(ve_test)
    internal_test_actionmenu_ltv_fullscreen(ve_test)
    internal_test_zaplist(ve_test)
    internal_test_vod(ve_test)
    internal_test_timeline(ve_test)
    internal_test_parental_control(ve_test)
    each_case_time(ve_test)
    ve_test.assertmgr.verifyAllCheckPoints()
    ve_test.end()




