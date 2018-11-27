
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

storage_type = "LocalStore" # san , nas

vcenter_host = 'vc-linx.srv.local'
datacenter_name = 'Datacenter-Linx'
cluster_name = 'linx-cluster01'
template_name = 'template_centos7.5'
vm_net_address = '172.20.20.0/24'
folder_name_vm = 'ewwwwe'
vm_data_expare = '10.10.19'

vm_name = 'testvm-clone'
vm_disk_size = 300
vm_ram = 8
vm_cpu = 2


########################


def Json_Parser(config_file):
    config = json.loads(open(config_file).read())
    return config


def content ():
    si = connect.SmartConnectNoSSL(host=vcenter_host, user=Json_Parser(config_vcenter)[vcenter_host][0],
                               pwd=Json_Parser(config_vcenter)[vcenter_host][1], port=443)
    content = si.RetrieveContent()
    return content

def get_obj(content, vimtype, name):
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


def Datacenter (datacenter_name, content):
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)
    if  datacenter.name == datacenter_name:
        return datacenter
    else:
        print ('Not found: ' +  datacenter_name)





def Cluster(content):
    cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name)
    if cluster == None:
        print('Not found ClusterName: '+ cluster_name)
    else:
        return cluster



def Template(content, template_name):
    template_name = get_obj(content, [vim.VirtualMachine], template_name)
    if template_name == None:
        print('Not found template name: ' + template_name)
    else:
        return template_name


def Folder_Dest (content, Datacenter, folder_name_vm):
    destfolder = get_obj(content, [vim.Folder], folder_name_vm)
    if destfolder == None:
        Datacenter.vmFolder.CreateFolder(folder_name_vm)
        destfolder = get_obj(content, [vim.Folder], folder_name_vm)
        return destfolder
    else:
        return destfolder


def PortGroup(content, vm_net_address):
    try:
        portgroup_conf_pars = Json_Parser(config_network)[Datacenter(datacenter_name).name][vm_net_address][0]
        portgroup = get_obj(content, [vim.Network], portgroup_conf_pars)
        return portgroup
    except:
        print ('Not config file in ' + Datacenter(datacenter_name).name + ' or ' + vm_net_address )


def change_port_group(vm):

    vm_portgroup = PortGroup(vm_net_address)
    device_change = []
    for device in vm.config.hardware.device:
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
    task = vm.ReconfigVM_Task(config_spec)
    wait_for_task(task)



def Choice_Esxi(Cluster, storage_type, vm_ram, vm_disk_size):
    host_list = []
    for host in Cluster.host:
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


def Choice_host(Cluster, Choice_Esxi):
    for host in Cluster.host:
        if host.name == Choice_Esxi:
            return host


def Choice_Store(Cluster, Choice_Esxi):
    for host in Cluster.host:
        if host.name == Choice_Esxi:
            for storage_name in host.datastore:
                if storage_name.parent.name == storage_type:
                    return storage_name
                else:
                    print('No type datastore')



def Clone_vm_localstore():
    datacenter = Datacenter (datacenter_name)
    choice_esxi = Choice_Esxi(Cluster(), storage_type, vm_ram, vm_disk_size)
    folder = Folder_Dest(datacenter, folder_name_vm)
    esxi = Choice_host(Cluster(), choice_esxi)
    datastore =  Choice_Store(Cluster(), choice_esxi)
    template = Template(template_name)

    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    # relospec.pool = cluster.resourcePool
    relospec.host = esxi
    # print(resource_pool.name)
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    #clonespec.powerOn = power_on
    print ("Cloning VM: " + template.name + ' to ' + vm_name )
    print("ESXI: " + choice_esxi + "   DATASTORE: " + datastore.name)
    task = template.Clone(folder=folder, name=vm_name, spec=clonespec)
    with tqdm.tqdm(total=100) as pbar:
        while task.info.progress != None:
            cur_perc = int(task.info.progress)
            pbar.update(cur_perc - pbar.n)
            if cur_perc == 95:
                break

def Cpu_Mem_Reconfig(vm, core_cpu, sock_cpu, ram_mb):
    cspec = vim.vm.ConfigSpec()
    cspec.cpuHotAddEnabled = True
    cspec.memoryHotAddEnabled = True
    cspec.numCPUs = 4
    cspec.numCoresPerSocket = 1
    cspec.memoryMB = 1024
    vm.Reconfigure(cspec)






def disk_vm_resize(vm, vm_disk_size):

    for dev in vm.config.hardware.device:
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
        task = vm.ReconfigVM_Task(spec=spec)
    else:
         print('Task resize disk Error')




def Annotation_VM(vm, descriptinon ):
    spec = vim.vm.ConfigSpec()
    spec.annotation = descriptinon
    task = vm.ReconfigVM_Task(spec)
    wait_for_task(task)

#vm, ip, netmask, gw, dns_prefix, dns_list

def Customiz_Os(vm, ip, netmask, gw, dns_prefix, dns_list):
    netmask_vm = Json_Parser(config_network)[Datacenter(datacenter_name).name][vm_net_address][2]
    gateway_vm = Json_Parser(config_network)[Datacenter(datacenter_name).name][vm_net_address][1]
    dns_prefix = Json_Parser(config_network)[Datacenter(datacenter_name).name]["dnsprefix"][0]
    dns_servers = Json_Parser(config_network)[Datacenter(datacenter_name).name]["dnslist"][0]




    def Nix_Customiz():
        adaptermap = vim.vm.customization.AdapterMapping()
        # globalip = vim.vm.customization.GlobalIPSettings()
        adaptermap.adapter = vim.vm.customization.IPSettings()
        adaptermap.adapter.ip = vim.vm.customization.FixedIp()
        adaptermap.adapter.ip.ipAddress = ip
        adaptermap.adapter.subnetMask = netmask_vm
        adaptermap.adapter.gateway = gateway_vm
        adaptermap.adapter.dnsDomain = dns_prefix
        globalip = vim.vm.customization.GlobalIPSettings()
        globalip.IPSetings.dnsServerList = dns_servers
        ident = vim.vm.customization.LinuxPrep(domain='srv.local',
                                               hostName=vim.vm.customization.FixedName(name=vm_name))
        customspec = vim.vm.customization.Specification()
        customspec.identity = ident
        customspec.nicSettingMap = [adaptermap]
        customspec.globalIPSettings = globalip
        task = vm.Customize(spec=customspec)

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
        task = vm.Customize(spec=customspec)

    guest_id_win = ['windows7Server64Guest', 'windows8Server64Guest']
    guest_id_nix = ['centos64Guest', 'centos7_64Guest', 'ubuntu64Guest']

    vm_guest_id = vm.guest.guestId
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








    #print(task)


    #wait_for_task(task)
#
#Clone_vm_localstore()

Customiz_Os()


                # if task.info.result == None:
    #     print('Cloning VM Error ')
    # else:
    #     vm_obj = task.info.result

    #change_port_group(vm_obj)
    # def updt(total, progress):
    #
    #     barLength, status = 20, ""
    #     progress = float(progress) / float(total)
    #     if progress >= 1.:
    #         progress, status = 1, "\r\n"
    #     block = int(round(barLength * progress))
    #     text = "\r[{}] {:.0f}% {}".format(
    #         "#" * block + "-" * (barLength - block), round(progress * 100, 0),
    #         status)
    #     sys.stdout.write(text)
    #     sys.stdout.flush()
    #
    # time.sleep(2)
    # with int(task.info.progress) != None:
    #     time.sleep(1)
    #     runs = int(task.info.progress)
    #     for run_num in range(runs):
    #         time.sleep(.1)
    #         updt(runs, run_num + 1)
    # time.sleep(3)
    # # with task.info.state == 'success':
    #
    # time.sleep(4)
    # with tqdm.tqdm(total=95) as pbar:
    #     while task.info.progress != None:
    #         cur_perc = int(task.info.progress)
    #         pbar.update(cur_perc - pbar.n)  # here we update the bar of increase of cur_perc
    #         if cur_perc == 95:
    #             break
    #
    #



















#print(PortGroup(vm_net_address))


#print(PortGroup(vm_net_address).name)




        # print(vm_obj)
        # print(int(task.info.progress))









        # vm = int(task.info.progress)
        # for vm == True:
        #     print (vm)
        # # Do some work
        # #     bar.next()
        # # bar.finish()
        #




    # try:
    #     bar = Bar('Processing', max=100)
    #
    #     time.sleep(5)
    #     for
    #         vm = int(task.info.progress):
    #         for i in vm:
    #             # Do some work
    #         bar.next()
    #     bar.finish()
    # except:
    #     print('ready')





    # vm = int(task.info.progress)
    #vm = task.info.result
    # bar = Bar('Processing', max=100)
    # for i in vm:
    #     # Do some work
    #     bar.next()
    # bar.finish()

    # print (vm)
    # time.sleep(5)
    # vm1 = task.info.progress
    # print(vm1)
    # time.sleep(5)
    # vm2 = task.info.progress
    # print(vm2)

   # print(help(task))
    #print(clonespec.location)





#Clone_vm_localstore()












    # for storage_name in host.datastore:
            #     if storage_name.parent.name == storage_type:
            #         return storage_name
            #     else:
            #         print('no type datastore '+ storage_type)
            #





#print(Optimal_Esxi_Host(Cluster(), storage_type, vm_ram, vm_disk_size))

# Choice_Esxi = Choice_Esxi(Cluster(), storage_type, vm_ram, vm_disk_size)
#
# Cluster = Cluster()



#
#
# print (Choice_Store(Cluster, Choice_Esxi))
#
#








#print (Choice_Store(Cluster, Choice_Esxi)


