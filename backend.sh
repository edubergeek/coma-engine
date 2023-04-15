#!/bin/bash

while true
do
  if netstat -plnt | grep '172.17.0.1:5054'
  then
    echo 'Backend is running'
  else
    echo 'Starting backend'
    timestamp=`date '+%Y%m%d%H%M%S'`
    test -f COMAAPI.log && mv COMAAPI.log logs/COMAAPI-${timestamp}.log
    nohup /COMA/Coma/bin/coma-json-server -web-server -web-host 172.17.0.1 -web-port 5054 >COMAAPI.log 2>&1 &
  fi
  sleep 60
done
