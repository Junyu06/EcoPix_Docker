#!/bin/zsh
docker buildx build --platform linux/amd64,linux/arm64 -t junyu07/ecopix_docker:latest --load .
# Container name
CONTAINER_NAME="ecopix_docker"

# Check if the container already exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
  echo "Container $CONTAINER_NAME already exists. Removing it..."
  # Stop and remove the container
  docker stop $CONTAINER_NAME >/dev/null 2>&1
  docker rm $CONTAINER_NAME >/dev/null 2>&1
fi

# Run the new container
docker run --name $CONTAINER_NAME \
  -e DATABASE_URI="mysql+pymysql://user:password@host.docker.internal:13316/photo_app" \
  -e USERNAME="user" \
  -e UPASSWORD="password" \
  -v /Users/teriri/WIP_CODE/CSC184/PhotoApp/Photo:/Photos \
  -p 15381:15381 \
  junyu07/ecopix_docker:latest
