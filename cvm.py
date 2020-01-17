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

#from parameters import template_list, vc_list, os_to_template, ds, port_int, net_default, stor_default

import datetime

# import paramaners list
from parameters import template_list, template_linux, template_wind, port_int

# get ip address
def ipam_create_ip(hostname, infraname, cidr):
    try:
        token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=(user_api, pass_api)).json()['data']['token']
        headers = {'token':token}
        if cidr is None:
          print("!!! --net is not defined, quit...")
          quit()
        cidr_url = 'https://ipam.phoenixit.ru/api/apiclient/subnets/cidr/' + cidr
        get_subnet_id = requests.get(url=cidr_url, headers=headers).json()['data'][0]['id']

        print ("### SUBnet ID for ["+cidr+"] is: ["+get_subnet_id+"]")
        if infraname is None:
           print ("!!! Description is None, exit")
           quit()

        get_ip_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+get_subnet_id
        ip = requests.get(url=get_ip_url, headers=headers).json()['data']
        create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+get_subnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
        print ("### PhpIPAM, create_url: " + create_url)
        create = requests.post(url = create_url , headers=headers).json()['success']
        if create == True:
           print ("### NEW IP for ["+hostname+"] is: ["+ip+"]")
           return ip  # get ip address
        else:
           print("!!! При выделении ip произошла ошибка.")
           quit()
    except:
       print("!!! При выделении IP произошла ошибка! ",sys.exc_info())
       quit()

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
def template(vm_template, vm_destination):

    if vm_template in template_linux:
        if vm_destination == 'host':
            ter_dir = './linux_host'
        else:
            ter_dir = './linux'
        print ("### TER DIR: ["""+ter_dir+"]")
        return ter_dir
    elif vm_template in template_wind:
        if vm_template == 'template_WinSrv2016EN':
            ter_dir = './windows_2016'
        else:
            ter_dir = './windows'
        if vm_destination == 'host':
            ter_dir = ter_dir+'_host'

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

## функция пробегает по всем элементам массива и выводит их на экран
def print_array(arr):
    for a in arr:
       print( str(a) )

def create_vm_terraform(ter_dir, hostname, ip, cidr, vc_host, vc_user, vc_pass, vc_dc, vm_destination2, vc_storage, vm_template,
                        vm_cpu, vm_ram, vm_disk_size, debug ):
    vm_ip_gw = re.sub('[/]', '', cidr)[:-3] + '1'  # get GW (example 192.168.222.1)
    vm_netmask = cidr[-2:]   # get prefix netmask (example /24)вд

    if port_int[cidr]:
        vm_portgroup = port_int.get(cidr)
        print ("### PortGroup is: " + vm_portgroup)
    else:
        print ('!!! No network portgroup!')

    #print("IP: " + ip)
    tf = Terraform(working_dir=ter_dir, variables={ 'vc_host': vc_host,
                                                    'vc_user': vc_user, 'vc_pass': vc_pass,
                                                    'vc_dc': vc_dc, 'vc_destination': vm_destination2, 'vc_storage': vc_storage,
                                                    'vm_portgroup': vm_portgroup, 'vm_template': vm_template,
                                                    'vm_hostname': hostname, 'vm_cpu': vm_cpu, 'vm_ram': vm_ram,
                                                    'vm_disk_size': vm_disk_size, 'vm_ip': ip, 'vm_ip_gw': vm_ip_gw,
                                                    'vm_netmask': vm_netmask} )


    print ("\nTeraform Init....")
    out_tinit = tf.init()
    if debug:
       print_array(out_tinit)

    print ("\nTeraform Plan....")
    out_tplan = tf.plan()
    if debug: 
       print_array(out_tplan)


    #try:
    #   #out = tf.plan(no_color=IsFlagged, refresh=False)
    #   if debug: # is debug mode print all output
    #      print( str(out[2]) )
    #      print( str(out[3]) )
    #   #else:
    #   #   tf.plan( no_color=IsFlagged, refresh=False, capture_output=True )
    #except:
    #   print ("!!! ERROR in create_vm_terraform(tf.plan()): ", sys.exc_info())
    #   bye()

    print ("\nTeraform Apply....")
    approve = {"auto-approve":True}
    out_tapply = tf.apply(auto_approve=True)
    if debug:
       print_array(out_tapply)
    err = str(out_tapply).find("Error")
    print( "ERRORs: "+str(err) )
    if err > 0: # если в выводе teraform apply есть слово Error то пишем ошибку и выходим.
       print("create_vm_terraform: Error applying plan")
       print_array(out_tapply)
       quit()

    #try:
    #   if debug: # is debug mode print all output
    #      print( tf.apply(auto_approve=True, capture_output=True) )
    #   else:
    #      tf.apply(auto_approve=True)
    #except:
    #   print ("!!! ERROR in create_vm_terraform(tf.apply()): ", sys.exc_info())
    #   bye()


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
    print("Found vm: {0}".format(vm.name))
    spec = vim.vm.ConfigSpec()
    spec.annotation = message
    task = vm.ReconfigVM_Task(spec)


def move_vm_to_folder(vc_host, ip, folder_vm, cluster, dc):
    
    if ip is None:
       print("!!! Please enter --ip xxx.xxx.xxx.xxx")
       quit()
    if folder_vm is None:
       print("!!! Please enter --folder Name")
       quit()

    #default folders path
    folder_dc_pass = { 'vc-linx.srv.local':'Datacenter-Linx/vm/', 'vcsa.srv.local':'PHX/vm/', 'vc-khut.srv.local':'ATK/vm/' }

    # for multi datacenter VCSA
    if cluster in ["sav-r11-cl2","sav-r24-cl1","sav-r24-cl2","sav-r24_e5-26","r24_SandyBridge","r39-cluster"]:
       folder_dc_pass['vcsa.srv.local'] = 'ATK/vm/'

    folder_dc = folder_dc_pass.get(vc_host)
    service_instance = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    vm = service_instance.content.searchIndex.FindByIp(None, ip, True)
    if vm == None:
       print("!!! VM: ["+ ip + "] IS NOT EXIST!")
       quit()
    folder = service_instance.content.searchIndex.FindByInventoryPath(folder_dc + folder_vm)
    print( "Folder: "+str(folder) )
    if folder != None:
       print ("Folder: "+str(folder_dc+folder_vm)+" Exist.")
       folder.MoveIntoFolder_Task([vm])
    else:
       print("!!! Folder: " +folder_dc+folder_vm+ " is not Exist.")
       print("Create folder: " + folder_vm)
       os.system('./tools/create_folder_in_datacenter.py -s "'+vc_host+'" -u "'+vc_user+'" -p "'+vc_pass+'" -d "'+ dc  +'" -f "'+folder_vm+'"')
       print("Check folder")
       folder = service_instance.content.searchIndex.FindByInventoryPath(folder_dc + folder_vm)
       if folder != None:
          print("Move vm "+ str(vm) +" to folder: "+folder_vm)
          folder.MoveIntoFolder_Task([vm])
       else:
          print("!!! Failed to create folder: " + folder_dc + folder_vm)
          quit()
       


def main(hostname, infraname, cidr, vc_host, vc_dc, vm_destination2, vc_storage, vm_template, vm_cpu, vm_ram, vm_disk_size, folder_vm, ip, debug, expire_vm_date, vm_destination):

    ter_dir = template(vm_template, vm_destination)

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

    create_vm_terraform(ter_dir, hostname, ip, cidr, vc_host, vc_user, vc_pass, vc_dc, vm_destination2, vc_storage, vm_template, vm_cpu, vm_ram, vm_disk_size, debug)

    return ip


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

