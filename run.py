#!/usr/bin/env python3.4

import sys, datetime, os
import argparse, argcomplete, requests
from cvm import *
from passwd import user_api, pass_api, vc_user, vc_pass

today = datetime.date.today()

parser = argparse.ArgumentParser()

# list of tapameters for choices
from parameters import template_list, vc_list, os_to_template, ds, port_int, net_default, stor_default

# parse parameters from our servicedesk (IntraService)
from servicedesk import get_parameters_vm

parser.add_argument('--net', '-l',         dest='net',     help="Network [EXAMPLE: --net 192.168.0.0/24]. Auto assign IP addres from IPAM", choices=port_int)
parser.add_argument('--vmname', '-n', '--name',      dest='vmname',  help="VM name [EXAMPLE: --vmname vm-01]")
parser.add_argument('--ip', dest='ip',     help='IP Address. If IP exist ip is not taken from IPAM')
parser.add_argument('--datastor', '-ds',   dest='ds',      help="Datastore name", choices=ds)
parser.add_argument('--folder',           dest='folder',  help='VM Folder in vCenter [EXMPLE: folder1/folder2]')
parser.add_argument('--datacenter', '-dc', dest='datacenter',  help='vSphere Datacenter name')
parser.add_argument('--cluster',   '-cl', dest='cluster',  help='vSphere Cluster')
parser.add_argument('--host', dest='host',  help='vSphere Host (esxi name)')

parser.add_argument('--hdd',   '--hdd', '-hdd', dest='hdd',   help='Disk Size')
parser.add_argument('--ram', '--mem', dest='ram',   help='RAM Size in GB')
parser.add_argument('--cpu',     '-c', dest='cpu',     help='CPU Count')
parser.add_argument('--desc',    '-d', dest='desc',    help='Description')
parser.add_argument('--template','-t', dest='template',    help='VM Template', choices=template_list)

parser.add_argument('--vcenter', '-v', dest='vcenter', help='vCenter URL',choices=vc_list)
parser.add_argument('--debug', '-D',   dest='debug',  help='debug mode', action='store_true')

parser.add_argument('--exp' ,    '-e',  dest='exp',    help='Expiry date [EXAMPLE: --exp "31/01/20"]')
parser.add_argument('--ONLYIP',  '--IP' ,'-IP',  dest='ONLYIP', help='Only IP allocation [EXAMPLE: --ONLYIP]', action='store_true')
parser.add_argument('--iprm', '-IPRM',  dest='IPRM', help='Remove IP allocation', action='store_true')
parser.add_argument('--expire' , '-E', dest='EXPIRE', help='ONLY Set expire to vm: --name',      action='store_true')
parser.add_argument('--move' , '-M', dest='MOVE', help='ONLY move vm: --name to folder: --folder',      action='store_true')
parser.add_argument('-N', dest='NODES', help='Edit Nodes only', action='store_true')
parser.add_argument('--resize', '-r',      dest='RESIZE', help='Resize disk (only on Linux vms) [EXMPLE --RESIZE]',      action='store_true')
parser.add_argument('-R',      dest='ONLYRESIZE', help='Only resize disk (only on Linux vms)',      action='store_true')
parser.add_argument('--task',  dest='task', help='Get parameters from ServiceDesk task (ram,hdd,cpu)')

#parser.add_argument('--', dest='',      help='')

argcomplete.autocomplete(parser)
args = parser.parse_args()

#
# wrile log statistics
#
argslog = ""
now = datetime.datetime.utcnow()
for arglog in sys.argv:
   argslog = argslog + str(arglog) + " "
logfile=open("run.logs", "a")
argslog = argslog + "\n"
log = "[" + str(now) + "]: " + argslog
print("\n"+log)
logfile.write(log)
logfile.close()
######################

def bye():
   print ("Good Bye....")
   quit()

#if args.folder is None and args.onlyip is not 'yes':
#    print("Please enter Folder name");
#    quit()

#if args.template is None and args.onlyip is not 'yes':
#    print("Please enter VM Template");
#    quit()

if args.debug:
   print("* * * You enter in Debug mode * * *\n")

# удаляем указанный адрес, --ip <IPADDR>
if args.IPRM:
   if args.ip is None:
      print("!!! Please enter IP")
      bye()
   if args.net is None:
      print("!!! Please enter --net (ex: --net 192.168.0.0/24)")
      bye()
   else:
      ipam_rm_ip(args.ip, args.net)
      bye()

if args.ONLYRESIZE:
    if args.ip is None:
       print("!!! Please enter IP")
    else:
       os.system('ssh root@'+args.ip+'" bash -s" < ./tools/resize-root.sh')
    bye()

def report():
   if args.exp is None:
       args.exp = 'NONE'
   if args.task is None:
       args.task = 'NONE'
   print ( "TASK: [" + args.task + "]\n--template " + args.template + "\n--vmname " + args.vmname + "\n--cpu " + args.cpu + "\n--hdd " + args.hdd + "\n--ram " + args.ram + "\n--exp " + args.exp + "\n--desc " + args.desc + "\n--folder " + args.folder )

# выстаскиваем значения из заявки
if args.task is not None:
   if re.match("[1-9][0-9].+", args.task):
      vmparam = get_parameters_vm( str(args.task) )
      if args.vmname is None: args.vmname = vmparam['hostname']
      if args.cpu is None: args.cpu = vmparam['cpu']
      if args.hdd is None: args.hdd = vmparam['hdd']
      if args.exp is None: args.exp = vmparam['exp'] 
      if args.ram is None: args.ram = vmparam['ram']
      if args.folder is None: args.folder = vmparam['block'] + '/' + vmparam['code']
      if args.template is None: args.template = os_to_template[vmparam['os']]
      if args.desc is None: args.desc = "SD:" + args.task + ";" + vmparam['taskname'] + ";O:" + vmparam['owner']
      report()

# отпеделяем vCenter сервер
if args.vcenter is None:
    if args.ds is None:
        
        if stor_default is None:
           print ("Please enter --datastor")
           bye()
        else:
           args.ds = stor_default
           print("--datastor is not defined, default DataStore is: " + stor_default)

    if ds[args.ds]['vc']:
        args.vcenter = ds[args.ds]['vc']
        print ( "--vcenter " + ds[args.ds]['vc'] )
    else:
        print("Please enter vCenter Name [--vcenter ...]")
        bye()

# время жизни машины, нужно для установки Shedudet Tasks
if args.exp is None:
    exp = today + datetime.timedelta(days = 356)
    args.exp = exp.strftime('%d')+"."+exp.strftime('%m')+"."+exp.strftime('%Y')
    print ("Expire set to: " + args.exp)

# только устанавливаем выключение машины па доте указанной в --exp и выходим
if args.EXPIRE:
    print("Set Expire for vm: "+args.vmname)
    if args.exp is not None:
       scheduledTask_poweroff(hostname=args.vmname, expire_vm_date=args.exp, vc_host=args.vcenter)
    else:
       print("!!! --exp is not to be None")
    bye()

if args.NODES:
   print("Only Edit Nodes for vm: "+args.vmname+" Ok....")
   if args.desc is None:
      print("!!! Please enter Dscriptin")
      bye()
   if args.ip is None:
      print("!!! Please enter IP")
      bye()
   else:
      ip=args.ip
   try:
      print (notes_write_vm(args.vcenter, vc_user, vc_pass, ip, args.desc, args.exp))
      bye()
   except:
      print ("!!! ERROR: notes_write_vm: ",sys.exc_info())
      bye()

if args.vmname is None:
    print("Please enter --vmname: vmname")
    quit()
else:
    # убираем недопустимые символы из имени машины
    oldname = args.vmname
    args.vmname = args.vmname.replace(".","-")
    args.vmname = args.vmname.replace("_","-")
    if oldname != args.vmname:
       print ("!!! YOU VM Name IS CHANGED FROM: " + oldname + " =TO=>: " + args.vmname)

# только выделяем ip для машины и выходим
if args.ONLYIP:
    print("Only reserv IP for vm : "+args.vmname)
    if args.desc is None:
       args.desc = args.vmname
    print ("vname: "+args.vmname + "; desc: "+args.desc)
    ip = ipam_create_ip(hostname=args.vmname, infraname=args.desc, cidr=args.net);
    bye()

# определяем переменную DataCenter
if args.datacenter is None:
    if ds[args.ds]['dc']:
       args.datacenter = ds[args.ds]['dc']
       print ( "--datacenter " + ds[args.ds]['dc'] )
    else:
       print("Please enter vCenter DataCenter Name [--datacenter ...]")
       bye()

if args.MOVE:
    print ("### Move VM to: ["+args.folder+"]")
    try:
       move_vm_to_folder(args.vcenter, args.ip, args.folder, args.cluster, args.datacenter )
    except:
       print ("!!! ERROR: move_vm_to_folder: ",sys.exc_info())
    bye()
else:
    # check on the fool
    if args.vcenter is None:
      if ds[args.ds]['vc']:
         args.vcenter = ds[args.ds]['vc']
         print ( "--vcenter " + ds[args.ds]['vc'] )
      else:
         print("Please enter vCenter Name [--vcenter ...]")
         quit()

    if args.cluster is None and args.host is None:
       if ds[args.ds]['dest'] == 'cluster':
          if ds[args.ds]['res']:
             args.cluster = ds[args.ds]['res']
             print ( "--cluster " + ds[args.ds]['res'] )
          else:
             print("Please enter vCenter Cluster Name [--cluster ...]")
             quit()
       else:
          if ds[args.ds]['res']:
             args.host = ds[args.ds]['res']
             print ( "--host " + ds[args.ds]['res'] )
          else:
             print("Please enter vCenter Host Name [--host ...]")
             quit()



    if args.ds is None:
       print("Please enter vCenter DataStore Name [--datastor ...]")
       quit()

    if args.net is None:
       args.net = net_default;
       print("--net is not defined, default Net is: " + net_default)
       #print("Please enter NETwork [--net ...]")

    if args.desc is None:
       print("Please enter Description [--desc ...]")

    if args.ram is not None: args.ram = str(int(args.ram)*1024) # convert GB to MB
    if args.cpu is None: args.cpu = 2
    if args.ram is None: args.ram = 2048
    if args.hdd is None: args.hdd = 50
    print('### [MEM: '+str(args.ram)+"], [HDD: "+str(args.hdd)+"], [CPU: "+str(args.cpu)+"]")

    #try:
    
    # where put the VM cluster or host 
    if args.host is not None:
       destination = 'host'
       destination2 = args.host
    else:
       destination = 'cluster'
       destination2 = args.cluster

    print("### Destination: " + destination + " " + destination2)

    ip = main(hostname=args.vmname, infraname=args.desc, cidr=args.net, folder_vm=args.folder,vm_template=args.template, vc_storage=args.ds, vm_cpu=args.cpu, vm_ram=args.ram, vm_disk_size=args.hdd, vc_dc=args.datacenter, vm_destination2=destination2, vc_host=args.vcenter, ip=args.ip, debug=args.debug, expire_vm_date=args.exp, vm_destination=destination)
    #except:
    #   print("!!! Ошибка при выделении IP адреса \n", sys.exc_info())
    #   quit()

    print ("### Edit nodes to: ["+str(args.desc)+" "+str(args.exp)+"]")
    try:
       print (notes_write_vm(args.vcenter, vc_user, vc_pass, ip, args.desc, args.exp))
    except:
       print ("!!! ERROR: notes_write_vm: ",sys.exc_info())
       quit()

    print ("### Move VM to: ["+args.folder+"]")
    try:
       move_vm_to_folder(args.vcenter, ip, args.folder, args.cluster, args.datacenter)
    except:
       print ("!!! ERROR: move_vm_to_folder: ",sys.exc_info())
       #quit()


    if args.exp is not None:
       try:
          print(args.exp)
          print ("### Create sheduled power off "+args.vmname+" in " + args.exp)
          scheduledTask_poweroff(hostname=args.vmname, expire_vm_date=args.exp, vc_host=args.vcenter)
       except:
          print ("!!! ERROR: scheduledTask_poweroff: ", sys.exc_info())
          #quit()
    else:
       print("!!! You did not enter the VM lifetime. PASS.")


    #if args.ReSIZE and re.match(r'linux', template(vm_template)): # resize HDD
    if re.search(r'centos', args.template.lower()) or re.search(r'ubuntu', args.template.lower()) or re.search(r'lin', args.template.lower() ): # resize HDD
       #answ = input('Run disk resize on '+ ip +' [Y/N]?')
       #if answ == 'Y':
       os.system('ssh root@'+ip+'" bash -s" < ./tools/resize-root.sh')

    report()
    if re.search(r'centos', args.template.lower()) or re.search(r'ubuntu', args.template.lower()) or re.search(r'lin', args.template.lower()
):
       print("NAME: " + args.vmname+"\nIP: " + ip + "\nSSH: user / qwerty$4")
    else:
       print("NAME: " + args.vmname+"\nIP: " + ip + "\nRDP: admin / qwerty$4")
  
