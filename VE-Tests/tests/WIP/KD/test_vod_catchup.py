__author__ = 'smuniapp'
import pytest

from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.KD.main_hub import Showcases
from tests_framework.ui_building_blocks.screen import ScreenActions

isTVMEDIATHEK=False
TVMEDIATHEK_MENU_LABEL='TV-Mediathek'

def verify_content(ve_test):
    elements = ve_test.milestones.getElements()    
    play = ve_test.milestones.get_dic_value_by_key("DIC_ACTION_MENU_PLAY_BUTTON").upper()     
    play_button = ve_test.milestones.getElement([("title_text", play, "==")], elements)
    if play_button:
        ve_test.appium.tap_element(play_button)
        ve_test.wait(2)
        playback_status = ve_test.milestones.getPlaybackStatus()
        state = playback_status["playbackState"]
        ve_test.log_assert(state == "PLAYING", "Play streaming is failed")
        ve_test.screens.vod_action_menu.navigate()
        ve_test.screens.store.go_to_previous_screen() 
        return True
    else:
        return False 
           
def  traverse_VOD_store_catchup_verify(ve_test, node):
    global isTVMEDIATHEK
    for child in node.children:             
        if child.leaf and isTVMEDIATHEK:
            contents = child.content
            contents_size = len(contents)
            if contents_size > ve_test.screens.store.PILL_BOX_CONTENT:
                ve_test.screens.store.tap_view_all(child.name)                
                full_content_screen = ve_test.screens.full_content_screen
                ve_test.wait(2)
                full_content_screen.scroll_to_edge(ScreenActions.DOWN)
                full_content_screen.scroll_to_edge(ScreenActions.UP)
                for i in range(contents_size):                    
                    full_content_screen.tap_event_by_title(contents[i]['title'].upper())
                    if verify_content(ve_test):
                        break       
                    ve_test.screens.store.go_to_previous_screen()
            else:    
                for i in range(contents_size):
                    ve_test.screens.store.select_event_by_title(contents[i]['title'])
                    if verify_content(ve_test):
                        break
                    ve_test.screens.store.go_to_previous_screen()
            isTVMEDIATHEK=False  
        if not child.leaf:
            if child.name ==TVMEDIATHEK_MENU_LABEL:
                isTVMEDIATHEK=True
            if isTVMEDIATHEK :   
                ve_test.screens.store.select_menu_item_by_title(child.name)
                traverse_VOD_store_catchup_verify(ve_test, child) 
    ve_test.screens.store.go_to_previous_screen()  
    
                                     
@pytest.mark.MF482_VOD_catchup
def test_vod_catchup():
    ve_test = VeTestApi("store:test_vod_catchup")
    ve_test.begin()
    screen_mainhub = ve_test.screens.main_hub
    screen_mainhub.navigate()
    screen_mainhub.focus_showcase(Showcases.STORE)
    store = ve_test.screens.store  
    store.navigate()    
    rootNode = store.create_category_tree()
    traverse_VOD_store_catchup_verify(ve_test, rootNode)         
    ve_test.end()