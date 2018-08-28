# VMware Automation #
набор скриптов для упращения развертывания виртуальныз машин в инфраструктуре vsphere

## INSTALLATION ##
 * pip3 install pyVim


### Create New PHPIpam IP ###
```./create_new_ip.py HOSTNAME DESCRIPTION SubnetID```

### Credentials ###
```
cat >> passwd.py<EOF
user_api = 'user'
pass_api = 'passwd'
vc_user = ''
vc_pass = ''
EOF
```

### run ###
````
run.py  --vmname=host045 --datastor=27_localstore_r10 --folde=test/test --datacenter=Datacenter-Linx
 --cluster=linx-cluster01 --dsize=40 --msize=3096 --cpu=2 --desc=INFRA
--net=192.168.222.0/24 --vcenter=vc-linx.srv.local  --template=template_centos7.3
````