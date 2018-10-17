#!/usr/bin/env python3

import sys
import argparse
#from ipam_create_ip import ipam_create_ip
from cvm import *
from passwd import user_api, pass_api, vc_user, vc_pass
version = '0.0.1'

parser = argparse.ArgumentParser()

parser.add_argument('--net', '-l',  dest='net',     help="Network [EXAMPLE: --net 192.168.0.0/24]. Auto assign IP addres from IPAM")
parser.add_argument('--vmname', '-n',   dest='vmname',  help="VM name [EXAMPLE: --vmname vm-01]", required=True)
parser.add_argument('--ip', dest='ip', help='IP Address. If IP exist ip is not taken from IPAM')
parser.add_argument('--datastor', '-ds', dest='ds',      help="Datastore name")
parser.add_argument('--folder', dest='folder',  help='VM Folder in vCenter [EXMPLE: folder1/folder2]')
parser.add_argument('--datacenter', '-dc', dest='datacenter',  help='vSphere Datacenter name')
parser.add_argument('--cluster', '-cl', dest='cluster',  help='vSphere Cluster')

parser.add_argument('--dsize', '--hdd', '-hdd', dest='dsize',   help='Disk Size')
parser.add_argument('--msize', '--mem', '--ram', '-m', dest='mem',   help='RAM Size in GB')
parser.add_argument('--cpu', '-c', dest='cpu',     help='CPU Count')
parser.add_argument('--desc', '-d', dest='desc',    help='Description')
parser.add_argument('--template', '-tm', dest='template',    help='VM Template')


parser.add_argument('--version', '-V', action='version', version='Version: '+version)

parser.add_argument('--vcenter', dest='vcenter', help='vCenter URL')
parser.add_argument('--debug', dest='debug',  help='debug mode', action='store_true')

parser.add_argument('--exp' , '--expdate',  dest='exp',    help='Expiry date [EXAMPLE: --exp "01/01/18"]')
parser.add_argument('--ONLYIP','--onlyip',  dest='ONLYIP', help='Only IP allocation [EXAMPLE: --ONLYIP]', action='store_true')
parser.add_argument('--EXPIRE' ,'--expire', dest='EXPIRE', help='Set only expire [EXMPLE --EXPIRE]',      action='store_true')
parser.add_argument('--resize' ,            dest='RESIZE', help='Resize disk (only on Linux vms) [EXMPLE --RESIZE]',      action='store_true')

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
    if args.cluster is None: 
       print("Please enter vCenter Cluster Name [--cluster ...]")
       quit()
    if args.datacenter is None: 
       print("Please enter vCenter DataCenter Name [--datacenter ...]")
       quit()
    if args.ds is None:
       print("Please enter vCenter DataStore Name [--datastor ...]")
       quit()
    if args.net is None:
       print("Please enter NETwork [--net ...]")
    if args.desc is None:
       print("Please enter Description [--desc ...]")
    
    if args.mem is not None: 
       args.mem = str(int(args.mem)*1024) # convert GB to MB
    
    if args.cpu   is None: args.cpu = 2
    if args.mem   is None: args.mem = 2048
    if args.dsize is None: args.dsize = 50
    print('### [MEM: '+args.mem+"], [HDD: "+args.dsize+"], [CPU: "+args.cpu+"]")

    try:
       ip = main(hostname=args.vmname, infraname=args.desc, cidr=args.net, folder_vm=args.folder,
         vm_template=args.template, vc_storage=args.ds, vm_cpu=args.cpu, vm_ram=args.mem,
         vm_disk_size=args.dsize, vc_dc=args.datacenter, vc_cluster=args.cluster, vc_host=args.vcenter, 
         ip=args.ip, debug=args.debug, expire_vm_date=args.exp)
    except:
       print("!!! Ошибка при выполнениие функции main()", sys.exc_info())
       quit()

    if args.exp is not None:
       try:
          print ("### Create sheduled power off "+args.vmname+" in " + args.exp)
          scheduledTask_poweroff(hostname=args.vmname, expire_vm_date=args.exp, vc_host=args.vcenter)
       except:
          print ("!!! ERROR: scheduledTask_poweroff: ", sys.exc_info())
          quit()


    if args.RESIZE: # resize HDD
       #answ = input('Run disk resize on '+ ip +' [Y/N]?')
       #if answ == 'Y':
       call(["./vms_prepare/grow_root.sh", ip, "root", "-s"])


