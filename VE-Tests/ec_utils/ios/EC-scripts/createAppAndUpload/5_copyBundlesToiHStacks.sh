#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_60.jdk/Contents/Home

ihstack_version=$(ectool getProperty "ihstack_version")
release_path=$(ectool getProperty "release_path")
mypwd=$(pwd)

#########################################
# Upload labs debug version
#########################################

if [[ "$(ectool getProperty "copy_labs_debug")" == "true" ]]; then
    
   ipa=KD_Pearl_debug.ipa
   lab=kd_labs
   build=debug

   #Download file
   wget http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$release_path/ios/$ipa

   #upload to IHStack   
   if [ -f ./$ipa ]; then
      curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa -T ./$ipa
      echo $lab $build version uploaded to http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa >> $mypwd/uploaded.txt
   fi
   rm $ipa
fi



#########################################
# Upload labs release version
#########################################

if [[ "$(ectool getProperty "copy_labs_release")" == "true" ]]; then

   ipa=KD_Pearl_release.ipa
   lab=kd_labs
   build=release

   #Download file
   wget http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$release_path/ios/$ipa

   #upload to IHStack   
   if [ -f ./$ipa ]; then
      curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa -T ./$ipa
      echo $lab $build version uploaded to http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa >> $mypwd/uploaded.txt
   fi
   rm $ipa
fi



#########################################
# Upload live debug version
#########################################

if [[ "$(ectool getProperty "copy_live_debug")" == "true" ]]; then
    
   ipa=KD_Pearl_live_dbg.ipa
   lab=kd_live
   build=debug

   #Download file
   wget http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$release_path/ios/$ipa

   #upload to IHStack   
   if [ -f ./$ipa ]; then
      curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa -T ./$ipa
      echo $lab $build version uploaded to http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa >> $mypwd/uploaded.txt
   fi
   rm $ipa
fi



#########################################
# Upload live release version
#########################################

if [[ "$(ectool getProperty "copy_live_release")" == "true" ]]; then

   ipa=KD_Pearl_live.ipa
   lab=kd_live
   build=release

   #Download file
   wget http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$release_path/ios/$ipa

   #upload to IHStack   
   if [ -f ./$ipa ]; then
      curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa -T ./$ipa
      echo $lab $build version uploaded to http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa >> $mypwd/uploaded.txt
   fi
   rm $ipa
fi



#########################################
# Upload staging release version
#########################################

if [[ "$(ectool getProperty "copy_staging_release")" == "true" ]]; then

   ipa=KD_Pearl_staging.ipa
   lab=kd_staging
   build=release

   #Download file
   wget http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$release_path/ios/$ipa

   #upload to IHStack   
   if [ -f ./$ipa ]; then
      curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa -T ./$ipa
      echo $lab $build version uploaded to http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa >> $mypwd/uploaded.txt
   fi
   rm $ipa
fi



#########################################
# Upload pipeline (cicd) zip debug version
#########################################

if [[ "$(ectool getProperty "copy_pipeline_debug")" == "true" ]]; then

   ipa=ProductKD.app.zip
   lab=jer_cicd
   build=debug

   #Download file
   wget http://engci-maven-master.cisco.com/artifactory/spvss-vci-service-release-repo/VEoP/ci/$release_path/ios/$ipa

   #upload to IHStack   
   if [ -f ./$ipa ]; then
      curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa -T ./$ipa
      echo $lab $build version uploaded to http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/Packages/$lab/$build/$ipa >> $mypwd/uploaded.txt
   fi
   rm $ipa
fi


#===============================================
#      Upload stack.json to ihstack
#===============================================
#Upload to IHStack stack.json:
echo {\"3rd_parties_rpms\": {}, \"compatibility\": {}, \"pre_req_stacks\": []} >> stack.json
curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/ -T ./stack.json
rm stack.json



#===============================================
#      Upload release notes to HIstacks
#===============================================
#Upload to IHStack release notes:
if [ -n "$(ectool getProperty "release_notes")" ]; then
    echo "$(ectool getProperty "release_notes")" >> releasenotes.txt
    curl http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/ -T ./releasenotes.txt
    echo release notes to http://spvss-cloud-ci-deployer:36VmaUEER2yBh7N@engci-maven-master.cisco.com/artifactory/simple/spvss-cloud-ci-yum-dev/IHstacks/ios/$ihstack_version/releasenotes.txt >> $mypwd/uploaded.txt
    rm releasenotes.txt
fi


