#!/usr/bin/env python3

import sys
import argparse
from ipam_create_ip import ipam_create_ip

parser = argparse.ArgumentParser()

parser.add_argument('--net',      dest='net',     help="Network (ex. --net 192.168.0.0/24")
parser.add_argument('--vmname',   dest='vmname',  help="VM name (ex. --vmname vm-01)")
parser.add_argument('--datastor', dest='ds',      help="Datastore")
parser.add_argument('--folde',    dest='folder',  help='VM Folder in vCenter')

parser.add_argument('--dsize',    dest='dsize',   help='Disk Size')
parser.add_argument('--msize',    dest='msize',   help='RAM Size')
parser.add_argument('--cpu',      dest='cpu',     help='CPU Count')
parser.add_argument('--desc',     dest='desc',    help='Description')
parser.add_argument('--onlyip',   dest='onlyip',  help='Only IP allocation (ex. --onlyip yes', default='No')

#parser.add_argument('--', dest='',      help='')

args = parser.parse_args()


if args.vmname is None:
    print('The --vmname can not be empty');
    quit();

if args.desc is None:
    print('The --desc can not be empty');
    quit();

if args.net is None:
    print('The --net can not be empty');
    quit();

if args.onlyip is not 'No':
    ipam_create_ip(hostname=args.vmname, infraname=args.desc, cidr=args.net);
#elif:
