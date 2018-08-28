import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from tools import tasks
from tools import tasks
from tools import cli

vc_host = 'vc-linx.srv.local'
vc_user = 'nokhrimenko@phoenixit.ru'
vc_pass = 'NikolonsO345831'

ip = '192.168.222.135'
folder_vm = 'test/test'




def notes_move_vm(vc_host, vc_user, vc_pass, ip, folder_vm):
    folder_dc = { 'vc-linx.srv.local': 'Datacenter-Linx/vm/',
                  'vcsa.srv.local'  : 'Datacenter-AKB/vm/',
                  'vc-khut.srv.local': 'Datacenter-KHUT/vm/'}.get(vc_host)
    service_instance = connect.SmartConnectNoSSL(host=vc_host,
                                                    user=vc_user,
                                                     pwd=vc_pass,
                                                     port=443)
    config_uuid = service_instance.content.searchIndex.FindByIp(None, ip, True)
    uuid = config_uuid.summary.config.instanceUuid
    task = vm.ReconfigVM_Task(spec)
    tasks.wait_for_tasks(service_instance, [task])
    folder = service_instance.content.searchIndex.FindByInventoryPath(folder_dc+folder_vm)
    print(folder)
    folder.MoveIntoFolder_Task([config_uuid])




