import sys
import argparse

#hostname = sys.argv[1]
#description = sys.argv[2]
#subnet_id = sys.argv[3]
#folder = sys.argv[4]

parser = argparse.ArgumentParser()

parser.add_argument('--net',      dest='net',     help="Network (ex. 192.168.0.0/24")
parser.add_argument('--vmname',   dest='vmname',  help="VM name (ex. vm-01)")
parser.add_argument('--datastor', dest='ds',      help="Datastore")
parser.add_argument('--folde',    dest='folder',  help='VM Folder in vCenter')

parser.add_argument('--dsize',    dest='dsize',   help='Disk Size')
parser.add_argument('--msize',    dest='msize',   help='RAM Size')
parser.add_argument('--cpu',      dest='cpu',     help='CPU Count')
parser.add_argument('--desc',     dest='desc',    help='Description')
#parser.add_argument('--', dest='',      help='')

args = parser.parse_args()

print (args)
