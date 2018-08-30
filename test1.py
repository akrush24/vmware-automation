from python_terraform import *
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import re

vc_host = 'vc-linx.srv.local'
vc_user = 'nokhrimenko@phoenixit.ru'
vc_pass = 'NikolonsO345831'
new_ip = '192.168.222.184'
new_mask = '255.255.255.0'
new_gw_ip = re.sub('[/]', '', cidr)[:-3] + '1'
dns_prefix = 'srv.local'
vm_name = 'host-test'
def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj



si = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
content = si.RetrieveContent()
vm = get_obj(content, [vim.VirtualMachine], vm_name)



def windows_change_ip():
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
    adaptermap.adapter.dnsDomain = dns_prefix
    adaptermap.adapter.dnsServerList = ['172.20.20.20', '192.168.245.20']
    globalip = vim.vm.customization.GlobalIPSettings()
    #globalip.dnsServerList = ['172.20.20.20', '192.168.245.20']
    ident = vim.vm.customization.Sysprep()
    ident.guiUnattended = vim.vm.customization.GuiUnattended()
    #ident.guiUnattended.autoLogon = False
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

windows_change_ip()