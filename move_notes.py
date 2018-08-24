import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from tools import tasks
from tools import tasks
from tools import cli



def move_notes(ip, folder, message):
    vc_host=''
    vc_user=''
    vc_pass=''
    service_instance = connect.SmartConnectNoSSL(host=vc_host,
                                                         user=vc_user,
                                                         pwd=vc_pass,
                                                         port=443)
config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
uuid = config_uuid.summary.config.instanceUuid
message = ip + " " + infraname
vm = service_instance.content.searchIndex.FindByUuid(None, uuid, True, True)
print ("Found: {0}".format(vm.name))
spec = vim.vm.ConfigSpec()
spec.annotation = message
task = vm.ReconfigVM_Task(spec)
tasks.wait_for_tasks(service_instance, [task])
folder = service_instance.content.searchIndex.FindByInventoryPath('Datacenter-Linx/vm/INV/')
print(folder)
folder.MoveIntoFolder_Task([config_uuid])




print ("Done.")
