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

### PHPIpam ###
For this stack need PhpIPAM system: https://github.com/phpipam/phpipam

Add ```$api_allow_unsafe = true;``` in config.php in your phpipam system

Example for create Only new IP in PHPIpam system run:
```
./run.py \
--vmname=test-vm01 \
--desc="Test IP"
--net=192.168.222.0/24 \
--onlyip
```

### Credentials ###
Before use create credential file
```
cat >passwd.py<<EOF
user_api = '' # IPAM user
pass_api = '' # IPAM user password
vc_user  = '' # vCenter administrator user name
vc_pass  = '' # vCenter administrator user password
EOF
```

### HELP ###
For Help USAGE: 
```
./run.py --help
```
