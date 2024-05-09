#!/bin/bash

scripts=`dirname $0`
XP=`cd -P $scripts/..; echo $PWD`

export CLASSPATH=$XP/etc:$XP/lib/*

xponents_args=" -Xmx500m -Xms500m "
logging_args="-Dlogback.configurationFile=$XP/etc/logback.xml"

java  $xponents_args $logging_args -cp $CLASSPATH \
  org.codehaus.groovy.tools.GroovyStarter --main groovy.ui.GroovyMain \
  $XP/script/XponentsCore.groovy  "$@"

echo "See Results in ./results/"
ls -1 ./results/
