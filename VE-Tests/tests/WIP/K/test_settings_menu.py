import logging

from tests_framework.ui_building_blocks.K.library_filter import FilterType
from tests_framework.ui_building_blocks.KD.notification import NotificationStrings
from tests_framework.ve_tests.ve_test import VeTestApi

def test_settings_disk_quota():
    # vgw test utils must be installed for running this test
    from vgw_test_utils.settings import Settings
    ve_test = VeTestApi("test_settings_disk_quota")
    ve_test.begin()

    Settings['household_id'] = ve_test.configuration["he"]["generated_household"]
    upmDeviceId = ve_test.he_utils.getDeviceIdFromDeviceAndHH(None, Settings['household_id'])
    Settings["device_id"] = upmDeviceId

    # Reduce disk quota for percentage to rise up faster
    ve_test.he_utils.set_households_disk_quota(Settings['household_id'],"1000")

    startUsedDiskPercentage = ve_test.screens.ksettings.navigate_and_get_disk_usage()
    endUsedDiskPercentage = startUsedDiskPercentage
    logging.info("usedDiskPercentage=%d", startUsedDiskPercentage)
    ve_test.log_assert(startUsedDiskPercentage <= 100, "usedDiskPercentage doesn't exist")

    discardEvent = ''
    foundEventToRecord = False
    minimum_remaining_time_minutes = 3
    maximum_remaining_time_minutes = 15
    for remaining_time_minutes in xrange(minimum_remaining_time_minutes, maximum_remaining_time_minutes):
        # Find ABR channel to record
        target_channel_id, event_title = ve_test.he_utils.get_channel_to_record_current_event(
            remaining_time_minutes = remaining_time_minutes,
            discardEvent = discardEvent,
            ignore_series = True,
            minLogicalChannelNumber = 1)

        if (ve_test.screens.search.search_and_try_to_open_action_menu_of_first_suggestion(':'.join(event_title.split(':')[:-2]))):
            foundEventToRecord = True
            break
        else:
            discardEvent = event_title

    if foundEventToRecord:
        # Start recording
        ve_test.screens.linear_action_menu.record_current_event(event_title)
        ve_test.wait(60) # Waiting a minute to have a recording

        # Go to Recording filter and stop recording
        logging.info("Go to library filter:%s expected to find event:%s", event_title, FilterType.RECORDINGS)
        ve_test.screens.library_filter.navigate()

        # Stop Recording
        ve_test.ui.verify_and_press_button_by_title(title=event_title, operator='==_')
        ve_test.screens.linear_action_menu.verify_active()
        ve_test.screens.linear_action_menu.verify_and_press_stop_button()

        # Verify and press YES on stop recording confirmation screen
        ve_test.screens.notification.verify_notification_message(NotificationStrings.STOP_RECORDING.value)
        ve_test.screens.notification.get_and_tap_notification_button("DIC_YES")

        # Wait for recording to actually stop
        ve_test.he_utils.wait_for_recording_status(event_title, status='RECORDED')

        # Check disk usage after recording
        endUsedDiskPercentage = ve_test.screens.ksettings.navigate_and_get_disk_usage()
        logging.info("usedDiskPercentage =%d", endUsedDiskPercentage)

    else:
        logging.error('Could not find event to record')
    ve_test.log_assert(startUsedDiskPercentage < endUsedDiskPercentage, "Quota did not change after recording (recording failed?)")
    ve_test.end()
