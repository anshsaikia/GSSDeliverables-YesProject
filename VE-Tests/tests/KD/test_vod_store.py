__author__ = 'paln'

import pytest
import json
from tests_framework.ve_tests.ve_test import VeTestApi
from operator import itemgetter
from vgw_test_utils.IHmarks import IHmark
from tests_framework.ui_building_blocks.KD.full_content_screen import SortType


# 1. Verify navigation from VIDEOTHEK to Store
# 2. Traverse all store categories and their sub categories
# 3. Verify events in all leaf-category
# 4. Tap on a event and verify it leads to action-menu screen
# 5. verify "VIEW ALL" is present, when contents size is greater PILL box max size. if preset navigate it and:
#    a. Verify that sort filters are present
#    b. Verify first 15 events are sorted by sort category
#    c. Verify tapping on events lead to action-menu screen

@IHmark.O_Android
@IHmark.MF260
@pytest.mark.MF260_VOD_store_screen
@pytest.mark.export_regression_chn
@pytest.mark.regression
@pytest.mark.export_regression_MF260_VOD_store_screen
@pytest.mark.level2
def test_traverse_and_verify_all_categories():
    ve_test = VeTestApi("store:test_traverse_and_verify_all_categories")
    ve_test.begin()

    store = ve_test.screens.store

    "Navigation"
    store.navigate()
    rootNode = store.create_category_tree()

    store.display_tree(rootNode)
    store.traverse_VOD_Store(rootNode)
    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF550
@pytest.mark.MF550_shopInshop_branding
@pytest.mark.export_regression_MF550_shopInshop_branding
def test_shop_and_shop_all():
    ve_test = VeTestApi("Shopinshop:test_traverse_and_verify_all_categories")
    ve_test.begin()

    store = ve_test.screens.store
    search = ve_test.screens.search

    "Navigation"
    store.navigate()
    rootNode = store.create_category_tree()

    store.display_tree(rootNode)
    store.traverse_VOD_Store(rootNode, shopInShop=True)

    sisAsset = None
    for category in rootNode.children:
        if category.type == "category_shop":
            sisGenre = category.children[0]
            sisAsset = sisGenre.content[0]['title']
            break

    ve_test.log_assert(sisAsset, "no shop in shop assets in headend")

    "check sis asset in search"
    search.navigate()
    search.input_text_into_search_field(sisAsset)
    search.tap_on_the_first_result()
    ve_test.wait(2)
    elements = ve_test.milestones.getElements()
    sisElement = ve_test.milestones.getElement([("title_text", sisAsset.upper(), "=="),("name", "event_view", "==")], elements)
    ve_test.log_assert(sisElement, "no shop in shop event in results")
    ve_test.wait(2)
    ve_test.appium.tap_element(sisElement)

    action_menu = ve_test.screens.vod_action_menu
    action_menu.verify_active()
    ve_test.wait(2) # otherwise the action menu has first dummy event
    action_menu.compare_vod_sis_actionmenu_metadata()

    ve_test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF260
@pytest.mark.MF260_VOD_store_screen
@pytest.mark.regression
@pytest.mark.export_regression_MF260_VOD_store_screen
def test_traverse_mini():
    ve_test = VeTestApi("store:test_traverse_mini")
    ve_test.begin()

    store = ve_test.screens.store

    "Navigation"
    store.navigate()
    rootNode = store.create_category_tree()

    store.display_tree(rootNode)
    store.traverse_VOD_Store(rootNode,miniTraverse=True)
    ve_test.end()


@IHmark.MF2224
@IHmark.FS_VE_VOD
@IHmark.F_Sort_VOD
@IHmark.O_Three_Rivers
def test_editorial_sorting():
    ve_test = VeTestApi("store:test_editorial_sorting")
    ve_test.begin()

    store = ve_test.screens.store
    drama_category = 'node:urn:spvss:ih:kd:term:store:Genres:Drama'

    "Navigation"
    store.navigate()
    store.select_menu_item_by_title('Genres')
    store.select_scroller_item_by_title('Drama')
    store.verify_full_content_and_sort(drama_category, SortType.EDITORIAL)

    ve_test.end()


@IHmark.MF2224
@IHmark.FS_VE_VOD
@IHmark.F_Sort_VOD
@IHmark.O_Three_Rivers
def test_shop_in_shop_editorial_sorting():
    ve_test = VeTestApi("store:test_shop_in_shop_editorial_sorting")
    ve_test.begin()

    store = ve_test.screens.store
    shop_category = 'urn:spvss:ih:cisco:term:SIS0s0000.0'

    "Navigation"
    store.navigate()
    store.select_menu_item_by_title('DE:DISNEY')
    store.select_menu_item_by_title('DE:HIGHLIGHTS')
    view_all_element = ve_test.milestones.getElement([("time_text", "VIEW ALL", "==")], ve_test.milestones.getElements())
    ve_test.log_assert(view_all_element, "no view all event in results")
    ve_test.wait(2)
    ve_test.appium.tap_element(view_all_element)
    store.verify_full_content_and_sort(shop_category, SortType.EDITORIAL)

    ve_test.end()


@IHmark.MF2224
@IHmark.FS_VE_VOD
@IHmark.F_Sort_VOD
@IHmark.O_Three_Rivers
def test_sushi_editorial_sorting():
    ve_test = VeTestApi("store:test_editorial_sorting")
    ve_test.begin()

    store = ve_test.screens.store
    classification_sushi = 'node:urn:spvss:ih:kd:term:store:TV-Mediathek:RTLNOW:Highlights'

    "Navigation"
    store.navigate()
    store.select_menu_item_by_title('TV-Mediathek')
    store.select_scroller_item_by_title('RTLNOW') # sub-genre in which there is editorial sorted sushi bar

    # Get list of sushi assets from device
    window_width, window_height = ve_test.milestones.getWindowSize()
    y = window_height / 2
    left_x = window_width - 100
    right_x = 10

    titleList = []
    elements = store.test.milestones.getElements()
    while elements is not None:
        for element in elements:
            if 'event_source' in element and element['event_source'] == 'EVENT_SOURCE_TYPE_VOD':
                if element['title_text'] not in titleList:
                    titleList.append(element['title_text'])

        store.test.mirror.swipe_area(left_x, y, right_x, y, 800)
        elements_after_swiping = store.test.milestones.getElements()
        if elements == elements_after_swiping:
            break
        else:
            elements = elements_after_swiping

    # Compare sushi assets in UI with list of assets received from CMDC
    if ve_test.platform.upper() == 'ANDROID':
        catalog_id = ve_test.he_utils.getCatalogueId('ANDROID')
    else:
        catalog_id = ve_test.he_utils.getCatalogueId('IOS')
    response = ve_test.he_utils.get_cmdc_assets(catalog_id, classification_sushi, 'seq')
    dictReply = response.json()

    i = 0
    for i in range(0,len(titleList)):
        ve_test.log_assert(dictReply['contents'][i]['title'].upper() == titleList[i], "Comparison failed")

    ve_test.end()


@IHmark.MF2224
@IHmark.FS_VE_VOD
@IHmark.F_Sort_VOD
@IHmark.O_Three_Rivers
def test_shop_in_shop_sushi_editorial_sorting():
    ve_test = VeTestApi("store:test_shop_in_shop_sushi_editorial_sorting")
    ve_test.begin()

    store = ve_test.screens.store
    shop_category = 'urn:spvss:ih:cisco:term:SIS0s0000.0'

    "Navigation"
    store.navigate()
    store.select_menu_item_by_title('DE:DISNEY')
    store.select_menu_item_by_title('DE:HIGHLIGHTS')

    # Get list of sushi assets from device
    window_width, window_height = ve_test.milestones.getWindowSize()
    y = window_height / 2
    left_x = window_width - 100
    right_x = 10

    titleList = []
    elements = store.test.milestones.getElements()
    while elements is not None:
        for element in elements:
            if 'event_source' in element and element['event_source'] == 'EVENT_SOURCE_TYPE_VOD':
                if element['title_text'] not in titleList:
                    titleList.append(element['title_text'])

        store.test.mirror.swipe_area(left_x, y, right_x, y, 800)
        elements_after_swiping = store.test.milestones.getElements()
        if elements == elements_after_swiping:
            break
        else:
            elements = elements_after_swiping

    # Compare sushi assets in UI with list of assets received from CMDC
    if ve_test.platform.upper() == 'ANDROID':
        catalog_id = ve_test.he_utils.getCatalogueId('ANDROID')
    else:
        catalog_id = ve_test.he_utils.getCatalogueId('IOS')
    response = ve_test.he_utils.get_cmdc_assets(catalog_id, shop_category, 'seq')
    dictReply = response.json()

    i = 0
    for i in range(0, len(titleList)):
        ve_test.log_assert(dictReply['contents'][i]['title'].upper() == titleList[i], "Comparison failed")

    ve_test.end()
