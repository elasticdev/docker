#!/bin/bash

#export VERSION=1.4.2
#export VERSION=1.8.1
export VERSION=1.13.0

# Install docker-compose
#sh -c "curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose"
#chmod +x /usr/local/bin/docker-compose
#sh -c "curl -L https://raw.githubusercontent.com/docker/compose/${VERSION}/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose"

curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m)"
chmod +x /usr/local/bin/docker-compose
