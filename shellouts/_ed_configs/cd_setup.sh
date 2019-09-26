#!/bin/bash

export CD_QUEUE_DIR=${CD_QUEUE_DIR:=/var/tmp/docker/cd/queue}
mkdir -p $CD_QUEUE_DIR
chmod 774 $CD_QUEUE_DIR
