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
# vm_name = 'testvm-clone'
# vm_disk_size = 300
# vm_ram = 8
# vm_cpu = 2


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



class ObjectContent():
    """docstring"""
    def __init__(self, vm_name, vm_cpu, vm_ram, vm_disk, vm_descriptinon):
        """Constructor"""
        self.datacenter = datacenter_name
        self.cluster = cluster_name
        self.vm = vm_name
        self.vm_disk = vm_disk
        self.vm_portgroup = vm_net_address
        self.folder = folder_vm


    def datacenter_obj(datacenter_name):
        """ return object datacenter, if he is """
        datacenter = get_obj(content, [vim.Datacenter], datacenter_name)
        try:
            if datacenter.name == datacenter_name:
                return datacenter
        except:
            print('Incorrect Datacenter: ' + datacenter_name)
            quit()


#####
    def cluster_obj(cluster_name):
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

#####
    def vm_obj(vm_name):
        """ return object VM, if he is """
        vm_name = get_obj(content, [vim.VirtualMachine], vm_name)
        if vm_name == None:
            print('Not found template name: ' + vm_name)
        else:
            return vm_name

####

    def folder_obj (datacenter_obj, folder_name_vm):
        """ return object folder obj, if not, then it creates  """

        destfolder = get_obj(content, [vim.Folder], folder_name_vm)
        if destfolder == None:
            datacenter_obj.vmFolder.CreateFolder(folder_name_vm)
            destfolder = get_obj(content, [vim.Folder], folder_name_vm)
            return destfolder
        else:
            return destfolder

####
    def portgroup_obj(datacenter_obj, vm_net_address):
        """ return object PortGroup ===> json  """
        try:
            portgroup_conf_pars = Json_Parser(config_network)[Datacenter_obj.name][vm_net_address][0]
            portgroup = get_obj(content, [vim.Network], portgroup_conf_pars)
            return portgroup
        except:
            print ('Not config file in ' + datacenter_obj.name + ' or ' + vm_net_address )





class VirtualMashin(object):
    """docstring"""

    def __init__(self, vm_name, vm_cpu, vm_ram, vm_disk, vm_descriptinon):
        """Constructor"""
        self.vm_name = vm_name
        self.vm_cpu = vm_cpu
        self.vm_ram = vm_ram
        self.vm_disk = vm_disk
        self.vm_portgroup = vm_net_address
        self.descriptinon = vm_descriptinon



    def get_vm_obj(self):
        """ return object VM, if he is """
        vm_name = get_obj(content, [vim.VirtualMachine], self.vm_name)
        if vm_name == None:
            print('Not found template name: ' + self.vm_name)
        else:
            return vm_name


    def cpu_reconfig(self):
        cspec = vim.vm.ConfigSpec()
        cspec.cpuHotAddEnabled = True
        cspec.numCPUs = self.vm_cpu
        cspec.numCoresPerSocket = 1
        vm_obj.Reconfigure(cspec)

    def ram_reconfig(self):
        cspec = vim.vm.ConfigSpec()
        cspec.memoryHotAddEnabled = True
        cspec.memoryMB = int(self.vm_ram * 1024)
        vm_obj.Reconfigure(cspec)


    def disk_resize(self):
        for dev in vm_obj.config.hardware.device:
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
            task = vm_obj.ReconfigVM_Task(spec=spec)
        else:
            print('Task resize disk Error')


    def annotation(self):
        spec = vim.vm.ConfigSpec()
        spec.annotation = descriptinon
        task = vm_obj.ReconfigVM_Task(spec)




if __name__ == "__main__":
    car = vm("testclonevm", 2, 2, 40)


    vm_obj = car.Get_VM_obj()
    car.disk_vm_resize()







