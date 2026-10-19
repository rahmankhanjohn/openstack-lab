#!/usr/bin/env bash
# Install OpenStack DevStack on a single Linux VM or bare metal host.
# DevStack is a development environment. It is not production. That is the point.
set -euo pipefail

TARGET_DIR="${TARGET_DIR:-$HOME/devstack}"
BRANCH="${DEVSTACK_BRANCH:-stable/2025.1}"

say() { printf '\n==> %s\n' "$1"; }

say "Installing prerequisites"
sudo apt-get update -qq
sudo apt-get install -y -qq git python3-pip python3-dev python3-venv \
    libffi-dev libssl-dev build-essential curl jq \
    mariadb-server mariadb-client apache2 libapache2-mod-dev \
    libvirt-dev libvirt-clients qemu-kvm xz-utils

say "Adding the OpenStack apt repository"
sudo apt-get install -y -qq software-properties-common
sudo add-apt-repository -y ppa:openstack/release
sudo apt-get update -qq

say "Cloning DevStack into $TARGET_DIR"
sudo git clone --branch "$BRANCH" https://github.com/openstack/devstack.git "$TARGET_DIR"
sudo chown -R "$USER":"$USER" "$TARGET_DIR"

say "Writing local.conf"
cat > "$TARGET_DIR/local.conf" <<'CONF'
[[local|roles]]
enable-service apache2

[[post-config|keystone]]
service_catalog_type = templated

[[post-config|nova-api]]
service_catalog_type = templated
CONF

say "Installing OpenStack client"
pip3 install --upgrade pip
pip3 install --upgrade --requirement "$TARGET_DIR/tools/requirements.txt"

say "Starting DevStack, this takes 20 to 40 minutes"
cd "$TARGET_DIR"
./stack/devstack 2>&1 | tee devstack.log

say "Sourcing the environment"
echo "  source $TARGET_DIR/openrc"
echo "  then run: python3 $TARGET_DIR/lab-status.py"

say "Done. Expect the control plane to need a restart after a host reboot, that is normal."
