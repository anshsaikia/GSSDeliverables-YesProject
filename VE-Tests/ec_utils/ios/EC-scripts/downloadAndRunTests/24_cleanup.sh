#!/usr/bin/env bash
############## say something ############

health_check=$(ectool getProperty "/myParent/health_check")
resource_name=$(ectool getProperty "/myJobStep/assignedResourceName")
friendly_name=`echo $resource_name | grep -o '..$' `

[[  $health_check = "BAD" ]] && printf  '\xd7\x91\xd7\x95\xd7\xa2\xd7\x96\x2c\x20\xd7\xa0\xd7\xa9\xd7\x95\xd7\x9e\xd7\x94\x2c\x20\xd7\xaa\xd7\xa2\xd7\xa9\xd7\x94\x20\xd7\xa8\xd7\x99\xd7\xa1\xd7\x98\xd7\x90\xd7\xa8\xd7\x98\x20\xd7\x9c\xd7\x9e\xd7\x9b\xd7\xa9\xd7\x99\xd7\xa8\x3a' | iconv -f utf-8 | echo "$(cat -)$friendly_name" |say --voice=Carmit

############## Delete unused ###########
rm -rf -- $(ectool getProperty "/myParent/APP_BUNDLE_NAME")'.app.zip'