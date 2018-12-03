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
from VirtualMashin import *

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
# vm_name = 'testvm-clone'
# vm_disk_size = 300
# vm_ram = 8
# vm_cpu = 2


########################


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


class ObjectContent:
    """docstring"""
    def __init__(self, datacenter_name, cluster_name=None, template_name=None, folder_name_vm=None, vm_net_address = None):
        """Constructor"""
        self.datacenter = datacenter_name
        self.cluster = cluster_name
        self.vm_name = template_name
        self.folder_name_vm = folder_name_vm
        self.vm_net_address = vm_net_address
        # self.vm_portgroup = vm_net_address
        # self.folder = folder_vm



    def datacenter_obj(self):
        """ return object datacenter, if he is """
        datacenter = get_obj(content, [vim.Datacenter], self.datacenter)
        try:
            if datacenter.name == datacenter_name:
                self.__datacenter = datacenter
                return datacenter
        except:
            print('Incorrect Datacenter: ' + self.datacenter)
            quit()

#####
    def cluster_obj(self):
        """ return object Cluster obj, if he is """
        try:
            cluster = get_obj(content, [vim.ClusterComputeResource], self.cluster)
            if cluster == None:
                print('Not found ClusterName: '+ cluster_name)
            else:
                return cluster
        except:
            print('Error cluster_obj ' + cluster_name)
            quit()

#####
    def vm_obj(self):
        """ return object VM, if he is """
        try:
            vm_name = get_obj(content, [vim.VirtualMachine], self.vm_name)
            if vm_name == None:
                print('Not found template name: ' + vm_name)
            else:
                return vm_name
        except:
            print('notfound VM ')

####
    def folder_obj (self):
        """ return object folder obj, if not, then it creates  """

        destfolder = get_obj(content, [vim.Folder], self.folder_name_vm)
        if destfolder == None:
            self.__datacenter.vmFolder.CreateFolder(self.folder_name_vm)
            destfolder = get_obj(content, [vim.Folder], self.folder_name_vm)
            return destfolder
        else:
            return destfolder

####
    def portgroup_obj(self):
        """ return object PortGroup ===> json  """
        try:
            portgroup_conf_pars = Json_Parser(config_network)[self.__datacenter.name][self.vm_net_address][0]
            portgroup = get_obj(content, [vim.Network], portgroup_conf_pars)
            return portgroup
        except:
            print ('Not config file in ' +  self.__datacenter.name + ' or ' + self.vm_net_address )

class VirtualMashin():
    """docstring"""

    def __init__(self, vm_name, vm_cpu=None, vm_ram=None, vm_disk=None, portgroup=None, ip=None):
        """Constructor"""

        self.vm_name = vm_name
        self.vm_cpu = vm_cpu
        self.vm_ram = vm_ram
        self.vm_disk = vm_disk
        self.portgroup = portgroup
        self.ip = ip


    def vm_obj(self):
        """ return object VM, if he is """
        try:
            vm_name = get_obj(content, [vim.VirtualMachine], self.vm_name)
            if vm_name == None:
                print('Not found template name: ' + vm_name)
            else:
                self.__vm_obj = vm_name
                return vm_name

        except:
            print('notfound VM ')



    def cpu_reconfig(self):
        cspec = vim.vm.ConfigSpec()
        cspec.cpuHotAddEnabled = True
        cspec.numCPUs = self.vm_cpu
        cspec.numCoresPerSocket = 1
        self.__vm_obj.Reconfigure(cspec)

    def ram_reconfig(self):
        cspec = vim.vm.ConfigSpec()
        cspec.memoryHotAddEnabled = True
        cspec.memoryMB = int(self.vm_ram * 1024)
        self.__vm_obj.Reconfigure(cspec)


    def disk_resize(self):
        for dev in self.__vm_obj.config.hardware.device:
            if hasattr(dev.backing, 'fileName'):
                if 'Hard disk 1' == dev.deviceInfo.label:
                    capacity_in_kb = dev.capacityInKB
                    new_disk_kb = int(self.vm_disk) * 1024 * 1024
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
            task = self.__vm_obj.ReconfigVM_Task(spec=spec)
        else:
            print('Task resize disk Error')


    def annotation(self):
        spec = vim.vm.ConfigSpec()
        spec.annotation = descriptinon
        task = self.__vm_obj.ReconfigVM_Task(spec)


    def Change_PortGroup(self):
        """ change portgroup on VM, from func Get_PortGroup_obj ===> json """
        device_change = []
        for device in self.__vm_obj.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard):
                nicspec = vim.vm.device.VirtualDeviceSpec()
                nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                nicspec.device = device
                nicspec.device.wakeOnLanEnabled = True
                network = self.portgroup
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
        task = self.__vm_obj.ReconfigVM_Task(config_spec)


    def Customiz_Os(self):

        netmask_vm = Json_Parser(config_network)[datacenter.name][vm_net_address][2]
        gateway_vm = Json_Parser(config_network)[datacenter.name][vm_net_address][1]
        dns_prefix = Json_Parser(config_network)[datacenter.name]["dnsprefix"][0]
        dns_server_1 = Json_Parser(config_network)[datacenter.name]["dnslist"][0]
        dns_server_2 = Json_Parser(config_network)[datacenter.name]["dnslist"][1]
        dns_servers = [dns_server_1, dns_server_2]


        def Nix_Customiz():

            adaptermap = vim.vm.customization.AdapterMapping()
            adaptermap.adapter = vim.vm.customization.IPSettings()
            adaptermap.adapter.ip = vim.vm.customization.FixedIp()
            adaptermap.adapter.ip.ipAddress = self.ip
            adaptermap.adapter.subnetMask = netmask_vm
            adaptermap.adapter.gateway = gateway_vm
            adaptermap.adapter.dnsDomain = dns_prefix
            globalip = vim.vm.customization.GlobalIPSettings()
            globalip.dnsServerList = dns_servers
            ident = vim.vm.customization.LinuxPrep(domain='srv.local',
                                                   hostName=vim.vm.customization.FixedName(name=self.__vm_obj.name))
            customspec = vim.vm.customization.Specification()
            customspec.identity = ident
            customspec.nicSettingMap = [adaptermap]
            customspec.globalIPSettings = globalip
            task = self.__vm_obj.Customize(spec=customspec)

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

        vm_guest_id = self.__vm_obj.config.guestId
        if vm_guest_id in guest_id_win:
            Win_Customiz()
        elif vm_guest_id in guest_id_nix:
            Nix_Customiz()
        else:
            print("No support OS")


class Esxi_localstore:
    """docstring"""
    def __init__(self, cluster, vm_ram, vm_disk_size ):
        """Constructor"""
        self.cluster = cluster
        self.vm_ram = vm_ram
        self.vm_disk_size = vm_disk_size


    def Load_Average_Esxi(self):
        """ return  esxi-host (name), if  Free-RAM > 10% and Free-Storage > 15 % + vm(ram, disk)"""
        host_list = []
        for host in self.cluster.host:
            capacity_ram = int(host.summary.hardware.memorySize)
            used_ram = int(host.summary.quickStats.overallMemoryUsage) * 1024 * 1024
            free_mem_perc = 100 - ((used_ram + self.vm_ram) / capacity_ram * 100)
            if free_mem_perc > 10:
                for store_name in host.datastore:
                    if store_name.parent.name == storage_type:
                        used_storage = int(store_name.summary.capacity - store_name.summary.freeSpace - self.vm_disk_size)
                        free_store_perc = 100 - (used_storage / store_name.summary.capacity * 100)
                        if free_store_perc > 15:
                            host_list.append({'host': str(host.name), 'ram': int(free_mem_perc),
                                              'disk': int(free_store_perc)})
        esxi_host = pd.DataFrame(host_list).sort_values(by=['ram'], ascending=False).reset_index()
        esxi_host = esxi_host['host'].iloc[0]
        self.__esxi_host = esxi_host




    def Get_Choice_esxi_obj(self):
        """ return object esxi, from func Load_Average_Esxi """
        for host in self.cluster.host:
            if host.name == self.__esxi_host:
                return host


    def Get_Choice_Storage_obj(self):
        """ return object storage, from func Load_Average_Esxi """
        for host in self.cluster.host:
            if host.name == self.__esxi_host:
                for storage_name in host.datastore:
                    if storage_name.parent.name == storage_type:
                        return storage_name
                    else:
                        print('No type datastore')

class Clone:

    def __init__(self, datacenter_name, cluster_name, template_name, folder_name, vm_name, vm_cpu, vm_ram, vm_disk, vm_net_address ):
        """Constructor"""
        self.datacenter = datacenter_name
        self.cluster = cluster_name
        self.folder = folder_name
        self.template = template_name
        self.vm_name = vm_name
        self.vm_cpu = vm_cpu
        self.vm_ram = vm_ram
        self.vm_disk_size = vm_disk
        # self.vm_portgroup = portgroup_vm
        # self.ip = ip
        self.vm_net_address = vm_net_address

    def Create_VM_localstore(self):

        try:
            init = ObjectContent(self.datacenter, self.cluster, self.template, self.folder, self.vm_net_address)
            init.datacenter_obj()
            folder = init.folder_obj()
            storage_type = "LocalStore"
            esxi_deploy = Esxi_localstore(self.cluster, self.vm_ram, self.vm_disk_size)
            print(esxi_deploy.Get_Choice_esxi_obj())
            template = init.vm_obj()
        except:
            print('Error Create varible', sys.exc_info())
            quit()
        try:
            relospec = vim.vm.RelocateSpec()
            relospec.datastore = esxi_deploy.Get_Choice_Storage_obj()
            relospec.host = esxi_deploy.Get_Choice_esxi_obj()
            clonespec = vim.vm.CloneSpec()
            clonespec.location = relospec
        except:
            print('Error Create relospec and clonspec', sys.exc_info())
            quit()


        print("Cloning VM: " + template.name + ' to ' + self.vm_name)
        print("ESXI: " + esxi_deploy.Get_Choice_esxi_obj() + "   DATASTORE: " + esxi_deploy.Get_Choice_Storage_obj())
        task = template.Clone(folder=folder, name=self.vm_name, spec=clonespec)

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
        except:
            if task.info.state == 'error':
                print("Clon vm error", sys.exc_info())
                quit()





if __name__ == "__main__":
    # init = ObjectContent(datacenter_name, cluster_name)
    # datacenter = init.datacenter_obj()
    # #print(init.cluster_obj().name)
    # esxi_deploy = Esxi_localstore(init.cluster_obj(), 4, 300)
    # esxi_deploy.Load_Average_Esxi()
    # print(esxi_deploy.Get_Choice_esxi_obj().name)
    # print(esxi_deploy.Get_Choice_Storage_obj().name)
    test = Clone(datacenter_name = 'Datacenter-Linx', cluster_name = 'linx-cluster01', template_name = 'template_centos7.5',
                 folder_name = 'ewwwwe', vm_name = 'testclone1', vm_cpu = 1, vm_ram = 2, vm_disk = 30, vm_net_address = '172.20.20.0/24')

    test.Create_VM_localstore()

    # vm = VirtualMashin("testclonevm", portgroup=init.portgroup_obj(), ip='172.20.20.253')
    # vm.vm_obj()
    #
    # vm.Customiz_Os()


    #vm.portgroup_obj()
    # dc.datacenter_obj()
    # print(dc.cluster_obj())




    #print(VirtualMashin("testclonevm").vm_obj())
   # car.cpu_reconfig()





   # vm_obj = car.vm_obj()
   # ObjectContent.vm_obj("testclonevm")
    #car.cpu_reconfig()





    #
    # vm_obj = car.Get_VM_obj()
    # car.disk_vm_resize()







