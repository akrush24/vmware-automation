import requests
import sys 
from passwd import user_api, pass_api

# EXAMPLE 
# python3 ipam_create_ip.py HOSTNAME DESCRIPTION PHPIPAM_SubnetID

hostname = sys.argv[1]
infraname= sys.argv[2]
subnet_id= sys.argv[3]

def ipam_create_ip(hostname, infraname, subnet_id):
    token = requests.post('https://ipam.phoenixit.ru/api/apiclient/user/', auth=(user_api, pass_api)).json()['data']['token']
    headers = {'token':token}
    baseurl = "https://ipam.phoenixit.ru/api/apiclient/addresses/first_free/"+subnet_id
    ip = requests.get(url=baseurl, headers=headers).json()['data']
    create_url = "https://ipam.phoenixit.ru/api/apiclient/addresses/?subnetId="+subnet_id+"&ip="+ip+"&hostname="+hostname+"&description="+infraname
    create = requests.post(url = create_url , headers=headers).json()['success']
    if create == True:
        print("Create ip address:"+ ip)

if hostname and infraname and subnet_id:
    ipam_create_ip(hostname=hostname, infraname=infraname, subnet_id=subnet_id)
