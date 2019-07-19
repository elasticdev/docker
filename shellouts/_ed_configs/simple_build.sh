#!/bin/bash

export DOCKER_BUILD_DIR=${DOCKER_BUILD_DIR:=/var/tmp/docker/build}
export DOCKER_ENV_FILE=${DOCKER_ENV_FILE:=${DOCKER_BUILD_DIR}/.env}
export DOCKER_FILE=${DOCKER_FILE:=Dockerfile}
export DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:=test}
export REPOSITORY_URI=${REPOSITORY_URI:=test}

# Build with custom image tag
cd $DOCKER_BUILD_DIR
echo "execute: docker build -t $REPOSITORY_URI:$DOCKER_IMAGE_TAG . -f $DOCKER_FILE "
docker build -t $REPOSITORY_URI:$DOCKER_IMAGE_TAG . -f $DOCKER_FILE|| exit 1
