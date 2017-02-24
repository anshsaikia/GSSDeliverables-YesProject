#!/bin/tcsh
set theFile="$1" #.app/Settings.bundle/Root.plist"
echo $theFile
set settingName="$2"
set settingValue="$3"
echo setting to change is $settingName and value is $settingValue
set cnt=`/usr/libexec/PlistBuddy -c "Print PreferenceSpecifiers:" ${theFile} | grep "Dict"|wc -l`
echo "the count is: $cnt."
set cnt=`expr "$cnt" '-' '1'`
foreach i (`seq 0 $cnt`) 
#echo "the index is: $i."
set val=`/usr/libexec/PlistBuddy -c "Print PreferenceSpecifiers:${i}:Key" ${theFile}`
#echo "the value of PreferenceSpecifiers:${i}:Key: is ${val}."
if ( "$val" == $settingName ) then
echo "the index of the entry whose 'Title' is $settingName is $i."
/usr/libexec/PlistBuddy -c "Add PreferenceSpecifiers:${i}:DefaultValue string $settingValue" ${theFile}
if ( $? != 0 ) then
#try to set instead of add
/usr/libexec/PlistBuddy -c "Set PreferenceSpecifiers:${i}:DefaultValue $settingValue" ${theFile}
endif
# just to be sure that it worked
set ver=`/usr/libexec/PlistBuddy -c "Print PreferenceSpecifiers:${i}:DefaultValue" ${theFile}`
echo 'PreferenceSpecifiers:$i:DefaultValue set to: ' $ver
endif
end
