#!/bin/bash

export DOCKER_BUILD_DIR=${DOCKER_BUILD_DIR:=/var/tmp/docker/build}

cd $DOCKER_BUILD_DIR
docker-compose build && docker-compose up -d && exit 0
