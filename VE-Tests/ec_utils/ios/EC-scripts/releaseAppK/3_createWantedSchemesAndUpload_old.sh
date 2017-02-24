#!/usr/bin/env bash
echo "Timestamp=[`date +"%Y-%m-%d_%H:%M:%S"`]"
set -x
SIGN_ID='iPhone Developer: Nadav Hassan'
mypwd=$(pwd)
APPSPOT_TARGET_PATH=K-Release/$(ectool getProperty "version")
workspaceDir=$(ectool getProperty "/myParent/parent/workspace_dir")

#====================================
#      release version
#====================================
neededFlavors=""
prodCfgs=()
targetNames=()
i=0
if [[ "$(ectool getProperty "create_YES")" == "true" ]]; then
    neededFlavors=$neededFlavors" _YES"
    targetNames[$i]="PYES_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_ZTV")" == "true" ]]; then
    neededFlavors=$neededFlavors" ZTV"
    targetNames[$i]="PZTV_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_ZTV_Prod")" == "true" ]]; then
    neededFlavors=$neededFlavors" ZTV_Prod"
    targetNames[$i]="PZTV_PROD"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_AEG")" == "true" ]]; then
    neededFlavors=$neededFlavors" _AEG"
    targetNames[$i]="PAEG_REL"
    i=($i+1)
fi

if [[ "$(ectool getProperty "create_Apollo")" == "true" ]]; then
    neededFlavors=$neededFlavors" _Apollo"
    targetNames[$i]="PAPOLLO_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_IVP_PoC")" == "true" ]]; then
    neededFlavors=$neededFlavors" _IVP"
    targetNames[$i]="PIVP_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_OSN_PoC")" == "true" ]]; then
    neededFlavors=$neededFlavors" _OSN"
    targetNames[$i]="POSN_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Proximus")" == "true" ]]; then
    neededFlavors=$neededFlavors" _Proximus"
    targetNames[$i]="PPROXIMUS_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Voo")" == "true" ]]; then
    neededFlavors=$neededFlavors" _Voo"
    targetNames[$i]="PVOO_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Etisalat")" == "true" ]]; then
    neededFlavors=$neededFlavors" _Etisalat"
    targetNames[$i]="PETISALAT_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Solaris")" == "true" ]]; then
    neededFlavors=$neededFlavors" _Solaris"
    targetNames[$i]="PSOLARIS_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_TME")" == "true" ]]; then
    neededFlavors=$neededFlavors" _TME"
    targetNames[$i]="PTME_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Videotron")" == "true" ]]; then
    neededFlavors=$neededFlavors" _Videotron"
    targetNames[$i]="PVTRON_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Net")" == "true" ]]; then
    neededFlavors=$neededFlavors" Net"
    targetNames[$i]="PNET_REL"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Net_Prod")" == "true" ]]; then
    neededFlavors=$neededFlavors" Net_Prod"
    targetNames[$i]="PNET_Prod"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_NET_IDM_Prod")" == "true" ]]; then
    neededFlavors=$neededFlavors" NET_IDM_Prod"
    targetNames[$i]="PNET_IDM_Prod"
	prodCfgs[$i]=dbg
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_NET_Prod_SD")" == "true" ]]; then
    neededFlavors=$neededFlavors" NET_Prod_SD"
    targetNames[$i]="PNET_Prod_SD"
    i=($i+1)
fi
if [[ "$(ectool getProperty "create_Telus")" == "true" ]]; then
    neededFlavors=$neededFlavors" _Telus"
    targetNames[$i]="PTELUS_REL"
    i=($i+1)
fi

i=0
somethingFailed=No
for flavor in $neededFlavors; do

	if [ "${prodCfgs[$i]}" != "" ]; then
		cfg=Debug
	else
		cfg=Release
	fi

	if [[ $flavor == _* ]]; then #all CiscoVE-based flavors start with _
		compiledApp=CiscoVE
		flavor=${flavor:1} #remove the _
	else
		compiledApp=$flavor
	fi
    cd $workspaceDir/WhitelabelApps/ProductK/
    echo "#@#@# build release target for $flavor type=${cfg}"
	echo "Timestamp=[`date +"%Y-%m-%d_%H:%M:%S"`]"
	echo "[`date +"%Y-%m-%d_%H:%M:%S"`] Starting $flavor">>$mypwd/build_times.txt
#    xcodebuild -project ProductK.xcodeproj -scheme ${targetNames[$i]} -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
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
    xcodebuild -project ProductK.xcodeproj -scheme ${targetNames[$i]} -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO || rc=`handleError`
	end=`date +%s`
	echo "xcodebuild took $((end-start)) seconds" >> $mypwd/build_times.txt
	rc=ok
	if [ $rc == ok ]; then 
		echo "#@#@# sign and create ipa"
		cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
		if [ "$flavor" == "Etisalat" ]; then
			./releaseSigning.sh $mypwd/derived/Build/Products/${cfg}-iphoneos/$compiledApp.app $flavor "Etisalat_VE_Demo_DIST.mobileprovision" "iPhone Distribution: Cisco Systems, Inc." "com.cisco.ve.etisalat"
		else
			./releaseSigning.sh $mypwd/derived/Build/Products/${cfg}-iphoneos/$compiledApp.app $flavor
		fi
		python ../common/publish_file_to_artifactory.py ./$flavor.ipa  $(ectool getProperty "version")/ios release
		echo release version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/$flavor.ipa >> $mypwd/uploaded.txt
		echo "#@#@# zip dsym + upload"
		cp -R $mypwd/derived/Build/Products/${cfg}-iphoneos/$compiledApp.app.dSYM ./
		zip -r $flavor.app.dSYM.zip ./$compiledApp.app.dSYM
		rm -r $compiledApp.app.dSYM
		python ../common/publish_file_to_artifactory.py $flavor.app.dSYM.zip  $(ectool getProperty "version")/ios release
		echo release version dsym uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/$flavor.app.dSYM >> $mypwd/uploaded.txt

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
    debugOutput=Happy
#    xcodebuild -project ProductK.xcodeproj -scheme "PK_DBG" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO CODE_SIGN_IDENTITY="$SIGN_ID"
	echo "[`date +"%Y-%m-%d_%H:%M:%S"`] Starting PK_DBG">>$mypwd/build_times.txt
	cd $workspaceDir/WhitelabelApps/ProductK/
	rc=ok
	flavor=PK_DBG
	start=`date +%s`
    xcodebuild -project ProductK.xcodeproj -scheme "PK_DBG" -derivedDataPath $mypwd/derived build ONLY_ACTIVE_ARCH=NO || rc=`handleError`
	end=`date +%s`
	echo "xcodebuild took $((end-start)) seconds" >> $mypwd/build_times.txt
	if [ $rc == ok ]; then 
		cd $(ectool getProperty "/myParent/tests_dir")/ec_utils/ios
		echo "#@#@# sign and create ipa"

		if [[ "$(ectool getProperty "create_pipeline_bundle")" == "true" ]]; then
			echo "#@#@# uploading .app.zip for pipeline"
			cp -rf $mypwd/derived/Build/Products/Debug-iphoneos/Happy.app .
			echo "============="
			pwd
			ls -l
			echo "============="

			zip -r ./Happy_PK_DBG.app.zip ./Happy.app
			rm -rf Happy.app
			python ../common/publish_file_to_artifactory.py ./Happy_PK_DBG.app.zip  $(ectool getProperty "version")/ios release
			echo pipeline version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/Happy_PK_DBG.app.zip >> $mypwd/uploaded.txt
		fi


		./releaseSigning.sh $mypwd/derived/Build/Products/Debug-iphoneos/${debugOutput}.app ProductK_debug
		echo "#@#@# upload to releases"
		python ../common/publish_file_to_artifactory.py ./ProductK_debug.ipa  $(ectool getProperty "version")/ios release
		echo debug version uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/ProductK_debug.ipa >>   $mypwd/uploaded.txt
		echo "#@#@# zip dsym + upload"
		cp -R $mypwd/derived/Build/Products/Debug-iphoneos/${debugOutput}.app.dSYM ./
		zip -r ProductK_debug.app.dSYM.zip ./${debugOutput}.app.dSYM
		rm -r ${debugOutput}.app.dSYM
		python ../common/publish_file_to_artifactory.py ProductK_debug.app.dSYM.zip  $(ectool getProperty "version")/ios release
		echo debug version dsym uploaded to http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$(ectool getProperty "version")/ios/ProductK_debug.app.dSYM >> $mypwd/uploaded.txt

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
