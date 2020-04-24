#!/bin/bash

htpasswd -Bbn $DOCKER_REGISTRY_USERNAME $DOCKER_REGISTRY_PASSWORD > /auth/.htpasswd
