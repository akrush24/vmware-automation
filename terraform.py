from python_terraform import *
from passwd import user_api, pass_api

def vlan_vm_int(cidr):
    port_int = {'192.168.222.0/24': '192.168.222',
                '192.168.199.0/24': '192.168.199',
                '192.168.245.0/24': '245'}

    if port_int[cidr]:
        vm_portgroup = port_int.get(cidr)
    else:
        print ('no network portgroup')

vm_template = 'template_centos7'

def template(vm_template, ):
    template_linux = ['template_centos7', 'template_ubuntu16.04']
    template_wind = ['template_wind2012', 'template_wind2008']
    if vm_template in template_linux:
        ter_dir = './terraform/linux'
    elif vm_template in template_wind:
        ter_dir = './terraform/windows'
    else:
        return
    tf = terraform(working_dir=ter_dir, variables={'vc_host': vc_host, 'vc_user': vc_user, 'vc_pass': vc_pass,
                                                   'vc_dc': vc_dc, 'vc_cluster': vc_cluster,'vc_storage': vc_storage,
                                                   'vm_portgroup': vm_portgroup, 'vm_template': vm_template,
                                                   'vm_hostname': vm_hostname, 'vm_cpu': vm_cpu,'vm_ram': vm_ram,
                                                   'vm_disk_size': vm_disk_size, 'vm_ip': vm_ip, 'vm_ip_gw': vm_ip_gw,
                                                   'vm_netmask': vm_netmask})
    kwargs = {"auto-approve": True}
    tf.apply(**kwargs)

def move_notes_vm(ip, folder, infraname):
    service_instance = connect.SmartConnectNoSSL(host=vc_host,
                                                         user=vc_user,
                                                         pwd=vc_pass,
                                                         port=443)
    config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
    uuid = config_uuid.summary.config.instanceUuid # получает uuid vm
    message = ip + " " + infraname  # формируется notes
    vm = service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)
    print ("Found: {0}".format(vm.name))
    spec = vim.vm.ConfigSpec()
    spec.annotation = message
    task = vm.ReconfigVM_Task(spec)
    tasks.wait_for_tasks(service_instance, [task])
    dirname = 'Datacenter-Linx/vm/' + folder # урл директории для ВМ
    movefolder = service_instance.content.searchIndex.FindByInventoryPath(dirname)
    movefolder.MoveIntoFolder_Task([config_uuid])


