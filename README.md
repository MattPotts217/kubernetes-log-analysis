# Kubernetes Log Analysis

***This project was created for Dr. Ngo's CSC 478 at West Chester University***

## Prerequisites

FABRIC Account

Populated keys directory with:
- fabric-bastion-key
- fabric-bastion-key.pub
- slice_key
- slice_key.pub
- Active id_token.json

Additionally, a populated .fabric/fabric_rc must be filled out. An example file is provided in .fabric/fabric_rc.example. A populated ssh_config file in .fabric/ssh_config must also be filled out. There is also an example file provided.

## Starting Slice
To start the application and get a FABRIC slice, run the following commands in the root directory:
```
source .fabric/fabric_rc
source .venv/bin/activate
python3 start_slice.py
```

## SSH

To ensure that you can SSH into a node, make sure that fabric-bastion-key and slice_key have permissions 600 and not 644:
```
chmod 600 keys/fabric-bastion-key
chmod 600 keys/slice_key
```

After permissions are properly set, you can use ```ssh -F .fabric/ssh_config -i keys/slice_key <ubuntu@node_management_ip_address>``` to SSH into an active node.

## Deploying the app

From the repo root on your machine (not on a slice node), with a slice running and `playbook/inventory.yml` up to date:

    ansible-playbook -i playbook/inventory.yml playbook-app.yml

This fills in the templates in `manifests/` with values from `vars/app.yml`, copies them to node1, applies them with `kubectl apply`, and waits for every rollout in the namespace to finish. It is safe to rerun on a live slice.

To deploy a new image version, push the new tag to Docker Hub and pass it in:

    ansible-playbook -i playbook/inventory.yml playbook-app.yml -e image_tag=0.1.1

Edit the templates in `manifests/`, not the rendered copies on node1, which are overwritten on every run.

## Refreshing Inventory

Use this when a slice is already running but `playbook/inventory.yml` is missing or points at an old slice, for example on a different machine or after running `start_slice.py` for another site. It rebuilds the inventory from the live slice without recreating it.

From the repo root:

```bash
python3 refresh_inventory.py              
python3 refresh_inventory.py project-NEWY
```

With no argument, the script uses the only running `project-*` slice. If it finds none or more than one, it lists them and exits, and you can rerun it with the slice name. It also prints an SSH tunnel command for the new slice.

Check that both nodes are reachable with the new inventory:

```bash
ansible -i playbook/inventory.yml all -m ping
```

Then deploy the app:

```bash
ansible-playbook -i playbook/inventory.yml playbook-app.yml
```
