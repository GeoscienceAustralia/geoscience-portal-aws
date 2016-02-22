#!/bin/sh

make install
RESULTS=$(nosetests ./test/*)

exit $?
