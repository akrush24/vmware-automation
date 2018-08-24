from python_terraform import *

vcentter_name = ''
cluster_name = ''
storage_name = ''
portgroup = ''
hostname = ''

def teraform_apply(vcentter_name, vsphere_datacenter, cluster_name, storage_name, portgroup, template_name, ip, hostname, cpu, memory_ram, disk_size ):
    tf = Terraform(working_dir='/etc/ansible/ansible-playbook', variables={'vmname':hostname, 'ipvm':ip})
    kwargs = {"auto-approve": True}
    tf.apply(**kwargs)







