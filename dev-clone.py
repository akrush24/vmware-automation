
from pyVim.connect import SmartConnect, Disconnect,SmartConnectNoSSL
from pyVmomi import vim
from pyVim import connect
import atexit
import argparse
import getpass
import json
import pandas as pd
import time
from progress.bar import Bar
import progressbar
from operator import itemgetter
########VARIBLE#########
config_vcenter = 'vcenter.json'
config_network = 'network.json'

storage_type = "LocalStore"

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

def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            print ("there was an error")
            task_done = True


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
            #network =  vm_portgroup
            dvs_port_connection = vim.dvs.PortConnection()
            dvs_port_connection.portgroupKey = network.key
            dvs_port_connection.switchUuid = network.config.distributedVirtualSwitch.uuid
            nicspec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
            nicspec.device.backing.port = dvs_port_connection
            nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
            nicspec.device.connectable.startConnected = True
            nicspec.device.connectable.allowGuestControl = True
            device_change.append(nicspec)
            break
        config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
        task = vm.ReconfigVM_Task(config_spec)
        wait_for_task(task)



    # def change_port_group(vm):
    #
    #     vm_portgroup = PortGroup(vm_net_address)
    #     device_change = []
    #     for device in vm.config.hardware.device:
    #         if isinstance(device, vim.vm.device.VirtualEthernetCard):
    #             nicspec = vim.vm.device.VirtualDeviceSpec()
    #             nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    #             nicspec.device = device
    #             nicspec.device.wakeOnLanEnabled = True
    #             network =  vm_portgroup
    #             dvs_port_connection = vim.dvs.PortConnection()
    #             dvs_port_connection.portgroupKey = network.key
    #             dvs_port_connection.switchUuid = network.config.distributedVirtualSwitch.uuid
    #             nicspec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
    #             nicspec.device.backing.port = dvs_port_connection
    #             nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    #             nicspec.device.connectable.startConnected = True
    #             nicspec.device.connectable.allowGuestControl = True
    #             device_change.append(nicspec)
    #             break
    #         config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
    #         task = vm.ReconfigVM_Task(config_spec)
    #         wait_for_task(task)






            #  Cluster, storage_type, vm_ram, vm_disk_size
####Optimal_Esxi_Host(Cluster(cluster_name), storage_type, vm_ram, vm_disk_size))
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
                        host_list.append ({'host': str(host.name), 'ram': int(free_mem_perc), 'disk': int(free_store_perc)})
    esxi_host = pd.DataFrame(host_list).sort_values(by=['ram'], ascending=False).reset_index()
    esxi_host = esxi_host['host'].iloc[0]
    return esxi_host
    #print(host_list, key=itemgetter('ram'))


#choice_esxi = Choice_Esxi(Cluster(), storage_type, vm_ram, vm_disk_size)
#print(choice_esxi)



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
    print ("cloning VM...")
    task = template.Clone(folder=folder, name=vm_name, spec=clonespec)
    wait_for_task(task)
    if task.info.result == None:
        print('Cloning VM Error ')
    else:
        vm_obj = task.info.result

    change_port_group(vm_obj)





#print(PortGroup(vm_net_address))

Clone_vm_localstore()

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


