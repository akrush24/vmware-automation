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

import datetime

from subprocess import call

# import paramaners list
from parameters import template_list, template_linux, template_wind, port_int

# get ip address
def ipam_create_ip(hostname, infraname, cidr):
    #try:
    token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=(user_api, pass_api)).json()['data']['token']
    headers = {'token':token}
    cidr_url = 'https://ipam.phoenixit.ru/api/apiclient/subnets/cidr/' + cidr
    get_subnet_id = requests.get(url=cidr_url, headers=headers).json()['data'][0]['id']

    print ("### SUBnet ID for ["+cidr+"] is: ["+get_subnet_id+"]")
    if infraname is None:
       print ("!!! Description is None, exit")
       quit()

    get_ip_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+get_subnet_id
    ip = requests.get(url=get_ip_url, headers=headers).json()['data']
    create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+get_subnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
    create = requests.post(url = create_url , headers=headers).json()['success']
    if create == True:
       print ("### NEW IP for ["+hostname+"] is: ["+ip+"]")
       return ip  # get ip address
    #except:
    #   print("!!! При выделении IP произошла ошибка! ",sys.exc_info())
    #   quit()

def ipam_rm_ip(ip, cidr):
    print ("function: ipam_rm_ip("+ ip +")")
    token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=(user_api, pass_api)).json()['data']['token']
    headers = {'token':token}
    cidr_url = 'https://ipam.phoenixit.ru/api/apiclient/subnets/cidr/' + cidr
    get_subnet_id = requests.get(url=cidr_url, headers=headers).json()['data'][0]['id']

    print ("### SUBnet ID for ["+cidr+"] is: ["+get_subnet_id+"]")

    rm_ip_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/"+ip+"/40/"
    rm_ip = requests.delete(url=rm_ip_url, headers=headers).json()
    print(rm_ip)
    #except:
    #   print("!!! При удалении IP произошла ошибка! ",sys.exc_info())
    #   quit()




#folder project terraform (linux&windows) return ter_dir (./linux, ./windows)
def template(vm_template):

    if vm_template in template_linux:
        ter_dir = './linux'
        print ("### TER DIR: ["""+ter_dir+"]")
        return ter_dir
    elif vm_template in template_wind:
        if vm_template == 'template_WinSrv2016EN':
            ter_dir = './windows_2016'
        else:
            ter_dir = './windows'
        print ("### TER DIR: ["+ter_dir+"]")
        return ter_dir
    else:
        print ('!!! No template found: '+vm_template+'!')
        i=1
        print("For Linux: ")
        for template in template_linux:
           print ("   "+str(i)+". "+template)
           i=i+1
        i=1
        print("For Windows: ")
        for template in template_wind:
           print ("   "+str(i)+". "+template)
           i=i+1
        quit()


#varible5
def create_vm_terraform(ter_dir, hostname, ip, cidr, vc_host, vc_user, vc_pass, vc_dc, vc_cluster, vc_storage, vm_template,
                        vm_cpu, vm_ram, vm_disk_size, debug ):
    vm_ip_gw = re.sub('[/]', '', cidr)[:-3] + '1'  # get GW (example 192.168.222.1)
    vm_netmask = cidr[-2:]   # get prefix netmask (example /24)вд
#get port_group_vm_interface  (return portgroup)
    def portgroup(cidr):
#        port_int = {'192.168.222.0/24': '192.168.222',
#                    '192.168.199.0/24': '192.168.199',
#                    '192.168.245.0/24': '192.168.245',
#                    '192.168.238.0/24': '192.168.238',
#                    '192.168.189.0/24': '192.168.189_uni',
#                    '192.168.231.0/24': '231_VMNetwork',
#                    '192.168.14.0/23' : 'VLAN14',
#                    '172.20.20.0/24'  : '172.20.20.0',
#                    '172.25.16.0/24'  : '172.25.16.0',
#                    '192.168.24.0/24' : 'VLAN_24', # ATC vcenter.at-consulting.ru
#                    '192.168.9.0/24'  : 'VLAN09', # ATC vcenter.at-consulting.ru
#                    '192.168.194.0/24': 'ds-VLAN_194', # ATC vcenter.at-consulting.ru
#                    '192.168.221.0/24': '192.168.221'
#}

        if port_int[cidr]:
            vm_portgroup = port_int.get(cidr)
            print ("### PortGroup is "+vm_portgroup)
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
    #kwargs = {"auto-approve": True}

    try:
       if debug: # is debug mode print all output
          print(tf.init())
       else:
          tf.init()
    except:
       print ("!!! ERROR in create_vm_terraform(tf.init()): ",sys.exc_info())
       quit()

    try:
       if debug: # is debug mode print all output
          print(tf.plan(no_color=IsFlagged, refresh=False, capture_output=True))
       else:
          tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    except:
       print ("!!! ERROR in create_vm_terraform(tf.plan()): ",sys.exc_info())
       quit()

    approve = {"auto-approve": True}
    try:
       if debug: # is debug mode print all output
          print(tf.apply(**approve))
       else:
          tf.apply(**approve)
    except:
       print ("!!! ERROR in create_vm_terraform(tf.apply()): ",sys.exc_info())
       quit()


    # remove teraform state file
    if os.path.exists(ter_dir+"/terraform.tfstate"):
        os.remove(ter_dir+"/terraform.tfstate")
        print("### Teraform state file removed")
    else:
        print("### Teraform state file is't Exist")


#change folder, write notes

def notes_write_vm(vc_host, vc_user, vc_pass, ip, infraname, expired):
    service_instance = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
    uuid = config_uuid.summary.config.instanceUuid
    message = "AutoDeploy, IP:" + ip + ", " + infraname
    if expired is not None:
       message = message + ", exp: " + expired
    vm = service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)
    print("Found: {0}".format(vm.name))
    spec = vim.vm.ConfigSpec()
    spec.annotation = message
    task = vm.ReconfigVM_Task(spec)


def move_vm_to_folder(vc_host, vc_user, vc_pass, ip, folder_vm, cluster):

    #default folders path
    folder_dc_pass = { 'vc-linx.srv.local':'Datacenter-Linx/vm/', 'vcsa.srv.local':'PHX/vm/', 'vc-khut.srv.local':'ATK/vm/' }

    # for multi datacenter VCSA
    if cluster in ["sav-r11-cl2","sav-r24-cl1","sav-r24-cl2","sav-r24_e5-26","r24_SandyBridge","r39-cluster"]:
       folder_dc_pass['vcsa.srv.local'] = 'ATK/vm/'

    folder_dc = folder_dc_pass.get(vc_host)
    service_instance = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
    uuid = config_uuid.summary.config.instanceUuid
    vm = service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)
    spec = vim.vm.ConfigSpec()
    task = vm.ReconfigVM_Task(spec)
    tasks.wait_for_tasks(service_instance, [task])
    folder = service_instance.content.searchIndex.FindByInventoryPath(folder_dc+folder_vm)
    print(folder_vm)
    folder.MoveIntoFolder_Task([config_uuid])


def main(hostname, infraname, cidr, vc_host, vc_dc, vc_cluster, vc_storage, vm_template, vm_cpu, vm_ram, vm_disk_size, folder_vm, ip, debug, expire_vm_date):

    ter_dir = template(vm_template)

    # remove teraform state file
    if os.path.exists(ter_dir+"/terraform.tfstate"):
       os.remove(ter_dir+"/terraform.tfstate")
       print("!!! Teraform state file exist, removed.")
    else:
       print("### Teraform state file is't Exist, it's OK.")

    if ip is None:
       ip = ipam_create_ip(hostname, infraname, cidr)
    else:
       print ("### YOUR IP is: ["+ip+"]")

    try:
       create_vm_terraform(ter_dir, hostname, ip, cidr, vc_host, vc_user, vc_pass, vc_dc, vc_cluster, vc_storage, vm_template, vm_cpu, vm_ram, vm_disk_size, debug)
       print ("### VM is Ready: ["+hostname+" : "+ip+"]")
    except:
       print ("!!! ERROR in create_vm_terraform: ",sys.exc_info())
       quit()

#    try:
#       notes_write_vm(vc_host, vc_user, vc_pass, ip, infraname)
#       print ("### Edit nodes to: ["+infraname+"]")
#    except:
#       print ("!!! ERROR: notes_write_vm: ",sys.exc_info())

#    try:
#       move_vm_to_folder(vc_host, vc_user, vc_pass, ip, folder_vm)
#       print ("### Move VM to: ["+folder_vm+"]")
#    except:
#       print ("!!! ERROR: move_vm_to_folder: ",sys.exc_info())

    return ip

#    if expire_vm_date is not None:
#       scheduledTask_poweroff(hostname=hostname, expire_vm_date=expire_vm_date, vc_host=vc_host)

# main (hostname='host889', infraname='INFRA8888', cidr='192.168.222.0/24', vc_host='vc-linx.srv.local',
#       vc_user='', vc_pass='', vc_dc='Datacenter-Linx', vc_cluster='linx-cluster01',
# vc_storage='27_localstore_r10', vm_template='template_centos7.3', vm_cpu='1', vm_ram='2048', vm_disk_size='30',
#       folder_vm = 'test')


#exemple expire_vm_date  'DD/MM/YY'
#hostname this is name vm vcenter
def scheduledTask_poweroff(hostname, expire_vm_date, vc_host):
    si = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    try:
       datefind = re.findall('(\w\w)',expire_vm_date)
       (d, m, y) = (datefind[0], datefind[1], datefind[len(datefind)-1])
       #dt = datetime.strptime(expire_vm_date+" 10:30", "%d/%m/%y %H:%M")
       dt = datetime.datetime.strptime(d + "/" + m + "/" + y +" 10:30", "%d/%m/%y %H:%M")
       print("### Expired date is: " + str(dt))
    except:
       print("!!! Invalid date specified"+expire_vm_date+"->"+str(dt))
       quit()

    view = si.content.viewManager.CreateContainerView(si.content.rootFolder, [vim.VirtualMachine],True)
    vms = [vm for vm in view.view if vm.name == hostname]
    if not vms:
       print('!!! VM not found')
       connect.Disconnect(si)
       quit()
       return -1
    vm = vms[0]
    spec = vim.scheduler.ScheduledTaskSpec()
    today = datetime.datetime.today().strftime("%d%m%Y.%H%M")
    spec.name = '[%s] PowerOff [%s]' % (today, hostname)
    spec.description = 'expire date order vm'
    spec.scheduler = vim.scheduler.OnceTaskScheduler()
    spec.scheduler.runAt = dt
    spec.action = vim.action.MethodAction()
    spec.action.name = vim.VirtualMachine.PowerOff
    spec.enabled = True
    si.content.scheduledTaskManager.CreateScheduledTask(vm, spec)

