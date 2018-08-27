#!/usr/bin/env python3

import sys
import argparse
from ipam_create_ip import ipam_create_ip
from createvm import *

version = '0.0.1'

parser = argparse.ArgumentParser()

parser.add_argument('--net', '-l',  dest='net',     help="Network (ex. --net 192.168.0.0/24", required=True)
parser.add_argument('--vmname', '-n',   dest='vmname',  help="VM name (ex. --vmname vm-01)", required=True)
parser.add_argument('--datastor', '-ds', dest='ds',      help="Datastore")
parser.add_argument('--folde', dest='folder',  help='VM Folder in vCenter')
parser.add_argument('--datacenter', '-dc', dest='datacenter',  help='vSphere Datacenter')
parser.add_argument('--cluster', '-cl', dest='cluster',  help='vSphere Cluster')

parser.add_argument('--dsize', '-hdd', dest='dsize',   help='Disk Size')
parser.add_argument('--msize', '-m', dest='mem',   help='RAM Size')
parser.add_argument('--cpu', '-c', dest='cpu',     help='CPU Count')
parser.add_argument('--desc', '-d', dest='desc',    help='Description', required=True)
parser.add_argument('--template', '-tm', dest='template',    help='VM Template')

parser.add_argument('--onlyip',dest='onlyip',  help='Only IP allocation (ex. --onlyip yes', default='No')

parser.add_argument('--version', '-V', action='version', version='Version: '+version)

#parser.add_argument('--', dest='',      help='')

args = parser.parse_args()

if args.folder is None:
    print("Please enter Folder name");
    quit()

if args.template is None:
    print("Please enter VM Template");
    quit()

if args.onlyip is not 'No':
    ipam_create_ip(hostname=args.vmname, infraname=args.desc, cidr=args.net);
else:
    main(hostname=args.vmname, infraname=args.desc, cidr=args.net, folder=args.folder, vm_template=args.template, vc_storage=args.ds, vm_cpu=args.cpu, vm_ram=args.mem, vm_disk_size=args.dsize, vc_dc=args.datacenter, vc_cluster=args.cluster)
