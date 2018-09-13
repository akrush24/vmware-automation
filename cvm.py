import requests
import sys
import re
import os
from passwd import user_api, pass_api, vc_user, vc_pass
from python_terraform import *
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from tools import tasks
from tools import tasks
from tools import cli


# get ip address
def ipam_create_ip(hostname, infraname, cidr):
    try:
       token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=(user_api, pass_api)).json()['data']['token']
       headers = {'token':token}
       cidr_url = 'https://ipam.phoenixit.ru/api/apiclient/subnets/cidr/' + cidr
       get_subnet_id = requests.get(url=cidr_url, headers=headers).json()['data'][0]['id']

       # временный обход для дублированных сетей (24,14,9)
       if cidr == '192.168.24.0/24':
          get_subnet_id = '130'
       elif cidr == '192.168.9.0/24':
          get_subnet_id = '131'
       elif cidr == '192.168.14.0/23': 
          get_subnet_id = '129'
       elif cidr == '192.168.194.0/24':
          get_subnet_id = '132'
       ####

       print ("### SUBnet ID: ["+get_subnet_id+"]")

       get_ip_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+get_subnet_id
       ip = requests.get(url=get_ip_url, headers=headers).json()['data']
       create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+get_subnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
       create = requests.post(url = create_url , headers=headers).json()['success']
       if create == True:
          return ip  # get ip address
    except:
       print("!!! При выделении IP произошла ошибка! ",sys.exc_info())
       quit()


#folder project terraform (linux&windows) return ter_dir (./linux, ./windows)
def template(vm_template):
    template_linux = ['template_centos7.3','template_ubuntu16.04','centos7.0-clear-v2-template','template_centos6.8_x86_64','centos-7-es-5.1.1-template','template_debian9','template_centos7.5_x86_64']
    template_wind = ['template_wind2012','template_wind2008','template_WinSrv2012R2RU']
    if vm_template in template_linux:
        ter_dir = './linux'
        print ("### TER DIR: ["""+ter_dir+"]")
        return ter_dir
    elif vm_template in template_wind:
        ter_dir = './windows'
        print ("### TER DIR: ["+ter_dir+"]")
        return ter_dir
    else:
        print ('!!! No template!')


#varible5
def create_vm_terraform(ter_dir, hostname, ip, cidr, vc_host, vc_user, vc_pass, vc_dc, vc_cluster, vc_storage, vm_template,
                        vm_cpu, vm_ram, vm_disk_size, debug ):
    vm_ip_gw = re.sub('[/]', '', cidr)[:-3] + '1'  # get GW (example 192.168.222.1)
    vm_netmask = cidr[-2:]   # get prefix netmask (example /24)вд
#get port_group_vm_interface  (return portgroup)
    def portgroup(cidr):
        port_int = {'192.168.222.0/24': '192.168.222',
                    '192.168.199.0/24': '192.168.199',
                    '192.168.245.0/24': '192.168.245',
                    '192.168.189.0/24': '192.168.189_uni',
                    '192.168.14.0/23' : 'VLAN14',
                    '192.168.24.0/24' : 'VLAN24-192.168.24.0', # ATC vcenter.at-consulting.ru
                    '192.168.9.0/24'  : 'dvSwitch6_192.168.9.0', # ATC vcenter.at-consulting.ru
                    '192.168.194.0/24': 'ds-VLAN_194' # ATC vcenter.at-consulting.ru
}

        if port_int[cidr]:
            vm_portgroup = port_int.get(cidr)
            return vm_portgroup
        else:
            print ('!!! No network portgroup!')


    vm_portgroup = portgroup(cidr)
    tf = Terraform(working_dir=ter_dir, variables={'vc_host': vc_host,
                                                   'vc_user': vc_user, 'vc_pass': vc_pass,
                                                   'vc_dc': vc_dc, 'vc_cluster': vc_cluster, 'vc_storage': vc_storage,
                                                   'vm_portgroup': vm_portgroup, 'vm_template': vm_template,
                                                   'vm_hostname': hostname, 'vm_cpu': vm_cpu, 'vm_ram': vm_ram,
                                                   'vm_disk_size': vm_disk_size, 'vm_ip': ip, 'vm_ip_gw': vm_ip_gw,
                                                   'vm_netmask': vm_netmask})
    kwargs = {"auto-approve": True}
    tf.init()

    if debug is not None: # is debug mode print all output
       print(tf.plan())
       print(tf.apply(**kwargs))
    else:
       tf.plan()
       tf.apply(**kwargs)

    # remove teraform state file
    if os.path.exists(ter_dir+"/terraform.tfstate"):
        os.remove(ter_dir+"/terraform.tfstate")
        print("### Teraform state file removed")
    else:
        print("### Teraform state file is't Exist")


#change folder, write notes

def notes_write_vm(vc_host, vc_user, vc_pass, ip, infraname):
    service_instance = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
    uuid = config_uuid.summary.config.instanceUuid
    message = ip + " " + infraname
    vm = service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)
    print("Found: {0}".format(vm.name))
    spec = vim.vm.ConfigSpec()
    spec.annotation = message
    task = vm.ReconfigVM_Task(spec)


def move_vm_to_folder(vc_host, vc_user, vc_pass, ip, folder_vm):
    folder_dc = { 'vc-linx.srv.local': 'Datacenter-Linx/vm/',
                  'vcsa.srv.local'  : 'Datacenter-AKB/vm/',
                  'vc-khut.srv.local': 'Datacenter-KHUT/vm/',
                  'vcenter.at-consulting.ru': 'SAV/vm/'}.get(vc_host)
    service_instance = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
    uuid = config_uuid.summary.config.instanceUuid
    vm = service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)
    spec = vim.vm.ConfigSpec()
    task = vm.ReconfigVM_Task(spec)
    tasks.wait_for_tasks(service_instance, [task])
    folder = service_instance.content.searchIndex.FindByInventoryPath(folder_dc+folder_vm)
    print(folder)
    folder.MoveIntoFolder_Task([config_uuid])




def main(hostname, infraname, cidr, vc_host, vc_dc, vc_cluster, vc_storage, vm_template, vm_cpu, vm_ram, vm_disk_size, folder_vm, ip, debug):

    ter_dir = template(vm_template)

    # remove teraform state file
    if os.path.exists(ter_dir+"/terraform.tfstate"):
       os.remove(ter_dir+"/terraform.tfstate")
       print("!!! Teraform state file exist, removed.")
    else:
       print("### Teraform state file is't Exist, it's OK.")

    if ip is None:
       ip = ipam_create_ip(hostname, infraname, cidr)
       print ("### NEW IPAM IP is: ["+ip+"]")
    else:
       print ("### YOUR IP is: ["+ip+"]")


    try:
       create_vm_terraform(ter_dir, hostname, ip, cidr, vc_host, vc_user, vc_pass, vc_dc, vc_cluster, vc_storage, vm_template, vm_cpu, vm_ram, vm_disk_size, debug)
       print ("### VM is Ready: ["+hostname+" : "+ip+"]")
    except:
       print ("!!! ERROR in create_vm_terraform: ",sys.exc_info())
       quit()

    try:
       notes_write_vm(vc_host, vc_user, vc_pass, ip, infraname)
       print ("### Edit nodes to: ["+infraname+"]")
    except:
       print ("!!! ERROR: notes_write_vm: ",sys.exc_info())

    try:
       move_vm_to_folder(vc_host, vc_user, vc_pass, ip, folder_vm)
       print ("### Move VM to: ["+folder_vm+"]")
    except:
       print ("!!! ERROR: move_vm_to_folder: ",sys.exc_info())



# main (hostname='host889', infraname='INFRA8888', cidr='192.168.222.0/24', vc_host='vc-linx.srv.local',
#       vc_user='', vc_pass='', vc_dc='Datacenter-Linx', vc_cluster='linx-cluster01',
# vc_storage='27_localstore_r10', vm_template='template_centos7.3', vm_cpu='1', vm_ram='2048', vm_disk_size='30',
#       folder_vm = 'test')


