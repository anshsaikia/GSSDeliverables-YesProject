import time
import logging
import xml.etree.ElementTree as et
import requests

class TA(object):

    def __init__(self, test):
        self.test = test
        __ta = None

    #THIS WILL SEND LEARN ACTION FOR ASSETS TYPED 6 CLASSIFICATION AND REFRESH THE TA TOPLIST
    #RETURN RESULT TRUE OR FALSE
    def initialize_top_list(self):
        from vgw_test_utils.settings import Settings
        __ta = "http://{ta_address}:{ta_port}/".format(**Settings)

        self.params = dict(
            curr_time = int(time.time() * 1000),
            **Settings
        )
        initresult = False
        if self.test.platform == 'Android':
            clienttype = '203'
        else:
            clienttype = '303'
        self.params = dict(
            clientType=clienttype,
            region1=(Settings['cmdc_region'].split("~"))[0],
            region2=(Settings['cmdc_region'].split("~"))[1],
            lang="eng",
            catalogueId=str(self.test.cmdc_queries.get_catalogId()),
            hhid=self.test.he_utils.default_credentials[0],
            **Settings)

        #Get CatalogId
        #Return CatalogId
        catId = self.test.cmdc_queries.get_catalogId()
        assert (catId is not 0), "No Cat ID Found by CMDC"
        #Get Root ClassificationId from CatalogId
        #Return Root ClassificationId
        rootclassId = self.test.cmdc_queries.get_root_classificationID_from_catalogId(catId)
        assert rootclassId!=0, "No rootclassID Found by CMDC"
        #Get Classification Type 6 in root classification from CatalogID and Root CatalogId
        #Return Classification Tree
        classType6List = self.test.cmdc_queries.get_classificationType6_from_catId_rootclassId(catId,rootclassId)
        assert classType6List!=[], "No Classification type6 in catalog"
        #Get all assets ID & InstanceID of all 6 type classificationId from Classification List
        #Return assets Id & InstanceId as dict
        diccmdcassetsids = self.test.cmdc_queries.get_assetIds_from_Classif_List(catId, classType6List)
        assert diccmdcassetsids!={}, "No assets typed type6 in catalog"
        successed_learnaction = 0
        learn_r = ""
        #SEND LEARN ACTIONS FOR ALL ASSETS PREVIOUSLY COLLECTED
        for contentItemId,contentItemInstanceId in diccmdcassetsids.iteritems():
            learn_action_url = "http://{ta_address}:{ta_port}/RE/REController.do?clientType={clientType}&contentSourceId=2&method=learnAction&subscriberId={hhid}&contentItemId=%s&contentItemInstanceId=%s_{catalogueId}&actionId=10".format(**self.params)%(contentItemId,contentItemInstanceId)
            try:
                learn_r = self.test.requests.get(learn_action_url)
                if learn_r.status_code == 200:
                    successed_learnaction += 1
                else:
                    logging.warning("WARN : LEARN ACTION REQUEST RESPONSE : %s" % learn_r.text)
            except requests.ConnectionError as err:
                logging.exception("LEARN ACTION REQUEST TO TA : %s\nFAILURE : %s " % (learn_r.text, err))

        #INVOKE FULLREFRESH OF TA TOPLIST
        invoke_url = "http://{ta_address}:{ta_port}/jmx-console/HtmlAdaptor?action=invokeOpByName&name=RecommendationEngineMonitor:name=topListTask&methodName=fullRefresh".format(**self.params)
        successed_invoke = 0
        invoke_r = ""
        try:
            invoke_r = self.test.requests.get(invoke_url)
            if invoke_r.status_code == 200:
                successed_invoke += 1
            else:
                logging.warning("WARN : INVOKE REQUEST RESPONSE : %s" % invoke_r.text)
        except requests.ConnectionError as err:
            logging.exception("INVOKE REQUEST TO TA : %s\nFAILURE : %s " % (invoke_r.text,err))

        #RETURN RESULT
        if (successed_learnaction > 0) & (successed_invoke > 0):
            initresult = True
            return initresult
        else:
            initresult = False
            return initresult


    def get_toplist_contentId_list(self):
        from vgw_test_utils.settings import Settings
        contentIdList=[]
        if self.test.platform == 'Android':
            setpanel = '201'
        else:
            setpanel = '301'
        self.params = dict(
            panel=setpanel,
            region1=(Settings['cmdc_region'].split("~"))[0],
            region2=(Settings['cmdc_region'].split("~"))[1],
            lang="eng",
            catalogueId=str(self.test.cmdc_queries.get_catalogId()),
            #catalogueId="16384",
            hhid=self.test.he_utils.default_credentials[0],
            **Settings)

        toplist_url = "http://{ta_address}:{ta_port}/RE/REController.do?method=getTopListAsContent&clientType={panel}&subscriberId={hhid}&applyMarketingBias=false&allowPreviousRecommendations=false&maxResults=9&topListId=MP_T_VOD%5E{catalogueId}&contentSourceId=2&region={region1}&region={region2}".format(
            **self.params)

        logging.info("toplist request : %s", toplist_url)
        try:
            toplist_resp = self.test.requests.get(toplist_url)
            xmlList = self.get_contentid_list_from_xml(toplist_resp.content)
        except :
            return []
        return xmlList

    def get_contentid_list_from_xml(self, string):
        data = []
        root = et.fromstring(string)
        recommendations = root.find('recommendations')
        if recommendations is None:
            return data
        for recommendation in recommendations.findall('recommendation'):
            reco_dict = {}
            for el in recommendation.getchildren():
                reco_dict[el.tag] = el.text
            data.append(reco_dict)
        contentidlist = [item['contentItemId'] for item in data]
        return contentidlist