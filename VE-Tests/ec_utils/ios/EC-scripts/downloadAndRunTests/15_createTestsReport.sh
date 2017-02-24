#!/usr/bin/env bash
set -x
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
SCRRENSHOT_DIR="screenshots"
REPORT_DIR="$(ectool getProperty "/myCall/reportDir")"

echo $(ectool getProperty "/myCall/reportDir")

# test failed but it was because of health check etc.
if [ ! -d "${REPORT_DIR}" ]; then
exit 0
fi

cd "$(ectool getProperty "/myCall/reportDir")"

echo "Download ant report scripts to $(ectool getProperty "/myCall/reportDir")"
wget -O "./build_junit_report.xml" "https://stash-eng-rtp1.cisco.com/stash/projects/CAMPNOU/repos/ci_utilities/browse/junit_reports/build_junit_report.xml?at=4ab8a05eb489e82b2f8d5303a7c11e905ad2067c&raw"
wget -O "./junit-frames.xsl" "https://stash-eng-rtp1.cisco.com/stash/projects/CAMPNOU/repos/ci_utilities/browse/junit_reports/junit-frames.xsl?at=0a682a2018536d72b8c7b3a0a6deeb323a41a69a&raw"
sed -i -- 's/frameset cols="20%/frameset cols="0%/g' junit-frames.xsl

SERIAL_NUMBER=$(ectool getProperty "/myParent/DEVICE_SERIAL")
echo "Build html output"
ant -f build_junit_report.xml -Darg0=$SERIAL_NUMBER.xml -Darg1=.

cp all-tests.html "$(ectool getProperty "/myCall/logDir")/test_report.html"

# comment because it is not working right now
# echo "Set EC link"
#   ectool setProperty "/myJob/report-urls/($(ectool getProperty "/myStep/stepName")) PyTest Report" --value "/commander/jobSteps/$(ectool getProperty "/myJobStep/jobStepId")/$(ectool getProperty "/myCall/shortReportDir")/overview-summary.html"
#   ectool setProperty "/myParent/report-urls/($(ectool getProperty "/myStep/stepName")) PyTest Report" --value "/commander/jobSteps/$(ectool getProperty "/myJobStep/jobStepId")/$(ectool getProperty "/myCall/shortReportDir")/overview-summary.html"

machine_name=$(ectool getProperty "/myResource/hostName")
resource_name=$(ectool getProperty "/myJobStep/assignedResourceName")

summary_url="http://"$machine_name"/$(ectool getProperty "/myJob/jobName")/$(ectool getProperty "/myCall/shortReportDir")/"
screenshots_url="http://"$machine_name"/$(ectool getProperty "/myJob/jobName")/$SCRRENSHOT_DIR"
echo "Summary URL = "$summary_url

ectool setProperty "/myParent/report-urls/Summary" --value $summary_url

cat overview-summary.html
cat stylesheet.css
echo $summary_url

cat>mail.sed <<EOF
  s~href=\"~href=\"${summary_url}/~g
  /<link/d
  /<head>/ {
  s/<head>/<head><style type="text\/css">/
  r stylesheet.css

  s_\$_\n<\/style>_

}
EOF

cat mail.sed
html_body=`cat overview-summary.html | sed -f mail.sed`
echo $html_body
ectool setProperty "/myParent/html_body" --value "$html_body"


cd ..
pwd

if [ "$(ls -A ./$SCRRENSHOT_DIR)" ]; then
     ectool setProperty "/myParent/report-urls/Screenshots" --value $screenshots_url
     #convert tiff format to jpg make it smaller size
     cd ./$SCRRENSHOT_DIR
     mogrify -rotate "90<" -format jpg *
     find ../screenshots/ -type f -not -name '*.jpg' | xargs rm -f
fi

