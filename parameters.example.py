vc_list = [
    'vcsa01.srv.local',
    'vcsa02.srv.local'
]

template_linux = [
    'template_centos7.5',
    'template_centos6.8',
    'template_ubuntu_16.04',
    'template_ubuntu_18.04']

template_wind = [
    'template_WindowsServer2008R2_SE',
    'template_WinSrv2012R2RU',
    'template_WinSrv2012R2EN',
    'template_SD_WinSrv2012R2EN']

os_to_template = {
    'Linux - Centos 7' : 'template_centos7.5',
    'Linux - Centos 6' : 'template_centos6.8',
    'Linux - Ubuntu 18.04': 'template_ubuntu_18.04',
    'Linux - Ubuntu 16.04': 'template_ubuntu_16.04',
    'Windows - Server 2008R2' : 'template_WindowsServer2008R2_SE',
    'Windows - Server 2012' : 'template_WinSrv2012R2EN'}

template_list = template_linux + template_wind

ds = {
 '15_localstore_r10' : { 'vc': 'vcsa01.srv.local', 'dc': 'Datacenter07', 'res': 'host01',    'dest' : 'host' },
 '30_localstore_r10' : { 'vc': 'vcsa02.srv.local', 'dc': 'Datacenter01', 'res': 'cluster001','dest' : 'cluster' },
 '31_localstore_r10' : { 'vc': 'vcsa03.srv.local', 'dc': 'Datacenter02', 'res': 'cluster02', 'dest' : 'cluster' }
}

port_int = {
# CIDR             : PORT GROUP NAME
 '192.168.222.0/24': '192.168.222',
 '192.168.199.0/24': '192.168.199',
 '192.168.245.0/24': '192.168.245',
 '192.168.238.0/24': '192.168.238',
 '192.168.221.0/24': '192.168.221'
}

net_default = "192.168.221.0/24"
