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
 ./run.py -h
usage: run.py [-h] --net NET --vmname VMNAME [--datastor DS] [--folde FOLDER]
              [--datacenter DATACENTER] [--cluster CLUSTER] [--dsize DSIZE]
              [--msize MEM] [--cpu CPU] --desc DESC [--template TEMPLATE]
              [--onlyip ONLYIP] [--version] [--vcenter VCENTER]

optional arguments:
  -h, --help            show this help message and exit
  --net NET, -l NET     Network (ex. --net 192.168.0.0/24
  --vmname VMNAME, -n VMNAME
                        VM name (ex. --vmname vm-01)
  --datastor DS, -ds DS
                        Datastore
  --folde FOLDER        VM Folder in vCenter
  --datacenter DATACENTER, -dc DATACENTER
                        vSphere Datacenter
  --cluster CLUSTER, -cl CLUSTER
                        vSphere Cluster
  --dsize DSIZE, -hdd DSIZE
                        Disk Size
  --msize MEM, -m MEM   RAM Size
  --cpu CPU, -c CPU     CPU Count
  --desc DESC, -d DESC  Description
  --template TEMPLATE, -tm TEMPLATE
                        VM Template
  --onlyip ONLYIP       Only IP allocation (ex. --onlyip yes
  --version, -V         show program's version number and exit
  --vcenter VCENTER     vCenter URL
```
