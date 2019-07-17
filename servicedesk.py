#!/usr/bin/env python3.4
import requests, re
from bs4 import BeautifulSoup
from passwd import sd_user, sd_pass

def get_parameters_vm(taskid):
    loginurl = 'https://servicedesk.phoenixit.ru'
    logindata = {'autologin' : '1', 'login' : sd_user, 'password' : sd_pass, 'enter' : 'submit'}
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0', 'Content-type' : 'application/x-www-form-urlencoded'}

    session=requests.session()
    login=session.post(loginurl, params=logindata, headers=headers)
    url = loginurl + '/Task/View/' + taskid
    soup = BeautifulSoup(session.get(url).content, 'html.parser')

    d = {}
    d.update({'hostname':soup.find('input', id='field1041').get('value')})
    d.update({'hdd': soup.find('select', id='field1015').find('option', selected="true").text})
    d.update({'cpu': soup.find('select', id='field1017').find('option', selected="true").text})
    d.update({'ram': soup.find('select', id='field1014').find('option', selected="true").text})
    d.update({'os': soup.find('select', id='field1016').find('option', selected="true").text})
    d.update({'exp': re.match( "\d\d.\d\d.20", soup.find('input', id='field1022').get('value') ).group(0)})
    d.update({'foldervm': soup.find('input', id='field1020').get('value')})
    d.update({'status': soup.find('select', class_='px200 required').find('option', selected="selected").text})
    d.update({'taskname': soup.find('input', id='name').get('value')})
    d.update({'practica': soup.find('input', id='field1024').get('value')})
    d.update({'owner': soup.find('ul', class_='users').find('a', class_='nounderline').text})
    return d

#print ( get_parameters_vm( "23091" ) )
