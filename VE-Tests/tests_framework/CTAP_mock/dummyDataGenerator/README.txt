Dummy data generation:
There are a few ways you can generate dummy data for the CTAP mock to use, or for your app to use. You can of course do it manually, but there are a few tools here you can use.

Explicit download: 
====================================================
python downloadUrlToFile.py <url to download from> <file name to dump content>
this will download the contents from the given url into a directory names "generated" with the file name requested.
It will also normalize the times in the response to be from epoch 0. The server serving the files does the opposite operation, and normalizes the times to be now.

Create data:
=====================================================
generation utils has two options: create channels response and create grid response.
For channel response creation use: python generationUtils.py createChannelResponse <fileNameToGenerate> <numberOfChannelsToCreate> 
For grid response creation use: python generationUtils.py createGridResponse <fileNameToGenerate> <numberOfChannelsToCreate> 

when more REF APIs get implemented we'll have extend this script

Download urls from log:
=======================================================
This is the best way of creating all the data the app needs. Run the app and do all the stuff a user will do and you want to record.
The script takes the log file and finds all the REF APIs the app used (recognized by the "/CTAP/1.5.0" string inside the url), and downloads them into files. The files will be named after the url they were created from. I.e a file downloaded from ../CTAP/1.5.0/agg/grid?limit=200&offset=0&startDateTime=12-06-15-7:20:06Z&duration=10800 will be named agg#grid#limit=200&offset=0&startDateTime=0&duration=10800. The "/" and "?" will be replaced by "#" and the time will be normalized.
The files will be placed in the "generated" folder.