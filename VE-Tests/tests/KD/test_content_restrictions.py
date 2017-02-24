import pytest
from tests_framework.ve_tests.ve_test import VeTestApi

__author__ = 'tmelamed'

# Short swipe up/down on full screen should tune and raise info layer	Fullscreen -> short swipe down/up -> verify (Info Layer)	commit
@pytest.mark.MF1409_Content_Restriction
@pytest.mark.unsupported
def test_check_geo_location_restriction():

    my_test = VeTestApi("content restriction: geo location restriction")
    my_test.begin()

    zaplist = my_test.screens.zaplist
    zaplist.tune_to_channel_by_sek("162",verify_streaming_started=False)
    my_test.screens.playback.verify_streaming_stopped()

    #verify Geo location error message
    element = my_test.milestones.getElement([("name", "text_view","==" )])
    print element
    my_test.log_assert("geographic" in element["title_text"],"Geo restriction message is not displayed")

    my_test.end()

# Tap on non playing channel from zap list or tv hub should tune and raise info layer	Zaplist/Tv Hub -> tap non playing channel -> verify (Info Layer)
@pytest.mark.MF1409_Content_Restriction
@pytest.mark.unsupported
def test_check_onNet_restriction():

    my_test = VeTestApi("content restriction: onNet restriction")
    my_test.begin()

    zaplist = my_test.screens.zaplist
    zaplist.tune_to_channel_by_sek("161",verify_streaming_started=False)
    my_test.screens.playback.verify_streaming_stopped()

    #verify Geo location error message
    print my_test.milestones.getElements()
    element = my_test.milestones.getElement([("name", "text_view","==" )])
    print element
    my_test.log_assert("vodafone" in element["title_text"],"onNet restriction message is not displayed")

    my_test.end()

# Tap (info layer is shown) should hide the info layer. Info Layer -> tap ->verify (NO Info Layer)	commit

@pytest.mark.MF1409_Content_Restriction
@pytest.mark.unsupported
def test_check_blacklist_restriction():

    my_test = VeTestApi("content restriction: blacklist restriction")
    my_test.begin()

    zaplist = my_test.screens.zaplist
    zaplist.tune_to_channel_by_sek("160",verify_streaming_started=False)
    my_test.screens.playback.verify_streaming_stopped()

    #verify Geo location error message
    element = my_test.milestones.getElement([("name", "text_view","==" )])
    my_test.log_assert(element and "title_text" in element, "BlackList restriction message is not displayed")
    my_test.log_assert("Hot spot" in element["title_text"],"BlackList restriction message is not displayed")

    my_test.end()

