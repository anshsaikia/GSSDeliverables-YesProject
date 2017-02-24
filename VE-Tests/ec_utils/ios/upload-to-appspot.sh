#!/bin/bash
set -x
EXTRA=
if [ "$3" == "link" ]; then
  EXTRA='-F output=link'
fi

ENVFILE=$(mktemp env-XXXX)
env > $ENVFILE

curl http://10.62.6.213/appLoad -F fileToUpload=@"$1" -F path="$2" -F keepToken=1 -F env_vars=@$ENVFILE $EXTRA

rm $ENVFILE
