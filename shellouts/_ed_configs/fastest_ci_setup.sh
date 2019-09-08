#!/bin/bash

export FASTEST_CI_QUEUE_DIR=${FASTEST_CI_QUEUE_DIR:=/var/tmp/docker/fastest_ci/queue}
mkdir -p $FASTEST_CI_QUEUE_DIR
chmod 774 $FASTEST_CI_QUEUE_DIR
