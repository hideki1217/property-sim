#!/bin/bash

set -eux 

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"

cd "$SCRIPT_DIR"

HOST_MTU="$(ip link show "$(ip route show default | awk '{print $5}' | head -n1)" | grep -oP 'mtu \K[0-9]+')"

rm -f .env
touch .env
echo "HOST_UID=$(id -u)" >> .env
echo "HOST_GID=$(id -g)" >> .env
echo "HOST_HOME=${HOME}" >> .env
echo "HOST_MTU=${HOST_MTU}" >> .env
