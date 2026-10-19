#!/usr/bin/env bash
# Deploy OpenStack with Kolla-Ansible, the production-shaped way, on one host.
# This is the rehearsal stage after the DevStack sandbox.
set -euo pipefail

VENV_DIR="${VENV_DIR:-$HOME/kolla-venv}"
BRANCH="${KOLLA_BRANCH:-stable/2025.1}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-labpassword}"

say() { printf '\n==> %s\n' "$1"; }

say "Installing prerequisites"
sudo apt-get update -qq
sudo apt-get install -y -qq python3-dev python3-venv git jq curl \
    chrony apparmor-utils containerd docker.io \
    python3-openstackclient

say "Creating the virtualenv"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip wheel

say "Cloning Kolla-Ansible"
cd "$HOME"
git clone --branch "$BRANCH" https://github.com/openstack/kolla-ansible.git
cd kolla-ansible

say "Writing the deployment configuration"
cat > "$HOME/kolla-deployments.conf" <<CONF
[DEFAULT]
use_mariadb=yes
database_password=$ADMIN_PASSWORD
keystone_admin_password=$ADMIN_PASSWORD
enable_ironic=no
enable_heat=no
CONF

say "Installing Kolla-Ansible and the OpenStack client"
pip install --upgrade --requirement requirements.txt
pip install --upgrade --requirement tools/requirements.txt

say "Deploying, this takes 30 to 60 minutes"
source "$VENV_DIR/bin/activate"
sudo kolla-ansible deploy --configfile "$HOME/kolla-deployments.conf" 2>&1 | tee "$HOME/kolla-deploy.log"

say "Sourcing the environment"
echo "  source /etc/kolla/admin-openrc.sh"
echo "  then run: python3 $PWD/lab-status.py"

say "Done. Compare this deployment with the DevStack sandbox and note the differences."
