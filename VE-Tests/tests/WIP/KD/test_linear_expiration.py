import time
import datetime
import pytest
from tests_framework.ve_tests.ve_test import VeTestApi
import logging
from time import sleep
from suds.client import Client

configServiceWSDL = '/config/configService?WSDL'
defaultLinearExpiration = 43200
defaultKeepAliveInterval = 300
newLinearExpiration = 300
newKeepAliveInterval = 50
keepAliveFailed = "A problem occurred during playback, please try later.(ERR-001)"


def get_property_value(client, propertyName, setName="catv-sm"):
    value = client.service.getPropertiesInSet(setName)
    for field in value:
        if field.PropertyDefName == propertyName:
            logging.info("DefValue for %s = \"%s\"" % (propertyName, field.PropertyDefValue))
            return (field.PropertyDefValue)
    logging.error('PropertyDefValue %s undefined' % propertyName)
    assert False


def update_ui_property_value(client, propertyName, propertyValue, setName="catv-sm"):
    logging.info('Setting property: ''%s'' with value %s' % (propertyName, propertyValue))
    client.service.updatePropertyValue(setName, propertyName, propertyValue)

    '''
#PLEASE DONT RUN THIS TEST AGAINST VEOP LAB!!
# 1. Tune on clear channel and verify expiration date
@pytest.mark.linearexpiration
def test_tune_channel_expiration_message():
    my_test = VeTestApi("test_expiration_behavior")
    my_test.begin(my_test.login_types.login)

    soap_url = my_test.he_utils.PrmUrl + configServiceWSDL
    client = Client(soap_url)


    logging.info("Updating Keep Alive Interval to %d seconds" % newKeepAliveInterval)
    update_ui_property_value(client, "net.beaumaris.catv.keepaliveinterval", newKeepAliveInterval)
    keep_alive_interval = int(get_property_value(client, "net.beaumaris.catv.keepaliveinterval"))
    my_test.log_assert(keep_alive_interval == newKeepAliveInterval,"Keep Alive Interval value was not updated correctly")

    logging.info("Updating Linear Expiration to %d seconds" % newLinearExpiration)
    update_ui_property_value(client, "net.beaumaris.response.linearExpiration", newLinearExpiration)
    timeout = int(get_property_value(client, "net.beaumaris.response.linearExpiration"))
    my_test.log_assert(timeout == newLinearExpiration, "Linear Expiration value was not updated correctly")

    channel_id, channel_prop = my_test.he_utils.getLinearContentABR("encrypted")
    my_test.screens.zaplist.tune_to_channel_by_sek(channel_id)

    logging.info("Waiting for timeout in %d seconds" % (timeout + newKeepAliveInterval + 5))
    sleep(timeout + newKeepAliveInterval + 5)

    logging.info("Checking for a notification error")
    element_notif = my_test.milestones.getElement([("name", "NotificationView", "==")])
    my_test.log_assert(element_notif, "Failed to retrieve Notification view ...")
    my_test.log_assert(element_notif["text_0"] == keepAliveFailed, "A keep alive error message was expected ...")
    my_test.end()
    '''