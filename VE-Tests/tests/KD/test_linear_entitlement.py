__author__ = 'mibenami'

import pytest
import logging
from tests_framework.ve_tests.ve_test import VeTestApi
from vgw_test_utils.IHmarks import IHmark

#without markers since there are no 2 channels with different offers for now
@IHmark.O_iOS
@IHmark.O_Android
def test_entitlement_change_2channels_subscription():
    ve_test = VeTestApi("Entitlement:test_entitlement_change_2channels_subscription")
    ve_test.begin()

    channelWithOfferX, channelWithOfferY = ve_test.screens.playback.findTwoChannelsWithDifferentOffers()
    ve_test.log_assert(channelWithOfferX and channelWithOfferY, "did not find 2 channels")
    channelWithOfferSek = channelWithOfferX['serviceEquivalenceKey']
    lcnWithOffer = channelWithOfferX['logicalChannelNumber']
    channelWithoutOfferSek = channelWithOfferY['serviceEquivalenceKey']
    lcnWithoutOffer = channelWithOfferY['logicalChannelNumber']

    offersToRemove = channelWithOfferY['offers']
    logging.info('Tuning to channel: %s   with offers: %s' %(channelWithoutOfferSek, offersToRemove))
    logging.info('tuning to channel %d before removing offers' % lcnWithoutOffer)
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelWithoutOfferSek)
    ve_test.wait(2)

    logging.info('remove offers: %s' %offersToRemove)
    logging.info('removing offers from channel %d' % lcnWithoutOffer)
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.configuration["he"]["generated_household"], offersToRemove, remove=True)
    ve_test.wait(5)

    logging.info('Tuning to channel: %s   with offers: %s' %(channelWithOfferSek,channelWithOfferX['offers']))
    #there is a good chance that if we go 4 channels back, we will be close to the channel which we want to play
    logging.info('Scrolling back 3 channels')
    ve_test.screens.zaplist.scroll_channels(-3)
    logging.info('tuning to channel %d which has the offers' % lcnWithOffer)
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelWithOfferSek)
    ve_test.wait(2)

    logging.info('Tuning to channel: %s   with offers: %s' %(channelWithoutOfferSek,offersToRemove))
    logging.info('tuning to channel %d without offer' % lcnWithoutOffer)
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelWithoutOfferSek, verify_streaming_started=False)
    ve_test.wait(3)

    ve_test.screens.notification.verify_entitlement_error_notification()

    ve_test.wait(1)
    logging.info('Adding back offers: %s' %offersToRemove)
    ve_test.say('setting offers back into channel %d' % lcnWithoutOffer)
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.configuration["he"]["generated_household"], offersToRemove)

    logging.info('Tuning again to channel: %s   with offers: %s' %(channelWithoutOfferSek,offersToRemove))
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelWithoutOfferSek)
    ve_test.wait(3)
    ve_test.end()

@IHmark.LV_L2
@IHmark.O_iOS
@IHmark.O_Android
@IHmark.MF244
@pytest.mark.MF244_Entitlement_check_linear
@pytest.mark.regression
@pytest.mark.export_regression_MF244_Entitlement_check_linear
@pytest.mark.level2
def test_entitlement_delete_offers():
    ve_test = VeTestApi("Entitlement:test_entitlement_delete_offers")
    ve_test.begin()

    #The test is valid playing encrypted channels only
    encryptedChannels = ve_test.screens.playback.getChannelsByFilters([("drmType", "vgDrm")])
    logging.info("drm channels = [%s]" % encryptedChannels)
    ve_test.log_assert(len(encryptedChannels) > 0, "Encrypted channels do not exist in the list!")

    channelX = encryptedChannels[list(encryptedChannels)[0]]
    channelY = ve_test.screens.playback.findChannelWithOfferX(encryptedChannels, channelX)
    ve_test.log_assert(channelX and channelY, "not found 2 channels")
    channelXSek = channelX['serviceEquivalenceKey']
    channelXlcn = channelX['logicalChannelNumber']
    channelYSek = channelY['serviceEquivalenceKey']
    channelYlcn = channelY['logicalChannelNumber']

    offersToRemove = channelY['offers']
    logging.info('Tuning to channel: %s   with offers: %s' %(channelYSek, offersToRemove))
    logging.info('tuning to channel %d before removing offers' % channelYlcn)
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelYSek)
    ve_test.wait(2)

    logging.info('remove offers: %s' %offersToRemove)
    logging.info('removing offers from channel %d' % channelYlcn)
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.configuration["he"]["generated_household"], offersToRemove, remove=True)
    ve_test.wait(5)

    logging.info('Tuning to channel: %s   with same offers: %s' %(channelXSek,channelX['offers']))
    logging.info('tuning to channel %d which has the offers' % channelXlcn)
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelXSek, verify_streaming_started=False)
    ve_test.wait(5)

    ve_test.screens.notification.verify_entitlement_error_notification()

    ve_test.wait(1)

    logging.info('Adding back offers: %s' %offersToRemove)
    ve_test.say('setting offers back into channel %d' % channelYlcn)
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.configuration["he"]["generated_household"], offersToRemove)

    ve_test.screens.main_hub.navigate()

    logging.info('Tuning again to channel: %s   with offers: %s' %(channelYSek,offersToRemove))
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelYSek)

    logging.info('Tuning again to channel: %s   with offers: %s' %(channelXSek,offersToRemove))
    ve_test.screens.zaplist.tune_to_channel_by_sek(channelXSek)

    ve_test.wait(3)
    ve_test.end()

@IHmark.O_iOS
@IHmark.O_Android
@pytest.mark.Entitlement_stability
def test_entitlement_channel_change_stress():
    ve_test = VeTestApi("Entitlement:test_entitlement_channel_change_stress")
    ve_test.begin()

    services = ve_test.he_utils.get_abr_linear_services_from_cmdc()

    channelWithOfferX, channelWithOfferY = ve_test.screens.playback.findTwoChannelsWithDifferentOffers()
    ve_test.log_assert(channelWithOfferX and channelWithOfferY, "did not find 2 channels")

    channelWithOfferSek = channelWithOfferX['serviceEquivalenceKey']
    lcnWithOffer = channelWithOfferX['logicalChannelNumber']
    channelWithoutOfferSek = channelWithOfferY['serviceEquivalenceKey']
    lcnWithoutOffer = channelWithOfferY['logicalChannelNumber']
    offersToRemove =channelWithOfferY['offers']
    logging.info('remove offers: %s' %offersToRemove)
    logging.info('removing offers from channel %d' % lcnWithoutOffer)
    ve_test.he_utils.setHouseHoldAuthorization(ve_test.configuration["he"]["generated_household"], offersToRemove, remove=True)

    for index in range(15):
        logging.info('Round %d, tuning to channel %d with offer' % (index, lcnWithOffer))
        ve_test.screens.zaplist.tune_to_channel_by_sek(channelWithOfferSek)
        ve_test.wait(4)
        ve_test.screens.zaplist.tune_to_channel_by_sek(channelWithoutOfferSek, verify_streaming_started=False)
        ve_test.wait(4)

        ve_test.screens.notification.verify_entitlement_error_notification()

        #there is a good chance that if we go 3 channels back, we will be close to the channel which we want to play
        ve_test.screens.zaplist.scroll_channels(-3)

    ve_test.wait(1)
    ve_test.end()
