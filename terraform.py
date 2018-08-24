from python_terraform import *

#vcentter_name = ''
#cluster_name = ''
#storage_name = ''
#portgroup = ''
#hostname = ''
i = 'template_wind2008'

template_all=['template_centos7', 'template_ubuntu16.04', 'template_wind2012', 'template_wind2008']

if  i in template_all:
    tmp = template_all.index(i).str
    print (tmp.find('wind'))
    template_all.index('template_wind2012')

else:
    print False

#a = template_all



#def workdir_linux_windows():








#def teraform_apply(vcentter_name, vsphere_datacenter, cluster_name, storage_name, portgroup, template_name, ip, hostname, cpu, memory_ram, disk_size ):
#    tf = Terraform(working_dir='/etc/ansible/ansible-playbook', variables={'vmname':hostname, 'ipvm':ip})
#    kwargs = {"auto-approve": True}
#    tf.apply(**kwargs)







