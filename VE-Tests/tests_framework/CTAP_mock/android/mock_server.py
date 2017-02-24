
__author__ = 'bwarshaw'

import re
import os.path
import difflib
from http_file_server import SimpleHttpServer
from requests.adapters import HTTPAdapter
from pyjsonrpc import parse_response_json
from json import loads, dump
import requests

''' Global constants '''
UPDATE_SNAPSHOTS_MODE = False
VALUE_FIELDS_TO_SKIP = ["title_text", "width", "value", "position"]
COMPARE_DATA_PATH = "DummyData/compare_data/"


class AndroidMockServer(object):

    def __init__(self, ve_test_api):
        self.ve_test = ve_test_api
        self.configuration = self.ve_test.configuration
        self.milestones = self.ve_test.milestones
        self.mock_server = SimpleHttpServer()
        self.mock_server.start()

        requests.adapters.DEFAULT_RETRIES = 5

        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=5))

    def post_milestones_request(self, method, params="null"):
        response = None
        try:
            payload = '{"jsonrpc": "2.0", "method": "' + method + '", "params": '+params+', "id" : 2}'
            response = requests.post("http://" + self.ve_test.device_ip +"/milestones", data=payload, timeout=5)
            if response:
                response = parse_response_json(response.text)
                response = loads(response.result)
                if "elements" not in response:
                    return response
                response = response["elements"]
        except Exception as ex:
            assert(False, "Failed to send milestone %s. ex = %s" %(method,ex))
        return response

    def stop_mock_server(self):
        self.mock_server.stop()
        self.mock_server.waitForThread()

    def close_mock_server(self):
        self.stop_mock_server()

    def set_mock_data(self, preference_name, preference_value):
        mock_ip = "http://" + str(self.mock_server.ip) + ":" + str(self.mock_server.port) + "/"
        self.post_milestones_request('setSharedPreference', '["'+preference_name+'", "' + mock_ip + preference_value+'"]')

    def get_mock_address_data(self, bundle_path):
        mock_ip = "http://" + str(self.mock_server.ip) + ":" + str(self.mock_server.port) + "/"
        return mock_ip + bundle_path

    def saveMilestonesToFile(self, milestones, file_path):
        toSave = {}

        result = self.removeUnComparableMilestones(milestones)
        toSave["elements"] = result
        with open(file_path, 'w') as outfile:
            dump(toSave, outfile, indent=4, separators=(',', ': '))

    def compareMilestonesWithFile(self, needToSave, elements, compareFilePath):
        if (UPDATE_SNAPSHOTS_MODE or needToSave):
            self.saveMilestonesToFile(elements, compareFilePath)

        self.ve_test.log_assert(os.path.isfile(compareFilePath), "compare file %s does not exsists" % compareFilePath)

        self.saveMilestonesToFile(elements, compareFilePath + "_")
        diff = difflib.ndiff(open(compareFilePath).readlines(), open(compareFilePath + "_").readlines())
        lines = list(diff)
        delta = ''.join([line
                         for line in lines
                         if re.match("^[+-?]", line)])
        if len(delta) != 0:
            full_delta = ''.join(lines)
            print full_delta

            text_file = open(compareFilePath+".diff", "w")
            text_file.write(full_delta)
            text_file.close()

            os.remove(compareFilePath + "_")
            self.ve_test.log_assert(False, "Snapshot and milestones are different for file: %s" %compareFilePath)
        os.remove(compareFilePath + "_")

    def removeUnComparableMilestones(self, milestones):
        result = []
        for element in milestones:
            if 'name' in element and element['name'] == 'event_view':
                element['time_text'] = "null"
                element['progress_bar'] = "null"
            if 'name' in element and element['name'] == 'airing_time':
                element['title_text'] = "null"
            if 'x_pos' in element:
                element['x_pos'] = "null"
            if 'y_pos' in element:
                element['y_pos'] = "null"
            if 'height' in element:
                element['height'] = "null"
            if 'width' in element:
                element['width'] = "null"
            if "compare_value" in element and element["compare_value"] == False:
                elementCopy = element.copy()
                for field in VALUE_FIELDS_TO_SKIP:
                    if field in elementCopy:
                        del(elementCopy[field])
                result.append(elementCopy)
            else:
                result.append(element)
        return result

    def compare_milestones_to_reference(self, screen_ref, needToSave=False, elements=None):
        reference_path = COMPARE_DATA_PATH + "screen_data_" + screen_ref + "_" + self.ve_test.milestones.getDeviceDetails()["device-model"] + ".json"
        reference_path = reference_path.replace(" ", "_")

        if elements is None:
            elements = self.ve_test.milestones.getElements()

        if UPDATE_SNAPSHOTS_MODE or needToSave:
            self.saveMilestonesToFile(elements, reference_path)

        self.ve_test.log_assert(os.path.isfile(reference_path))

        self.saveMilestonesToFile(elements, reference_path + "_")
        diff = difflib.ndiff(open(reference_path).readlines(), open(reference_path + "_").readlines())
        lines = list(diff)
        delta = ''.join([line
                         for line in lines
                         if re.match("^[+-?]", line)])
        if len(delta) != 0:
            full_delta = ''.join(lines)
            print full_delta

            text_file = open(reference_path+".diff", "w")
            text_file.write(full_delta)
            text_file.close()

            os.remove(reference_path + "_")
            self.ve_test.log_assert(False, "Snapshot and milestones are different for file - %s" % reference_path)
        os.remove(reference_path + "_")
