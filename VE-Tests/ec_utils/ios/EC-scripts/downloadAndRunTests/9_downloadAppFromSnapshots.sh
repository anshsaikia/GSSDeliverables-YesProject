#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt:/opt/X11/bin



if [ -a locking.txt ]; then
    echo "Download has started in another thread. Waiting for app ready..."

    while [[ ! -a app_ready.flag ]]; do
      sleep 2
      date +%r
    done

    #if already downloaded ignore, no need to do it again
    if [ ! -d "$(ectool getProperty "/myParent/APP_FULL_NAME").app" ]; then
        echo "Downloading from other thread has failed - retrying"
    else
        echo "App is now ready. finished processing by the other step"
        exit 0
    fi
fi

touch locking.txt
touch lockedBy_$(ectool getProperty "/myJobStep/assignedResourceName").txt


#if there's appUrl, take that. If not, try for appPath from the parent, otherwise, fail
echo $(ectool getProperty "app_url")
downloadFrom="none"
if [[ -n "$(ectool getProperty "app_url")" ]]; then
downloadFrom="$(ectool getProperty "app_url")"
fi
if [[ $downloadFrom == "none" ]]; then
echo downloading latest
downloadFrom=`ectool getProperty "/projects/VE_iOS/last_ios_app_url_$(ectool getProperty "/myParent/APP_FULL_NAME")"`
fi
echo downloading from $downloadFrom
curl -vv -o $(ectool getProperty "/myParent/APP_FULL_NAME").app.zip $downloadFrom
ls
unzip $(ectool getProperty "/myParent/APP_FULL_NAME").app.zip
