from python_terraform import *

vm_template = 'template_centos7'

def template(vm_template):
    template_linux = ['template_centos7', 'template_ubuntu16.04']
    template_wind = ['template_wind2012', 'template_wind2008']
    if vm_template in template_linux:
        ter_dir = '/home/terraform/linux'
    elif vm_template in template_wind:
        ter_dir = '/home/terraform/windows'
    else:
        return
    tf = Terraform(working_dir=ter_dir, variables={'vc_host': vc_host, 'vc_user': vc_user, 'vc_pass': vc_pass,
                                                   'vc_dc': vc_dc, 'vc_cluster': vc_cluster,'vc_storage': vc_storage,
                                                   'vm_portgroup': vm_portgroup, 'vm_template': vm_template,
                                                   'vm_hostname': vm_hostname, 'vm_cpu': vm_cpu,'vm_ram': vm_ram,
                                                   'vm_disk_size': vm_disk_size, 'vm_ip': vm_ip, 'vm_ip_gw': vm_ip_gw,
                                                   'vm_netmask': vm_netmask})
    kwargs = {"auto-approve": True}
    tf.apply(**kwargs)
