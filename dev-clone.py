
from pyVim.connect import SmartConnect, Disconnect,SmartConnectNoSSL
from pyVmomi import vim
from pyVim import connect
import atexit
import argparse
import getpass
import json
import pandas as pd

########VARIBLE#########
config_vcenter = 'vcenter.json'
config_network = 'network.json'

storage_type = "LocalStore"

vcenter_host = 'vc-linx.srv.local'
datacenter_name = 'Datacenter-Linx'
cluster_name = 'linx-cluster01'
template_name = 'centos7-minimal'
vm_net_address = '172.20.20.0/24'
folder_name_vm = 'ewwwewe'
vm_data_expare = '10.10.19'

vm_disk_size = 300
vm_ram = 8
vm_cpu = 2


########################


def Json_Parser(config_file):
    config = json.loads(open(config_file).read())
    return config


si = connect.SmartConnectNoSSL(host=vcenter_host, user=Json_Parser(config_vcenter)[vcenter_host][0],
                               pwd=Json_Parser(config_vcenter)[vcenter_host][1], port=443)
content = si.RetrieveContent()

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

def Datacenter (datacenter_name):
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)
    if  datacenter.name == datacenter_name:
        return datacenter
    else:
        print ('Not found: ' +  datacenter_name)





def Cluster():
    cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name)
    if cluster == None:
        print('Not found ClusterName: '+ cluster_name)
    else:
        return cluster



def Template(template_name):
    template_name = get_obj(content, [vim.VirtualMachine], template_name)
    if template_name == None:
        print('Not found template name: ' + template_name)
    else:
        return template_name


def Folder_Dest (Datacenter, folder_name_vm):
    destfolder = get_obj(content, [vim.Folder], folder_name_vm)
    if destfolder == None:
        Datacenter.vmFolder.CreateFolder(folder_name_vm)
        destfolder = get_obj(content, [vim.Folder], folder_name_vm)
        return destfolder
    else:
        return destfolder


def PortGroup(vm_net_address):
    try:
        portgroup_conf_pars = Json_Parser(config_network)[datacenter(datacenter_name).name][vm_net_address][0]
        portgroup = get_obj(content, [vim.Network], portgroup_conf_pars)
        return portgroup
    except:
        print ('Not config file in ' + Datacenter(datacenter_name).name + ' or ' + vm_net_address )



####Optimal_Esxi_Host(Cluster(cluster_name), storage_type, vm_ram, vm_disk_size))
def Optimal_Esxi_Host(Cluster, storage_type, vm_ram, vm_disk_size):
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
                        host_list.append ({'host': str(host.name), 'ram': int(free_mem_perc), 'disk': int(free_store_perc)})
    esxi_host = pd.DataFrame(host_list).sort_values(by=['ram'], ascending=False).reset_index()
    esxi_host = esxi_host['host'].iloc[0]
    return esxi_host


def Esxi_local_store(Optimal_Esxi_Host, Cluster):
    for host in Cluster.host:
        print (host.name)
        if host.name == Optimal_Esxi_Host:
            for storage_name in host.datastore:
                if storage_name.parent.name == storage_type:
                    return storage_name
                else:
                    print('no type datastore '+ storage_type)


print(Esxi_local_store(Optimal_Esxi_Host(Cluster(), storage_type, vm_ram, vm_disk_size), Cluster()))


