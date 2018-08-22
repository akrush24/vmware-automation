import  paramiko
import time
import socket
import os
ip = '192.168.222.70'
def disk_ext(ip):
    files = ['disk-size.part1.sh', 'disk-size.part2.sh']
    remote_images_path = '/root/'
    local_path = '/home/nokhrimenko/'
    username = 'root'
    port = 22
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())

    for file in files:
        file_local = local_path + file
        file_remote = remote_images_path + file
        print (file_local + '>>>' + file_remote)
        ssh.connect(hostname=ip, port=port, username=username, key_filename='/home/nokhrimenko/.ssh/id_dsa')
        sftp = ssh.open_sftp()
        sftp.put(file_local, file_remote)
        ssh.exec_command("chmod +x" " " + str(file_remote))
        stdin, stdout, stderr = ssh.exec_command(file_remote)
        print ("stderr: ", stderr.readlines())
        print ("pwd: ", stdout.readlines())
        time.sleep(50)
    sftp.close()
    ssh.close()

disk_ext(ip = ip)


