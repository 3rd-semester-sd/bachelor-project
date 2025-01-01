#!/bin/bash

# This script builds and pushes Docker images for microservices.
# Example usage:
# ./build_and_push.sh mslaursen 0.1
# ./build_and_push.sh mslaursen 0.1 notification_service

# Constants
ROOT_DIR="./services"

# Script arguments
DOCKER_REPO=${1:-mslaursen}
TAG=${2:-0.1}
SERVICE_FILTER=${3:-}

# Function to handle errors
handle_error() {
  echo "Error: $1"
  exit 1
}

# Function to build and push Docker image for a service
process_service() {
  local SERVICE_DIR="$1"
  local SERVICE_NAME
  local IMAGE_NAME

  SERVICE_NAME=$(basename "$SERVICE_DIR" | sed 's/_/-/g')
  IMAGE_NAME="$DOCKER_REPO/$SERVICE_NAME:$TAG"

  echo "Processing service: $SERVICE_NAME"
  echo "Building Docker image: $IMAGE_NAME"

  # Navigate to the service directory
  cd "$SERVICE_DIR" || handle_error "Failed to enter directory $SERVICE_DIR"

  # Build the Docker image
  docker build -t "$IMAGE_NAME" . --no-cache || handle_error "Failed to build Docker image for $SERVICE_NAME"

  # Push the Docker image
  docker push "$IMAGE_NAME" || handle_error "Failed to push Docker image for $SERVICE_NAME"

  # Return to the root directory
  cd - > /dev/null || handle_error "Failed to return to root directory"

  echo "Successfully built and pushed: $IMAGE_NAME"
  echo "-----------------------------------------"
}

# Main script logic
if [ -n "$SERVICE_FILTER" ]; then
  # Process a specific service
  SERVICE_DIR="$ROOT_DIR/$SERVICE_FILTER"
  if [ -d "$SERVICE_DIR" ]; then
    process_service "$SERVICE_DIR"
  else
    handle_error "Service directory $SERVICE_DIR does not exist"
  fi
else
  # Process all services
  echo "Processing all services in $ROOT_DIR..."
  for SERVICE_DIR in "$ROOT_DIR"/*; do
    if [ -d "$SERVICE_DIR" ]; then
      process_service "$SERVICE_DIR"
    fi
  done
fi

echo "All services have been successfully processed."
