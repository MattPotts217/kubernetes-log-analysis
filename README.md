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

## Alerts Details

# Timestamps

- All times are ISO 8601 in UTC: `2026-11-02T22:34:18Z`.
- Storage records its own `received_at` time for every event. The 60-second brute-force window uses `received_at`, because the sender's clock can be wrong or faked.
- The sender's `timestamp` is kept as `event_time` and used for display.

# Severity

Levels: `low`, `medium`, `high`, `critical`.

| Rule | Severity |
|---|---|
| Data exfiltration (request over 100 MB) | critical |
| Brute force (more than 5 failed logins from one IP in 60 seconds) | high |
| SQL injection, confidence ≥ 0.8 | high |
| SQL injection, confidence < 0.8 | medium |

# GET /alerts response

```json
{
  "alerts": [
    {
      "id": "uuid",
      "rule": "sql_injection",
      "severity": "high",
      "confidence": 0.9,
      "source_ip": "203.0.113.7",
      "event_time": "2026-11-02T22:34:18Z",
      "received_at": "2026-11-02T22:34:18Z",
      "description": "string"
    }
  ]
}
```


# Repeated brute-force alerts

An IP gets at most one brute-force alert per 60-second window. Storage enforces this in a single transaction: it inserts the alert only if no brute-force alert exists for that IP in the last 60 seconds. If each analyzer replica checked for itself instead, two replicas could see the 6th failure at the same moment and both create an alert.

# Storage tables (SQLite)

- **alerts**: `id` (UUID), `rule`, `severity`, `confidence`, `source_ip`, `event_time`, `received_at`, `description`
- **failed_logins**: `source_ip`, `received_at`, indexed on `(source_ip, received_at)`
- **audit_records**: `id`, `request_id`, `method`, `path`, `source_ip`, `status`, `received_at`. Append-only
