#!/bin/tcsh
set theFile="./$2.app/Settings.bundle/Root.plist"
set settingsFile="./$2.app/Settings.bundle/HeadendSettings.plist"

if (! -d "./$2.app" ) then
pwd
echo "Error: ./$2.app is Not there"
exit 1
endif

echo $theFile
set cnt=`/usr/libexec/PlistBuddy -c "Print PreferenceSpecifiers:" ${theFile} | grep "Dict"|wc -l`
echo "the count is: $cnt."
set cnt=`expr "$cnt" '-' '1'`
foreach i (`seq 0 $cnt`) 
    echo "the index is: $i."
    set val=`/usr/libexec/PlistBuddy -c "Print PreferenceSpecifiers:${i}:Title" ${theFile}`
    echo "the value of PreferenceSpecifiers:${i}:Title: is ${val}."

    if ( "$val" == "CTAP Headend" ) then
        echo "the index of the entry whose 'Title' is 'CTAP Headend' is $i."

        set allValues=`/usr/libexec/PlistBuddy -c "Print PreferenceSpecifiers:${i}:Values" ${theFile}`
        echo "All values = $allValues"
        set foundLab=0

        foreach curr ($allValues)
            echo $curr
            if ( "$curr" == "$1" ) then
                echo " ---- found $curr"
                set foundLab=1
                break
            endif
        end

        echo $foundLab
        if ( $foundLab ) then
            /usr/libexec/PlistBuddy -c "Add PreferenceSpecifiers:${i}:DefaultValue string $1" ${theFile}
            if ( $? != 0 ) then
                #try to set instead of add
                /usr/libexec/PlistBuddy -c "Set PreferenceSpecifiers:${i}:DefaultValue $1" ${theFile}
            endif

            # just to be sure that it worked
            set ver=`/usr/libexec/PlistBuddy -c "Print PreferenceSpecifiers:${i}:DefaultValue" ${theFile}`
            echo 'PreferenceSpecifiers:$i:DefaultValue set to: ' $ver
            break
        else
            echo "Lab not found - using CSDS"

            if ( "$1" =~ "openstack*") then
                echo "Using open stack"
                if ( "$1" =~ "openstack-lwr*") then
                    set CSDS_URL="http://csds-server.$1.phx.cisco.com:8080"
                else
                    set CSDS_URL="http://csds.$1.phx.cisco.com:8080"
                endif
            else
                echo "Using VM"
                set CSDS_URL="http://sgw.$1.phx.cisco.com:8080"
            endif

            #10 is the index of the CSDS dictionary in the file
            /usr/libexec/PlistBuddy -c "Add PreferenceSpecifiers:8:DefaultValue string $CSDS_URL" ${settingsFile}

            if ( $? != 0 ) then
                #try to set instead of add
                /usr/libexec/PlistBuddy -c "Set PreferenceSpecifiers:8:DefaultValue $CSDS_URL" ${settingsFile}
            endif

            break
        endif

    endif

end
