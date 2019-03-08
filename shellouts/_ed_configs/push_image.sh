#!/bin/bash

#export DOCKER_REGISTRY=${DOCKER_REGISTRY:=docker.io}
#export REPO_NAME=$DOCKER_REGISTRY/$DOCKER_USERNAME/$DOCKER_REPO
#export DOCKER_IMAGE=$REPO_NAME:$DOCKER_REPO_TAG
#export DOCKER_IMAGE=$DOCKER_REGISTRY/$DOCKER_USERNAME/$DOCKER_REPO:$DOCKER_REPO_TAG
#DOCKER_IMAGE="docker.io/signup3000/sample-flask

export DOCKER_IMAGE=`echo "$DOCKER_IMAGE" | sed -e 's/ //g'`
export REPO_NAME=`echo $DOCKER_IMAGE | cut -d ":" -f 1`
export DOCKER_REPO_TAG=`echo $DOCKER_IMAGE | cut -d ":" -f 2`
export DOCKER_REGISTRY=`echo $REPO_NAME | cut -d "/" -f 1`
export DOCKER_REPO=`echo $REPO_NAME | cut -d "/" -f 3`
export DOCKER_USERNAME=${DOCKER_USERNAME:=`echo $REPO_NAME | cut -d "/" -f 2`}
#echo $DOCKER_IMAGE
#echo $DOCKER_REPO_TAG
#echo $REPO_NAME
#echo $DOCKER_REGISTRY
#echo $DOCKER_USERNAME
#export DOCKER_USERNAME=`echo $REPO_NAME | cut -d "/" -f 2`
#echo $DOCKER_REPO

echo ""
echo ""
echo "docker login into repository"
echo ""
echo "Logging into $DOCKER_REGISTRY with user=$DOCKER_USERNAME and password=$DOCKER_PASSWORD"
echo ""
echo ""

#Changed the endpoint to reflect below
#https://index.docker.io/v1/
docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD https://index.$DOCKER_REGISTRY/v1/

#docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD -e ${EMAIL-no-email@test.com} $DOCKER_REGISTRY
#
#if [ $DOCKER_REGISTRY == 'docker.io' ]
#then
#    docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD -e ${EMAIL-no-email@test.com} 
#else
#    docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD -e ${EMAIL-no-email@test.com} $DOCKER_REGISTRY
#fi

echo "docker tag $DOCKER_REPO $REPO_NAME:latest"
docker tag $DOCKER_REPO $REPO_NAME:latest

echo "docker push $REPO_NAME:latest"
docker push $REPO_NAME:latest

echo "docker tag $DOCKER_REPO $REPO_NAME:$DOCKER_REPO_TAG"
docker tag $DOCKER_REPO $REPO_NAME:$DOCKER_REPO_TAG

echo "docker push $DOCKER_IMAGE"
docker push $DOCKER_IMAGE

