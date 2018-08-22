import  paramiko
import time
files = ['disk-size.part1.sh', 'disk-size.part2.sh']
ip = '192.168.222.70'
def disk_ext():
    time_start = int(time.time())
    while True:
     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     result = sock.connect_ex((ip, 22))
     if result == 0:
        print ('Open to 22')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        paramiko.util.log_to_file('/tmp/paramiko.log')
        paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        file_local = '/home/nokhrimenko/' + files
        file_remote = '/root/' + files
        ssh.connect(hostname=ip, port=22, username='root', key_filename='/home/nokhrimenko/.ssh/id_dsa')
        sftp = ssh.open_sftp()
        sftp.put(file_local, file_remote)
        ssh.exec_command("chmod +x" " " + str(file_remote))
        stdin, stdout, stderr = ssh.exec_command(file_remote)
        sftp.close()
        ssh.close()
        break
     else:
        time_curent = int(time.time())- time_start

        if time_curent > 100:
            print('ssh server not start')
            break
        else:
            continue

for files in files:
    disk_ext(ip, files )
