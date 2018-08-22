
import  paramiko
import time
import socket
import os

#files = ['disk-size.part1.sh', 'disk-size.part2.sh']
file = 'disk-size.part1.sh'
ip = '192.168.222.70'

def disk_ext(ip, files):
    time_start = int(time.time())
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, 22))
        if result == 0:
            print ('Open to 22')
            try:
                ssh.connect(hostname=ip, port=22, username='root', key_filename='/home/nokhrimenko/.ssh/id_dsa')
#               stdin, stdout, stderr = ssh.exec_command('ls -l')
#               data = stdout.read() + stderr.read()
#               print(data)
                time.sleep(3)
                file_local = '/home/nokhrimenko/' + files
                file_remote = '/root/' + files
                sftp = ssh.open_sftp()
                sftp.put(file_local, file_remote)
                sftp.close
                time.sleep(1)
                ssh.connect(hostname=ip, port=22, username='root', key_filename='/home/nokhrimenko/.ssh/id_dsa')
                ssh.exec_command("chmod +x" " " + str(file_remote))
                stdin, stdout, stderr = ssh.exec_command(file_remote)
     #          sftp.close
                ssh.close()
            except:
                print ('no connect')

            break
        else:
            time_curent = int(time.time())- time_start
            if time_curent > 100:
                print('ssh server not start')
                break
            else:
                continue

disk_ext(ip=ip, files=file)


