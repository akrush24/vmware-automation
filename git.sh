#!/bin/bash
if [[ $1 ]]
then
  comment=$1
else
  comment="`date`"
fi

git commit -a -m "$comment" && git push
