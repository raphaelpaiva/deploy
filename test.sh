#!/bin/bash

set -e

TEST_PATTERN="*_tests.py"
JBOSSCLI_PATTERN="jbosscli*"

if [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    PATH=$PATH:/c/Python27
fi

rm -f .coverage

for f in $TEST_PATTERN; do
  echo "-- $f"
  python -m coverage run --omit=$TEST_PATTERN,$JBOSSCLI_PATTERN -a $f
done

python -m coverage html

#python -m unittest `ls *_tests.py | sed 's/\.py//g'`
