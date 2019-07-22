#!/usr/bin/env python3.4

import sys, datetime
import argparse, argcomplete, requests
#from ipam_create_ip import ipam_create_ip
from cvm import *
from passwd import user_api, pass_api, vc_user, vc_pass

today = datetime.date.today()

version = '0.0.3.0'

parser = argparse.ArgumentParser()

# list of tapameters for choices
from parameters import template_list, vc_list, os_to_template, ds

# parse parameters from our servicedesk (IntraService)
from servicedesk import get_parameters_vm

parser.add_argument('--net', '-l',         dest='net',     help="Network [EXAMPLE: --net 192.168.0.0/24]. Auto assign IP addres from IPAM")
parser.add_argument('--vmname', '-n',      dest='vmname',  help="VM name [EXAMPLE: --vmname vm-01]")
parser.add_argument('--ip', dest='ip',     help='IP Address. If IP exist ip is not taken from IPAM')
parser.add_argument('--datastor', '-ds',   dest='ds',      help="Datastore name")
parser.add_argument('--folder',           dest='folder',  help='VM Folder in vCenter [EXMPLE: folder1/folder2]')
parser.add_argument('--datacenter', '-dc', dest='datacenter',  help='vSphere Datacenter name')
parser.add_argument('--cluster',   '-cl', dest='cluster',  help='vSphere Cluster')

parser.add_argument('--hdd',   '--hdd', '-hdd', dest='hdd',   help='Disk Size')
parser.add_argument('--ram', dest='ram',   help='RAM Size in GB')
parser.add_argument('--cpu',     '-c', dest='cpu',     help='CPU Count')
parser.add_argument('--desc',    '-d', dest='desc',    help='Description')
parser.add_argument('--template','-t', dest='template',    help='VM Template', choices=template_list)

parser.add_argument('--version', '-V', action='version', version='Version: '+version)

parser.add_argument('--vcenter', '-v', dest='vcenter', help='vCenter URL',choices=vc_list)
parser.add_argument('--debug',   dest='debug',  help='debug mode', action='store_true')

parser.add_argument('--exp' ,    '-e',  dest='exp',    help='Expiry date [EXAMPLE: --exp "31/01/20"]')
parser.add_argument('--ONLYIP',  '--onlyip' ,'-IP',  dest='ONLYIP', help='Only IP allocation [EXAMPLE: --ONLYIP]', action='store_true')
parser.add_argument('-IPRM',  dest='IPRM', help='Remove IP allocation', action='store_true')
parser.add_argument('--EXPIRE' , '-E', dest='EXPIRE', help='Set only expire [EXMPLE --EXPIRE]',      action='store_true')
parser.add_argument('-N', dest='NODES', help='Edit Nodes only', action='store_true')
parser.add_argument('--resize', '-r',      dest='RESIZE', help='Resize disk (only on Linux vms) [EXMPLE --RESIZE]',      action='store_true')
parser.add_argument('--task',  dest='task', help='Get parameters from ServiceDesk task (ram,hdd,cpu)')

#parser.add_argument('--', dest='',      help='')

argcomplete.autocomplete(parser)
args = parser.parse_args()

#if args.folder is None and args.onlyip is not 'yes':
#    print("Please enter Folder name");
#    quit()

#if args.template is None and args.onlyip is not 'yes':
#    print("Please enter VM Template");
#    quit()

# удаляем указанный адрес, --ip <IPADDR>
if args.IPRM:
   if args.ip is None:
      print("!!! Please enter IP")
      quit()
   if args.net is None:
      print("!!! Please enter --net (ex: --net 192.168.0.0/24)")
      quit()
   else:
      ipam_rm_ip(args.ip, args.net)
      quit()

# выстаскиваем значения из заявки
if args.task is not None:
   if re.match("[1-9][0-9].+", args.task):
      vmparam = get_parameters_vm( str(args.task) )
      if args.vmname is None: args.vmname = vmparam['hostname']
      if args.cpu is None: args.cpu = vmparam['cpu']
      if args.hdd is None: args.hdd = vmparam['hdd']
      if args.exp is None: args.exp = vmparam['exp'] 
      if args.ram is None: args.ram = vmparam['ram']
      if args.template is None: args.template = os_to_template[vmparam['os']]
      args.desc = "SD:" + args.task + ";" + vmparam['taskname'] + "; O:" + vmparam['owner'] + ";"
      print ( "TASK: [" + args.task + "]\n--template " + args.template + "\n--vmname " + args.vmname + "\n--cpu " + args.cpu + "\n--hdd " + args.hdd + "\n--ram " + args.ram + "\n--exp " + args.exp + "\n--desc " + args.desc )
      # quit() # for debug

if args.vmname is None:
    print("Please enter --vmname: vmname")
    quit()

if args.exp is None:
    exp = today + datetime.timedelta(days = 356)
    args.exp = exp.strftime('%d')+"."+exp.strftime('%m')+"."+exp.strftime('%Y')
    print (args.exp)

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
      if ds[args.ds]['vc']:
         args.vcenter = ds[args.ds]['vc']
      else:
         print("Please enter vCenter Name [--vcenter ...]")
         quit()

    if args.datacenter is None: 
       if ds[args.ds]['dc']:
          args.datacenter = ds[args.ds]['dc']
       else:
          print("Please enter vCenter DataCenter Name [--datacenter ...]")
          quit()

    if args.cluster is None:
       if ds[args.ds]['cl']:
          args.cluster = ds[args.ds]['cl']
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

    if args.ram is not None: args.ram = str(int(args.ram)*1024) # convert GB to MB
    if args.cpu   is None: args.cpu = 2
    if args.ram   is None: args.ram = 2048
    if args.hdd is None: args.hdd = 50
    print('### [MEM: '+str(args.ram)+"], [HDD: "+str(args.hdd)+"], [CPU: "+str(args.cpu)+"]")

    try:
       ip = main(hostname=args.vmname, infraname=args.desc, cidr=args.net, folder_vm=args.folder,vm_template=args.template, vc_storage=args.ds, vm_cpu=args.cpu, vm_ram=args.ram,
                 vm_disk_size=args.hdd, vc_dc=args.datacenter, vc_cluster=args.cluster, vc_host=args.vcenter, ip=args.ip, debug=args.debug, expire_vm_date=args.exp)
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
          print(args.exp)
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
