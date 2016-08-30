#!/bin/bash

set -e

TEST_PATTERN="*_tests.py"
JBOSSCLI_PATTERN="jbosscli*"
INIT_PATTERN="*__init__*"

if [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    PATH=$PATH:/c/Python27
fi

rm -f .coverage

for f in `git ls-files **/*_tests.py | sed 's/\//\./g' | sed 's/\.py//g'`; do
  echo "-- $f"
  python -m coverage run --omit=$TEST_PATTERN,$JBOSSCLI_PATTERN,$INIT_PATTERN -a -m $f
done

python -m coverage html

#python -m unittest `ls *_tests.py | sed 's/\.py//g'`
