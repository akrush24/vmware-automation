import requests
import sys
from passwd import user_api, pass_api, vc_user, vc_pass
from python_terraform import *
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from tools import tasks
from tools import tasks
from tools import cli

# EXAMPLE
# python3 ipam_create_ip.py HOSTNAME DESCRIPTION PHPIPAM_SubnetID

#hostname = sys.argv[1]
#infraname= sys.argv[2]
#cidr = sys.argv[3]



def ipam_create_ip(hostname, infraname, cidr):
    token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=(user_api, pass_api)).json()['data']['token']
    headers = {'token':token}
    cidr_url = 'http://ipam.phoenixit.ru/api/apiclient/subnets/cidr/' + cidr
    get_sudnet_id = requests.get(url=cidr_url, headers=headers).json()['data'][0]['id']
    get_ip_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+get_sudnet_id
    ip = requests.get(url=get_ip_url, headers=headers).json()['data']
    create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+get_sudnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
    create = requests.post(url = create_url , headers=headers).json()['success']
    if create == True:
        return ip


def vlan_vm_int(cidr):
    port_int = {'192.168.222.0/24': '192.168.222',
                '192.168.199.0/24': '192.168.199',
                '192.168.245.0/24': '245'}

    if port_int[cidr]:
        vm_portgroup = port_int.get(cidr)
    else:
        print ('no network portgroup')

    return vm_portgroup


def template(vm_template):
    template_linux = ['template_centos7.3', 'template_ubuntu16.04']
    template_wind = ['template_wind2012', 'template_wind2008']
    if vm_template in template_linux:
        ter_dir = './linux'
        return ter_dir
    elif vm_template in template_wind:
        ter_dir = './windows'
        return ter_dir
    else:
        print ('no template')

def create_vm_terraform(ter_dir, vm_portgroup, ip):
    tf = Terraform(working_dir=ter_dir, variables={'vc_host': vc_host,
                                                                                                         'vc_user': vc_user, 'vc_pass': vc_pass,
                                                   'vc_dc': vc_dc, 'vc_cluster': vc_cluster, 'vc_storage': vc_storage,
                                                   'vm_portgroup': vm_portgroup, 'vm_template': vm_template,
                                                   'vm_hostname': hostname, 'vm_cpu': vm_cpu, 'vm_ram': vm_ram,
                                                   'vm_disk_size': vm_disk_size, 'vm_ip': ip, 'vm_ip_gw': vm_ip_gw,
                                                   'vm_netmask': vm_netmask})
    kwargs = {"auto-approve": True}
    print(kwargs)
    tf.init()
    print(tf.plan())
    print(tf.apply(**kwargs))


def move_notes_vm(ip, folder, infraname):
    service_instance = connect.SmartConnectNoSSL(host=vc_host,
                                                         user=vc_user,
                                                         pwd=vc_pass,
                                                         port=443)
    config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
    uuid = config_uuid.summary.config.instanceUuid # получает uuid vm
    message = ip + " " + infraname  # формируется notes
    vm = service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)
    print ("Found: {0}".format(vm.name))
    spec = vim.vm.ConfigSpec()
    spec.annotation = message
    task = vm.ReconfigVM_Task(spec)
    tasks.wait_for_tasks(service_instance, [task])
    dirname = 'Datacenter-Linx/vm/' + folder # урл директории для ВМ
    movefolder = service_instance.content.searchIndex.FindByInventoryPath(dirname)
    movefolder.MoveIntoFolder_Task([config_uuid])


def main(hostname, infraname, cidr, folder, vm_template, vc_storage, vm_cpu, vm_ram, vm_disk_size, vc_dc, vc_cluster, vc_host):
    ip = ipam_create_ip(hostname, infraname, cidr)
    vm_portgroup = vlan_vm_int(cidr)
    ter_dir = template(vm_template)
    create_vm_terraform(ter_dir, vm_portgroup, ip, vm_template,  vc_storage, vm_cpu, vm_ram, vm_disk_size, vc_dc, vc_cluster, vc_host)
    move_notes_vm(ip, folder, infraname)

