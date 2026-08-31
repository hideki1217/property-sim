#!/bin/bash

set -eux 

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"

cd "$SCRIPT_DIR"

rm -f .env
touch .env
echo "HOST_UID=$(id -u)" >> .env
echo "HOST_GID=$(id -g)" >> .env
echo "HOST_HOME=${HOME}" >> .env
