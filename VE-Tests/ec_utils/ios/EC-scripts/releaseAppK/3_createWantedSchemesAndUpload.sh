#!/usr/bin/env bash
echo "Timestamp=[`date +"%Y-%m-%d_%H:%M:%S"`]"
set -x
SIGN_ID='iPhone Developer: Nadav Hassan'
mypwd=$(pwd)
ParamVersion=$(ectool getProperty "A_version")
APPSPOT_TARGET_PATH=K-Release/$ParamVersion
workspaceDir=$(ectool getProperty "/myParent/parent/workspace_dir")

#====================================
#      release version
#====================================
neededFlavors=""
targetNames=()
i=0
if [[ "$(ectool getProperty "create_YES")" == "true" ]]; then
    neededFlavors=$neededFlavors" YES"
    targetNames[$i]="PYES_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_ZTV_Prod")" == "true" ]]; then
    neededFlavors=$neededFlavors" ZTV_Prod"
    targetNames[$i]="PZTV_PROD"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_ZTV")" == "true" ]]; then
    neededFlavors=$neededFlavors" ZTV"
    targetNames[$i]="PZTV_REL"
    i=($i+1)
fi
# if [[ "$(ectool getProperty "create_AEG")" == "true" ]]; then
#     neededFlavors=$neededFlavors" AEG"
#     targetNames[$i]="PAEG_REL"
#     i=($i+1)
# fi

if [[ "$(ectool getProperty "create_Apollo")" == "true" ]]; then
    neededFlavors=$neededFlavors" Apollo"
    targetNames[$i]="PAPOLLO_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_IVP_PoC")" == "true" ]]; then
    neededFlavors=$neededFlavors" IVP"
    targetNames[$i]="PIVP_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_OSN_PoC")" == "true" ]]; then
    neededFlavors=$neededFlavors" OSN"
    targetNames[$i]="POSN_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Proximus")" == "true" ]]; then
    neededFlavors=$neededFlavors" Proximus"
    targetNames[$i]="PPROXIMUS_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Voo")" == "true" ]]; then
    neededFlavors=$neededFlavors" Voo"
    targetNames[$i]="PVOO_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Etisalat")" == "true" ]]; then
    neededFlavors=$neededFlavors" Etisalat"
    targetNames[$i]="PETISALAT_REL"
    i=($i+1)
fi
# if [[ "$(ectool getProperty "create_Solaris")" == "true" ]]; then
#     neededFlavors=$neededFlavors" Solaris"
#     targetNames[$i]="PSOLARIS_REL"
#     i=($i+1)
# fi
if [[ "$(ectool getProperty "create_TME")" == "true" ]]; then
    neededFlavors=$neededFlavors" TME"
    targetNames[$i]="PTME_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Videotron")" == "true" ]]; then
    neededFlavors=$neededFlavors" Videotron"
    targetNames[$i]="PVTRON_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Net_Prod")" == "true" ]]; then
    neededFlavors=$neededFlavors" Net_Prod"
    targetNames[$i]="PNET_PROD"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Net")" == "true" ]]; then
    neededFlavors=$neededFlavors" Net"
    targetNames[$i]="PNET_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Net_OldKey")" == "true" ]]; then
    neededFlavors=$neededFlavors" NetOldKey"
    targetNames[$i]="PNET_OLDKEY"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_NET_IDM_Prod")" == "true" ]]; then
    neededFlavors=$neededFlavors" NET_IDM_Prod"
    targetNames[$i]="PNET_IDM_PROD"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_NET_Z_IDM_Appstore")" == "true" ]]; then
    neededFlavors=$neededFlavors" NET_IDM_Appstore"
    targetNames[$i]="PNET_IDM_APPS"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_NET_Prod_SD")" == "true" ]]; then
    neededFlavors=$neededFlavors" NET_Prod_SD"
    targetNames[$i]="PNET_PROD_SD"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_NET_Z_Appstore")" == "true" ]]; then
    neededFlavors=$neededFlavors" NET_AppStore"
    targetNames[$i]="PNET_APPS"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Telus")" == "true" ]]; then
    neededFlavors=$neededFlavors" Telus"
    targetNames[$i]="PTELUS_REL"
    i=($i+1)
fi

i=0
somethingFailed=No
compiledApp=CiscoVE
for flavor in $neededFlavors; do
    cd $workspaceDir/WhitelabelApps/ProductK/
    echo "#@#@# building $flavor"
	echo "Timestamp=[`date +"%Y-%m-%d_%H:%M:%S"`]"
	echo "[`date +"%Y-%m-%d_%H:%M:%S"`] Starting $flavor">>$mypwd/build_times.txt
	
	#if first in the loop fails, abort. otherwise report and continue
	function handleError() {
		somethingFailed=Yes
		if [ $i == 0 ]; then 
			echo "** first build failed - aborting! **" >> $mypwd/appspot.txt
			echo "** first build failed - aborting! **" >> $mypwd/build_times.txt
			echo abort
			exit -1 #will cause the whole script to exit
		else 
			echo "${flavor} FAILED" >> $mypwd/appspot.txt 
			echo "${flavor} FAILED" >> $mypwd/build_times.txt 
			echo skip
		fi
	}
	start=`date +%s`
#    xcodebuild -project ProductK.xcodeproj -scheme ${targetNames[$i]} -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
    (xcodebuild -project ProductK.xcodeproj -scheme ${targetNames[$i]} -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO | sed -f clean_comp_log.sed | tee compile.out ) || rc=`handleError`
	end=`date +%s`
	cfg=`sed -n -e 's:.*export BUILT_PRODUCTS_DIR=.*Products/\(.*\)-.*:\1:p' compile.out | head -1`
	echo "xcodebuild [$cfg] took $((end-start)) seconds" >> $mypwd/build_times.txt
	appFolder=`sed -n -e 's:.*export CODESIGNING_FOLDER_PATH=\(.*\):\1:p' compile.out | head -1`
	rc=ok
	if [ $rc == ok ]; then 
		echo "#@#@# sign and create ipa"
		cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
		
		if [ "$flavor" == "Etisalat" ]; then
			./releaseSigning.sh $appFolder $flavor "Etisalat_VE_Demo_DIST.mobileprovision" "iPhone Distribution: Cisco Systems, Inc." "com.cisco.ve.etisalat"
		elif [ "$flavor" == "NET_AppStore" ]||[ "$flavor" == "NET_IDM_AppStore" ]; then
			./releaseSigning.sh $appFolder $flavor "NET_dist.mobileprovision" "iPhone Distribution: NET SERVICOS DE COMUNICACAO S/A" "br.com.net.allip.cisco"
		else																    
			./releaseSigning.sh $appFolder $flavor
		fi
		python ../common/publish_file_to_artifactory.py ./$flavor.ipa  $ParamVersion/ios release
		echo release version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$ParamVersion/ios/$flavor.ipa >> $mypwd/uploaded.txt
		echo "#@#@# zip dsym + upload"
		cp -R $appFolder.dSYM ./
		zip -q -r $flavor.app.dSYM.zip ./$compiledApp.app.dSYM
		rm -r $compiledApp.app.dSYM
		python ../common/publish_file_to_artifactory.py $flavor.app.dSYM.zip  $ParamVersion/ios release
		echo release version dsym uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$ParamVersion/ios/$flavor.app.dSYM >> $mypwd/uploaded.txt

		echo "#@#@# upload release to appspot"
		./upload-to-appspot.sh ./$flavor.ipa K_app/ci/$APPSPOT_TARGET_PATH/release/$flavor>> $mypwd/appspot.txt;

		rm -r $flavor.ipa
		rm -r $flavor.app.dSYM.zip
	fi
	((i=i+1))
done

#====================================
#      debug version
#====================================

if [[ "$(ectool getProperty "create_debug")" == "true" ]] || [[ "$(ectool getProperty "create_pipeline_bundle")" == "true" ]]; then
    echo "#@#@# build debug"
    debugOutput=CiscoVE
#    xcodebuild -project ProductK.xcodeproj -scheme "PK_DBG" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
	echo "[`date +"%Y-%m-%d_%H:%M:%S"`] Starting PK_DBG">>$mypwd/build_times.txt
	cd $workspaceDir/WhitelabelApps/ProductK/
	rc=ok
	flavor=PK_DBG
	start=`date +%s`
    (xcodebuild -project ProductK.xcodeproj -scheme "PK_DBG" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO | sed -n -f clean_comp_log.sed) || rc=`handleError`
	end=`date +%s`
	echo "xcodebuild took $((end-start)) seconds" >> $mypwd/build_times.txt
	if [ $rc == ok ]; then 
		cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
		echo "#@#@# sign and create ipa"

		if [[ "$(ectool getProperty "create_pipeline_bundle")" == "true" ]]; then
			echo "#@#@# uploading .app.zip for pipeline"
			cp -rf $mypwd/derived/Build/Products/Debug-iphoneos/CiscoVE.app .
			mv CiscoVE.app Happy.app
			echo "============="
			pwd
			ls -l
			echo "============="

			zip -q -r ./Happy_PK_DBG.app.zip ./Happy.app
			rm -rf Happy.app
			python ../common/publish_file_to_artifactory.py ./Happy_PK_DBG.app.zip  $ParamVersion/ios release
			echo pipeline version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$ParamVersion/ios/Happy_PK_DBG.app.zip >> $mypwd/uploaded.txt
		fi


		./releaseSigning.sh $mypwd/derived/Build/Products/Debug-iphoneos/${debugOutput}.app ProductK_debug
		echo "#@#@# upload to releases"
		python ../common/publish_file_to_artifactory.py ./ProductK_debug.ipa  $ParamVersion/ios release
		echo debug version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$ParamVersion/ios/ProductK_debug.ipa >>   $mypwd/uploaded.txt
		echo "#@#@# zip dsym + upload"
		cp -R $mypwd/derived/Build/Products/Debug-iphoneos/${debugOutput}.app.dSYM ./
		zip -q -r ProductK_debug.app.dSYM.zip ./${debugOutput}.app.dSYM
		rm -r ${debugOutput}.app.dSYM
		python ../common/publish_file_to_artifactory.py ProductK_debug.app.dSYM.zip  $ParamVersion/ios release
		echo debug version dsym uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$ParamVersion/ios/ProductK_debug.app.dSYM >> $mypwd/uploaded.txt

		echo "#@#@# upload debug to appspot"
		./upload-to-appspot.sh ./ProductK_debug.ipa K_app/ci/$APPSPOT_TARGET_PATH/debug>> $mypwd/appspot.txt;

		rm -r ProductK_debug.ipa
		rm -r ProductK_debug.app.dSYM.zip
	fi
fi
echo "[`date +"%Y-%m-%d_%H:%M:%S"`] Finished">>$mypwd/build_times.txt
if [ $somethingFailed == Yes ]; then
	exit -1 #force failure of script
fi
