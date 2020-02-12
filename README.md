# VMware Automation #
This are a set of scripts to simplify the deployment of virtual machines in the VMWare vSphere infrastructure from python script.

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

### PHPipam ###
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
cat >passwd.py<<EOF!
user_api = '__you_user_name__' # IPAM user
pass_api = '__pwd__' # IPAM user password
vc_user  = '__you_user_name__' # vCenter administrator user name
vc_pass  = '__pwd__' # vCenter administrator user password
sd_user = '__you_user_name__' # ServiceDesk User
sd_pass = '__pwd__' # ServiceDesk password

EOF!
```

### PARAMETERS file ###

```
cat >parameters.py<<EOF!
vc_list = [
    'vcsa01.srv.local',
    'vcsa02.srv.local',
    ....
]

template_linux = [
    'template_centos',
    'template_ubuntu'
    ......
]

template_wind = [
    'template_win2008',
    'template_win2012R2',
    ......
]

template_list = template_linux + template_wind
EOF!
```

### HELP ###
For Help USAGE: 
```
./run.py --help
```
