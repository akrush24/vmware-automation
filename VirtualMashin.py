

class VirtualMashin():
    """docstring"""

    def __init__(self, vm_name, vm_cpu, vm_ram, vm_disk):
        """Constructor"""

        self.vm_name = vm_name
        self.vm_cpu = vm_cpu
        self.vm_ram = vm_ram
        self.vm_disk = vm_disk


    def vm_obj(self):
        """ return object VM, if he is """
        try:
            vm_name = get_obj(content, [vim.VirtualMachine], self.vm_name)
            if vm_name == None:
                print('Not found template name: ' + vm_name)
            else:
                self.__vm_obj = vm_name

        except:
            print('notfound VM ')



    def cpu_reconfig(self):
        cspec = vim.vm.ConfigSpec()
        cspec.cpuHotAddEnabled = True
        cspec.numCPUs = self.vm_cpu
        cspec.numCoresPerSocket = 1
        self.__vm_obj.Reconfigure(cspec)

    def ram_reconfig(self):
        cspec = vim.vm.ConfigSpec()
        cspec.memoryHotAddEnabled = True
        cspec.memoryMB = int(self.vm_ram * 1024)
        self.__vm_obj.Reconfigure(cspec)


    def disk_resize(self):
        for dev in vm_obj.config.hardware.device:
            if hasattr(dev.backing, 'fileName'):
                if 'Hard disk 1' == dev.deviceInfo.label:
                    capacity_in_kb = dev.capacityInKB
                    new_disk_kb = int(self.vm_disk) * 1024 * 1024
                    if new_disk_kb > capacity_in_kb:
                        dev_changes = []
                        disk_spec = vim.vm.device.VirtualDeviceSpec()
                        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                        disk_spec.device = vim.vm.device.VirtualDisk()
                        disk_spec.device.key = dev.key
                        disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
                        disk_spec.device.backing.fileName = dev.backing.fileName
                        disk_spec.device.backing.diskMode = dev.backing.diskMode
                        disk_spec.device.controllerKey = dev.controllerKey
                        disk_spec.device.unitNumber = dev.unitNumber
                        disk_spec.device.capacityInKB = new_disk_kb
                        dev_changes.append(disk_spec)
                    else:
                        print('Disk size not corect')
                else:
                    print('No disk Hard_disk 1')
        if dev_changes != []:
            spec = vim.vm.ConfigSpec()
            spec.deviceChange = dev_changes
            task = vm_obj.ReconfigVM_Task(spec=spec)
        else:
            print('Task resize disk Error')


    def annotation(self):
        spec = vim.vm.ConfigSpec()
        spec.annotation = descriptinon
        task = vm_obj.ReconfigVM_Task(spec)


