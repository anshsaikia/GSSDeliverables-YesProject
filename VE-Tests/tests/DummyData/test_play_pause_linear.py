__author__ = 'bwarshaw'



'''
def DONT_RUN_test_play_pause(ve_test):
    start_app_signin(ve_test, "test_play_pause")

    ve_test.android_mock_server.set_mock_data("bundle_action_menu_live", "bundle_action_menu_play_pause.json")
    ve_test.android_mock_server.set_mock_data("bundle_fullscreen_live", "some_file_to_cause_failure")

    ve_test.building_blocks.tune_to_channel_by_sek(103)

    ve_test.building_blocks.navigate_to_action_menu()

   # elements = ve_test.milestones.getElements()
   # compared_file_path = "KD/android/DummyData/compare_data/screen_data_action_menu_play_pause_" + \
   #                      getListElementByKey(elements, "device") + ".json"
   # compareMilestonesWithFile(False, elements, compared_file_path)

    ve_test.android_mock_server.compare_milestones_to_reference("screen_data_action_menu_play_pause")
'''