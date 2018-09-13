#!/usr/bin/env python3

import sys
import argparse
#from ipam_create_ip import ipam_create_ip
from cvm import *
from passwd import user_api, pass_api, vc_user, vc_pass
version = '0.0.1'

parser = argparse.ArgumentParser()

parser.add_argument('--net', '-l',  dest='net',     help="Network (ex. --net 192.168.0.0/24). Auto assign IP addres from IPAM", required=True)
parser.add_argument('--ip', dest='ip', help='IP Address. If IP exist "--net" not required')
parser.add_argument('--vmname', '-n',   dest='vmname',  help="VM name (ex. --vmname vm-01)", required=True)
parser.add_argument('--datastor', '-ds', dest='ds',      help="Datastore name")
parser.add_argument('--folde', dest='folder',  help='VM Folder in vCenter')
parser.add_argument('--datacenter', '-dc', dest='datacenter',  help='vSphere Datacenter name')
parser.add_argument('--cluster', '-cl', dest='cluster',  help='vSphere Cluster')

parser.add_argument('--dsize', '-hdd', dest='dsize',   help='Disk Size')
parser.add_argument('--msize', '-m', dest='mem',   help='RAM Size')
parser.add_argument('--cpu', '-c', dest='cpu',     help='CPU Count')
parser.add_argument('--desc', '-d', dest='desc',    help='Description', required=True)
parser.add_argument('--template', '-tm', dest='template',    help='VM Template')

parser.add_argument('--onlyip',dest='onlyip',  help='Only IP allocation (ex. --onlyip yes)', default='No')

parser.add_argument('--version', '-V', action='version', version='Version: '+version)

parser.add_argument('--vcenter', dest='vcenter', help='vCenter URL')
parser.add_argument('--debug', dest='debug',  help='debug mode')

#parser.add_argument('--', dest='',      help='')

args = parser.parse_args()

#if args.folder is None and args.onlyip is not 'yes':
#    print("Please enter Folder name");
#    quit()

#if args.template is None and args.onlyip is not 'yes':
#    print("Please enter VM Template");
#    quit()

if args.onlyip is not 'No':
    ip = ipam_create_ip(hostname=args.vmname, infraname=args.desc, cidr=args.net);
    print ("### NEW IPAM IP is: ["+ip+"]")
else:
    main(hostname=args.vmname, infraname=args.desc, cidr=args.net, folder_vm=args.folder,
         vm_template=args.template, vc_storage=args.ds, vm_cpu=args.cpu, vm_ram=args.mem,
         vm_disk_size=args.dsize, vc_dc=args.datacenter, vc_cluster=args.cluster, vc_host=args.vcenter, 
         ip=args.ip, debug=args.debug)

#
# main (hostname='host889'! , infraname='INFRA8888'! , cidr='192.168.222.0/24! ', vc_host='vc-linx.srv.local',
#       vc_user='nokhrimenko@phoenixit.ru', vc_pass='NikolonsO345831', vc_dc='Datacenter-Linx', vc_cluster='linx-cluster01',
# vc_storage='27_localstore_r10'! , vm_template='template_centos7.3!'! , vm_cpu='1!', vm_ram='2048!', vm_disk_size='30!',
#       folder_vm = 'test'! )
