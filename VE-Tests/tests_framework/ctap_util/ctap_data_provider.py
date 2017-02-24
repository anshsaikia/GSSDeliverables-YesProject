__author__ = 'nahassan'

import json
import pytz.reference
import urllib
import logging
import time
import calendar
import pytz.reference
from datetime import datetime
from tests_framework.ve_tests.tests_conf import DeviceType
from tests_framework.ui_building_blocks.KD.full_content_screen import SortType

'''Globlas'''
CTAP_GRID_API = "/ctap/r1.3.0/agg/grid"
CTAP_CONTENT_API = "/ctap/r1.3.0/contentInstances/"
CTAP_AGG_CONTENT_API = "/ctap/r1.3.0/agg/content/"
CTAP_CATEGORIES_API = "/ctap/r1.3.0/categories/"
CTAP_PINCODE_STATUS_API = "/ctap/r1.3.0/household/me/pins/parental/status"
CTAP_SEARCH_SUGGESTIONS_API = "/ctap/r1.3.0/keywords/suggest"
CTAP_RECOMMENDATIONS_API = "/ctap/r1.3.0/agg/recommendations"
CTAP_RECOMMENDATIONS_PREF_API = "/ctap/r1.3.0/agg/recommendations/preference"
CTAP_ON_AIR_CHANNELS_API = "/ctap/r1.3.0/channels?offset=0&limit=11"

class CtapDataProvider(object):
    def __init__(self, ve_test):
        self.ve_test = ve_test
        self.configuration = ve_test.configuration
        self.milestones = ve_test.milestones

    def get_ctap_url(self, api_name, payload=None):
        base_url = self.configuration["he"]["applicationServerIp"]
        if api_name == 'GRID':
            start_time = datetime.now()
            limit = '255' #max channels to return
            channel_offset = '0' #first channel index
            durationParam = '&duration=7200' #2 hours schedule
            eventsLimitParam = ''
            pastEventsLimitParam = ''
            if payload:
                if 'start_time' in payload:
                    start_time = payload['start_time']
                if 'duration' in payload:
                    durationParam = '&duration=' + payload['duration']
                if 'limit' in payload:
                    limit = payload['limit']
                if 'offset' in payload:
                    channel_offset = payload['offset']
                if 'eventsLimit' in payload:
                    eventsLimitParam = '&eventsLimit=' + payload['eventsLimit']
                    durationParam = ''
                if 'pastEventsLimit' in payload:
                    pastEventsLimitParam = '&pastEventsLimit=' + payload['pastEventsLimit']


            start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S.000")
            offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone

            if (offset < 0):
             timeZN = "%2b" + str(offset / 60 / 60 *-1).zfill(2) + "00"
            else:
             timeZN = "%2d" + str(offset / 60 / 60).zfill(2) + "00"

            options = "?startDateTime="+start_time+timeZN + durationParam + "&carousel=true&isAdult=false&offset="+channel_offset+"&limit=" + limit + eventsLimitParam + pastEventsLimitParam

            return "http://" + base_url + CTAP_GRID_API + options

        elif api_name == 'ACTION_MENU':
            return "http://" + base_url + CTAP_CONTENT_API + urllib.quote_plus(payload["event_id"])
        elif api_name == 'CATEGORIES':
            return "http://" + base_url + CTAP_CATEGORIES_API + urllib.quote_plus(payload["category_id"])
        elif api_name == 'AGG_CONTENT':
            options = "?categoryId=" + payload['categoryId']
            if payload:
                if 'sort' in payload:
                    sort = payload['sort']
                    options = options + "&sort=" + sort
                if 'limit' in payload:    
                    limit = payload['limit']
                    options = options + "&limit=" + limit +"&isErotic=true"
                if 'offset' in payload:
                    offset = payload['offset']
                    options = options + "&offset=" + offset
            return "http://" + base_url + CTAP_AGG_CONTENT_API + options
        elif api_name == 'RECOMMENDATIONS':
            options = "?source=" + payload['source']
            if payload:
                if 'limit' in payload:
                    limit = payload['limit']
                    options = options + "&limit=" + limit
                if 'isAdult' in payload:
                    isAdult = payload['isAdult']
                    options = options + "&isAdult=" + isAdult
            return "http://" + base_url + CTAP_RECOMMENDATIONS_API + options
        elif api_name == 'LINEAR_RECOMMENDATIONS':
            options = "?source=ltv"
            if payload:
                if 'limit' in payload:
                    limit = payload['limit']
                    options = options + "&limit=" + limit
            options = options + "&isAdult=false&isErotic=true"
            return "http://" + base_url + CTAP_RECOMMENDATIONS_PREF_API + options
        elif api_name == 'PINCODE_STATUS':
            return "http://" + base_url + CTAP_PINCODE_STATUS_API
        elif  api_name == 'SEARCH_SUGG':
            options = "?q=" + payload['q'] + "&limit="  + payload['limit'] + "&type=" + payload['type']
            return "http://" + base_url + CTAP_SEARCH_SUGGESTIONS_API + options
        elif api_name == 'ON_AIR_LIST':
            return "http://" + base_url + CTAP_ON_AIR_CHANNELS_API
        return None

    def send_request(self, api_name, payload):
        url = self.get_ctap_url(api_name, payload)
        hh_id = self.configuration["he"]["generated_household"]
        sg_header =  self.ve_test.he_utils.create_session_guard_header(hh_id)
        logging.info("url = %s \n header= %s" % (url,sg_header))
        data = self.ve_test.he_utils.send_getRequest(url, sg_header)
        return data

    def get_current_event_by_lcn(self, lcn):
       return self.get_current_event(lcn, "logicalChannelNumber")

    def get_current_event_by_id(self, channelId):
       return self.get_current_event(channelId, "id")

    def get_current_event(self, channel_id, channel_id_type):
        data = self.send_request("GRID", None)

        event = None
        for channel in data["channels"]:
            if str(channel[channel_id_type]).strip()== str(channel_id).strip():
                schedule = channel["schedule"]
                if len(schedule) >= 1:
                    event = schedule[0]
                return event
        return event


    def get_title_from_event(self, event):
        title = event['content']["title"]
        return title

    def get_airingTime_from_event(self, event):

        start = event["startDateTime"]
        duration = event["duration"]

        timeString = self.formatTimes(start, duration)

        return  timeString

    def formatTimes(self, startTime, duration):
        device_details = self.milestones.getDeviceDetails()
        timeZone = device_details['timezone']

        start_time_utc = datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%S.%fZ")
        start_time_utc = int(calendar.timegm(start_time_utc.utctimetuple())) * 1000
        start_time_local = datetime.fromtimestamp(start_time_utc/1000, pytz.timezone(timeZone))
        end_time_utc = start_time_utc + duration
        end_time_local = datetime.fromtimestamp(end_time_utc/1000, pytz.timezone(timeZone))

        if self.ve_test.project != "KD":
            utcStartStr = start_time_local.strftime('%I:%M')
            utcStartStr = utcStartStr.lstrip('0')
            utcEndStr = end_time_local.strftime('%I:%M %p')
            utcEndStr = utcEndStr.lstrip('0')
            mdash = unichr(8212)
            timeStr = "{}".format(utcStartStr) + mdash +"{}".format(utcEndStr)

        else:
            utcStartStr = start_time_local.strftime('%H.%M')
            utcEndStr = end_time_local.strftime('%H.%M')
            timeStr = "{} to {}".format(utcStartStr , utcEndStr )

        return timeStr


    def get_duration_from_event(self, event):

        duration = event["duration"]

        timeString = self.formatDuration(duration)

        return  timeString

    def formatDuration(self, duration):
        timeStr = str(duration/60000) + " min"
        return timeStr

    def server_data_for_lcn(self, lcn):
        event = self.get_current_event_by_lcn(lcn)
        self.ve_test.log_assert(event, "event for lcn %s Not found in ctap"%lcn)
        event["airingTime"] = self.get_airingTime_from_event(event)
        return event

    def server_data_for_event_id(self, event_id):
        data =  self.send_request("ACTION_MENU", {"event_id" : event_id})
        return data

    def server_data_for_action_menu(self, event_id):
        data =  self.send_request("ACTION_MENU", {"event_id" : event_id})
        return data

    def get_credits_from_content(self, server_data, contentName, credit_type):
        self.ve_test.log_assert(server_data, "No server data supplied")
        self.ve_test.log_assert(contentName in server_data, "Cannot find " + contentName + " in " + str(server_data))
        content = server_data[contentName]
        #self.ve_test.log_assert("credits" in content, "No credits section in content: %s" % content)
        credits = []
        if "credits" in content:
            for credit in content['credits']:
                if credit['type'] == credit_type:
                    credits.append(credit['name'])

        #self.ve_test.log_assert(credits, "No %s in credits" % credit_type)
        return credits

    def get_channel_index(self, channel_id, grid_info=None):
        if grid_info == None:
            grid_info =  self.send_request('GRID', None)
        for i in range(0, grid_info['count']):
            if grid_info['channels'][i]['id'] == channel_id:
                return i
        self.ve_test.log_assert(False, "channel %s Not found in ctap"%channel_id)

    def get_channel_info(self, channel_id, grid_info=None):
        if grid_info == None:
            grid_info =  self.send_request('GRID', None)
        for i in range(0, grid_info['count']):
            if grid_info['channels'][i]['id'] == channel_id:
                return grid_info['channels'][i]
        self.ve_test.log_assert(False, "channel %s Not found in ctap"%channel_id)

    def get_event_time_utc(self, event_time_date):
        time_utc = time.strptime(event_time_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        time_utc = int(calendar.timegm(time_utc)) * 1000
        return time_utc

    def compare_event_progress_bar(self, server_event, client_progress):
        start_time_utc = self.get_event_time_utc(server_event['startDateTime'])
        now = self.ve_test.appium.get_device_time() * 1000 #time in UTC
        logging.info("now: %d, event start time: %d, duration=%d "%(now, start_time_utc, server_event['duration']))
        progress = (now - start_time_utc) / float(server_event['duration'])
        if progress > 1:
            progress = 0.0
        self.ve_test.log_assert(abs(progress - float(client_progress)) < 0.2, "Progress %f doesn't match actual progress %f" % (float(client_progress), progress))

    def compare_event_metadata(self, milestone_event, ctap_channel=None, eventIndex=0, compareProgress=True, compareDuration=False):
        self.ve_test.log_assert(milestone_event, "No milestone event to compare")
        if ctap_channel == None:
            ctap_channel = self.get_channel_info(milestone_event['channel_id'])

        logging.info('event title: %s, channel_id: %s' % (milestone_event['title_text'], milestone_event['channel_id']))
        cur_ctap_event = ctap_channel['schedule'][eventIndex]

        self.ve_test.log_assert(int(milestone_event['channel_number']) == ctap_channel['logicalChannelNumber'], "Logical channel number (%d) does not match ctap Logical channel number(%d)"%(int(milestone_event['channel_number']),ctap_channel['logicalChannelNumber']))
        self.ve_test.log_assert(milestone_event['channel_name'] == ctap_channel['name'], "channelName (%s) does not match ctap channelName (%s)"%(milestone_event['channel_name'],ctap_channel['name']))

        ctap_channel_logo = None
        for logo in ctap_channel['media']:
            if logo['type'] == "regular" and 'url' in logo:
                ctap_channel_logo = logo['url']
        # not supporting svg format
        if not("svg" in str(ctap_channel_logo)):
            self.ve_test.log_assert(milestone_event['channel_logo_url'] == ctap_channel_logo, "channel logo (%s) does not match ctap channel logo (%s) on channel (%s)"%(milestone_event['channel_logo_url'],ctap_channel_logo,milestone_event['channel_number']))
        self.ve_test.log_assert(milestone_event['event_id'] == cur_ctap_event['id'], "eventId (%s) does not match ctap eventId (%s) on channel (%s)"%(milestone_event['event_id'],cur_ctap_event['id'],milestone_event['channel_number']))

        #if the event is a part of a series, client display the season number and episode number in the title
        if 'seasonNumber' in cur_ctap_event['content']:
            expected_title =  cur_ctap_event['content']['title'].upper() + " | S" +  cur_ctap_event['content']['seasonNumber'] + " E" + cur_ctap_event['content']['episodeNumber']

        else:
            expected_title = cur_ctap_event['content']['title'].upper()

        milestone_title = milestone_event['title_text'].upper()
        if self.ve_test.project != 'KD': #just check if milestone title is a correct substring since it might have been cropped
            self.ve_test.log_assert(milestone_title in expected_title, "title (%s) does not match ctap title (%s) on channel (%s)" % (milestone_title, expected_title, milestone_event['channel_number']))
        else:
            self.ve_test.log_assert(milestone_title == expected_title, "title (%s) does not match ctap title (%s) on channel (%s)" % (milestone_title, expected_title, milestone_event['channel_number']))

        self.ve_test.log_assert(milestone_event['event_image_url'] == cur_ctap_event['content']['media'][0]['url'], "thumbnails url (%s) does not match ctap thumbnails url (%s) on channel (%s)"%(milestone_event['event_image_url'],cur_ctap_event['content']['media'][0]['url'],milestone_event['channel_number']))
        if self.ve_test.device_type == DeviceType.TABLET:
            self.ve_test.log_assert(milestone_event['synopsis'] == cur_ctap_event['content']['synopsis']['shortSynopsis'], "synopsis (%s) is not match ctap synopsis (%s) on channel (%s)"%(milestone_event['synopsis'],cur_ctap_event['content']['synopsis']['shortSynopsis'],milestone_event['channel_number']))

        if compareDuration:
            timeStr = self.get_duration_from_event(cur_ctap_event)
        else:
            timeStr = self.get_airingTime_from_event(cur_ctap_event)

        self.ve_test.ui.detailed_compare(timeStr, milestone_event['time_text'], "event time doesn't match")

        if compareProgress:
            self.compare_event_progress_bar(cur_ctap_event, milestone_event['progress_bar'])

    def get_categories_by_id(self, categoryId = ""):
        data = self.send_request("CATEGORIES", {"category_id" : categoryId})
        return data

    def get_content_list_for_category(self, categoryId = None, sortBy = SortType.A_TO_Z):
        self.ve_test.log_assert(categoryId != None, "category id is mandatory")
        payload = {'categoryId': categoryId, 'limit': '150','offset':'0'}
        payload['sort'] = sortBy.value
        data = self.send_request("AGG_CONTENT", payload)
        return data

    def find_best_media_in_array_with_type(self,mediaArray,type):
        bestMedia=None
        bestRatio=0
        for media in mediaArray:
            if media['type'] != type:
                continue
            if media['height']*media['width']>bestRatio:
                bestMedia=media
                bestRatio = media['height']*media['width']
        return bestMedia

    def get_linear_event(self, elements):
        linear_event = self.ve_test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_LINEAR", "==")], elements)
        return linear_event

    def get_vod_event(self, elements):
        vod_event = self.ve_test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_VOD", "==")], elements)
        return vod_event

    def get_catchup_event(self, elements):
        catchup_event = self.ve_test.milestones.getElement([("event_source", "EVENT_SOURCE_TYPE_CATCHUP", "==")], elements)
        return catchup_event

    def get_event_id(self,elements,type ="linear"):
        if type == "linear":
            linear_event = self.get_linear_event(elements)
            self.ve_test.log_assert(linear_event, "Cannot find element for linear")
            event_id = linear_event["event_id"]
        elif type =="vod":
            vod_event = self.get_vod_event(elements)
            self.ve_test.log_assert(vod_event, "Cannot find element for vod")
            event_id = vod_event["event_id"]
        elif type =="catchup":
            catchup_event = self.get_catchup_event(elements)
            self.ve_test.log_assert(catchup_event, "Cannot find element for catchup")
            event_id = catchup_event["event_id"]

        return event_id

    def compare_imprint(self,milestones, ctap_data):
        self.ve_test.log_assert(ctap_data[0][u'uri'] == milestones["imprint_text_url"], "text url (%s) does not match to ctap ctap text url (%s)"%(ctap_data[0][u'uri'], milestones["imprint_text_url"]))


    def compare_background_image(self,milestones_background_image, ctap_vod_data):
        backgroundImageFromCTAP = self.find_best_media_in_array_with_type(ctap_vod_data['branding']['media'],'background')
        if backgroundImageFromCTAP:
            imageUrl = backgroundImageFromCTAP['url']
        else:
            imageUrl = ""
        self.ve_test.log_assert(milestones_background_image['background_image_url'] == imageUrl, "background image (%s) does not match to ctap background image(%s)"%(milestones_background_image['background_image_url'],imageUrl))

    def compare_logo_top_image(self,milestones_logo_image, ctap_vod_data):
        logoImageFromCTAP = self.find_best_media_in_array_with_type(ctap_vod_data['branding']['media'],'logo_top')
        if logoImageFromCTAP:
            imageUrl = logoImageFromCTAP['url']
        else:
            imageUrl = ""
        self.ve_test.log_assert(milestones_logo_image['logo_image_url'] == imageUrl, "logo image (%s) does not match to ctap logo image(%s)"%(milestones_logo_image['logo_image_url'],imageUrl))

    def compare_logo_bottom_image(self,milestones_logo_image, ctap_vod_data):
        logoImageFromCTAP = self.find_best_media_in_array_with_type(ctap_vod_data['branding']['media'],'logo_bottom')
        if logoImageFromCTAP:
            imageUrl = logoImageFromCTAP['url']
        else:
            imageUrl = ""
        self.ve_test.log_assert(milestones_logo_image['logo_image_url'] == imageUrl, "logo image (%s) does not match to ctap logo image(%s)"%(milestones_logo_image['logo_image_url'],imageUrl))

    def compare_text_color(self,milestones_text_color, ctap_vod_data):
        textColor = ctap_vod_data['branding']['lookAndFeel']['textColor']
        self.ve_test.log_assert(milestones_text_color['text_color'].upper() in textColor.upper(), "text color (%s) does not match to ctap text color image(%s)"%(milestones_text_color['text_color'],textColor))

    def compare_vod_event_metadata(self, milestone_event, ctap_vod_event):

        logging.info('event title: %s, event_id: %s' % (milestone_event['title_text'], milestone_event['event_id']))

        self.ve_test.log_assert(milestone_event['event_id'] == ctap_vod_event['id'], "Event Id (%s) is not match to ctap eventid(%s)"%(milestone_event['event_id'],ctap_vod_event['id']))

        is_logo_found = False
        for logo in ctap_vod_event['content']['media']:
            if logo['url'] == milestone_event['event_image_url']:
                is_logo_found = True
                break
        self.ve_test.log_assert(is_logo_found == True, "Event logo (%s) is not found in ctap content media for event (%s)"%(milestone_event['event_image_url'],milestone_event['event_id']))

        expected_title = ctap_vod_event['content']['title'].upper()
        self.ve_test.log_assert(milestone_event['title_text'][:20] == expected_title[:20], "title (%s) is not match ctap title (%s) event (%s)" % (milestone_event['title_text'], expected_title, milestone_event['event_id']))

        #if self.ve_test.device_type == DeviceType.TABLET:
            #self.ve_test.log_assert(milestone_event['synopsis'] == ctap_vod_event['content']['synopsis']['shortSynopsis'], "synopsis (%s) is not match ctap synopsis (%s) on event (%s)"%(milestone_event['synopsis'],ctap_vod_event['content']['synopsis']['shortSynopsis'],milestone_event['event_id']))
