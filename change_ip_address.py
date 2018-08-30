from python_terraform import *
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from passwd import user_api, pass_api, vc_user, vc_pass
import requests

# get ip address
def ipam_create_ip(hostname, infraname, cidr):
    try:
       token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=(user_api, pass_api)).json()['data']['token']
       headers = {'token':token}
       cidr_url = 'http://ipam.phoenixit.ru/api/apiclient/subnets/cidr/' + cidr
       get_sudnet_id = requests.get(url=cidr_url, headers=headers).json()['data'][0]['id']
       get_ip_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+get_sudnet_id
       ip = requests.get(url=get_ip_url, headers=headers).json()['data']
       create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+get_sudnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
       create = requests.post(url = create_url , headers=headers).json()['success']
       if create == True:
          print ( ' ##### IP: '+ip+' ###### ')
          return ip  # get ip address
    except:
       print("При выделении IP произошла ошибка!")





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

def power_off():
    if vm.runtime.powerState != 'poweredOff':
        vm.PowerOff()

def power_on():
    if vm.runtime.powerState == 'poweredOff':
        vm.PowerOn()

def change_port_group(cidr):
    cidr_to_portgrup = {'192.168.222.0/24': '192.168.222',
                        '192.168.199.0/24': '192.168.199',
                        '192.168.245.0/24': '245',
                        '192.168.14.0/23': 'VLAN14',
                        '192.168.238.0/24': '192.168.238'}
    if cidr_to_portgrup[cidr]:
        vm_portgroup = cidr_to_portgrup.get(cidr)

    device_change = []
    for device in vm.config.hardware.device:

        if isinstance(device, vim.vm.device.VirtualEthernetCard):
            nicspec = vim.vm.device.VirtualDeviceSpec()
            nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            nicspec.device = device
            nicspec.device.wakeOnLanEnabled = True
            network = get_obj(content, [vim.dvs.DistributedVirtualPortgroup], vm_portgroup)
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

   # https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/change_vm_vif.py


def guest_os():
    windows = ['windows7Server64Guest', 'windows8Server64Guest']
    linux = ['centos64Guest', 'centos7_64Guest', 'ubuntu64Guest']
    vm_os = vm.guest.guestId
    if vm_os in windows:
        windows_change_ip()
    elif vm_os in linux:
        linux_change_ip()
    else:
        print("No support OS")

def linux_change_ip():
    adaptermap = vim.vm.customization.AdapterMapping()
    #globalip = vim.vm.customization.GlobalIPSettings()
    adaptermap.adapter = vim.vm.customization.IPSettings()
    adaptermap.adapter.ip = vim.vm.customization.FixedIp()
    adaptermap.adapter.ip.ipAddress = ip_address_
    adaptermap.adapter.subnetMask = netmask_
    adaptermap.adapter.gateway = gw_ipaddres_
    adaptermap.adapter.dnsDomain = dns_prefix
    globalip = vim.vm.customization.GlobalIPSettings()
    globalip.IPSetings.dnsServerList = ['172.20.20.20', '192.168.245.20']
    ident = vim.vm.customization.LinuxPrep(domain='srv.local', hostName=vim.vm.customization.FixedName(name=vm_name))
    customspec = vim.vm.customization.Specification()
    customspec.identity = ident
    customspec.nicSettingMap = [adaptermap]
    customspec.globalIPSettings = globalip
    task = vm.Customize(spec=customspec)

def windows_change_ip():
    #https://github.com/vmware/pyvmomi/issues/261
    si = connect.SmartConnectNoSSL(host=vc_host, user=vc_user, pwd=vc_pass, port=443)
    content = si.RetrieveContent()
    vm = get_obj(content, [vim.VirtualMachine], vm_name)
    adaptermap = vim.vm.customization.AdapterMapping()
    globalip = vim.vm.customization.GlobalIPSettings()
    adaptermap.adapter = vim.vm.customization.IPSettings()
    adaptermap.adapter.ip = vim.vm.customization.FixedIp()
    adaptermap.adapter.ip.ipAddress = ip_address_
    adaptermap.adapter.subnetMask = netmask_
    adaptermap.adapter.gateway = gw_ipaddres_
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


def main(hostname, cidr, infraname):
    ip_address_ = ipam_create_ip(hostname, infraname, cidr)
    gw_ipaddres_ = re.sub('[/]', '', cidr)[:-3] + '1'
    netmask_ = '255.255.255.0'
    dns_prefix = 'srv.local'
    power_off()
    guest_os()
    change_port_group(cidr)
    power_on()

