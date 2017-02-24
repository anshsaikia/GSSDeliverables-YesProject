# -*- coding: utf-8 -*-
''' Constants '''

''' WAIT '''
GENERIC_WAIT = 2
SMALL_WAIT = 0.5
LONG_WAIT = 5
TEN_MINUTES_WAIT = 600
FIFTEEN_MINUTES_WAIT = 900

''' TIMEOUT '''
WAIT_TIMEOUT = 10
INFOLAYER_TIMEOUT = 6
SCREEN_TIMEOUT = 15
DCA_TIMEOUT = WAIT_TIMEOUT + INFOLAYER_TIMEOUT

''' SCREENS NAMES '''
SCREEN_GUIDE = 'guide'
SCREEN_MAIN_HUB = 'main_hub'
SCREEN_ACTION_MENU = 'action_menu'

'''SCREEN CONSTANTS'''
FULLCONTENT_ASSETS_PER_LINE_2_BY_3 = 6
#TO DO
FULLCONTENT_ASSETS_PER_LINE_16_BY_9 = 0
FULLCONTENT_MIXED_ASSETS_LINE_WIDTH = 56

MAX_ACTIONS = 10

''' FULLSCREEN LOCKED '''
LOW_RATING = 10
MID_RATING = 14
HIGH_RATING = 20
NO_PC_THRESHOLD = -1
PC_CHANNEL = "6"
PC_CHANNEL2 = "8"

g_no_suggestions_msg_text = "No suggestion available."
supported_sorts = ['BY SOURCE', 'ALPHABETICAL']


''' HUB '''

HUB_TV = "LIVE TV"

''' ACTION MENU '''

A_SUMMARY = 'SUMMARY'
A_PLAY = 'PLAY'
A_RECORD = 'RECORD'
A_WATCHLIST = 'WATCH LIST'
A_BACK_TO_LIVE = 'BACK_TO_LIVE'
A_LIKE = 'LIKE'
A_RELATED = 'RELATED'
A_ADD_TO_FAVOURITE = 'ADD TO FAVORITES'
A_BUY_ALL_EPISODES = 'BUY ALL EPISODES'
A_RENT = 'RENT'
A_LANGUAGE = 'LANGUAGES'

''' SEARCH '''
g_keyboard0_chars_num = (u'\ue00f', u'\ue019', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
g_keyboard1_chars = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                     'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
g_keyboard1_chars_deu = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                         'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
g_keyboard2_chars_deu = (u'\xc4', u'\xd6', u'\xdc', u'\xdf')

g_no_suggestions_msg_text = "No suggestion available."

supported_sorts = ['BY SOURCE', 'ALPHABETICAL']


''' ACTION MENU '''

dummy_actionlist_video_live_current_event = ['SUMMARY', 'BACK TO LIVE', 'RECORD', 'LANGUAGES', 'ADD TO FAVORITES', 'WATCH LIST', 'RELATED', 'LIKE']

#  Actions for current event on current channel on guide
actionlist_video_guide_current_event = ['SUMMARY', 'PLAY', 'RECORD', 'WATCH LIST', 'LIKE', 'ADD TO FAVORITES']
actionlist_video_guide_current_event_audios = ['SUMMARY', 'PLAY', 'RECORD', 'WATCH LIST', 'LIKE', 'LANGUAGES', 'ADD TO FAVORITES']

# Actions for current event on current channel on timeline
actionlist_video_timeline_current_event = ['SUMMARY', 'PLAY', 'RECORD', 'WATCH LIST', 'LIKE', 'ADD TO FAVORITES']
actionlist_video_timeline_current_event_audios = ['SUMMARY', 'PLAY', 'RECORD', 'WATCH LIST', 'LIKE', 'LANGUAGES', 'ADD TO FAVORITES']

# Actions for current event on non current channel
actionlist_video_live_current_event_other_channel = ['SUMMARY', 'PLAY', 'RECORD', 'WATCH LIST', 'LIKE', 'ADD TO FAVORITES']
# Actions for future event (current channel or not)
actionlist_video_live_future_event = ['SUMMARY', 'RECORD', 'WATCH LIST', 'LIKE', 'ADD TO FAVORITES']

actionlist_vod_event = ['SUMMARY', 'BUY ALL EPISODES', 'PLAY', 'RENT', 'WATCH LIST', 'RELATED', 'LIKE']
dummy_actionlist_vod_event = ['SUMMARY', 'BUY ALL EPISODES', 'PLAY', 'RENT', 'WATCH LIST', 'RELATED', 'LIKE']

actionlist_optional_item = ['LANGUAGES']

dummy_audio_list = ["ENGLISH", "FRENCH", "RUSSIAN", "GERMAN"]
dummy_sublist_optional_item = {
    actionlist_optional_item[0]: dummy_audio_list
}

''' GRID focus state '''
GRID_STATE = {
    1: 'NOW',
    2: 'NEXT',
    3: 'TONIGHT',
    4: 'GRID'
}

GRID_STATE_NOW = 1
GRID_STATE_NEXT = 2
GRID_STATE_TONIGHT = 3
GRID_STATE_GRID = 4

# Specific channels
channel_number_classic_1 = 1
channel_number_classic_2 = 4
channel_number_without_logo = 201
channel_number_with_several_audio = 44
channel_number_with_closed_caption = 40
channel_number_with_dvb_sub = 45

# SETTINGS 
DEFAULT_FOCUSED_INDEX = 0

list_sysinfo = ['CONNECTIVITY', 'SYSTEM INFORMATION', 'LOG OUT']
list_sysinfo2 = ['CONNECTIVITY', 'SYSTEM INFORMATION', 'AUSLOGGEN']
SETTINGS_SYSINFO_CONNECTIVITY_INDEX = 0 # CONNECTIVITY index
SETTINGS_SYSINFO_SYSINFO_INDEX = 1      # SYSTEM INFORMATION index: settings/system information/system information
SETTINGS_SYSINFO_LOGOUT_INDEX  = 2      # LOGOUT index

list_preferences_eng = ['DISK SPACE MANAGEMENT','LANGUAGE','CLOSED CAPTION', 'AUDIO', 'SUBTITLES']
list_preferences_ger = ['DISK SPACE MANAGEMENT','SPRACHE','CLOSED CAPTION', 'AUDIO', 'UNTERTITEL']
PREF_DISK_SPACE_MNGT = 0        # disk space management index
PREF_LANGUAGE_INDEX = 1         # prefered language index
PREF_CLOSED_CAPTION_INDEX = 2   # prefered CC index
PREF_AUDIO_INDEX = 3            # index for going to menu settings/preferences/audio
PREF_SUBTITLE_INDEX = 4         # prefered subtitle index

list_settings_eng = ['PREFERENCES', 'PIN CODE AND PARENTAL CONTROL', 'SYSTEM INFORMATION']
list_settings_ger = ['VORLIEBEN', 'PIN UND JUGENDSCHUTZ', 'SYSTEM INFORMATION']
SETTINGS_SYSINFO_INDEX = 2    # SYSTEM INFORMATION index: settings/system information

list_sysinfo_eng = ['CONNECTIVITY', 'SYSTEM INFORMATION', 'LOG OUT']
list_sysinfo_ger = ['CONNECTIVITY', 'SYSTEM INFORMATION', 'AUSLOGGEN']

list_languages = ['English', 'Deutsch', 'Português']
list_audio_language_eng = ['English', 'German', 'French', 'Italian', 'Spanish', 'Portuguese']
list_audio_language_ger = ['Englisch', 'Deutsch', 'Franzosisch', 'Italienisch', 'Spanisch', 'Portugiesisch']

#[u'None', u'English', u'German', u'French', u'Italian', u'Spanish', u'Portuguese'],
list_subtitles_eng = ['None', 'English', 'German', 'French', 'Italian', 'Spanish', 'Portuguese']
list_subtitles_ger = ['Keine', 'Englisch', 'Deutsch', 'French', 'Italian', 'Spanish', 'Portugiesisch']

list_closedcaption_eng = ['None', 'cc1']
list_closedcaption_ger = ['Keine', 'cc1']

list_devices_languages = ['eng', 'deu', 'por']
list_items_languages = ["LANGUAGE","SPRACHE","IDIOMA"]

list_pin_parental_control_eng = ['PIN MANAGEMENT', 'PARENTAL CONTROL']
list_pin_parental_control_ger = ['JUGENDSCHUTZ-PIN ÄNDERN', 'ELTERLICHE KONTROLLE']

CHANGE_PARENTAL_PIN_INDEX = 0
MODIFY_PARENTAL_THRESHOLD_INDEX = 1
list_parental_threshold_policy = ['OFF', 'YA17+', 'T13+', 'C7+']
list_parental_threshold_policy2 = ['OFF', 'YA17+', 'T13+', 'C7+']
POLICY_OFF_INDEX = 0
POLICY_YA17_INDEX = 1
POLICY_T13_INDEX = 2
POLICY_C7_INDEX = 3

list_pcpe_maxrating = ['30', '17', '13', '7']

#''' HUB '''
HUB_TV = "LIVE TV"
HUB_LIBRARY_NAMES_BY_LANG = ["LIBRARY","SAMMLUNG"]
HUB_ITEMS_NAME_ENG = {"LIVE TV":"fullscreen", "GRID":"guide", "LIBRARY":"filter", "STORE":"action_menu", "SEARCH":"search", "SETTINGS":"filter"}
HUB_ITEMS_NAME_DEU = {"LIVE": "fullscreen", "PROGRAMM": "guide", "SAMMLUNG": "filter", "STORE":"action_menu", "SUCHE":"search", "EINSTELLUNGEN":"filter"}

#''' LIBRARY '''
LIBRARY_ITEMS = [ "full_content", "full_content", "full_content" ]
LIBRARY_ITEMS_NAME_ENG = [ "MANAGE RECORDINGS", "SCHEDULED RECORDING", "FAILED RECORDINGS" ]

#''' TRESHOLD '''
MIN_THRESHOLD = "C7+"
MIN_THRESHOLD_UPM = "7"

MAX_THRESHOLD = "OFF"
MAX_THRESHOLD_UPM = "30"


# Values taken from the CTAP implementation
dico_languages = {
    'eng': "ENGLISH",
    'nor': "NORWEGIAN",
    'ukr': "UKRANIAN",
    'rus': "RUSSIAN",
    'por': "PORTUGUESE",
    'tha': "THAI",
    'swe': "SWEDISH",
    'ita': "ITALIAN",
    'spa': "SPANISH",
    'hun': "HUNGARIAN",
    'tam': "TAMIL",
    'kad': "KANNADA",
    'tel': "TELUGU",
    'hin': "HINDI",
    'ger': "GERMAN",
    'deu': "GERMAN",
    'fre': "FRENCH",
    'fra': "FRENCH",
    'ara': "ARABIC",
    'tur': "TURKISH",
    'heb': "HEBREW",
    'chi': "CHINESE",
    'zho': "CHINESE",
    'cze': "CZECH",
    'ces': "CZECH",
    'dan': "danish",
    'dut': "DUTCH",
    'nld': "DUTCH",
    'fin': "FINNISH",
    'pol': "POLISH",
    'urd': "URDU",
    'gre': "GREEK",
    'ell': "GREEK",
    'rum': "ROMANIAN",
    'ron': "ROMANIAN",
    'per': "PERSIAN",
    'fas': "PERSIAN",
    'lit': "LITHUANIAN"
}
