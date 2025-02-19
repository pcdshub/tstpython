#!/bin/bash
HERE="$(dirname $(readlink -f ${BASH_SOURCE[0]}))"
CONF="${HERE}/redis.conf"
REDIS_DIR="/cds/group/pcds/pyps/apps/redis/6.2.1/bin"

"${REDIS_DIR}/redis-server" "${CONF}"
