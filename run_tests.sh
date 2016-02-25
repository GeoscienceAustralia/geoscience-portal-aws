#!/bin/sh

make install
nosetests -s ./test/*.py

exit $?
