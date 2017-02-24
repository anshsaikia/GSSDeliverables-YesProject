#!/bin/bash
function validateProvisioningExpiration() {
#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#cd $DIR
ALERT_IF_MONTHS_LESS_THEN=4
MOBILE_PROV_FILE=$PROVISIONING_PROFILE
#security unlock-keychain -p a:123456
#sudo security default-keychain -d system -s /Users/cswci/Library/Keychains/login.keychain
#sudo security unlock-keychain -p a:123456 /Users/cswci/Library/Keychains/login.keychain
#echo "Increase keychain unlock timeout"
#sudo security set-keychain-settings -lut 7200 /Users/cswci/Library/Keychains/login.keychain

EXP=$(sudo security cms -D -i $MOBILE_PROV_FILE | sed -n -e '/ExpirationDate/ {n; s:.::; s:<[^>]*>::g; s:T.*::; p; }')
EXP_EPOCH=$(date -j -f '%Y-%m-%d' $EXP +%s)
CUR_EPOCH=$(date +'%s')
let "MONTHS_LEFT=(EXP_EPOCH-CUR_EPOCH)/2635200"
echo "Months left for $MOBILE_PROV_FILE: $MONTHS_LEFT"
NEED_ALERT=$(if [[ $MONTHS_LEFT -lt $ALERT_IF_MONTHS_LESS_THEN ]]; then echo ALERT; else echo NO_ALERT; fi)
if [ $NEED_ALERT == "ALERT" ]; then
                echo "Warning: Mobile Provisioning is about to expire, please consider renew"
                ectool setProperty "/myjob/expireSoon" --value "true"
else
                echo "Mobile provisioning $$PROVISIONING_PROFILE"
fi
}

set -x
APP_TO_SIGN="$1"
APP_NAME="$2"
PROVISIONING_PROFILE="$3"
CODESIGN_ID="$4"
APP_ID="$5"
echo $APP_TO_SIGN
cp -r $APP_TO_SIGN $APP_NAME.app
zip -r $APP_NAME.app.zip $APP_NAME.app
rm -r $APP_NAME.app
MY_APP_ZIP=$APP_NAME.app.zip

if [ "$PROVISIONING_PROFILE" == "" ]; then
    PROVISIONING_PROFILE=./Cisco_Generic_App_IL.mobileprovision
fi

validateProvisioningExpiration

if [ "$CODESIGN_ID" == "" ]; then
    CODESIGN_ID="iPhone Distribution: Cisco Video Technologies Israel Ltd (ent)"
fi
MY_EMAIL=""
MY_NOTES="$3"
IPA_URL=$(curl http://macserver-29568.il.nds.com/CodeSign -F upload=@$MY_APP_ZIP -F profile=@$PROVISIONING_PROFILE -F email="$MY_EMAIL" -F notes="$MY_NOTES" -F appspot=false -F codeSignIdentity="$CODESIGN_ID" -F appId="$APP_ID")
if [ -z $IPA_URL ]; then
    echo "Failed creating IPA. Check signer machine"
    exit 15
fi
echo $IPA_URL
curl $IPA_URL > ./$APP_NAME.ipa
rm $MY_APP_ZIP

