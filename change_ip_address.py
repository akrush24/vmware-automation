from python_terraform import *
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim


def power_off_on():



def change_port_group():
   # https: // github.com / vmware / pyvmomi - community - samples / blob / master / samples / change_vm_vif.py

def guest_os():




def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj





def linux_change_ip(vm_name, new_ip):
    si = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    content = si.RetrieveContent()
    vm = get_obj(content, [vim.VirtualMachine], vm_name)
    adaptermap = vim.vm.customization.AdapterMapping()
    globalip = vim.vm.customization.GlobalIPSettings()
    adaptermap.adapter = vim.vm.customization.IPSettings()
    adaptermap.adapter.ip = vim.vm.customization.FixedIp()
    adaptermap.adapter.ip.ipAddress = new_ip
    adaptermap.adapter.subnetMask = new_mask
    adaptermap.adapter.gateway = new_gw_ip
    globalip.dnsServerList = dns_server
    adaptermap.adapter.dnsDomain = dns_prefix
    globalip = vim.vm.customization.GlobalIPSettings()
    ident = vim.vm.customization.LinuxPrep(domain='srv.local', hostName=vim.vm.customization.FixedName(name=vm_name))
    customspec = vim.vm.customization.Specification()
    customspec.identity = ident
    customspec.nicSettingMap = [adaptermap]
    customspec.globalIPSettings = globalip
    task = vm.Customize(spec=customspec)


def windows_change_ip(vm_name, new_ip):
    #https://github.com/vmware/pyvmomi/issues/261
    si = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    content = si.RetrieveContent()
    vm = get_obj(content, [vim.VirtualMachine], vm_name)
    adaptermap = vim.vm.customization.AdapterMapping()
    globalip = vim.vm.customization.GlobalIPSettings()
    adaptermap.adapter = vim.vm.customization.IPSettings()
    adaptermap.adapter.ip = vim.vm.customization.FixedIp()
    adaptermap.adapter.ip.ipAddress = new_ip
    adaptermap.adapter.subnetMask = new_mask
    adaptermap.adapter.gateway = new_gw_ip
    globalip.dnsServerList = dns_server
    adaptermap.adapter.dnsDomain = dns_prefix
    globalip = vim.vm.customization.GlobalIPSettings()
    ident = vim.vm.customization.Sysprep()
    ident.guiUnattended = vim.vm.customization.GuiUnattended()
    ident.userData = vim.vm.customization.UserData()
    ident.userData.computerName = vim.vm.customization.FixedName()
    ident.userData.computerName.name = vm_name
    ident.identification = vim.vm.customization.Identification()






