#!/bin/bash

export DOCKER_IMAGE=`echo "$DOCKER_IMAGE" | sed -e 's/ //g'`
export REPO_NAME=`echo $DOCKER_IMAGE | cut -d ":" -f 1`
export DOCKER_REPO_TAG=`echo $DOCKER_IMAGE | cut -d ":" -f 2`
export DOCKER_REGISTRY=`echo $REPO_NAME | cut -d "/" -f 1`
export DOCKER_REPO=`echo $REPO_NAME | cut -d "/" -f 3`
export DOCKER_USERNAME=${DOCKER_USERNAME:=`echo $REPO_NAME | cut -d "/" -f 2`}

#aws ecr get-login-password | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.us-east-1.amazonaws.com
aws ecr get-login-password | docker login --username AWS --password-stdin $ACCOUNT_ECR

echo "docker tag $DOCKER_REPO $REPO_NAME:latest"
docker tag $DOCKER_REPO $REPO_NAME:latest

echo "docker push $REPO_NAME:latest"
docker push $REPO_NAME:latest

echo "docker tag $DOCKER_REPO $REPO_NAME:$DOCKER_REPO_TAG"
docker tag $DOCKER_REPO $REPO_NAME:$DOCKER_REPO_TAG

echo "docker push $DOCKER_IMAGE"
docker push $DOCKER_IMAGE

