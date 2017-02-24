import pytest
import operator
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark
import logging


def check_ltv_related_recommendation_requests(test,VIPproviderName):
    my_test = test
    linearactionmenu = my_test.screens.linear_action_menu
    notification = my_test.screens.notification
    timeline = my_test.screens.timeline
    providerName = VIPproviderName
    dictAssetsNameList = {}
    dictServiceInfo = {}
    # Get serviceId list with provider name
    dictServiceInfo = my_test.cmdc_queries.get_serviceInfo_forall_services()
    my_test.log_assert(len(dictServiceInfo) != 0, 'No information in Service info map')
    for svcId in dictServiceInfo.keys():
        if str(dictServiceInfo[svcId][2]) != str(providerName):
            del dictServiceInfo[svcId]
    my_test.log_assert(len(dictServiceInfo) != 0, 'No service with provider : %s %s' % (providerName,str(providerName)))
    # Get only 4 Services from dictServiceInfo
    dictServiceInfofour = dict(sorted(dictServiceInfo.iteritems(), key=operator.itemgetter(1), reverse=True)[:4])
    # Get all related assets from service list
    for svcId in dictServiceInfofour.keys():
        relatedAssetsIdList = []
        timeline.navigate()
        serviceEk = dictServiceInfofour[svcId][1]
        # go to ltv service
        my_test.wait(2)
        timeline.tune_to_channel_by_sek(str(serviceEk),False)
        my_test.wait(2)
        screen = my_test.milestones.get_current_screen()
        #Check if notification displayed in case of no video streaming
        if screen == "notification":
            notification.dismiss()
        my_test.wait(2)
        linearactionmenu.navigate()
        relatedAssetsIdList = linearactionmenu.get_all_ltv_related_elements()
        my_test.log_assert(len(relatedAssetsIdList) > 0, 'No related assets for SEK : %s' % str(serviceEk))
        logging.info('\n \n %s assets in relatedAssetsIdList :\n %s', len(relatedAssetsIdList), relatedAssetsIdList)
        #if my_test.platform == "Android":
        for relatedasset in relatedAssetsIdList:
            logging.info("relatedasset : %s" % relatedasset)
            eventdetails = ((relatedasset["event_id"]))
            eventid=(eventdetails.replace(':__', '%3A%2F%2F'))[:-4]
            eventprovidername=my_test.cmdc_queries.get_provider_from_eventId(eventid)
            my_test.log_assert(eventprovidername is not None, 'No providerName: %s' % eventprovidername)
            exclusionprovider = ["RELATED1", "RELATED2", "RELATED3","RELATED4"]
            if providerName in exclusionprovider:
                my_test.log_assert(eventprovidername == providerName, "Provider %s found for EventID %s, expected : %s" %(eventprovidername,eventid,providerName))
            else:
                my_test.log_assert(eventprovidername not in exclusionprovider, "Provider %s found for EventID %s, expected : %s" %(eventprovidername,eventid,providerName))

@IHmark.LV_L2
@IHmark.MF2048
@IHmark.MF2407
@pytest.mark.MF2048_LTV_Related_Vip_Content_Provider
@pytest.mark.MF2407_LTV_Exclusion_Restrict_Content_Provider
@pytest.mark.regression
@pytest.mark.export_regression_LTV_Related_Vip_Content_Provider
def test_check_ltv_related_recommendation_requests():
    my_test = VeTestApi("related_content:specified_linear_provider")
    my_test.begin()
    providerName = "RELATED1"
    logging.info("RELATED1 CHECK")
    check_ltv_related_recommendation_requests(my_test, providerName)
    logging.info("RELATED2 CHECK")
    providerName = "RELATED2"
    check_ltv_related_recommendation_requests(my_test, providerName)
    logging.info("KD CHECK")
    providerName = "KD"
    check_ltv_related_recommendation_requests(my_test, providerName)
    my_test.end()