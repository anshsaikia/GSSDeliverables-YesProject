import pytest
import logging
import json
import pprint
from tests_framework.ve_tests.ve_test import VeTestApi
from tests_framework.ui_building_blocks.screen import ScreenActions
from vgw_test_utils.settings import Settings


logger = logging.getLogger("cmdc_utils")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(name)-5s %(levelname)-8s : %(message)s')

#Get CatalogId from cmdc region
#Return CatalogId
def get_catalogId(test):
    if test.platform == 'Android':
        catId_url = "http://{cmdc_address}:{cmdc_port}/cmdc/region/{cmdc_region}/device/ANDROID/catalogueId".format(**Settings)
    else:
        catId_url = "http://{cmdc_address}:{cmdc_port}/cmdc/region/{cmdc_region}/device/IOS/catalogueId".format(**Settings)

    catId_r = test.requests.get(catId_url)
    logger.info("Get CatalogueId : %s", catId_r)
    try:
        resp = json.loads(catId_r.text)
        logger.info(pprint.pformat(resp))
        catId =  resp['catalogueId']['id']

        return catId
    except: return 0

def get_editorial_contentId_list(test):
    contentIdList=[]
    catalog_id = str(get_catalogId(test))
    #Get root classificationId
    #url = "http://{cmdc_address}:{cmdc_port}/cmdc/classification?catalogueId={catalogue_id}".format(**self.params)
    url = "http://{cmdc_address}:{cmdc_port}/cmdc/classification?catalogueId=".format(**Settings) + catalog_id
    result = test.requests.get(url)
    logger.info("Get root classificationId : %s", result)
    try:
        resp = json.loads(result.text)
        logger.info(pprint.pformat(resp))
        root_classification_id = resp['classifications'][0]['classificationId']

        #Get classificationId for editorial:
        url = "http://{cmdc_address}:{cmdc_port}/cmdc/classification/%s/classification?catalogueId=%s".format(**Settings)%(root_classification_id,catalog_id)
        result = test.requests.get(url)
        logger.info("Get editorial classificationId : %s", result)
        resp = json.loads(result.text)
        logger.info(pprint.pformat(resp))
        for index in range(len(resp['classifications'])):
            if resp['classifications'][index]['type'] == 41:   #41 = classification editorial type
                editorial_classification_id = resp['classifications'][index]['classificationId']
                break

        #Get editorial contents:
        url = "http://{cmdc_address}:{cmdc_port}/cmdc/content?classificationId=%s&catalogueId=%s".format(**Settings)%(editorial_classification_id,catalog_id)
        result = test.requests.get(url)
        logger.info("Request : "+url)
        logger.info("CMDC Region : {cmdc_region}".format(**Settings) )
        logger.info("Get editorial contentId : %s", result)
        resp = json.loads(result.text)
        logger.info("Resp : "+str(resp))
        for index in range(len(resp['contents'])):
            contentIdList.append(resp['contents'][index]['id'])
        logger.info("Editorial contentId list : %s", contentIdList)

        return contentIdList
    except : return []


@pytest.mark.vod_hub
def test_vod_hub():
    assets = {}
    finished = False
    test = VeTestApi("test_vod_hub")
    test.begin()
    store = test.screens.store_filter
    store.navigate()

    #elements = store.scroll_and_return_elements("RECOTESTS")
    if test.platform == "iOS":
        store.scroll_top_section()
    store.scroll_to_top_of_screen()

    while not finished:
        finished = True
        elements = test.milestones.getElements()
        for element in elements:
            logging.info('elements : %s' %elements)
            if ('name' in element and element['name'] == 'event_view') and ('section' in element and element['section'] == 'poster'):
                if element['event_id'] not in assets:
                    assets[element['event_id']] = element
                    finished = False

        test.log_assert(assets, "No asset found in store")
        window_width, window_height = test.milestones.getWindowSize()
        test.appium.swipe_element(assets.values()[0], window_width / 2, ScreenActions.LEFT)


    editorial = get_editorial_contentId_list(test)

    assetsContentId = assets.keys()

    contentId=[]
    for i in range(len(assetsContentId)):
        contentId.append(assetsContentId[i].split('~')[0])

    logging.info('==========================')
    logging.info('List of assets contentId in HUB device : %s' % contentId)
    logging.info('List of assets from cmdc request : %s' % editorial)
    logging.info('lenght editorialinters: %s lenght contentid : %s ' % (len(set(editorial).intersection(contentId)),len(contentId)))

    # check the smallest list is included in largest one
    l1 = []
    l2 = []
    if len(editorial) > len(contentId):
        l1 = editorial
        l2 = contentId
    else:
        l1 = contentId
        l2 = editorial

    test.log_assert(len(set(l1).intersection(l2)) == len(l2), "Editorial recommendations don't match")

    test.end()
