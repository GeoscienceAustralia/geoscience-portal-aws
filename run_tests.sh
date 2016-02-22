#!/bin/sh

make install
RESULTS=$(nosetests ./Test/*.py)

exit $?
