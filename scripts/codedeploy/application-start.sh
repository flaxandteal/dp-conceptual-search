#!/bin/bash

AWS_REGION=
CONFIG_BUCKET=
ECR_REPOSITORY_URI=
GIT_COMMIT=

INSTANCE=$(curl -s http://instance-data/latest/meta-data/instance-id)
INSTANCE_NUMBER=$(aws --region $AWS_REGION ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE" "Name=key,Values=Name" --output text | awk '{print $6}')
CONFIG=$(aws --region $AWS_REGION ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE" "Name=key,Values=Configuration" --output text | awk '{print $5}')

if [[ $DEPLOYMENT_GROUP_NAME =~ [a-z]+-publishing ]]; then
  CONFIG_DIRECTORY=publishing
  DOCKER_NETWORK=publishing
else
  CONFIG_DIRECTORY=web
  DOCKER_NETWORK=website
fi

(aws s3 cp s3://$CONFIG_BUCKET/conceptual-search/$CONFIG_DIRECTORY/$CONFIG.asc . && gpg --decrypt $CONFIG.asc > $CONFIG) || exit $?

source $CONFIG

if [[ $DEPLOYMENT_GROUP_NAME =~ [a-z]+-web ]]; then
  if [[ $INSTANCE_NUMBER == 1 ]]; then
    ELASTICSEARCH_HOST=$ELASTICSEARCH_1
    CONTENT_SERVICE_URL=$CONTENT_SERVICE_URL_1
  else
    ELASTICSEARCH_HOST=$ELASTICSEARCH_2
    CONTENT_SERVICE_URL=$CONTENT_SERVICE_URL_2
  fi
fi

docker run -d                                                           \
  --env=SEARCH_CONFIG=$SEARCH_CONFIG                                    \
  --env=ELASTIC_SEARCH_SERVER=$ELASTICSEARCH_HOST                       \
  --env=ELASTIC_SEARCH_ASYNC_ENABLED=$ELASTIC_SEARCH_ASYNC_ENABLED      \
  --env=ELASTIC_SEARCH_TIMEOUT=$ELASTIC_SEARCH_TIMEOUT                  \
  --env=SEARCH_INDEX=$SEARCH_INDEX                                      \
  --env=CONCEPTUAL_SEARCH_ENABLED=$CONCEPTUAL_SEARCH_ENABLED            \
  --env=USER_RECOMMENDATION_ENABLED=$USER_RECOMMENDATION_ENABLED        \
  --env=BIND_HOST=$BIND_HOST                                            \
  --env=BIND_PORT=$BIND_PORT                                            \
  --env=GA_SALT=$GA_SALT                                                \
  --env=GA_SUBSTR_INDEX=$GA_SUBSTR_INDEX                                \
  --name=dp-conceptual-search                                           \
  --net=$DOCKER_NETWORK                                                 \
  --restart=always                                                      \
  $ECR_REPOSITORY_URI/dp-conceptual-search:$GIT_COMMIT
