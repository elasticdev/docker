#!/bin/bash

# Expects REPOSITORY_URI, REPO_NAME, ECR_LOGIN, DOCKER_IMAGE_TAG

export DOCKER_BUILD_DIR=${DOCKER_BUILD_DIR:=/var/tmp/docker/build}
export DOCKER_ENV_FILE=${DOCKER_ENV_FILE:=${DOCKER_BUILD_DIR}/.env}

echo "Building for repository $REPOSITORY_URI at $DOCKER_BUILD_DIR"

cd $DOCKER_BUILD_DIR
echo "execute: docker build -t $REPOSITORY_URI . "
docker build -t $REPOSITORY_URI . || exit 1

echo "Login to repository $REPOSITORY_URI"
$ECR_LOGIN || exit 1

echo "Pushing latest image $IMAGE_ID to repository $REPOSITORY_URI"
echo "execute: docker push $REPOSITORY_URI"
docker push $REPOSITORY_URI || exit 1

export IMAGE_ID=$(docker images -q ${REPOSITORY_URI}| head -n 1)

echo "execute: docker tag $IMAGE_ID $DOCKER_IMAGE_TAG"
docker tag $IMAGE_ID $DOCKER_IMAGE_TAG || exit 1

echo "Pushing latest image $IMAGE_ID with tag $DOCKER_IMAGE_TAG to repository $REPOSITORY_URI"
echo "execute: docker push $DOCKER_IMAGE_TAG"
docker push $DOCKER_IMAGE_TAG || exit 1

cd -

#docker tag build -t $DOCKER_REPO:$DOCKER_IMAGE_TAG . || exit 1
