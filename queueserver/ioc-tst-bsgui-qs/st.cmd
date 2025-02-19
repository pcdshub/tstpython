#!/bin/bash
set -e

export QS_STARTUP_DIR
QS_STARTUP_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
# shellcheck disable=SC1091
source "${QS_STARTUP_DIR}/../../tstenv"

# Why are these set to the wrong numbers in startup somewhere?
export EPICS_CA_SERVER_PORT=5064
export EPICS_CA_REPEATER_PORT=5065

export MPLBACKEND="agg"

cd "${QS_STARTUP_DIR}"

echo ""
echo "* The working directory for the IOC is: ${PWD}"
echo "* The startup directory is: ${QS_STARTUP_DIR}"

echo ""
echo "* Rebuilding list of plans and devices..."
qserver-list-plans-devices --startup-dir "${QS_STARTUP_DIR}"

echo ""
echo "* Starting the RE manager..."
start-re-manager --startup-dir "${QS_STARTUP_DIR}"
