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
