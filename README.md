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

Additionally, a populated .fabric/fabric_rc must be filled out. An example file is provided in .fabric/fabric_rc.example.

## Starting Slice
To start the application and get a FABRIC slice, run the following commands in the root directory:
```
source keys/fabric_rc
source .venv/bin/activate
python3 start_slice.py
```