
from pyVim.connect import SmartConnect, Disconnect,SmartConnectNoSSL
from pyVmomi import vim
from pyVim import connect
import atexit
import argparse
import getpass
import re
import json
import pandas as pd
import sys
import time
import tqdm
import requests
########VARIBLE#########
config_vcenter = 'vcenter.json'
config_network = 'network.json'
config_template = ''
config_storage_type = 'cluster_storage.json'

storage_type = "LocalStore" # san , nas

vcenter_host = 'vc-linx.srv.local'
datacenter_name = 'Datacenter-Linx'
cluster_name = 'linx-cluster01'
template_name = 'template_centos7.5'
vm_net_address = '172.20.20.0/24'
folder_name_vm = 'ewwwwe'
vm_data_expare = '10.10.19'
descriptinon = 'test'
user_api = 'ansible'
pass_api = 'qwerty123'
vm_name = 'testvm-clone'
vm_disk_size = 300
vm_ram = 8
vm_cpu = 2


########################


def Json_Parser(config_file):
    """ Json parser config (config_vcenter, config_network """
    config = json.loads(open(config_file).read())
    return config

def Connect_vCenter(vcenter_host):
    try:
        si = connect.SmartConnectNoSSL(host=vcenter_host, user=Json_Parser(config_vcenter)[vcenter_host][0],
                               pwd=Json_Parser(config_vcenter)[vcenter_host][1], port=443)
        content = si.RetrieveContent()
        return content
    except:
        print('Error connect: '+ vcenter_host)
        quit()

content = Connect_vCenter(vcenter_host)

def get_obj(content, vimtype, name):
    """ return object (datacenter, cluster, vm.... """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break
    return obj


def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            print ("there was an error")
            task_done = True


def Get_Datacenter_obj (datacenter_name):
    """ return object datacenter, if he is """
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)
    try:
        if datacenter.name == datacenter_name:
            return datacenter
    except:
        print ('Incorrect Datacenter: ' +  datacenter_name)
        quit()


def Get_Cluster_obj(cluster_name):
    """ return object Cluster obj, if he is """
    try:
        cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name)
        if cluster == None:
            print('Not found ClusterName: '+ cluster_name)
        else:
            return cluster
    except:
        print('Error cluster_obj ' + cluster_name)
        quit()


def Get_VM_obj(vm_name):
    """ return object VM, if he is """
    vm_name = get_obj(content, [vim.VirtualMachine], vm_name)
    if vm_name == None:
        print('Not found template name: ' + vm_name)
    else:
        return vm_name



def Get_Folder_Dest_obj (Datacenter_obj, folder_name_vm):
    """ return object folder obj, if not, then it creates  """

    destfolder = get_obj(content, [vim.Folder], folder_name_vm)
    if destfolder == None:
        Datacenter_obj.vmFolder.CreateFolder(folder_name_vm)
        destfolder = get_obj(content, [vim.Folder], folder_name_vm)
        return destfolder
    else:
        return destfolder


def Get_PortGroup_obj(Datacenter_obj, vm_net_address):
    """ return object PortGroup ===> json  """
    try:
        portgroup_conf_pars = Json_Parser(config_network)[Datacenter_obj.name][vm_net_address][0]
        portgroup = get_obj(content, [vim.Network], portgroup_conf_pars)
        return portgroup
    except:
        print ('Not config file in ' + Datacenter_obj.name + ' or ' + vm_net_address )


def Change_PortGroup(vm_obj, PortGroup_obj):
    """ change portgroup on VM, from func Get_PortGroup_obj ===> json """
    vm_portgroup = PortGroup_obj(vm_net_address)
    device_change = []
    for device in vm_obj.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualEthernetCard):
            nicspec = vim.vm.device.VirtualDeviceSpec()
            nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            nicspec.device = device
            nicspec.device.wakeOnLanEnabled = True
            network =  vm_portgroup
            dvs_port_connection = vim.dvs.PortConnection()
            dvs_port_connection.portgroupKey = network.key
            dvs_port_connection.switchUuid = network.config.distributedVirtualSwitch.uuid
            nicspec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
            nicspec.device.backing.port = dvs_port_connection
            nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
            nicspec.device.connectable.startConnected = True
            nicspec.device.connectable.allowGuestControl = True
            device_change.append(nicspec)
        config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
    task = vm_obj.ReconfigVM_Task(config_spec)
    wait_for_task(task)


def Load_Average_Esxi(Cluster_obj, storage_type, vm_ram, vm_disk_size):
    """ return  esxi-host (name), if  Free-RAM > 10% and Free-Storage > 15 % + vm(ram, disk)"""
    host_list = []
    for host in Cluster_obj.host:
        capacity_ram = int(host.summary.hardware.memorySize)
        used_ram = int(host.summary.quickStats.overallMemoryUsage) * 1024 * 1024
        free_mem_perc = 100 - ((used_ram + vm_ram) / capacity_ram * 100)
        if free_mem_perc > 10:
            for store_name in host.datastore:
                if store_name.parent.name == storage_type:
                    used_storage = int(store_name.summary.capacity - store_name.summary.freeSpace - vm_disk_size)
                    free_store_perc = 100 - (used_storage / store_name.summary.capacity * 100)
                    if free_store_perc > 15:
                        host_list.append ({'host': str(host.name), 'ram': int(free_mem_perc),
                                           'disk': int(free_store_perc)})
    esxi_host = pd.DataFrame(host_list).sort_values(by=['ram'], ascending=False).reset_index()
    esxi_host = esxi_host['host'].iloc[0]
    return esxi_host



def Get_Choice_esxi_obj(Cluster_obj, Load_Average_Esxi):
    """ return object esxi, from func Load_Average_Esxi """
    for host in Cluster_obj.host:
        if host.name == Load_Average_Esxi:
            return host


def Get_Choice_Storage_obj(Cluster_obj, Load_Average_Esxi):
    """ return object storage, from func Load_Average_Esxi """
    for host in Cluster_obj.host:
        if host.name == Load_Average_Esxi:
            for storage_name in host.datastore:
                if storage_name.parent.name == storage_type:
                    return storage_name
                else:
                    print('No type datastore')



def Cpu_Mem_Reconfig(vm_obj, vm_cpu, vm_ram):
    cspec = vim.vm.ConfigSpec()
    cspec.cpuHotAddEnabled = True
    cspec.memoryHotAddEnabled = True
    cspec.numCPUs = vm_cpu
    cspec.numCoresPerSocket = 1
    cspec.memoryMB = int(vm_ram * 1024)
    vm_obj.Reconfigure(cspec)




def disk_vm_resize(vm_obj, vm_disk_size):
    for dev in vm_obj.config.hardware.device:
        if hasattr(dev.backing, 'fileName'):
            if  'Hard disk 1'  ==  dev.deviceInfo.label:
                capacity_in_kb = dev.capacityInKB
                new_disk_kb = int(vm_disk_size) * 1024 * 1024
                if new_disk_kb > capacity_in_kb:
                    dev_changes = []
                    disk_spec = vim.vm.device.VirtualDeviceSpec()
                    disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                    disk_spec.device = vim.vm.device.VirtualDisk()
                    disk_spec.device.key = dev.key
                    disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
                    disk_spec.device.backing.fileName = dev.backing.fileName
                    disk_spec.device.backing.diskMode = dev.backing.diskMode
                    disk_spec.device.controllerKey = dev.controllerKey
                    disk_spec.device.unitNumber = dev.unitNumber
                    disk_spec.device.capacityInKB = new_disk_kb
                    dev_changes.append(disk_spec)
                else:
                    print('Disk size not corect')
            else:
                print('No disk Hard_disk 1')
    if dev_changes != []:
        spec = vim.vm.ConfigSpec()
        spec.deviceChange = dev_changes
        task = vm_obj.ReconfigVM_Task(spec=spec)
    else:
         print('Task resize disk Error')




def Annotation_VM(vm_obj, descriptinon):
    spec = vim.vm.ConfigSpec()
    spec.annotation = descriptinon
    task = vm_obj.ReconfigVM_Task(spec)
    wait_for_task(task)




#vm, ip, netmask, gw, dns_prefix, dns_list

def Customiz_Os(Datacenter_obj, vm_obj, vm_ip_address, vm_net_address):

    netmask_vm = Json_Parser(config_network)[Datacenter_obj(datacenter_name).name][vm_net_address][2]
    gateway_vm = Json_Parser(config_network)[Datacenter_obj(datacenter_name).name][vm_net_address][1]
    dns_prefix = Json_Parser(config_network)[Datacenter_obj(datacenter_name).name]["dnsprefix"][0]
    dns_server_1 = Json_Parser(config_network)[Datacenter_obj(datacenter_name).name]["dnslist"][0]
    dns_server_2 = Json_Parser(config_network)[Datacenter_obj(datacenter_name).name]["dnslist"][1]
    dns_servers = [dns_server_1, dns_server_2]

    def Nix_Customiz():

        adaptermap = vim.vm.customization.AdapterMapping()
        adaptermap.adapter = vim.vm.customization.IPSettings()
        adaptermap.adapter.ip = vim.vm.customization.FixedIp()
        adaptermap.adapter.ip.ipAddress = ip
        adaptermap.adapter.subnetMask = netmask_vm
        adaptermap.adapter.gateway = gateway_vm
        adaptermap.adapter.dnsDomain = dns_prefix
        globalip = vim.vm.customization.GlobalIPSettings()
        globalip.dnsServerList = dns_servers
        ident = vim.vm.customization.LinuxPrep(domain='srv.local',
                                               hostName=vim.vm.customization.FixedName(name=vm_obj.name))
        customspec = vim.vm.customization.Specification()
        customspec.identity = ident
        customspec.nicSettingMap = [adaptermap]
        customspec.globalIPSettings = globalip
        task = vm_obj.Customize(spec=customspec)


    def Win_Customiz():
        # https://github.com/vmware/pyvmomi/issues/261

        adaptermap = vim.vm.customization.AdapterMapping()
        globalip = vim.vm.customization.GlobalIPSettings()
        adaptermap.adapter = vim.vm.customization.IPSettings()
        adaptermap.adapter.ip = vim.vm.customization.FixedIp()
        adaptermap.adapter.ip.ipAddress = ip
        adaptermap.adapter.subnetMask = netmask_vm
        adaptermap.adapter.gateway = gateway_vm
        adaptermap.adapter.dnsDomain = dns_prefix
        adaptermap.adapter.dnsServerList = dns_servers
        globalip = vim.vm.customization.GlobalIPSettings()
            # globalip.dnsServerList = ['172.20.20.20', '192.168.245.20']
        ident = vim.vm.customization.Sysprep()
        ident.guiUnattended = vim.vm.customization.GuiUnattended()
            # ident.guiUnattended.autoLogon = False
        ident.guiUnattended.password = vim.vm.customization.Password()
        ident.guiUnattended.password.plainText = True
        ident.guiUnattended.password.value = 'qwerty$4'
        ident.userData = vim.vm.customization.UserData()
        ident.userData.fullName = vm_name
        ident.userData.orgName = "Rtech"
        ident.userData.computerName = vim.vm.customization.FixedName()
        ident.userData.computerName.name = vm_name
        ident.identification = vim.vm.customization.Identification()
        customspec = vim.vm.customization.Specification()
        customspec.identity = ident
        customspec.nicSettingMap = [adaptermap]
        customspec.globalIPSettings = globalip
        task = vm_obj.Customize(spec=customspec)

    guest_id_win = ['windows7Server64Guest', 'windows8Server64Guest']
    guest_id_nix = ['centos64Guest', 'centos7_64Guest', 'ubuntu64Guest']

    vm_guest_id = vm.config.guestId
    if vm_guest_id in guest_id_win:
        Win_Customiz()
    elif vm_guest_id in guest_id_nix:
        Nix_Customiz()
    else:
        print("No support OS")


def scheduledTask_poweroff(vm, expire_vm_date, vc_host):
    try:
       datefind = re.findall('(\w\w)',expire_vm_date)
       (d, m, y) = (datefind[0], datefind[1], datefind[len(datefind)-1])
       #dt = datetime.strptime(expire_vm_date+" 10:30", "%d/%m/%y %H:%M")
       dt = datetime.strptime(d + "/" + m + "/" + y +" 10:30", "%d/%m/%y %H:%M")
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
    spec.name = 'PowerOff vm %s' % vm.name
    spec.description = 'expire date order vm'
    spec.scheduler = vim.scheduler.OnceTaskScheduler()
    spec.scheduler.runAt = dt
    spec.action = vim.action.MethodAction()
    spec.action.name = vim.VirtualMachine.PowerOff
    spec.enabled = True
    si.content.scheduledTaskManager.CreateScheduledTask(vm, spec)





def ipam_get_ip(hostname, infraname, cidr):
    try:
       token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/',
                             auth=(user_api, pass_api)).json()['data']['token']
       headers = {'token':token}
       cidr_url = 'https://ipam.phoenixit.ru/api/apiclient/subnets/cidr/' + cidr
       get_subnet_id = requests.get(url=cidr_url, headers=headers).json()['data'][0]['id']

       print("### SUBnet ID for [" + cidr + "] is: [" + get_subnet_id + "]")
       if infraname is None:
           print("!!! Description is None, exit")
           quit()

       get_ip_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+get_subnet_id
       ip = requests.get(url=get_ip_url, headers=headers).json()['data']
       create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+get_subnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
       create = requests.post(url = create_url , headers=headers).json()['success']

       if create == True:
          print ("### NEW IP for ["+hostname+"] is: ["+ip+"]")
          return ip  # get ip address

    except:
       print("!!! При выделении IP произошла ошибка! ",sys.exc_info())
       quit()




def Storage_Type(Datacenter_obj, Cluster_obj):
    try:
        storage_type = Json_Parser(config_storage_type)[Datacenter_obj.name][Cluster_obj.name][0]
        return storage_type
    except:
        print('Error parse json storage_type')



def Create_VM_localstore(datacenter_name, cluster_name, folder_name_vm, template_name, vm_net_address, vm_name,
                         descriptinon, vm_disk_size, vm_ram, vm_cpu ):

    try:
        Datacenter_obj = Get_Datacenter_obj(datacenter_name)
        Cluster_obj = Get_Cluster_obj(cluster_name)
        #storage_type = Storage_Type(Datacenter_obj, Cluster_obj)
        storage_type = "LocalStore"
        choice_esxi = Load_Average_Esxi(Cluster_obj, storage_type, vm_ram, vm_disk_size)
        esxi = Get_Choice_esxi_obj(Cluster_obj, choice_esxi)
        datastore = Get_Choice_Storage_obj(Cluster_obj, choice_esxi)
        folder = Get_Folder_Dest_obj(Datacenter_obj, folder_name_vm)
        template = Get_VM_obj(template_name)
        PortGroup_obj = Get_PortGroup_obj(Datacenter_obj, vm_net_address)
    except:
        print('Error Create varible',sys.exc_info())
        quit()
    try:
        relospec = vim.vm.RelocateSpec()
        relospec.datastore = datastore
        relospec.host = esxi
        clonespec = vim.vm.CloneSpec()
        clonespec.location = relospec
    except:
        print('Error Create relospec and clonspec', sys.exc_info())
        quit()

    print("Cloning VM: " + template.name + ' to ' + vm_name)
    print("ESXI: " + choice_esxi + "   DATASTORE: " + datastore.name)
    task = template.Clone(folder=folder, name=vm_name, spec=clonespec)

    with tqdm.tqdm(total=100) as pbar:
        while task.info.progress != None:
            cur_perc = int(task.info.progress)
            pbar.update(cur_perc - pbar.n)
            if cur_perc == 95:
                break

    time.sleep(3)
    try:
        if task.info.state == 'success':
            new_vm_obj = task.info.result
            print('====== Cloning VM  Success ======')
            Cpu_Mem_Reconfig(new_vm_obj, vm_cpu, vm_ram)
            disk_vm_resize(new_vm_obj, vm_disk_size)
            Annotation_VM(new_vm_obj, descriptinon)
            vm_portgroup = Get_PortGroup_obj(Datacenter_obj, vm_net_address)
            Change_PortGroup(new_vm_obj, vm_portgroup)
            ip = ipam_get_ip(vm_name, descriptinon, vm_net_address)
            Customiz_Os(new_vm_obj, ip, vm_net_address)
    except:
        if task.info.state == 'error':
            print("Clon vm error", sys.exc_info())
            quit()







Create_VM_localstore(datacenter_name = 'Datacenter-Linx', cluster_name='linx-cluster01',
                    folder_name_vm = 'ewwwwe', template_name='template_centos7.5', vm_net_address='172.20.20.0/24',
                    vm_name='testclonevm2', descriptinon='test', vm_disk_size=30, vm_ram=2, vm_cpu=2 )


#print(Get_Datacenter_obj(datacenter_name='123asdf23ed'))

#
# Datacenter_obj = Get_Datacenter_obj(datacenter_name)
# Cluster_obj = Get_Cluster_obj(cluster_name)
# Storage_Type(Datacenter_obj, Cluster_obj)

#print(Json_Parser(config_storage_type)[Datacenter_obj.name][Cluster_obj.name][0])
#Get_Cluster_obj(cluster_name)


# def clone_cluster_drs(folder_name_vm, datastore_name):
#     Datacenter_obj = Get_Datacenter_obj(datacenter_name)
#     Cluster_obj =  Cluster_obj = Get_Cluster_obj(cluster_name)
#     folder = Get_Folder_Dest_obj(Datacenter_obj, folder_name_vm)
#
#
#     if datastore_name:
#         datastore = get_obj(content, [vim.Datastore], datastore_name)
#     else:
#         datastore = get_obj(
#             content, [vim.Datastore], template.datastore[0].info.name)
#



