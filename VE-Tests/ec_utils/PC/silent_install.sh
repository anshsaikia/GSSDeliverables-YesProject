#!/bin/bash

dmgPath=$1
diskName=`/usr/bin/hdiutil attach $dmgPath -nobrowse  |/usr/bin/grep CiscoVideoGuard | /usr/bin/cut -f1 | sed 's/ *$//'`
volPath=`/usr/bin/hdiutil attach $dmgPath -nobrowse | /usr/bin/grep CiscoVideoGuard | /usr/bin/cut -f3`

cd $volPath
pkFileName=`/bin/ls  |/usr/bin/grep CiscoVideoGuard |/usr/bin/cut -f1 | sed 's/ *$//'`
pkgPath=$volPath/$pkFileName

installer -verboseR -pkg "$pkgPath" -tgt CurrentUserHomeDirectory

rc=$?

/usr/bin/hdiutil detach $diskName

echo installer return status is $rc

exit $rc


