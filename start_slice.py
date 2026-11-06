from pathlib import Path
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager
import socket
import sys
from ipaddress import IPv4Network
import subprocess


# Force IPv4: one of the bastion's IPv6 addresses is unreachable and paramiko hangs on it
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only(host, port, family=0, *args, **kwargs):
    return _orig_getaddrinfo(host, port, socket.AF_INET, *args, **kwargs)
socket.getaddrinfo = _ipv4_only

nodeCnt = 3   # number of nodes
coreCnt = 4   # number of CPUs per node
memSize = 8  # memory per node
diskSize = 30 # storage per node

TEMPLATES_DIR = Path("templates").resolve()
PLAYBOOK_DIR = Path("playbook").resolve()
PLAYBOOK_DIR.mkdir(exist_ok=True)
assert (TEMPLATES_DIR / "host.yml.template").exists(), f"not found in {TEMPLATES_DIR}"

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

for _candidate in [Path.cwd(), *Path.cwd().parents]:
    if (_candidate / "utils" / "ansible.py").exists():
        sys.path.insert(0, str(_candidate))
        break
else:
    raise ImportError("Could not find repo root containing utils/ansible.py")

from utils.ansible import generate_rke2_playbooks

fablib = fablib_manager(fabric_rc=str(Path.cwd() / ".fabric" / "fabric_rc"))
fablib.verify_and_configure()

# change the user name to your username
slicePrefix = "pottsmatt217-project-"
network_name = "project-network"
nic_name = "projectnic"

# calculate resource requirements
minCores = nodeCnt * coreCnt * 2
minMem = nodeCnt * memSize * 2

# lauching site
resources = fablib.get_resources()
resources.update()
sites = resources.get_site_names()
selectedSite = ""

for site in sites:
    cores = resources.get_core_available(site)
    ram = resources.get_ram_available(site)
    if cores < minCores or ram < minMem:
        continue
    sliceName = slicePrefix + site

    # Clean up left-over slices with the same names
    for s in fablib.get_slices():
        if s.get_name() == sliceName:
            print(f"Deleting existing slice: {sliceName}")
            s.delete()
            break

    # Set up new slice
    slice = fablib.new_slice(name=sliceName)
    net = slice.add_l2network(name=network_name, subnet=IPv4Network("192.168.1.0/24"))

    for i in range(1, nodeCnt + 1):
        node = slice.add_node(name=f"node{i}",
                              site=site,
                              cores=coreCnt,ram=memSize,disk=diskSize,
                              image="default_ubuntu_22",)
        iface = node.add_component(model="NIC_Basic", name=nic_name).get_interfaces()[0]
        iface.set_mode("config")
        net.add_interface(iface)

    print("==========================================================================")
    try:
        print(f"Submitting slice at {site}...")
        slice.submit(progress=False, wait=True)
    except Exception as e:
        print(f"{site}: slice submission failed with error {e}")
        try:
            slice.delete()
        except Exception:
            pass
        continue

    slice.update()
    if slice.get_state() == "Closing":
        print(f"{site}: slice is closing, need to find new site")
        try:
            slice.delete()
        except Exception:
            pass
        continue

    # Setup networking
    for i in range(1, nodeCnt + 1):
        node = slice.get_node(name=f"node{i}")
        iface = node.get_interface(network_name=network_name)
        iface.ip_link_up()
        iface.ip_addr_add(
            addr=f"192.168.1.{i}",
            subnet=IPv4Network("192.168.1.0/24"),
        )
        print(f"{node.get_name()} -> 192.168.1.{i}")

    selectedSite = site
    print(f"Slice at {selectedSite} is stable: {slice.isStable()}")
    break

if not selectedSite:
    sys.exit("No site had enough resources or every submission failed")

sliceName = slicePrefix + selectedSite
slice = fablib.get_slice(name=sliceName)

generate_rke2_playbooks(slice, fablib, network_name, templates_dir=TEMPLATES_DIR, playbook_dir=PLAYBOOK_DIR)


def run_playbook(name, label, template=False):
    if template:
        playbook = PLAYBOOK_DIR / f"playbook-{name}.yml"
    else:
        playbook = Path(f"playbook-{name}.yml").resolve()

    log_path = LOG_DIR / f"{selectedSite}-ansible-{name}.log"
    with open(log_path, "w") as log_file:
        print(f"==== Running {label} playbook ====")
        result = subprocess.run(["ansible-playbook","-i",
                                 str(PLAYBOOK_DIR / "inventory.yml"),
                                 str(playbook),],
            stdout=log_file,stderr=subprocess.STDOUT,text=True,)

    if result.returncode != 0:
        sys.exit(f"{selectedSite}: {label} playbook failed, see {log_path}")
    print(f"{label} playbook is completed")


run_playbook("prereqs", "Prerequisite", True)
run_playbook("nfs", "NFS")
run_playbook("rke2", "RKE2", True)
run_playbook("app", "App")

# RKE2 Validation

server = slice.get_node("node1")
print("==== nodes ====")
stdout, stderr = server.execute("kubectl get nodes -o wide", quiet=True)
print(stdout)

nodes = slice.get_nodes()
for node in nodes:
    print("----", node.get_name(), "----")
    print("management ip:", node.get_management_ip())
    print(node.get_ssh_command())
