#!/usr/bin/env bash

export DOCKER_BUILD_DIR=${DOCKER_BUILD_DIR:=/var/tmp/docker/build}
export WORKING_DIR="${DOCKER_BUILD_DIR}"

if [ ! -z "$MapDir" ]
then
   export WORKING_DIR="${DOCKER_BUILD_DIR}/${MapDir}"
fi

cd /
rm -rf $WORKING_DIR
mkdir -p $WORKING_DIR
