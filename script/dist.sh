#!/bin/bash

msg(){
  echo
  echo $1
  echo "========================="
}

scripts=`dirname $0`
XP=`cd -P $scripts/..; echo $PWD`
mkdir -p $XP/../dist
cd $XP

msg "Prepare release"
VER=3.7
DIST=$XP/../dist
RELEASE=$DIST/xponents-core-$VER/
if [ -d $RELEASE ]  ; then
  rm -rf $RELEASE
fi

msg "Prepare Python API"
PYSRC=$PWD/src/main/python
if [ -d "$PYSRC/dist" ]; then
  rm -f $PYSRC/dist/*
fi
(cd $PYSRC  &&  python3.9 ./setup.py sdist)

mkdir -p $RELEASE

msg "Prepare Java API"
# Not for build.  Build ahead of time. This just copies
# mvn clean install
if [ -d ./lib ] ; then
  rm -f ./lib/*
fi
mvn dependency:copy-dependencies
cp target/*jar ./lib

msg "Copy items to Release $RELEASE"
unzip -q -d $RELEASE/etc/ ./etc/langdetect-profiles-v3.zip
cp -r ./script ./doc ./lib $RELEASE

cp LICENSE NOTICE *.md $RELEASE
mkdir $RELEASE/python
cp src/main/python/dist/opensextant*tar.gz $RELEASE/python
