import json
import calendar
from datetime import date, timedelta, datetime
import time
import logging
import collections
import pprint

from vgw_test_utils.settings import Settings

class CMDC(object):

    def __init__(self, test):
        self.test = test
        if self.test.vgwUtils:
            __services = "http://{cmdc_address}:{cmdc_port}/cmdc/services?region=".format(**Settings)
            __schedules = "http://{cmdc_address}:{cmdc_port}/cmdc/services/schedule/".format(**Settings)
            __content = "http://{cmdc_address}:{cmdc_port}/cmdc/content/".format(**Settings)
            __genres = "http://{cmdc_address}:{cmdc_port}/cmdc/genres".format(**Settings)
            __cmdc_region = Settings["cmdc_region"]
            self.params = dict(
                curr_time = int(time.time() * 1000),
                **Settings
            )
        else:
            __services = None
            __schedules = None
            __content = None
            __content = None
            __genres = None
            __cmdc_region = None

    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    @classmethod
    def cmdc_time_to_epoch_ms(cls,date, startTime, startEnd = 'exact'):
        return int(cls.__timeToEpochMilliSeconds(date,startTime, startEnd))

    @classmethod
    def cmdc_by_time_serviceID(cls,dateTime, startTime, endTime, serviceId = None, eventCount = None):
        translateStartTime = cls.__timeToEpochMilliSeconds(dateTime, startTime, 'start')
        translateEndTime = cls.__timeToEpochMilliSeconds(dateTime, endTime, 'end')
        if translateStartTime > translateEndTime:
            dateTime = str(datetime.strptime(dateTime, '%Y-%m-%d')+ timedelta(days=1)).split(' ')[0]
            translateEndTime = cls.__timeToEpochMilliSeconds(dateTime, endTime, 'end')

        url = cls.__schedules+translateStartTime+"~"+translateEndTime+"?region="+cls.__cmdc_region
        if serviceId is not None:
            url += "&serviceList="+str(serviceId)
        #url += "&direction=backward&locator=%7B4%2Cjava.lang.Integer%2CNORMAL%7D-%7C-%7BY2FmOTRiOWUxNWRjZmRjYTllYjc%3D%2Cjava.lang.String%2CNORMAL%7D%5B%2B%5D%7BlogicalChannelNumber.24960%2CNORMAL%7D-%7C-%7BhashKey%2CNORMAL%7D" \
        #       "&isNormalized=true&sort=logicalChannelNumber&pset=As_BasicC&carousel=true&serviceDeliveryType=cable&source=ltv"
        if eventCount:
            url += "&eventCount="+str(eventCount)
        result = cls.test.requests.get(url)
        return result

    @classmethod
    def cmdc_by_epStartTime_serviceID(cls, epStartTime, serviceId=None, eventCount=None):
        url = cls.__schedules + str(epStartTime) + "~" + str(epStartTime+100) + "?region=" + cls.__cmdc_region
        if serviceId is not None:
            url += "&serviceList=" + str(serviceId)
        if eventCount:
            url += "&eventCount=" + str(eventCount)
        result = cls.test.requests.get(url)
        return result

    @classmethod
    def cmdc_get_show_programId_from_ep(cls,date, startTime, endTime, serviceId):
        showId = cls.cmdc_get_up_layer_programId_from_ep(date, startTime, endTime, serviceId, 'cmdcShow')
        seasons = cls.cmdc_get_all_seasons_from_seriesId(showId)
        return seasons

    @classmethod
    def serviceId2Lcn(cls, serviceId):
        epoch_time = int(time.time())
        startTime = str(epoch_time) + '000'
        endTime = startTime + '100'
        url = cls.__schedules + startTime + "~" + endTime + "?region=" + cls.__cmdc_region
        url += "&serviceList=" + str(serviceId) + "&eventCount=1"
        result = cls.test.requests.get(url)
        if result.status_code == 200:
            services = json.loads(result.content)['services']
            if len(services) > 0 and 'id' in services[0]:
                assert services[0]['id'] == str(serviceId)
                return services[0]['logicalChannelNumber']
        return None

    @classmethod
    def cmdc_get_up_layer_programId_from_ep(cls, date, startTime, endTime, serviceId, layer):
        cmdcEventInfo = cls.cmdc_by_time_serviceID(date, startTime, endTime, serviceId)

        if cmdcEventInfo.status_code == 200:
            services = json.loads(cmdcEventInfo.content)['services']
            if len(services) > 0 and 'contents' in services[0]:
                contents = services[0]['contents']

                if len(contents) > 0:
                    episode = contents[0]
                    if episode['source'] == 'ltv' and 'parentGroupId' in episode:
                        if layer == 'cmdcSeries':
                            return episode['parentGroupId'].split('//')[1]
                        if layer == 'cmdcShow':
                            if 'parentGroups' in episode:
                                if len(episode['parentGroups']) == 2 and episode['parentGroups'][0]['groupType'] == 'Show' and episode['parentGroups'][1]['groupType'] == 'Series':
                                    return episode['parentGroups'][0]['groupId'].split('//')[1]
                    else:
                        logging.info('EpisodeGetUpLayer ERROR: episode: id:{}, instanceId:{}'.format(episode['id'], episode['instanceId']))
                else:
                    logging.info('EpisodeGetUpLayer ERROR')
        return False

    @classmethod
    def cmdc_get_all_seasons_from_seriesId(cls, id=False):
        if id != False:
            #url = cls.__content[:-1]+"?region=" + cls.__cmdc_region +"&filter=source~group&parentGroupId=groupid%3A%2F%2F"+ id +"&collapse=false"
            url = cls.__content[:-1]+"?log&filter=source~group&catalogueId=16384&parentGroupId=groupid%3A%2F%2F" + id +"&collapse=false&&lang=deu"
            result = cls.test.requests.get(url)
            if result.status_code == 200:
                services = json.loads(result.content)
                if len(services) > 0 and 'contents' in services:
                    return services['contents']
                else:
                    logging.info('CMDC: seasons_from_seriesId Failed, No contents: url:{}'.format(url))
            else:
                logging.info('CMDC: seasons_from_seriesId Failed: retCode:{} url:{}'.format(result.status_code, url))
        return False


    @classmethod
    def get_all_season_episodes(cls, test, season_id=None, serviceId=None):
        from vgw_test_utils.settings import Settings
        if season_id is not None:
            if serviceId is not None:
                url = cls.__content[:-1]+"?region=" + cls.__cmdc_region +"&filter=source~ltv&serviceList=" + str(serviceId) +"&parentGroupId=groupid%3A%2F%2F"+ str(season_id) + "&collapse=false"
            else:
                url = "http://{cmdc_address}:{cmdc_port}/cmdc/content/".format(**Settings)+"?region=" + Settings["cmdc_region"] +"&filter=source~ltv&parentGroupId=groupid%3A%2F%2F"+ str(season_id) + "&collapse=false"
            result = test.requests.get(url)
            contents = json.loads(result.content)['contents']
            count = json.loads(result.content)['header']['total']
            print "cmdc query returned count ({})  URL for cmdc call getting all episodes in season ({}) : ({})".format(count,url, season_id)
            return contents, count
        return False

    @classmethod
    def cmdc_content_program_by_programID_and_InstanceId(cls, id, instanceId, lang = 'eng', rspUrl = False):
        if id is not None:
            url = cls.__content+"programid%3A%2F%2F"+id+"~programid%3A%2F%2F"+instanceId+"?count=1&region="+cls.__cmdc_region+'&lang='+lang
            if rspUrl:
                return url
            result = cls.test.requests.get(url)
            return result
        return False

    @classmethod
    def cmdc_content_program_by_programID(cls, id):
        if id is not None:
            url = cls.__content+"programid%3A%2F%2F"+id
            result = cls.test.requests.get(url)
            contents = json.loads(result.content)['contents']
            return contents
        return False

    @classmethod
    def getGenreStr(cls, search_criteria = ""):
        result = cls.test.requests.get(cls.__genres)
        if result.status_code == 200:
            load = json.loads(result.content)
            if len(load) > 0:
                if 'genres' in load:
                    genres = load['genres']
                    for g in genres:
                        if 'value' in g:
                            if g['value'] == search_criteria:
                                if 'name' in g:
                                    name_eng = g['name'].split('eng ')
                                    if len(name_eng) > 1:
                                        no_eng = name_eng[1]
                                        if '/' in no_eng:
                                            name_first = no_eng.split('/')
                                            return name_first[0]
                                        else:
                                            return no_eng
                                    else:
                                        return name_eng[0]

        return ''

    @classmethod
    def checkAllEpisodeParams(cls, content):
        episodeField = ['episodeNumber', 'seasonNumber', 'seriesId', 'parentGroupId', 'parentGroups', 'type', 'source']
        if all (w in content for w in episodeField):
            if content['source'] == 'ltv' and content['type'] == 'instance':
                if int(content['parentGroups'][1]['groupId'].split('//')[1]) == content['seriesId']:
                    return True
        logging.info('EpisodeParams ERROR: id:{}, instanceId:{}, {}'.format(content['id'], content['instanceId'], content['parentGroups'][1]['groupId'] ))
        return False

    @classmethod
    def count_multiple_channel_episode(cls, content = {}):
        if content:
            if len(content) > 0:
                channels = Set()
                for epInstance in content:
                    channelNumber = epInstance['serviceId']
                    logging.info('Episode found on Channel: '+str(channelNumber))
                    channels.add(channelNumber)
                return len(channels)
        return 0

    @classmethod
    def get_episode_info(cls, response):
        if hasattr(response, 'status_code'):
            if response.status_code != 200:
                return False
            else:
                load = json.loads(response.content)
        else:
            load = response
        if len(load) > 0:
            contents = load['contents']
            if len(contents) > 0:
                for content in contents:
                    title = content['title']
                    season = content['seasonNumber']
                    epNumber = content['episodeNumber']
                    serviceId = content['serviceId']
                    return title, season, epNumber, serviceId
        return ''

    @classmethod
    def isEventType(cls, eventType, response = {}):
        if hasattr(response, 'status_code'):
            if response.status_code != 200:
                return False
            else:
                load = json.loads(response.content)
        else:
            load = response

        if len(load) > 0:
            contents = load['contents']
            if len(contents) > 0:
                for content in contents:
                    if eventType == 'movie':
                        if content['source'] == 'ltv' and 'parentGroupId' not in content:
                            return True
                    if eventType == 'episode':
                        if 'parentGroups' in content and len(content['parentGroups']) == 2:
                            if content['parentGroups'][0]['groupType'] == 'Show' and content['parentGroups'][1]['groupType'] == 'Series':
                                return cls.checkAllEpisodeParams(content)
                    if eventType == 'open_series':
                        if 'parentGroups' in content and len(content['parentGroups']) == 1:
                            if content['parentGroups'][0]['groupType'] == 'Show':
                                return True

        return False

    @classmethod
    def get_credits_actors_director(cls, response = {}, maxCountDirectors = 1000 ,maxCountActors = 1000):
        mActors = []
        mDirectors = []
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'credits' in contensToJson[0]:
                    credits = contensToJson[0]['credits']
                    if len(credits) > 0:
                        i = 0
                        j = 0
                        for credit in credits:
                            name = ""
                            lastName = ""
                            if "personGivenName" in credit:
                                name = credit['personGivenName']
                            if "personFamilyName" in credit:
                                lastName = credit['personFamilyName']
                            if credit['classification'] == "urn:tva:metadata:cs:TVARoleCS:2005:ACTOR" and i < maxCountActors:
                                nameToAdd = name
                                if lastName:
                                    nameToAdd = nameToAdd +" "+lastName
                                mActors.append(nameToAdd)
                                i = i + 1
                            if credit['classification'] == "urn:tva:metadata:cs:TVARoleCS:2005:DIRECTOR" and j < maxCountDirectors:
                                nameToAdd = name
                                if lastName:
                                    nameToAdd = nameToAdd +" "+lastName
                                mDirectors.append(nameToAdd)
                                j = j + 1
                        return mActors,mDirectors
        return [], []

    @classmethod
    def get_productionYear(cls, response = {}):
        productionYear = None
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'productionYear' in contensToJson[0]:
                    productionYear = contensToJson[0]['productionYear']
                    if productionYear:
                        return str(productionYear)
        return False

    @classmethod
    def get_productionLocation(cls, response = {}):
        productionLocation = None
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'productionLocation' in contensToJson[0]:
                    productionLocation = contensToJson[0]['productionLocation']
                    if productionLocation:
                        return str(productionLocation)
        return ""


    @classmethod
    def get_genres(cls, response = {}):
        genres = None
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'genres' in contensToJson[0]:
                    genres = contensToJson[0]['genres']
                    if genres:
                        for genre in genres:
                            return cls.getGenreStr(genre)
        return False

    @classmethod
    def get_StartTime(cls, response = {}):
        genres = None
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'StartTime' in contensToJson[0]:
                    StartTime = contensToJson[0]['StartTime']
                    if StartTime:
                        return StartTime
        return False

    @classmethod
    def get_synopsis(cls, synopsisType = 'synopsis', response = {}):
        genres = None
        if synopsisType != 'longSynopsis' and synopsisType != 'shortSynopsis' and synopsisType != 'synopsis':
            synopsisType = 'synopsis'
            logging.info("cmdc: get_synopsis, synopsis key {} is wrong, changed to default: synopsis", format(synopsisType))
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if synopsisType in contensToJson[0]:
                    synopsis = contensToJson[0][synopsisType]
                    if synopsis:
                        return synopsis
        return False

    @classmethod
    def get_parentalRating(cls, response = {}):
        genres = None
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'parentalRating' in contensToJson[0]:
                    parentalRating = contensToJson[0]['parentalRating']
                    if parentalRating:
                        return parentalRating['rating']
        return False

    @classmethod
    def get_videoFormat(cls, response = {}):
        genres = None
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'videoFormat' in contensToJson[0]:
                    videoFormat = contensToJson[0]['videoFormat']
                    if videoFormat:
                        return videoFormat
        return False

    @classmethod
    def get_serviceId(cls, response = {}):
        genres = None
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'serviceId' in contensToJson[0]:
                    serviceId = contensToJson[0]['serviceId']
                    if serviceId:
                        return serviceId
        return False

    @classmethod
    def get_content_info(cls, param, response = {}):
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if param in contensToJson[0]:
                    info = contensToJson[0][param]
                    if info:
                        return info
        return False

    @classmethod
    def get_durationInMin(cls, response = {}):
        duration = 0
        if response.status_code == 200:
            contensToJson = json.loads(response.content)['contents']
            if len(contensToJson) > 0:
                if 'duration' in contensToJson[0]:
                    duration = contensToJson[0]['duration']
                    if duration:
                        minutes = duration/(1000*60)
                        return str(minutes)
        return False
    @classmethod
    def get_program_id(self, result):
        #parse to json
        toJson = json.loads(result.content)
        services = toJson['services']
        if len(services) == 1:
            contents = services[0]['contents']
            if len(contents)>0:
                id = contents[0]["id"]
                programID = id.split("//")
                if len(programID) == 2:
                    return programID[1]
        return False

    @classmethod
    def get_program_instance_id(self, result):
        #parse to json
        toJson = json.loads(result.content)
        services = toJson['services']
        if len(services) == 1:
            contents = services[0]['contents']
            if len(contents)>0:
                id = contents[0]["instanceId"]
                programID = id.split("//")
                if len(programID) == 2:
                    return programID[1]
        return False

    @classmethod
    def get_episode_season_id(cls, result):
        #parse to json
        toJson = json.loads(result.content)
        #contents = toJson['contents']
        contents = toJson['services'][0]['contents']
        #if len(contents) == 1:
        if contents[0]['parentGroups'][1]['groupType'] == 'Series':
            id = contents[0]['parentGroups'][1]['groupId'].split('//')[1]
            return id
        return False

    #SORTED LISTE OF NUMBER EPISODES OF SEASON
    @classmethod
    def get_episodes_number_list(cls, cmdcEpisodes = []):
        listEpisodes = set()
        for episode in cmdcEpisodes:
            listEpisodes.add(episode['episodeNumber'])
        epList = list(listEpisodes)
        sorted(epList)
        return epList

    @classmethod
    def get_program_title(self, result):
        #parse to json
        toJson = json.loads(result.content)
        services = toJson['services']
        if len(services) == 1:
            if 'contents' in services[0]:
                contents = services[0]['contents']
                if len(contents)>0:
                    title = contents[0]["title"]
                    return title
        return False
    @classmethod
    def get_cmdc_movies_by_date_and_serviceID(self,serviceID = None, iDate = None, type='movie'):
        mEventss = []
        #if we dont get a date we use the same day
        if iDate is None:
            iDate = str(date.today()+timedelta(1))

        response_by_time = self.cmdc_by_time_serviceID(iDate,"00:00","23:59", serviceID)

        if response_by_time.status_code == 200:
            services = json.loads(response_by_time.content)['services']
            if len(services) > 0:
                if 'contents' in services[0]:
                    contents = services[0]['contents']
                    if len(contents) > 0:
                        if type == 'movie':
                            for movie in contents:
                                if movie['source'] == 'ltv' and 'parentGroupId' not in movie:
                                    movieClass = self.__parse_movie_to_class(serviceID, movie)
                                    mEventss.append(movieClass)
                            return mEventss
                        if type == 'episode':
                            for episode in contents:
                                if episode['source'] == 'ltv' and 'parentGroupId' in episode:
                                    eventClass = self.__parse_movie_to_class(serviceID, episode)
                                    mEventss.append(eventClass)
                            return mEventss

        return False

    @classmethod
    def __parse_movie_to_class(cls,serviceID = None, movie = []):
        if movie:
            mv = Movie()
            programId = movie["id"].split("//")[1]
            mv.mProgramId = programId
            programInstanceId = movie["instanceId"].split("//")[1]
            mv.mProgramInstanceId = programInstanceId
            #######MOVIE INFO##########
            response = cls.cmdc_content_program_by_programID_and_InstanceId(mv.mProgramId,mv.mProgramInstanceId)
            actors, directors = cls.get_credits_actors_director(response)
            mv.mReleaseYear = cls.get_productionYear(response)
            mv.mActors = actors
            mv.mDirectors = directors
            #Date, Start Time and End Time
            sc = Schedule()
            sc.mServiceId = serviceID
            sc.mDate, sc.mStartTime = cls.__convert_epoch_to_date_and_time(movie['broadcastDateTime'])
            endTime = int(movie['broadcastDateTime']) + int(movie['duration'])
            sc.mDate, sc.mEndTime = cls.__convert_epoch_to_date_and_time(endTime)
            #CMDC if program finish after 00:00 change date one day before
            if (datetime.strptime(sc.mEndTime, '%H:%M')  - datetime.strptime(sc.mStartTime, '%H:%M')).days == -1:
                sc.mDate = datetime.strftime(datetime.strptime(sc.mDate, '%Y-%m-%d') - timedelta(days=1), "%Y-%m-%d")
            
            mv.mSchedules.append(sc)
            return mv
    @classmethod
    def __convert_epoch_to_date_and_time(self, epochTime):
        s = int(epochTime / 1000)
        dateTime = time.strftime('%Y-%m-%d %H:%M', time.gmtime(s))
        date = dateTime.split(" ")[0]
        hm = dateTime.split(" ")[1]
        return date, hm

    @classmethod
    def __convert_time_to_local(self,date,hmTime):
        utc = str(datetime.strptime(date + ' ' + hmTime, self.TIME_FORMAT))
        timestamp =  calendar.timegm((datetime.strptime( utc, self.TIME_FORMAT)).timetuple())
        local = datetime.fromtimestamp(timestamp).strftime(self.TIME_FORMAT)
        return local


    @classmethod
    def __timeToEpochMilliSeconds(self,date,hmTime, startEnd = 'exact'):
        t = self.__convert_time_to_local(date,hmTime+":00")
        response = time.mktime(datetime.strptime(t,self.TIME_FORMAT).timetuple())
        if startEnd == 'start':
            return str(int(response))+"001"
        if startEnd == 'end':
            return str(int(response)-1)+"000"
        # exact time
        return str(int(response))+"000"

    @classmethod
    def get_cmdc_all_possible_events_on_service(self, abrService):

        url = "http://{cmdc_address}:{cmdc_port}/cmdc/content".format(**Settings) + "?region=" + Settings["cmdc_region"] + "&filter=source~ltv&serviceList="+ abrService
        result = self.test.requests.get(url)
        if result.status_code == 200:
            allEventsInScheduleOnService = json.loads(result.content)
            if len(allEventsInScheduleOnService) > 0 and 'contents' in allEventsInScheduleOnService:
                return allEventsInScheduleOnService['contents']
            else:
                logging.info('CMDC: all events query Failed, No contents: url:{}'.format(url))
        else:
            logging.info('CMDC: all events query Failed: retCode:{} url:{}'.format(result.status_code, url))
        return False

    @classmethod
    def get_all_episodes_events_on_service(self, allEventsInScheduleOnService):

        allEpisodesScheduledOnService = []

        for event in allEventsInScheduleOnService:
            if 'parentGroups' in event:
                for groupType in event['parentGroups']:
                    if groupType['groupType'] == "Series":
                        allEpisodesScheduledOnService.append(event)
                        break

        assert (allEpisodesScheduledOnService != [], "Failed reason: There is no episodes on all services")
        return allEpisodesScheduledOnService


    @classmethod
    def get_cmdc_all_services(self,test):

        self.test=test

        if (self.test.vgwUtils):
            url = "http://{cmdc_address}:{cmdc_port}/cmdc/bulk/services/all/link".format(**Settings) + "?region=" + Settings[
            "cmdc_region"] + "&pset=_full"
        else:
            url = "http://{cmdc_address}:{cmdc_port}/cmdc/bulk/services/all/link".format(**Settings) + "?region=" + Settings[
            "cmdc_region"] + "&pset=_full"
        result = test.requests.get(url)
        if result.status_code == 200:
            allServices = json.loads(result.content)
            if len(allServices) > 0 and 'services' in allServices:
                allServices = [service['id'] for service in allServices['services']]
                return allServices
            else:
                logging.info('CMDC: all events query Failed, No contents: url:{}'.format(url))
        else:
            logging.info('CMDC: all events query Failed: retCode:{} url:{}'.format(result.status_code, url))
        return False


    @classmethod
    def get_all_duplicated_episodes_id(self, allEpisodesProgramId):

        allduplicateEpisodesProgramId = [item for item, count in collections.Counter(allEpisodesProgramId).items() if count > 1]
        return allduplicateEpisodesProgramId


    @classmethod
    def get_all_episodes_id_on_all_services(self, allEpisodesArray):

        allEpisodesProgramId = [programId['id'] for programId in allEpisodesArray if type(programId) is dict]
        return allEpisodesProgramId

    @classmethod
    def get_all_episodes_id_on_all_services(self, allduplicateEpisodesOnMultipuleServices):

        allEpisodesProgramId = [programId['id'] for programId in allduplicateEpisodesOnMultipuleServices if type(programId) is dict]
        return allEpisodesProgramId

    @classmethod
    def get_all_duplicated_episodes_on_all_services(self, allduplicateEpisodesProgramId, allEpisodesUnderAllServicesArray):

        allduplicateEpisodesOnAllServices = []

        for dupIndex in allduplicateEpisodesProgramId:
            for allEpIndex in allEpisodesUnderAllServicesArray:
                if 'id' in allEpIndex and type(allEpIndex) is dict:
                    if dupIndex == allEpIndex['id']:
                        allduplicateEpisodesOnAllServices.append(allEpIndex)
                        break

        assert (allduplicateEpisodesOnAllServices != [], "Failed reason: There is no duplicated episodes on the schedule")
        return allduplicateEpisodesOnAllServices


    @classmethod
    def get_all_duplicated_episodes_on_multi_services(self, allduplicateEpisodesOnAllServices):

        allduplicateEpisodesOnMultipuleServices = []

        for epIndex in allduplicateEpisodesOnAllServices:
            for innerEpIndex in allduplicateEpisodesOnAllServices:
                if epIndex["id"] == innerEpIndex['id'] and epIndex["serviceEquivalenceKey"] != innerEpIndex['serviceEquivalenceKey']:
                    allduplicateEpisodesOnMultipuleServices.append(innerEpIndex)

        assert (allduplicateEpisodesOnMultipuleServices != [], "Failed reason: There is no duplicated episodes on multiple channels in the schedule")
        return allduplicateEpisodesOnMultipuleServices


    @classmethod
    def get_cmdc_all_episodes_on_all_service(self, allServices):

        allEpisodesOnAllServicesArray = []

        if allServices != False:
            for service in allServices:
                allEventsInScheduleOnService = self.get_cmdc_all_possible_events_on_service(service)
                if allEventsInScheduleOnService != False:
                    allEpisodesInScheduleOnService = self.get_all_episodes_events_on_service(allEventsInScheduleOnService)
                    if allEpisodesInScheduleOnService != False:
                        allEpisodesOnAllServicesArray.extend(allEpisodesInScheduleOnService)
                    else:
                        logging.info('No Episodes on service' + service)
                else:
                    logging.info('No Events on service' + service)
        else:
            logging.info('No Services results')

        assert (allEpisodesOnAllServicesArray != [], "Failed reason: There are no episodes on all services")
        return allEpisodesOnAllServicesArray

    # Get provider name for a contentId
    # Return provider name
    def get_provider_from_contentId(self, contentId):
        self.params = dict(
            content_id=contentId,
            catalog_id = str(self.get_catalogId()),
            **Settings
        )
        provider_url = "http://{cmdc_address}:{cmdc_port}/cmdc/content/{content_id}?catalogueId={catalog_id}".format(**self.params)
        provider_result = self.test.requests.get(provider_url)
        logging.info("PROVIDER URL: %s", provider_url)
        resp = json.loads(provider_result.text)
        # logging.info(pprint.pformat(resp))
        # get provider
        provider = ""
        logging.info("Number of program ID found : %d", resp['header']['total'])
        if resp['header']['total'] > 0:
            logging.info("resp[contents][provider]=%s", resp['contents'][0]['provider'])
            provider = resp['contents'][0]['provider']
        return provider

    # Get provider name for an LTV eventId
    # Return provider name
    def get_provider_from_eventId(self, eventid):
        from vgw_test_utils.settings import Settings
        self.params = dict(
            eventId=eventid,
            **Settings
        )
        provider_url = "http://{cmdc_address}:{cmdc_port}/cmdc/content/{eventId}".format(**self.params)
        provider_result = self.test.requests.get(provider_url)
        resp = json.loads(provider_result.text)
        # get provider
        provider = ""
        logging.info("Number of program ID found : %d", resp['header']['total'])
        if resp['header']['total'] > 0:
            logging.info("resp[contents][broadcaster]=%s", resp['contents'][0]['broadcaster'])
            provider = resp['contents'][0]['broadcaster']
        return provider

    # Get provider name for a serviceId
    # Return provider name
    def get_provider_from_serviceId(self, svcId):
        self.params = dict(
            service_id=svcId,
            **Settings
        )
        provider_url = "http://{cmdc_address}:{cmdc_port}/cmdc/services/events/1~0?region={cmdc_region}&filter=source~ltv&count=1&serviceList={service_id}".format(**self.params)
        provider_result = self.test.requests.get(provider_url)
        resp = json.loads(provider_result.text)
        #logging.info(pprint.pformat(resp))
        # get provider
        provider = ""
        logging.info("Number of program ID found : %d", resp['header']['total'])
        if resp['header']['total'] > 0:
            logging.info("resp[services][provider]=%s", resp['services'][0]['provider'])
            provider = resp['services'][0]['provider']
        return provider


    # Get service information for all services
    # Return a dictionnary
    def get_serviceInfo_forall_services(self):
        self.params = dict(
            **Settings
        )
        serviceNb_url = "http://{cmdc_address}:{cmdc_port}/cmdc/services?region={cmdc_region}&filter=source~ltv&isNormalized=true".format(
            **self.params)
        serviceNb_result = self.test.requests.get(serviceNb_url)
        resp = json.loads(serviceNb_result.text)
        # logger.info(pprint.pformat(resp))
        # get info
        dictServiceInfo = {}
        serviceId = 0
        serviceNb = 0
        serviceEK = 0
        provider = ""
        #logging.info("Number of services found : %d", resp['header']['total'])
        for index in range(resp['header']['total']):
            serviceId = resp['services'][index]['id']
            serviceNb = int(resp['services'][index]['logicalChannelNumber'])
            serviceEK = int(resp['services'][index]['serviceEquivalenceKey'])
            provider = resp['services'][index]['provider']
            logging.info("serviceId=%s, logicalChannelNumber=%d, serviceEquivalenceKey=%d, provider=%s" % (serviceId, serviceNb, serviceEK, provider))
            dictServiceInfo[serviceId] = (serviceNb, serviceEK, provider)
        return dictServiceInfo

    #Get all assets ID & InstanceID of all classtype type classificationId from Classification List
    #Return a dic of assets Id & InstanceId
    def get_assetIds_from_Classif_List(self, catId, classType):
        self.params['catalogue_id'] = catId
        dicassetsids = {}
        try:
            for classId in classType:
                self.params['classification_id'] = classId
                assetsList_r_url = "http://{cmdc_address}:{cmdc_port}/cmdc/content?classificationId={classification_id}&collapse=false&catalogueId={catalogue_id}&region={cmdc_region}".format(**self.params)
                assetsList_r = self.test.requests.get(assetsList_r_url)
                assetsList_resp = json.loads(assetsList_r.text)
                for id in range(0,len(assetsList_resp['contents'])):
                    dicassetsids[(assetsList_resp['contents'][id]['id']).replace('://','%3A%2F%2F')] = (assetsList_resp['contents'][id]['instanceId']).replace('://','%3A%2F%2F')
        except : return {}
        return dicassetsids


    #Get Classification Type 41 in root classification from CatalogID and Root CatalogId
    #Return list of ClassificationId in Tree
    def get_classificationType41_from_catId_rootclassId(self, catId, rootclassId):
        self.params['catalogue_id'] = catId
        self.params['rootclass_id'] = rootclassId
        listclasstype = []
        classTree_url = "http://{cmdc_address}:{cmdc_port}/cmdc/classification/{rootclass_id}/classification?catalogueId={catalogue_id}".format(**self.params)
        classTree_r = self.test.requests.get(classTree_url)
        try:
            classTree_resp = json.loads(classTree_r.text)
            logging.info('lenght of dic : %i', len(classTree_resp['classifications']))
            for id in range(0,len(classTree_resp['classifications'])):
                classType = classTree_resp['classifications'][id]['type']
                logging.info('classType : %s',classType)
                if classType == 41:
                    listclasstype.append(classTree_resp['classifications'][id]['classificationId'])
                    logging.info('classificationId : %s',classTree_resp['classifications'][id]['classificationId'])
            return listclasstype
        except : return []

    #Get Classification Type 6 in root classification from CatalogID and Root CatalogId
    #Return list of ClassificationId in Tree
    def get_classificationType6_from_catId_rootclassId(self, catId, rootclassId):
        self.params['catalogue_id'] = catId
        self.params['rootclass_id'] = rootclassId
        listclasstype = []
        classTree_url = "http://{cmdc_address}:{cmdc_port}/cmdc/classification/{rootclass_id}/classification?catalogueId={catalogue_id}".format(**self.params)
        classTree_r = self.test.requests.get(classTree_url)
        try:
            classTree_resp = json.loads(classTree_r.text)
            logging.info('lenght of dic : %i', len(classTree_resp['classifications']))
            for id in range(0,len(classTree_resp['classifications'])):
                classType = classTree_resp['classifications'][id]['type']
                logging.info('classType : %s',classType)
                if classType == 6:
                    listclasstype.append(classTree_resp['classifications'][id]['classificationId'])
                    logging.info('classificationId : %s',classTree_resp['classifications'][id]['classificationId'])
            return listclasstype
        except : return []


    #Get Root ClassificationId from CatalogId
    #Return Root ClassificationId
    def get_root_classificationID_from_catalogId(self, catId):
        self.params['catalogue_id'] = catId
        rootclassId_url = "http://{cmdc_address}:{cmdc_port}/cmdc/classification?catalogueId={catalogue_id}".format(**self.params)
        try:
            rootclassId_r = self.test.requests.get(rootclassId_url)
            rootclassId_resp = json.loads(rootclassId_r.text)
            logging.info('ROOT_CLASSID_RESP : %s', pprint.pformat(rootclassId_resp))
            rootclassId = rootclassId_resp['classifications'][0]['classificationId']
            logging.info('rootclassifId : %s',rootclassId)
            return rootclassId
        except : return 0

    # Get CatalogId from cmdc region
    # Return CatalogId
    def get_catalogId(self):
        if self.test.platform == 'Android':
            catId_url = "http://{cmdc_address}:{cmdc_port}/cmdc/region/{cmdc_region}/device/ANDROID/catalogueId".format(
                **Settings)
        else:
            catId_url = "http://{cmdc_address}:{cmdc_port}/cmdc/region/{cmdc_region}/device/IOS/catalogueId".format(
                **Settings)

        catId_r = self.test.requests.get(catId_url)
        logging.info("Get CatalogueId : %s", catId_r)
        try:
            resp = json.loads(catId_r.text)
            logging.info(pprint.pformat(resp))
            catId = resp['catalogueId']['id']

            return catId
        except:
            return 0

    def get_editorial_contentId_list(self):
        contentIdList={}
        catalog_id = str(self.get_catalogId())
        #Get root classificationId
        url = "http://{cmdc_address}:{cmdc_port}/cmdc/classification?catalogueId=".format(**Settings) + catalog_id
        result = self.test.requests.get(url)
        try:
            resp = json.loads(result.text)
            root_classification_id = resp['classifications'][0]['classificationId']
            #Get classificationId for editorial:
            url = "http://{cmdc_address}:{cmdc_port}/cmdc/classification/%s/classification?catalogueId=%s".format(**Settings)%(root_classification_id,catalog_id)
            result = self.test.requests.get(url)
            resp = json.loads(result.text)
            for index in range(len(resp['classifications'])):
                if resp['classifications'][index]['type'] == 41:   #41 = classification editorial type
                    editorial_classification_id = resp['classifications'][index]['classificationId']
                    break

            #Get editorial contents:
            url = "http://{cmdc_address}:{cmdc_port}/cmdc/content?classificationId=%s&catalogueId=%s".format(**Settings)%(editorial_classification_id,catalog_id)
            result = self.test.requests.get(url)
            resp = json.loads(result.text)
            for index in range(len(resp['contents'])):
                contentIdList[(resp['contents'][index]['id']).replace('://', '%3A%2F%2F')] = (resp['contents'][index]['instanceId']).replace('://', '%3A%2F%2F')
            return contentIdList
        except : return []
