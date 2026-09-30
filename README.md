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

After permissions are properly set, you can use ```ssh -F .fabric/ssh_config -i keys/slice_key <node_management_ip_address>``` to SSH into an active node.