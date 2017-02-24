__author__ = 'bbagland'

import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KSTB.playback import LIVE_INACTIVITY_TYPE

' Global constants '
SHORT_DURATION = 5*60
LONG_DURATION = 24*60*60

def make_report(ve_test):
    ve_test.screens.playback.kpi_to_html(LIVE_INACTIVITY_TYPE)

def check_status(ve_test, duration):
    for i in range(0, duration/60):
       ve_test.wait(60)
       ve_test.screens.playback.verify_streaming_playing_kpi(LIVE_INACTIVITY_TYPE)

@pytest.mark.sanity
@pytest.mark.FS_Live
@pytest.mark.ethernet
@pytest.mark.wifi
@pytest.mark.LV_L3
def test_inactivity_short():
    ve_test = VeTestApi("test_inactivity_short")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    check_status(ve_test, SHORT_DURATION)
    # Call KPI measurement request in order to externalize the KPI to jenkins
    make_report(ve_test)
    ve_test.end()

@pytest.mark.robustness
@pytest.mark.FS_Live
@pytest.mark.ethernet
@pytest.mark.wifi
@pytest.mark.LV_L4
def test_inactivity_long():
    ve_test = VeTestApi("test_inactivity_long")
    ve_test.begin(screen=ve_test.screens.fullscreen)
    check_status(ve_test, LONG_DURATION)
    # Call KPI measurement request in order to externalize the KPI to jenkins
    make_report(ve_test)
    ve_test.end()

