import json
import logging

import time

try:
    import vgw_test_utils.test_utils
    from vgw_test_utils.headend_util import get_all_catalog, delete_booking
    from vgw_test_utils.settings import Settings
    vgw_test_utils_installed = True
except:
    logging.info("no vgw_test_utils !")
    vgw_test_utils_installed = False

logger = logging.getLogger(__name__)

class Labels():
    THIS_EPISODE, RECORD_SEASON = None, None


def error_string_message(expected_label, found_label):
    return "We looked for the string \"{0}\" but we found the string \"{1}\"".format(expected_label, found_label)


def get_all_bookings_from_PPS(test, household_id):
    '''
    :reference: Based on the document CHLIN-ICD-3254 Personal Planner System (PPS) Version 2.doc
    taken from http://wikicentral.cisco.com/display/ACT/4.78.0-341
    :param household_id: The household for which the information about bookings required
    :return: List of dictionaries of all bookings, per given household - includes also already recorded events
    [unlike get_bookings from vgw_test_utils.headend_util]
    '''
    if vgw_test_utils_installed:
        url = 'http://{pps_address}:{pps_port}/pps/households/'.format(**Settings) + household_id +'/catalog'
    else:
        url = 'http://{pps_address}:{pps_port}/pps/households/'+ household_id +'/catalog'
    logger.debug("Url for request to pps\n{}".format(url))
    r = test.requests.get(url)
    data = json.loads(r.text)
    #return filter(lambda x: x[u'state'] == u'BOOKED', data)[0]
    return data

def get_episodes_from_pps(bookings_for_pps, sorted=True):

    """

    US19203 - Season booking with real metadata
    TA20003 - Validate pps booking compare to the  season episodes
    Validate pps booking compare to the  season episodes

    :description:get list of all booking from pps, and return dictionary, where
    seriesId's are keys, and the values are lists of episodes for each series   
    :param bookings_from_pps: list of all booking from pps
    :param sorted:define whether sorting the list of episodes for every series
    or not, default set to True
    """

    series_episodes = {}

    for booking in bookings_for_pps:

        if not booking.has_key("seriesId"):
            print "This record has no seriesId.Skipping to the next record"
            continue
            
            
        if not booking.has_key("content"):
            print "This record has no id.Skipping to the next record"
            continue


        seriesId = booking['content']['seriesId']
        id = booking['content']['id'].split("://")[-1]
        print "seriesId : {}, id : {}".format(seriesId, id)

        if not series_episodes.has_key(seriesId):
            print "Adding series {}".format(seriesId)
            series_episodes[seriesId] = []

        print "Adding episode {} to series {}".format(id, seriesId)
        series_episodes[seriesId].append(id)

    print "\nseries_and_episodes_from_pps before sorting:\n" + str(series_episodes)

    if sorted==True:

        for booking in series_episodes.keys():
            series_episodes[booking].sort()

        print "\nseries_and_episodes_from_pps after sorting:\n" + str(series_episodes)
    elif sorted==False:
        print "List of episodes won't be sorted"

    return series_episodes

def get_series_channels_from_pps(bookings_for_pps):

    """
    US19203 - Season booking with real metadata

    :description:get list of all booking from pps, and return dictionary, where
    seriesId's are keys, and the channels are represented as lists for each series
    :param bookings_from_pps: list of all booking from pps
    """

    series_channels = {}

    for booking in bookings_for_pps:

        if not booking.has_key("seriesId"):
            logger.debug("This record has no seriesId.Skipping to the next record")
            continue
            
        if not booking.has_key("content"):
            logger.debug("This record has no instanceId.Skipping to the next record")
            continue

        seriesId = booking['content']['seriesId']
        channelId = booking['channelId']
        logger.debug("seriesId : {}, channelId : {}".format(seriesId, channelId))

        if not series_channels.has_key(seriesId):
            logger.debug("Adding series {}".format(seriesId))
            series_channels[seriesId] = []

        logger.debug("Adding channel {} to series {}".format(channelId, seriesId))
        series_channels[seriesId].append(channelId)

    logger.debug("\nseries_channels:\n" + str(series_channels))

    return series_channels


def episodes_of_series_from_cmdc(all_season_episods_from_cmdc, series_id, only_future_episodes=True):

    """

    US19203 - Season booking with real metadata

    :description:get list of all season's episods from cmdc, and return list
    of dictionaries, with next parameters
    seriesId
    id
    broadcastDateTime
    serviceId

    :param all_season_episods_from_cmdc: list of all episodes of season, taken from cmdc
    :seriesId: the id of series, required in order to verify data are valid
    :param only_future_episodes:define whether remove non-future episodes, default set to True
    """

    list_episodes_of_series_from_cmdc = []

    current_time = int(time.time())

    logger.debug("Current time is {}".format(current_time))

    past_episodes = 0

    for episode in all_season_episods_from_cmdc:

        seriesId = episode['seriesId']
        id = episode['id'].split("://")[-1]
        broadcastDateTime = episode['broadcastDateTime']+episode['duration']
        serviceId = episode['serviceId']

        logger.debug("seriesId : {}, id : {}, broadcastDateTime : {}, serviceId : {}".format(seriesId, id, broadcastDateTime, serviceId))

        if only_future_episodes==True:
            if broadcastDateTime/1000<=current_time:
                logger.debug("Episode {} is not future episode. Current time is {} while episode brodcast time is {}.Difference is {}. \nSkipping to next episode.".format(id, current_time, broadcastDateTime/1000, current_time - broadcastDateTime/1000))
                continue
                past_episodes+=1

        if series_id!=seriesId:
            raise AssertionError, "Find incorrect seriesId.\nWe looked for series {} but found {}".format(series_id, seriesId)

        dict_for_episode = {"seriesId" : seriesId, "id" : id, "broadcastDateTime" : broadcastDateTime, "serviceId" : serviceId}

        logger.debug("dict_for_episode : " + str(dict_for_episode))

        list_episodes_of_series_from_cmdc.append(dict_for_episode)

    logger.debug("\nlist_episodes_of_series_from_cmdc :\n" + str(list_episodes_of_series_from_cmdc))

    if only_future_episodes==True:
        logger.debug("{} episodes were skipped because they were passed episodes".format(past_episodes))

    return list_episodes_of_series_from_cmdc

def compare_episodes_lists(series_id, episodes_list_from_pps, episodes_list_from_cmdc):

    logger.debug("Comparing eposides for series {}, between pps and cmdc".format(series_id)) 

    def mismatch_found(message):
        mismatch_found.count += 1
        mismatch_found.message = "{}\n{}. {}".format(mismatch_found.message, mismatch_found.count, message) 

    mismatch_found.count = 0
    mismatch_found.message = ""

    #sorting the lists
    episodes_list_from_pps.sort()
    episodes_list_from_cmdc.sort()

    #checking the length of both lists
    len_episodes_list_from_pps = len(episodes_list_from_pps)
    len_episodes_list_from_cmdc = len(episodes_list_from_cmdc)
    print "episodes_list_from_pps has {} epsiodes, episodes_list_from_cmdc {} epsiodes".format(len_episodes_list_from_pps,    len_episodes_list_from_cmdc)
    print "episodes_list_from_pps={}\nepisodes_list_from_cmdc={} ".format(episodes_list_from_pps,    episodes_list_from_cmdc)

    if len_episodes_list_from_pps!=len_episodes_list_from_cmdc:
        mismatch_found("The number of items is not the same on both lists, in pps there are {} itmes, in cmdc there are {} items.".format(len_episodes_list_from_pps, len_episodes_list_from_cmdc))

    candidate_for_removing_from_episodes_list_from_cmdc = []
    candidate_for_removing_from_episodes_list_from_pps = []

    for episode in episodes_list_from_pps:
        if episode in episodes_list_from_cmdc:
            logger.debug("episode {} appears in episodes_list_from_pps and in episodes_list_from_cmdc".format(episode))
            candidate_for_removing_from_episodes_list_from_cmdc.append(episode)#episodes_list_from_cmdc.remove(episode)            
        else:
            error_message = "episode \"{}\" appears in episodes_list_from_pps but was not found in episodes_list_from_cmdc".format(episode)
            logger.error(error_message)
            mismatch_found(error_message)
        candidate_for_removing_from_episodes_list_from_pps.append(episode)#episodes_list_from_pps.remove(episode)

    logger.debug("candidate_for_removing_from_episodes_list_from_pps={}\ncandidate_for_removing_from_episodes_list_from_cmdc={} ".format(candidate_for_removing_from_episodes_list_from_pps,    candidate_for_removing_from_episodes_list_from_cmdc))

    for episode in candidate_for_removing_from_episodes_list_from_pps:
        episodes_list_from_pps.remove(episode)

    for episode in candidate_for_removing_from_episodes_list_from_cmdc:
        episodes_list_from_cmdc.remove(episode)

    assert len(episodes_list_from_pps)==0, "Something went wrong, the list episodes_list_from_pps was suppose to be empty"

    if len(episodes_list_from_cmdc) > 0:
        for episode in episodes_list_from_cmdc:
            error_message = "episode \"{}\" appears in episodes_list_from_cmdc but was not found in episodes_list_from_pps".format(episode)
            logger.error(error_message)
            mismatch_found(error_message)
            episodes_list_from_cmdc.remove(episode)

    # Returning the results
    if mismatch_found.count == 0:
        logger.debug("Episodes lists are identical.")
        return True
    else:
        raise AssertionError, ("\nCount of mismatches were found : {}\nMismatches were found :{}".format(mismatch_found.count, mismatch_found.message))


class SERIES(object):

    @classmethod
    def delete_all_catalog(cls):
        # clean all booking catalog
        data = get_all_catalog()
        if len(data) > 0:
            for booking in data:
                delete_booking(booking)
            assert len(get_all_catalog()) == 0

    @classmethod
    def verify_all_episodes_one_series(cls, title):

        data = get_all_catalog()
        #verify more than one event is booking (series)
        assert len(data) > 1

        # verify all booking events with same seriesId
        seriesId = data[0]['seriesId']
        for booking in data:
            assert seriesId == booking['seriesId']
            assert booking['recurrence'] == 'SERIES'
            assert booking['recurrenceActive'] == True
            assert booking['title'] == title
