__author__ = 'srevg'

import pytest
import datetime
import logging
import pytz
from pytz import timezone
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import EventViewPosition

' Global constants '
TIMEOUT = 5
status_bar_date_format = "%A %d. %B"
event_time_format = "%H.%M"


def get_current_local_time(ve_test, update):
    device_details = ve_test.milestones.getDeviceDetails(update)
    logging.info('UTC time-internal in millis : %s ' % (str(device_details["time-internal"])))
    logging.info('Device TimeZone : %s' % (str(device_details["timezone"])))

    utc_time_in_millis = long(device_details["time-internal"])
    current_device_tz = timezone(device_details["timezone"])
    current_utc_datetime = datetime.datetime.fromtimestamp(utc_time_in_millis/1000, pytz.UTC)
    current_local_time = current_utc_datetime.astimezone(current_device_tz)
    return current_local_time

def verify_hub_linear_events_time(ve_test, event_time):
    ve_test.screens.main_hub.navigate()
    linear_events_list = ve_test.screens.main_hub.get_events_by_type("EVENT_CONTENT_TYPE_STANDALONE")

    for linear_event in linear_events_list:
        event_time_list = linear_event["time_text"].split("to")
        if(((float)(event_time_list[0])) - ((float)(event_time_list[1]) + 2) > 0 ):
            event_time_list[1] = (float)(event_time_list[1]) + 24.00
            if(((float)(event_time_list[0])) - ((float)(event_time)) > 0):
                event_time = event_time + 24.00
            ve_test.log_assert(float(event_time_list[0]) <= event_time <= float(event_time_list[1])+2, "Main Hub event linear event time not synchronized")
        else:
            ve_test.log_assert(float(event_time_list[0]) <= event_time <= float(event_time_list[1])+2, "Main Hub event linear event time not synchronized")

def verify_guide_now_header_time(ve_test, event_time):
    screen_data = ve_test.milestones.getElements()
    now_header_element = ve_test.milestones.getElementContains(screen_data, ve_test.milestones.get_dic_value_by_key('DIC_GUIDE_NOW', 'general') , "title_text")
    now_time = now_header_element["title_text"].split(" ")
    if(float(now_time[1]) - (float(event_time))) < 0:
        now_time[1] = float(now_time[1]) + 24.00
        ve_test.log_assert(((float(now_time[1])-4) <= event_time <= float(now_time[1])+4), "Now time in Guide screen is not synchronized to current time")
    else:
        ve_test.log_assert(((float(now_time[1])-4) <= event_time <= float(now_time[1])+4), "Now time in Guide screen is not synchronized to current time")


@pytest.mark.MF1323_UTC_Clock_Synchronization
@pytest.mark.export_regression_chn
def test_verify_utc_time_verification():
    ve_test = VeTestApi("utctime:test_verify_main_hub_time")
    ve_test.begin()

    # Main Hub Time Verification
    current_local_time = get_current_local_time(ve_test,update=False)
    event_time = float(current_local_time.strftime(event_time_format))
    logging.info('Current Time HH:MM : %s' % (str(event_time)))
    verify_hub_linear_events_time(ve_test, event_time)

    # Guide Time Verification
    guide = ve_test.screens.guide
    guide.navigate()

    ve_test.wait(TIMEOUT)
    current_local_time = get_current_local_time(ve_test,update=False)
    event_time = float(current_local_time.strftime(event_time_format))
    logging.info('Current Time HH:MM : %s' % (str(event_time)))

    verify_guide_now_header_time(ve_test, event_time)

    ve_test.end()
