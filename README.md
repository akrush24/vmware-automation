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
USAGE: ./run.py --help
```
