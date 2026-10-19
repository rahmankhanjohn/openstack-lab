# openstack-lab

The free OpenStack path, in scripts.

Every resource that made me competent at OpenStack was free. What separated people who finished from people who bookmarked was the order, and being honest about what each resource is actually good for.

This repository holds the scripts for that order: a DevStack sandbox, a Kolla-Ansible rehearsal, and a status checker that tells you what is actually running.

## The six-week path

| Week | What you do | Resource |
|------|-------------|----------|
| 1 | Vocabulary and the service map | Linux Foundation LFS158 on edX, free audit |
| 2 | Stand up a sandbox, break it, restore it | `install-devstack.sh` |
| 3 | Deploy the production-shaped way and compare | `install-kolla.sh` |
| 4 | Networking deep dive | Neutron, subnets, routers, floating IPs |
| 5 | Run a real workload | image in, instance up, volume attached, snapshot taken |
| 6 | Write up what broke and share it | the community answers logs, not theory |

## Requirements

Linux. Ubuntu 22.04 or 24.04 is what these scripts target. 16 GB RAM minimum for Kolla, 8 GB for DevStack. Root access for the package installs.

## DevStack, the sandbox

```
chmod +x install-devstack.sh
./install-devstack.sh
source ~/devstack/openrc
python3 lab-status.py
```

DevStack is a development environment. It breaks on reboot and it is not production. That is exactly why it is the right first step: you can break it without consequence, and every failure teaches you something a production deployment would charge you for.

## Kolla-Ansible, the rehearsal

```
chmod +x install-kolla.sh
./install-kolla.sh
source /etc/kolla/admin-openrc.sh
python3 lab-status.py
```

Kolla-Ansible is the containerised deployment model that resembles how production clouds are actually built. Compare it against the DevStack sandbox and write down the differences. That comparison is the lesson.

## lab-status.py

Reads the running cloud and tells you what is up, what is missing and what to fix next.

```
$ python3 lab-status.py
OpenStack lab status
====================================================================
  ok   identity    4 rows        auth as admin
  ok   services    12 rows       keystone and the rest are registered
  ok   images      3 rows        at least one image to boot
  ok   flavors     6 rows        flavors to launch with
  ok   networks    4 rows        a network for the port
  ok   volumes     1 rows        block storage is alive
  ok   instances   2 rows        any running instance

  Lab looks healthy. Try breaking it on purpose, that is the point of a lab.
```

Exit code 1 when a check fails. It reads only, it changes nothing.

## Tests

```
python3 -m unittest test_lab_status -v
```

## Where this comes from

Written while preparing *OpenStack Without a Training Budget: The Free Path That Actually Works*.

## License

MIT
