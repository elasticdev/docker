#!/bin/bash

# Expects REPOSITORY_URI, REPO_NAME, ECR_LOGIN, DOCKER_IMAGE_TAG

export DOCKER_BUILD_DIR=${DOCKER_BUILD_DIR:=/var/tmp/docker/build}
export DOCKER_ENV_FILE=${DOCKER_ENV_FILE:=${DOCKER_BUILD_DIR}/.env}

echo ""
echo "Building for repository $REPOSITORY_URI at $DOCKER_BUILD_DIR"
echo ""

# Build with custom image tag
cd $DOCKER_BUILD_DIR
echo ""
echo "execute: docker build -t $REPOSITORY_URI:$DOCKER_IMAGE_TAG . "
echo ""
docker build -t $REPOSITORY_URI:$DOCKER_IMAGE_TAG . || exit 1

# Build/tag with tag "latest"
echo ""
echo "execute: docker build -t $REPOSITORY_URI:latest . "
echo ""
docker build -t $REPOSITORY_URI:latest . || exit 1

echo ""
echo "Login to repository $REPOSITORY_URI"
echo ""
echo $ECR_LOGIN 
echo ""
$ECR_LOGIN || exit 1

echo ""
echo "Pushing latest image $IMAGE_ID to repository $REPOSITORY_URI"
echo "execute: docker push $REPOSITORY_URI"
echo ""
docker push $REPOSITORY_URI || exit 1
