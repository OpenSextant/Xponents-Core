#!/bin/bash

PYVER=1.6

msg(){
  echo
  echo $1
  echo "========================="
}

cmd=$1

msg "Setup Project resource data"
ant setup

# Python setup.
msg "Build Python libraries"
unset PYTHONPATH
PYSRC=$PWD/src/main/python
if [ -d "$PYSRC/dist" ]; then
  rm -f $PYSRC/dist/*
fi
(cd $PYSRC  &&  python3.9 ./setup.py sdist)

msg "Install Python resources"
pip3 install -U --target ../piplib lxml bs4 arrow requests pyshp pycountry \
  ./src/main/python/dist/opensextant-${PYVER}*.tar.gz

if [ "$cmd" = "pydoc" ]; then 
  export PYTHONPATH=$PYSRC:$PWD/../piplib
  mkdir -p ./doc/python
  pushd ./doc/python
  pydoc3 -w opensextant \
    opensextant.xlayer opensextant.utility \
    opensextant.phonetics  opensextant.advas_phonetics \
    opensextant.gazetteer opensextant.extractors \
    opensextant.TaxCat opensextant.FlexPat
fi

msg Done

cat <<EOF
If you are developing libraries here remove the installed opensextant lib, e.g., 

   ../piplib/opensextant* 

or adjust your venv or PYTHONPATH to use the project source first in path:  ./src/main/python/

EOF

