import requests
import sys
from passwd import user_api, pass_api

# EXAMPLE
# python3 ipam_create_ip.py HOSTNAME DESCRIPTION PHPIPAM_SubnetID

hostname = sys.argv[1]
infraname= sys.argv[2]
cidr = sys.argv[3]

def ipam_create_ip(hostname, infraname, cidr):
    token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=(user_api, pass_api)).json()['data']['token']
    headers = {'token':token}
    cidr_url = 'http://ipam.phoenixit.ru/api/apiclient/subnets/cidr/' + cidr
    get_sudnet_id = requests.get(url=cidr_url, headers=headers).json()['data'][0]['id']
    get_ip_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+get_sudnet_id
    ip = requests.get(url=get_ip_url, headers=headers).json()['data']
    create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+get_sudnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
    create = requests.post(url = create_url , headers=headers).json()['success']
    if create == True:
        print("Create ip address:"+ ip)

if hostname and infraname and cidr:
    ipam_create_ip(hostname=hostname, infraname=infraname, cidr=cidr)
