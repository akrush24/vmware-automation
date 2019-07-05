# VMware Automation #
набор скриптов для упращения развертывания виртуальныз машин в инфраструктуре vsphere

## INSTALLATION ##
```
pip3 install pyVim pyVmomi requests argcomplete paramiko python_terraform requests 
```
For autocomplete in bash
 *  https://argcomplete.readthedocs.io/en/latest/
 *  https://github.com/kislyuk/argcomplete
```
pip install argcomplete
activate-global-python-argcomplete

echo 'eval "$(register-python-argcomplete YouScriptDir(ex. ./run.sh) )"' >> ~/.bashrc
sourse ~/.bashrc
```

### Create Only New PHPIpam IP ###
```
./run.py \
--vmname=test-vm01 \
--desc="Test IP"
--net=192.168.222.0/24 \
--onlyip
```

### Credentials ###
```
cat >passwd.py<<EOF
user_api = ''
pass_api = ''
vc_user  = ''
vc_pass  = ''
EOF
```

### run ###
```
usage: run.py [-h] [--net NET] [--vmname VMNAME] [--ip IP] [--datastor DS]
              [--folder FOLDER] [--datacenter DATACENTER] [--cluster CLUSTER]
              [--dsize DSIZE] [--msize MEM] [--cpu CPU] [--desc DESC]
              [--template TEMPLATE] [--version] [--vcenter VCENTER] [--debug]
              [--exp EXP] [--ONLYIP] [-IPRM] [--EXPIRE] [-N] [--resize]

optional arguments:
  -h, --help            show this help message and exit
  --net NET, -l NET     Network [EXAMPLE: --net 192.168.0.0/24]. Auto assign
                        IP addres from IPAM
  --vmname VMNAME, -n VMNAME
                        VM name [EXAMPLE: --vmname vm-01]
  --ip IP               IP Address. If IP exist ip is not taken from IPAM
  --datastor DS, -ds DS
                        Datastore name
  --folder FOLDER       VM Folder in vCenter [EXMPLE: folder1/folder2]
  --datacenter DATACENTER, -dc DATACENTER
                        vSphere Datacenter name
  --cluster CLUSTER, -cl CLUSTER
                        vSphere Cluster
  --dsize DSIZE, --hdd DSIZE, -hdd DSIZE
                        Disk Size
  --msize MEM, --mem MEM, --ram MEM, -m MEM
                        RAM Size in GB
  --cpu CPU, -c CPU     CPU Count
  --desc DESC, -d DESC  Description
  --template TEMPLATE, -t TEMPLATE
                        VM Template
  --version, -V         show program's version number and exit
  --vcenter VCENTER, -v VCENTER
                        vCenter URL
  --debug               debug mode
  --exp EXP, -e EXP     Expiry date [EXAMPLE: --exp "31/01/20"]
  --ONLYIP, --onlyip, -IP
                        Only IP allocation [EXAMPLE: --ONLYIP]
  -IPRM                 Remove IP allocation
  --EXPIRE, -E          Set only expire [EXMPLE --EXPIRE]
  -N                    Edit Nodes only
  --resize, -r          Resize disk (only on Linux vms) [EXMPLE --RESIZE]
```

### HELP ###
```
USAGE: ./run.py --help
```
