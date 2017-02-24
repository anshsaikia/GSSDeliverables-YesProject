Purpose:
=========================================================
	The mock CTAP server is intended for use as dummy data, with no real HE, or as test server, to test applications with various data that is hard to create in real HE environments. 
	Later network problems and latency can be added.
	

How the server decides what file to serve:
=========================================================
	The mock server is serving files according to the request sent.
	It replaces the "?" and "/" in the url with "#" and searches for a json file with that name in the served files dir (regarding that, please see below).
	

Running the server:
=========================================================
	From the CTAP_mock directory you can just call python server.py. The files served will be the files in the filesToServe folder.
	If you want the files served by the server to be taken from a specific location you can specify it with the -d parameter: python server.py -d <folderLocation>. This is useful if you run the mock from a different directory. So, for example, if you run the server from the root of the VE-Tests folder you can use: python tests_framework/CTAP_mock/server.py tests_framework/CTAP_mock/filesToServe
	If you want the server to return generic responses and not specific per request you can run it in test mode using -m test. This will make the server not search for the specific request and params, and instead just return the gridResponse.json file for grid request and channelsResponse.json for channel requests etc.

Server is running on local host port 9000 

usage:
============================
from CTAP_mock dir: python server.py
from another dir: python <CTAP_mock_addr>/server.py <CTAP_mock_addr>/filesToServe
for test mode: python server.py -m test