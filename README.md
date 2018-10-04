# VMware Automation #
набор скриптов для упращения развертывания виртуальныз машин в инфраструктуре vsphere

## INSTALLATION ##
 * pip3 install pyVim pyVmomi requests paramiko python_terraform requests

### Create Only New PHPIpam IP ###
```
./run.py \
--vmname=test-vm01 \
--desc="Test IP"
--net=192.168.222.0/24 \
--onlyip yes
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
./run.py --vcenter=vc-linx.srv.local \
--datacenter=Datacenter-Linx \
--datastor=27_localstore_r10 \
--template=template_centos7.3 
--vmname=test-vm01 \
--folde=test/test \
--cluster=linx-cluster01 \
--dsize=40 --msize=3096 --cpu=2 --desc="Descriptions" \
--net=192.168.222.0/24 \
```

### HELP ###
```
usage: run.py [-h] --net NET [--ip IP] --vmname VMNAME [--datastor DS]
              [--folder FOLDER] [--datacenter DATACENTER] [--cluster CLUSTER]
              [--dsize DSIZE] [--msize MEM] [--cpu CPU] --desc DESC
              [--template TEMPLATE] [--onlyip ONLYIP] [--version]
              [--vcenter VCENTER] [--debug DEBUG] [--exp EXP]

optional arguments:
  -h, --help            show this help message and exit
  --net NET, -l NET     Network [EXAMPLE: --net 192.168.0.0/24]. Auto assign
                        IP addres from IPAM
  --ip IP               IP Address. If IP exist ip is not taken from IPAM
  --vmname VMNAME, -n VMNAME
                        VM name [EXAMPLE: --vmname vm-01]
  --datastor DS, -ds DS
                        Datastore name
  --folder FOLDER       VM Folder in vCenter
  --datacenter DATACENTER, -dc DATACENTER
                        vSphere Datacenter name
  --cluster CLUSTER, -cl CLUSTER
                        vSphere Cluster
  --dsize DSIZE, --hdd DSIZE, -hdd DSIZE
                        Disk Size
  --msize MEM, --mem MEM, --ram MEM, -m MEM
                        RAM Size [SIZE: 1024, 2048, 4096, 6114]
  --cpu CPU, -c CPU     CPU Count
  --desc DESC, -d DESC  Description
  --template TEMPLATE, -tm TEMPLATE
                        VM Template
  --onlyip ONLYIP       Only IP allocation [EXAMPLE: --onlyip yes]
  --version, -V         show program's version number and exit
  --vcenter VCENTER     vCenter URL
  --debug DEBUG         debug mode
  --exp EXP             expire date [EXAMPLE: --exp "01/01/18"]

```
