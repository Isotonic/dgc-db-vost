#!/bin/sh

# Credit to Michael Herman
# https://testdriven.io/blog/deploying-flask-to-heroku-with-docker-and-gitlab/#docker

IMAGE_ID=$(docker inspect registry.heroku.com/${HEROKU_APP_NAME}/web --format={{.Id}})
PAYLOAD='{"updates": [{"type": "web", "docker_image": "'"$IMAGE_ID"'"}]}'

curl -n -X PATCH https://api.heroku.com/apps/$HEROKU_APP_NAME_PRODUCTION/formation \
  -d "${PAYLOAD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
  -H "Authorization: Bearer ${HEROKU_AUTH_TOKEN}"

curl -n -X PATCH https://api.heroku.com/apps/$HEROKU_APP_NAME_STAGING/formation \
  -d "${PAYLOAD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
  -H "Authorization: Bearer ${HEROKU_AUTH_TOKEN}"