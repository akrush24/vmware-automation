#!/usr/bin/python3
import requests
import sys
import  paramiko
import time
import os
from python_terraform import *
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from tools import tasks
from tools import tasks
from tools import cli

hostname = sys.argv[1]
infraname= sys.argv[2]
subnet_id= sys.argv[3]


token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=('ansible', 'qwerty123')).json()['data']['token']
headers = {'token':token}
baseurl = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+subnet_id
ip = requests.get(url=baseurl, headers=headers).json()['data']
create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+subnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
create = requests.post(url = create_url , headers=headers).json()['success']
if create == True:
    print(ip)

tf = Terraform(working_dir='/etc/ansible/ansible-playbook', variables={'vmname':hostname, 'ipvm':ip})

tf.apply(no_color=IsFlagged)

print(ip)

paramiko.util.log_to_file('/tmp/paramiko.log')
paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))

host = ip
port = 22
username = 'root'

files = ['disk-size.part1.sh', 'disk-size.part2.sh']
remote_images_path = '/root/'
local_path = '/home/nokhrimenko/'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())

for file in files:
    file_local = local_path + file
    file_remote = remote_images_path + file
    print (file_local + '>>>' + file_remote)
    ssh.connect(hostname=host, port=port, username=username, key_filename='/home/nokhrimenko/.ssh/id_dsa')
    sftp = ssh.open_sftp()
    sftp.put(file_local, file_remote)
    ssh.exec_command("chmod +x" " " + str(file_remote))
    stdin, stdout, stderr = ssh.exec_command(file_remote)
    print ("stderr: ", stderr.readlines())
    print ("pwd: ", stdout.readlines())
    time.sleep(50)
sftp.close()
ssh.close()


vc_host='vc-linx.srv.local'
vc_user='administrator@vsphere.local'
vc_pass='Bsdserver$4$5'
service_instance = connect.SmartConnectNoSSL(host=vc_host,
                                                         user=vc_user,
                                                         pwd=vc_pass,
                                                         port=443)
config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
uuid = config_uuid.summary.config.instanceUuid
message = ip + " " + infraname
vm = service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)
print ("Found: {0}".format(vm.name))
spec = vim.vm.ConfigSpec()
spec.annotation = message
task = vm.ReconfigVM_Task(spec)
tasks.wait_for_tasks(service_instance, [task])
folder = service_instance.content.searchIndex.FindByInventoryPath('Datacenter-Linx/vm/INV/')
print(folder)
folder.MoveIntoFolder_Task([config_uuid])




print ("Done.")
