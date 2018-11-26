#!/usr/bin/env python3

import sys
import argparse
#from ipam_create_ip import ipam_create_ip
from cvm import *
from passwd import user_api, pass_api, vc_user, vc_pass
version = '0.0.2'

parser = argparse.ArgumentParser()

parser.add_argument('--net', '-l',         dest='net',     help="Network [EXAMPLE: --net 192.168.0.0/24]. Auto assign IP addres from IPAM")
parser.add_argument('--vmname', '-n',      dest='vmname',  help="VM name [EXAMPLE: --vmname vm-01]", required=True)
parser.add_argument('--ip', dest='ip',     help='IP Address. If IP exist ip is not taken from IPAM')
parser.add_argument('--datastor', '-ds',   dest='ds',      help="Datastore name")
parser.add_argument('--folder',           dest='folder',  help='VM Folder in vCenter [EXMPLE: folder1/folder2]')
parser.add_argument('--datacenter', '-dc', dest='datacenter',  help='vSphere Datacenter name')
parser.add_argument('--cluster',   '-cl', dest='cluster',  help='vSphere Cluster')

parser.add_argument('--dsize',   '--hdd', '-hdd', dest='dsize',   help='Disk Size')
parser.add_argument('--msize',   '--mem', '--ram', '-m', dest='mem',   help='RAM Size in GB')
parser.add_argument('--cpu',     '-c', dest='cpu',     help='CPU Count')
parser.add_argument('--desc',    '-d', dest='desc',    help='Description')
parser.add_argument('--template','-t', dest='template',    help='VM Template')


parser.add_argument('--version', '-V', action='version', version='Version: '+version)

parser.add_argument('--vcenter', '-v', dest='vcenter', help='vCenter URL')
parser.add_argument('--debug',   dest='debug',  help='debug mode', action='store_true')

parser.add_argument('--exp' ,    '-e',  dest='exp',    help='Expiry date [EXAMPLE: --exp "01/01/18"]')
parser.add_argument('--ONLYIP',  '--onlyip' ,'-IP',  dest='ONLYIP', help='Only IP allocation [EXAMPLE: --ONLYIP]', action='store_true')
parser.add_argument('--EXPIRE' , '-E', dest='EXPIRE', help='Set only expire [EXMPLE --EXPIRE]',      action='store_true')
parser.add_argument('-N', dest='NODES', help='Edit Nodes only',      action='store_true')
parser.add_argument('--resize' , '-r',      dest='RESIZE', help='Resize disk (only on Linux vms) [EXMPLE --RESIZE]',      action='store_true')

#parser.add_argument('--', dest='',      help='')

args = parser.parse_args()

#if args.folder is None and args.onlyip is not 'yes':
#    print("Please enter Folder name");
#    quit()

#if args.template is None and args.onlyip is not 'yes':
#    print("Please enter VM Template");
#    quit()


if args.EXPIRE:
    print("Set Expire for vm: "+args.vmname)
    if args.exp is not None:
       scheduledTask_poweroff(hostname=args.vmname, expire_vm_date=args.exp, vc_host=args.vcenter)
    else:
       print("!!! --exp is not to be None")
    quit()

if args.NODES:
   print("Only Edit Nodes for vm: "+args.vmname+" Ok....")
   if args.desc is None:
      print("!!! Please enter Dscriptin")
      quit()
   if args.ip is None:
      print("!!! Please enter IP")
      quit()
   else:
      ip=args.ip
   try:
      print (notes_write_vm(args.vcenter, vc_user, vc_pass, ip, args.desc, args.exp))
      quit()
   except:
      print ("!!! ERROR: notes_write_vm: ",sys.exc_info())
      quit()


if args.ONLYIP:
    print("Only reserv IP for vm :"+args.vmname)
    if args.desc is None:
       args.desc = args.vmname
    ip = ipam_create_ip(hostname=args.vmname, infraname=args.desc, cidr=args.net);
else:
    # check on the fool
    if args.vcenter is None:
       print("Please enter vCenter Name [--vcenter ...]")
       quit()

    if args.datacenter is None: 
       if args.vcenter == 'vc-linx.srv.local':
          args.datacenter = 'Datacenter-Linx'
       else:
          print("Please enter vCenter DataCenter Name [--datacenter ...]")
          quit()

    if args.cluster is None:
       if args.datacenter == 'Datacenter-Linx':
          args.cluster = 'linx-cluster01'
       else:
          print("Please enter vCenter Cluster Name [--cluster ...]")
          quit()

    if args.ds is None:
       print("Please enter vCenter DataStore Name [--datastor ...]")
       quit()

    if args.net is None:
       print("Please enter NETwork [--net ...]")

    if args.desc is None:
       print("Please enter Description [--desc ...]")

    if args.mem is not None: args.mem = str(int(args.mem)*1024) # convert GB to MB
    if args.cpu   is None: args.cpu = 2
    if args.mem   is None: args.mem = 2048
    if args.dsize is None: args.dsize = 50
    print('### [MEM: '+args.mem+"], [HDD: "+args.dsize+"], [CPU: "+args.cpu+"]")

    try:
       ip = main(hostname=args.vmname, infraname=args.desc, cidr=args.net, folder_vm=args.folder,vm_template=args.template, vc_storage=args.ds, vm_cpu=args.cpu, vm_ram=args.mem,
                 vm_disk_size=args.dsize, vc_dc=args.datacenter, vc_cluster=args.cluster, vc_host=args.vcenter, ip=args.ip, debug=args.debug, expire_vm_date=args.exp)
    except:
       print("!!! Ошибка при выполнениие функции main()", sys.exc_info())
       quit()

    print ("### Edit nodes to: ["+str(args.desc)+" "+str(args.exp)+"]")
    try:
       print (notes_write_vm(args.vcenter, vc_user, vc_pass, ip, args.desc, args.exp))
    except:
       print ("!!! ERROR: notes_write_vm: ",sys.exc_info())
       quit()

    print ("### Move VM to: ["+args.folder+"]")
    try:
       move_vm_to_folder(args.vcenter, vc_user, vc_pass, ip, args.folder, args.cluster)
    except:
       print ("!!! ERROR: move_vm_to_folder: ",sys.exc_info())
       quit()


    if args.exp is not None:
       try:
          print ("### Create sheduled power off "+args.vmname+" in " + args.exp)
          scheduledTask_poweroff(hostname=args.vmname, expire_vm_date=args.exp, vc_host=args.vcenter)
       except:
          print ("!!! ERROR: scheduledTask_poweroff: ", sys.exc_info())
          quit()
    else:
       print("!!! You did not enter the VM lifetime. PASS.")


    if args.RESIZE: # resize HDD
       #answ = input('Run disk resize on '+ ip +' [Y/N]?')
       #if answ == 'Y':
       call(["./vms_prepare/grow_root.sh", ip, "root", "-s"])
