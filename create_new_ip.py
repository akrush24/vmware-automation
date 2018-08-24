#!/usr/bin/python3
from ipam_create_ip import ipam_create_ip
import sys
from p import *

hostname = sys.argv[1]
infraname= sys.argv[2]
subnet_id= sys.argv[3]

ipam_create_ip(hostname=hostname, infraname=infraname, subnet_id=subnet_id)

