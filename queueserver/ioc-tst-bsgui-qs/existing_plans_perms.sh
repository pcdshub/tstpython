#!/bin/bash
set -e
HERE="$(dirname $(readlink -f ${BASH_SOURCE[0]}))"
FNAME="${HERE}/existing_plans_and_devices.yaml"
touch "${FNAME}"
chgrp ps-ioc "${FNAME}"