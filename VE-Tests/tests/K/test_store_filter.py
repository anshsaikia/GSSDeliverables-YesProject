
from tests_framework.ve_tests.ve_test import VeTestApi
import pytest
import logging


@pytest.mark.store_filter
def test_shop_in_shop_row():
    # Scenario test #1 - #2:
    #
    # Step1: From Hub - application main screen Enter Store.Home screen
    # Step2: check `CHANNEL STORES` row is displayed as seen in the expected result image
    #        Channel stores posters are displayed for this menu including Store Name (Category Name, as a text)
    #        presented under the store poster. 'See all' option will appear ONLY in case there are more than
    #        10 stores ingested(Studio to  update
    #        Right / Left scrolling options are available in order to view the rest of the channel stores
    #        check if the first event in feature poster change to the last tuned channel
    # Step3: in case there are more than n stores ingested Tap on the option to 'See all' to display Store.FullContent
    #        screen. Channel stores posters are displayed including Store Name (Category Name, as a text) presented
    #        under the store poster. Up/Down scrolling options are available in order to view the rest of the channel
    #        stores. screen title (top left on the screen) indicates the previous screen <Store and Channel Stores
    #        Checking the posters is done only manually
    #        Only if there are more then n (n=9 based on code) stores up down scrolling (less then n there is no
    #        scrolling - you need to tap on a specific element). Note: pre requisite is that there will be more then n shops

    test = VeTestApi("test_shop_in_shop_row")
    test.begin()
    store = test.screens.store_filter
    store.navigate()
    root_node = store.create_category_tree()
    ctap_shops = store.extract_shops_from_tree(root_node)

    store.navigate_to_channel_stores_row()
    ui_shops = store.scroll_and_return_elements("VodChannels")
    logging.info("Shops from UI are: {}".format(ui_shops))

    store.verify_shops(ui_shops, ctap_shops)
    test.end()


@pytest.mark.store_filter
def test_store_row_filter():
    # Scenario of tests #3 - #4:
    #
    # Step1: From Store.Home OR Store.FullContent: select a store and tap on it to enter Store.Filter screen
    #        ( tap STORE -> DISNEY )
    #
    # Step2: verify all classifications according to ctap are displayed ( Highlights, Shows, Games, Mangas etc. displayed)
    #        and there are assets associated to it
    # Step3: verify Store Logo is displayed on the left top corner of the screen ( DISNEY word displayed )
    # Step4: verify that if more than 6 assets displayed in classification -
    #       1. 'See all' option will appear ( for example in HIGHLIGHTS section is displayed SEE ALL because more than 6 assets )
    #       2. Tap on the option to See all on one of the genres to display Store.FullContent screen
    #       3. Verify screen title(top left on the screen) indicates the previous screen ( "HIGHLIGHTS" for example )
    #       4. Verify assets with their posters are displayed (this should be done manually)
    # Step5: Up / Down scrolling options are available in order to view the rest of the assets
    #        (up down scrolling will be made only if there are more then x assets x = 18?) -
    #        this is not checked because not enough assets, but checked previously by Guy Itzhaki
    # Step6: In auto e2e tests from Store.Home select the first store
    #        Checking the store log can be by checking its contains an image
    #        (this requires adding the logo url to the milestones)
    # Step7: check if the first event in feature poster change to the last tuned channel

    test = VeTestApi("test_store_row_filter")
    test.begin()
    store = test.screens.store_filter
    ctap_info = store.create_category_tree()
    ctap_shops = store.extract_shops_from_tree(ctap_info)

    store.navigate()
    store.navigate_to_channel_stores_row()
    store.tap_channel_stores_element()
    test.screens.store_filter.verify_channel_logo([d for d in ctap_shops[0].branding_media if d['type'] == 'logo_top'][0]['url'])
    for section in ctap_shops[0].children:
        # case of assets
        test.screens.store_filter.verify_content_full_section(section, ctap_shops[0].name, store)
    test.end()


@pytest.mark.store_filter
def test_verify_store_row():
    test = VeTestApi("test_verify_store_row")
    test.begin()
    store = test.screens.store_filter
    store.navigate()
    tree = store.create_category_tree()

    for section in tree.children:
        # case of assets
        if (section.type == "content_full") or (section.type == "category_promotions"):
            test.screens.store_filter.verify_content_full_section(section, tree.name, store)

        # case of sub categories
        elif section.type == "category_list":
            test.screens.store_filter.verify_category_list_section(section)

    test.end()


def test_shop_in_shop_asset_action_menu():
    # Scenario test #5
    # From (Store.Filter) - a Channel store -  Tap to select an asset under the store
    # Verify asset action menu has the correct Store logo next to the asset poster as seen on the image on the right
    # (need to be retrieved from milestones)
    test = VeTestApi("test_shop_in_shop_asset_action_menu")
    test.begin()
    store = test.screens.store_filter
    search = test.screens.search
    store.navigate()
    store.navigate_to_channel_stores_row()
    store.tap_channel_stores_element()  # enter first store.
    top_genre = store.get_top_section_scroller()
    assets = store.get_events_by_section_channel_stores(top_genre["section_title_header"])
    test.appium.tap_element(assets[0])  # tap on the first asset on the top scroller.
    event_name = store.verify_channel_logo_in_asset_action_menu()

    # Now Find the same event in search screen and verify the action menu channel logo url

    search.navigate()
    search.input_text_into_search_field(event_name)
    search.tap_on_the_first_result()
    asset_element = test.milestones.getElement(
        [("event_source", "EVENT_SOURCE_TYPE_VOD", "=="), ("section", "STORE", "==")])
    test.appium.tap_element(asset_element)
    store.verify_channel_logo_in_asset_action_menu()
    test.end()
