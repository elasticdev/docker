#!/bin/bash

# Expects REPOSITORY_URI, REPO_NAME, DOCKER_LOGIN

export REPO_NAME=`echo $DOCKER_IMAGE | cut -d ":" -f 1`
export DOCKER_REPO_TAG=`echo $DOCKER_IMAGE | cut -d ":" -f 2`

MANIFEST=$(aws ecr batch-get-image --repository-name ${REPO_NAME} --image-ids imageTag=latest --query 'images[].imageManifest' --output text)
aws ecr put-image --repository-name ${REPO_NAME} --image-tag ${DOCKER_REPO_TAG} --image-manifest "$MANIFEST"
aws ecr describe-images --repository-name $REPO_NAME
