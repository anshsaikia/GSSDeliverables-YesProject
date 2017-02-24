__author__ = 'srevg'

from tests_framework.ve_tests.ve_test import VeTestApi


def test_programme_rating():
    ve_test = VeTestApi("test_mock_device_upgrade_required")
    ve_test.begin()
    elements = ve_test.milestones.getElements()
    channelId = elements[1]["channelId"]

    ve_test.log("Getting parental Ratings from Ctap")
    eventInfo = ve_test.ctap_data_provider.get_current_event(channelId, "id")
    rating_ctap = eventInfo['content']['parentalRating']['value']

    ve_test.log("Navigate to Action Menu")
    ve_test.screens.linear_action_menu.navigate()

    elements = ve_test.milestones.getElements()
    action_menu_element = ve_test.milestones.getElement([("title_text", "RATINGS", "_)")], elements)
    title_text = action_menu_element['title_text']
    string = title_text.encode('utf-8').split()
    index = string.index("RATINGS")+1
    rating = string[index]

    ve_test.log("Comparing the rating retrieved from ctap and milestone")
    ve_test.log_assert(str(rating) in str(rating_ctap), "Rating mismatch")
    ve_test.log("The Ratings matched")
    ve_test.end()