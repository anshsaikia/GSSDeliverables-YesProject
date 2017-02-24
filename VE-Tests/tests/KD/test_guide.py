import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

__author__ = 'dpedro'

# Navigate to and from Guide 10 times commit
@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF249
@IHmark.MF1377
@pytest.mark.MF249_TV_Filter_Guide
@pytest.mark.MF1377_TV_Filter_Display_14_day_guide
@pytest.mark.level2
def test_guide_navigation_10_times():
	my_test = VeTestApi("Guide:test_guide_navigation_10_times")
	my_test.begin()
	guide = my_test.screens.guide
	fullscreen = my_test.screens.fullscreen

	for reapeatIndex in range(0,10):
		guide.navigate()
		fullscreen.navigate()
	my_test.end()


''' Navigate to Guide->
 Raise the Action Menu of the centered EVENT-> Navigate back to Guide
 Start playback, from the centered EVENT->wait 1 minute-> Navigate back to Guide
 Raise the Action Menu of the centered CHANNEL-> Navigate back to Guide
 Start playback, from centered CHANNEL-> wait 1 minute-> Navigate back to Guide
 Repeat all 15 times.	commit'''
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1377
@pytest.mark.guide_stability
@pytest.mark.MF1377_TV_Filter_Display_14_day_guide
@pytest.mark.stability
def test_guide_Stability():

	my_test = VeTestApi("Guide:test_guide_Stability")
	my_test.begin()
	guide = my_test.screens.guide
	fullscreen = my_test.screens.fullscreen
	for reapeatIndex in range(1,15):
		'''Navigate to Guide'''
		guide.navigate()
		'''Raise the Action Menu of the centered EVENT and then navigate back'''
		my_test.wait(1)
		guide.showAndVerifyActionMenu()
		guide.navigate()
		'''Play the current EVENT from the event list and wait 60 seconds'''
		my_test.wait(1)
		guide.playCurrentCenteredEvent()
		my_test.wait(60)
		'''Navigate to Guide again'''
		guide.navigate()
		'''Raise the Action Menu of the centered Channel and then navigate back'''
		#my_test.wait(1)
		#guide.CurrentCenteredChannelActionMenu()
		#guide.navigate()
		'''Play the current CHANNEL from the Channel list and wait 60 seconds'''
		my_test.wait(1)
		guide.playCurrentCenteredChannel()
		my_test.wait(60)
	my_test.end()

#Cyclical vertical scrolling in Grid section
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF249
@IHmark.MF1377
@pytest.mark.export_regression_MF249_TV_Filter_Guide
@pytest.mark.MF249_TV_Filter_Guide
@pytest.mark.MF1377_TV_Filter_Display_14_day_guide
#@pytest.mark.regression
def test_guide_Cyclical_vertical_scrolling():
	'''Navigate to guide
		Go to Grid section
		Store the first channel
		Swipe up in the CHANNEL List, till you get to the first channel.
		Repeat but with swipe Up
		Navigate back to Guide to make sure we start fresh
		Swipe up in the EVENT List, till you get to the first channel.
		Repeat but with swipe Up
		'''

	my_test = VeTestApi("Guide:test_guide_Cyclical_vertical_scrolling")

	my_test.begin()
	guide = my_test.screens.guide
	guide.navigate()
	#Scrolling Down in the CHANNEL List
	guide.checkCyclicChannelList(guide.actionTypes.DOWN)
	#Scrolling Up in the CHANNEL List
	guide.checkCyclicChannelList(guide.actionTypes.UP)
	#Navigatre to Guide again to make sure we start fresh
	guide.navigate()
	#Scrolling Down in the EVENT List
	guide.checkCyclicEventList(guide.actionTypes.DOWN)
	#Scrolling Up in the EVENT List
	guide.checkCyclicEventList(guide.actionTypes.UP)
	my_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF1377
@pytest.mark.MF1377_TV_Filter_Display_14_day_guide
#@pytest.mark.regression
def test_guide_Jump_to_day():
	'''Navigate to Guide -> Switch to Grid section -> Save leftmost time -> Open days menu ->Verify:Guide screen shown, day selection menu Open
	Jump to the 14th day->Swipe Right till you reach the last events in the grid->
	Tap on Grid events area->Verify: Guide screen shown, day selection menu closed'''

	my_test = VeTestApi("Guide:test_guide_Jump_to_day")

	my_test.begin()
	guide = my_test.screens.guide
	#Navigate to Guide screen
	guide.navigate()
	#Save the current time
	guide.storeCurrentTime()
	#Switch to date view, verify the switch to date view and scroll to the next day
	guide.jumpToDay(2)
	my_test.wait(2)

	my_test.log_assert(guide.checkAllEventsAreNotCurrent(),"Current events still on guide")
	#Make sure the Header has changed back to Time view
	headerDisplay = guide.isDatesVisible()
	my_test.log_assert(headerDisplay == False, "Expected the header to switch back to time\hours display, but remained in days!")
	my_test.end()
