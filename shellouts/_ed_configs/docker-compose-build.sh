#!/bin/bash

#CONTAINER_FILES is a file expected by the Dockerfile
#that copies it into the container.  It allows 
#a single file such as a environmental one 
#to be copied to be dynamic.
export DOCKER_BUILD_DIR=${DOCKER_BUILD_DIR:=/var/tmp/docker/build}
export CONTAINER_FILES=${CONTAINER_FILES:=/root/.env}

export BUILD_BASEDIR="`dirname $CONTAINER_FILES`"
export DEST_ENV_DIR=${DOCKER_BUILD_DIR}/${BUILD_BASEDIR}

if [ -f "$CONTAINER_FILES" ]
then   
    echo "$CONTAINER_FILES found."      
    mkdir -p $DEST_ENV_DIR
    cp -rp $CONTAINER_FILES $DEST_ENV_DIR/
else   
    echo "$CONTAINER_FILES not found."
fi

#Determine the registry through the repo name
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

export DOCKER_REGISTRY=${DOCKER_REGISTRY:=docker.io}

#If DOCKER_USERNAME exists, we login.  otherwise, we assume config.json
#has the correct credentials

if [ ! -z "$DOCKER_USERNAME" ]
then
    echo "Logging in as $DOCKER_USERNAME"
    docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD $DOCKER_REGISTRY
else
    echo "Using config.json or logging in not required"
fi

cd $DOCKER_BUILD_DIR
docker-compose build
