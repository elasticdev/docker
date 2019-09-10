#!/bin/bash

export DOCKER_BUILD_DIR=${DOCKER_BUILD_DIR:=/var/tmp/docker/build}
export DOCKER_RUN_DIR=${DOCKER_RUN_DIR:=$DOCKER_BUILD_DIR}
export DOCKER_RUN_IGNORE_COPY=${DOCKER_RUN_IGNORE_COPY:=None}
export DOCKER_COMPOSE_BUILD=${DOCKER_COMPOSE_BUILD:=None}
export DOCKER_COMPOSE_BACKGROUND=${DOCKER_COMPOSE_BACKGROUND:=True}

if [ $DOCKER_BUILD_DIR != $DOCKER_RUN_DIR ] && [ $DOCKER_RUN_IGNORE_COPY != "True" ]
then
    #Clean up run dir
    rm -rf $DOCKER_RUN_DIR
    DIRNAME=$(dirname "$DOCKER_RUN_DIR")
    mkdir -p $DIRNAME
    cp -rp $DOCKER_BUILD_DIR $DOCKER_RUN_DIR

else
    echo "DOCKER_BUILD_DIR and DOCKER_RUN_DIR are the same directory"

fi

cd $DOCKER_RUN_DIR

if [ $DOCKER_COMPOSE_BUILD == "True" ]
then
   docker-compose build || exit 1
fi

if [ $DOCKER_COMPOSE_BACKGROUND == "True" ]
then
   docker-compose up -d
else
   docker-compose up
fi

exit_status=`docker-compose ps -q | xargs docker inspect -f '{{ .State.ExitCode }}' | grep -v 0 | wc -l | tr -d ' '`

exit $exit_status
