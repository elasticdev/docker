#!/bin/bash

#DOCKER_ENV_FILE is a file expected by the Dockerfile
#that copies it into the container.  It allows 
#files to be copied to be dynamic.

# Most commont is to specify the DOCKER_REPO environmental variable
# which is in the format: <REPO_NAME:TAG>.  if tag is absent, then 
# latest is automatically tagged.

# If DOCKER_REPO is not provided, we try to deduce it from the 
# DOCKER_IMAGE, which is the fully qualified path
# REGISTRY/USERNAME/REPO_NAME:TAG
# e.g. DOCKER_IMAGE=docker.io/jimjones/flask_sample:78348sdffa08

export DOCKER_BUILD_DIR=${DOCKER_BUILD_DIR:=/var/tmp/docker/build}
export DOCKER_ENV_FILE=${DOCKER_ENV_FILE:=${DOCKER_BUILD_DIR}/.env}
#export BUILD_BASEDIR="`dirname $DOCKER_ENV_FILE`"
#export DEST_ENV_DIR=${DOCKER_BUILD_DIR}/${BUILD_BASEDIR}

if [ -f "$DOCKER_ENV_FILE" ]
then
    echo "DOCKER_ENV_FILE $DOCKER_ENV_FILE found."      
    if [ "$DOCKER_ENV_FILE" != "$DOCKER_BUILD_DIR/.env" ]; then
       cp -rp $DOCKER_ENV_FILE $DOCKER_BUILD_DIR/.env || exit 1
    fi
else
    echo ""
    echo "WARNING: $DOCKER_ENV_FILE not found."
    echo ""
    #exit 1
fi

if [ -z ${DOCKER_REPO+x} ]
then
    echo "DOCKER_REPO is unset"

    export DOCKER_IMAGE=`echo "$DOCKER_IMAGE" | sed -e 's/ //g'`
    export DOCKER_REPO_TAG=`echo $DOCKER_IMAGE | cut -d ":" -f 2`
    export REPO_NAME=`echo $DOCKER_IMAGE | cut -d ":" -f 1`

    export DOCKER_REGISTRY=`echo $REPO_NAME | cut -d "/" -f 1`
    export USERNAME=`echo $REPO_NAME | cut -d "/" -f 2`
    export DOCKER_REPO=`echo $REPO_NAME | cut -d "/" -f 3`
fi

if [ -z ${DOCKER_REPO+x} ]; 
then  
    echo ""
    echo "ERROR: DOCKER_REPO (e.g. flask_sample) needs to be set to do a build"
    echo ""
    exit 1
fi

if [ ! -z ${DOCKER_REPO_TAG+x} ]
then
    echo "Doing docker build of DOCKER_REPO $DOCKER_REPO with TAG $DOCKER_REPO_TAG."
    cd $DOCKER_BUILD_DIR || exit 1
    docker build -t $DOCKER_REPO:$DOCKER_REPO_TAG . || exit 1
fi

echo "Doing docker build of DOCKER_REPO $DOCKER_REPO with TAG latest."
cd $DOCKER_BUILD_DIR || exit 1
docker build -t $DOCKER_REPO . || exit 1
