import os
import sys
from pathlib import Path

from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager

from utils.ansible import generate_rke2_playbooks

NETWORK_NAME = "project"

fabric_rc_path = str(Path.cwd() / '.fabric' / 'fabric_rc')
os.environ['FABRIC_RC_LOCATION'] = fabric_rc_path
fablib = fablib_manager(fabric_rc=fabric_rc_path)

if len(sys.argv) > 1:
    slice = fablib.get_slice(name=sys.argv[1])
else:
    slices = [s for s in fablib.get_slices() if s.get_name().startswith("project-")]
    if len(slices) != 1:
        names = [s.get_name() for s in slices]
        sys.exit(f"Found {len(slices)} project slices {names}; pass the slice name as an argument")
    slice = slices[0]

print("Using slice:", slice.get_name())
generate_rke2_playbooks(slice, fablib, NETWORK_NAME)

node1 = slice.get_node("node1")
print("Tunnel to the nginx demo:")
print(f"  ssh -F .fabric/ssh_config -i keys/slice_key -N -L 8080:192.168.1.1:30090 ubuntu@{node1.get_management_ip()}")
