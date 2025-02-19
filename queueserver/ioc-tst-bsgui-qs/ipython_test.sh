#!/bin/bash
# ipython check of what we would load for queue server
HERE="$(dirname $(readlink -f ${BASH_SOURCE[0]}))"
source "${HERE}/../../tstenv"
ipython -i "${HERE}/ui_objs.py"
