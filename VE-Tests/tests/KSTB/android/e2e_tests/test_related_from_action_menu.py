# -*- coding: utf-8 -*-
from tests_framework.ve_tests.assert_mgr import AssertMgr
from tests_framework.ve_tests.ve_test import VeTestApi

import pytest
import logging
import sys

local_debug = True 

'''Globals'''
INFOLAYER_TIMEOUT = 6
GENERIC_WAIT = 2
MAX_STORE_ITEMS = 8
#serie_list = ["serie","artung"]         # tag 'serie' for asset

# Actions for current event on current channel
actionlist_video_live_current_event = ['SUMMARY', 'RECORD', 'WATCH LIST', 'RELATED', 'LIKE', 'ADD TO FAVORITES']
actionlist_video_live_current_event2 = ['INHALT', 'AUFNEHMEN', 'WATCH LIST', 'ÄHNLICHE', 'LIKE', 'ZU FAVORITEN HINZUFÜGEN']

popularContents= ["MixedEditorialPopular"]
related_item_lang = ["RELATED","ÄHNLICHE"]



def goto_store_related(ve_test):

    # Check all action list items
    for nb in range(0, MAX_STORE_ITEMS):
        selected_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")       # which item is focused ?
        if selected_item in popularContents:  #related_item_lang:
            break                               # found 'MixedEditorialPopular' item: no more search
        elif local_debug:
            logging.info("goto_store_related: we are on item:  %s"%(selected_item))
        ve_test.move_towards('down')               # less moves than 'up' to go to TESTS

    else:       # no break exit from 'for loop'
        return False

    if local_debug:
        logging.info("goto_store_related: we are on '%s' item at pos:(%d)"%(selected_item,nb))
    ve_test.validate_focused_item(2)           # go into the item to find related
    
    
    # focus assets (on the first line only) to find one with related
    previous_asset =""    
    while previous_asset != False:
        selected_asset = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "selected_item")       # which asset is focused ?
        if previous_asset == selected_asset:  # end of line reached
            logging.info("no related on this line of assets => error")
            return False
        previous_asset = selected_asset         # to verify end of line

        if local_debug:
            logging.info("goto_store_related: we are on asset:  %s go to it"%(selected_asset))
        ve_test.validate_focused_item(2)                       # go into the asset to find related
        items_list = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements, "titleItems")  # ex: "[SUMMARY, PLAY, WATCH LIST, related?, LIKE]",
        
        logging.info("items list= %s"%(items_list))
        for item in related_item_lang:
            logging.info("verify item: " + item)
            if item in items_list:
                logging.info("related item found in the list, go to focus it")
                max_moves = 10
                while max_moves:
                    focused_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")  # go to focus RELATED
                    if focused_item not in related_item_lang:
                        ve_test.move_towards('up',1)
                    else:
                        return True         # focus RELATED item
                    max_moves -= 1          # security
                return False                # Related in the list but unfocusable
        logging.info("no related on this asset, => next")
        ve_test.go_to_previous_screen(1)       # back to assets screen
        ve_test.move_towards('right',1)        # focus next asset

    return False            # no 'related' found

@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.FS_Related
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_related_from_live_video():
    '''
    Verify that the related assets can be found from the live screen
    '''
    ve_test = VeTestApi("test_related_from_live_video")

    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.fullscreen)

    # Go to Initial Conditions: fullscreen
    ve_test.log_assert(ve_test.milestones.get_current_screen(), "Fail to go to fullscreen")
    ve_test.wait(INFOLAYER_TIMEOUT)

    reload(sys)
    sys.setdefaultencoding("utf-8")             # to treat string as utf8 (ascii by default) to avoid crash with deutch text containing Ü or Ä ...

    logging.info("Verify that ActionMenu can be launch by OK key press on full screen")
    status = ve_test.screens.action_menu.navigate()
    ve_test.log_assert(status, "Fail to launch the ActionMenu")
    ve_test.wait(GENERIC_WAIT)

    # Check all action list items 
    found = False
    items_list = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "titleItems")        # list of items on screen

    for item in related_item_lang:
        logging.info("verify item: " + item)
        if item in items_list:
            logging.info("related item found in the list, go to focus it")
            max_moves = 10
            while max_moves:
                focused_item = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_item")  # go to focus RELATED
                if focused_item not in related_item_lang:
                    ve_test.move_towards('up',1)
                else:
                    found = True
                    break         # focus RELATED item
                max_moves -= 1    # security
            break
    
    else:       # exit from 'for loop' without  break -> no related
        assertmgr.addCheckPoint("test_related_from_live_video", 1, False, "no RELATED item on live found!")
        if local_debug:
            logging.info("related item not found in the list: error !")
            logging.info("list : %s"%(items_list))
            
    if found:                                   # related item was found       
        nbAssets = 0
        firstAssetName = ""
        assetName = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_asset")
        while assetName != firstAssetName and assetName != "":  # loop to count assets
            asset_info = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "infolines")
            if asset_info == False:
                if local_debug:
                    logging.info("trfl: bad asset, no infolines !")
                break                           # not a related asset. STRANGE !
            nbAssets += 1
            ve_test.move_towards('right',1)        # next asset
            if firstAssetName == "":
                firstAssetName = assetName      # the first
            if local_debug:
                logging.info("trfl: %d) %s"%(nbAssets,assetName))    
            if nbAssets >= 50:
                assertmgr.addCheckPoint("test_related_from_live_video", 4, False, "too much assets (>50) !")
                break
            assetName = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(),"focused_asset")   # next asset
       
        #for nb in range(0,nbAssets):
        #test.validate_focused_item(1)           # go into the asset to get info

        if nbAssets == 0:
            assertmgr.addCheckPoint("test_related_from_live_video", 5, False, "no related asset !")
            if local_debug:
                logging.info("trfl: no related asset")
        
    else:
        assertmgr.addCheckPoint("test_related_from_live_video", 3, False, "fail to go into related item") 
        if local_debug:
            logging.info("trfl: fail to find related item from live")
    
    assertmgr.verifyAllCheckPoints()
    ve_test.end()
    logging.info("##### End test_related_from_live_video #####")


@pytest.mark.non_regression
@pytest.mark.FS_ActionMenu
@pytest.mark.FS_Related
@pytest.mark.dummy
@pytest.mark.LV_L3
def test_related_from_store():
    '''
    Verify that the related assets can be found from the store screen
    '''
    ve_test = VeTestApi("test_related_from_store")
    assertmgr = AssertMgr(ve_test)
    ve_test.begin(screen=ve_test.screens.fullscreen)

    # Go to store
    status = ve_test.screens.main_hub.navigate()
    status = ve_test.screens.main_hub.navigate_to_store()
    if status == False:
        assertmgr.addCheckPoint("test_related_from_store", 1, status, "Fail to go to Store")

    reload(sys)
    sys.setdefaultencoding("utf-8")             # to treat string as utf8 (ascii by default) to avoid crash with deutch text containing Ü or Ä ...


    status = goto_store_related(ve_test)
                
    if status:            
        first_related_asset = ve_test.milestones.get_value_by_key(ve_test.milestones.getElements(), "focused_asset")
        if first_related_asset == False or first_related_asset == "":
            assertmgr.addCheckPoint("test_related_from_store", 4, False, "related asset list is empty")
        else:
            logging.info("first_related_asset= %s"%(first_related_asset))
        
    else:
        assertmgr.addCheckPoint("test_related_from_store", 2, False, "fail to go into related item") 
        if local_debug:
            logging.info("trfs: fail to find related item from store")

    
    assertmgr.verifyAllCheckPoints()
    ve_test.end()
    logging.info("##### End test_related_from_store #####")

