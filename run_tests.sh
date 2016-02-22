#!/bin/sh

make install
RESULTS=$(nosetests ./Test/*)

exit $?
