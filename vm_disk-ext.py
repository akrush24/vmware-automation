import  paramiko
import time
import socket
import os

ip = '192.168.222.70'
files = ['disk-size.part1.sh', 'disk-size.part2.sh']
time_start = int(time.time())

def time_out(time_start):
    time_curent = int(time.time()) - time_start
    if time_curent > 50:
        return True
    else:
        return False

def connect_ssh(ip, file):
    local_path = '/home/nokhrimenko/'
    remote_images_path = '/root/'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())
    file_local = local_path + file
    file_remote = remote_images_path + file
    print(file_local + '>>>' + file_remote)
    ssh.connect(hostname=ip, port=22, username='root', key_filename='/home/nokhrimenko/.ssh/id_dsa')
    sftp = ssh.open_sftp()
    sftp.put(file_local, file_remote)
    ssh.exec_command("chmod +x" " " + str(file_remote))
    stdin, stdout, stderr = ssh.exec_command(file_remote)
    print("stderr: ", stderr.readlines())
    print("pwd: ", stdout.readlines())
    sftp.close()
    ssh.close()
    return True

def check_ssh_port(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, 22))
    if result == 0:
        return True
    else:
        return False

def checktime():
    close_check = 100
    while (time_out(time_start) == False):
        if check_ssh_port(ip) == True:
            return True
            break
        else:
            continue

def start_main():
    if check_ssh_port(ip) == True:
        connect_ssh(ip, file=files[0])
        time.sleep(10)
        if checktime() == True:
            connect_ssh(ip, file=files[1])
        else:
            print('Connect timeout')


start_main()







