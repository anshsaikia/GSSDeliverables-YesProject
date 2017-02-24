___author__ = 'mtlais'

from tests_framework.ui_building_blocks.screen import Screen
from tests_framework.he_utils.he_utils import ServiceDeliveryType
import logging

# DVB subtitles can be reported asynchronously after the playback has started
DVB_SUB_MIN_PERIOD_WAIT = 5

LANG_TO_DIC = {
"eng":"DIC_SETTINGS_LANG_ENG",
"deu":"DIC_SETTINGS_LANG_FRE",
"ger":"DIC_SETTINGS_LANG_DEU",
"fre":"DIC_SETTINGS_LANG_FRE",
"fra":"DIC_SETTINGS_LANG_FRE",
"por":"DIC_SETTINGS_LANG_POR",
"ita":"DIC_SETTINGS_LANG_ITA",
"heb":"DIC_SETTINGS_LANG_HEB",
"spa":"DIC_SETTINGS_LANG_SPA",
"none" : "DIC_NONE"
}

class DvbSubtitles(Screen):
    def __init__(self, test):
        Screen.__init__(self, test, "DvbSubtitles")

    # helper function to zap to the dvb sub channel
    def play_live_dvb_sub(self,dvb_sub_filter):
        logging.info("zapping to DVB sub channel")
        id = self.test.he_utils.getContent("LINEAR", dvb_sub_filter, ServiceDeliveryType.ABR, 0)
        sek = self.test.he_utils.services[id]['serviceEquivalenceKey']

        zaplist = self.test.screens.zaplist
        zaplist.tune_to_channel_by_sek(sek, True)
        self.test.wait(DVB_SUB_MIN_PERIOD_WAIT)


    # helper function to play a dvb sub vod
    def play_vod_dvb_sub(self,dvb_sub_vod_asset):
        logging.info("Play VOD DVB sub asset")
        self.test.screens.search.navigate()
        if self.test.platform == "iOS":
            self.test.screens.search.input_text_into_search_field(dvb_sub_vod_asset)
        else:
            self.test.screens.search.input_event_into_search_filed_and_search(dvb_sub_vod_asset)
        suggestions = self.test.screens.search.get_all_suggestions()
        self.test.log_assert(len(suggestions) > 0, "search for \"%s\" did not return anything" % dvb_sub_vod_asset)
        self.test.screens.search.navigate_to_action_menu_by_event_title(suggestions[0]["title_text"])
        self.test.screens.vod_action_menu.verify_active()
        self.test.screens.vod_action_menu.play_asset()
        self.test.wait(DVB_SUB_MIN_PERIOD_WAIT)


    # lang is the iso code
    def settings_select_subtitle_lang(self,lang):
        logging.info("navigate to ksettings")
        self.test.screens.ksettings.navigate()

        logging.info("selecting %s as subtitle" % lang)
        subtitleValue = self.test.milestones.get_dic_value_by_key("DIC_SETTINGS_SUBTITLES").upper()
        langValue = self.test.milestones.get_dic_value_by_key(self.lang_to_dic(lang)).upper()

        select_settings = self.test.screens.ksettings.select(subtitleValue, langValue)
        self.test.log_assert(select_settings, "can not select "+langValue+ " in "+subtitleValue)

        logging.info("Back to main hub")
        self.test.screens.ksettings.go_to_previous_screen()
        self.test.screens.tv_filter.verify_active()

    def lang_to_dic(self,lang):
        return LANG_TO_DIC.get(lang, "")
