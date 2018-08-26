import paramiko
p = paramiko.SSHClient()
cred = open('esx.csv', 'r')
for i in cred.readlines():
    line=i.strip()
    ls = line.split(",")
    print (ls)

#['192.168.1.10', 'root', 'password']
#['192.168.1.10', 'root', 'password']
    p.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    p.connect("%s"%ls[0], port=22, username= "%s"%ls[1], password="%s"%ls[2])
    stdin, stdout, stderr = p.exec_command("passwd root")
    opt = stdout.readlines()
    opt = "".join(opt)
    print(opt)
    temp = open("%s.txt" % ls[0], "w")
    temp.write(opt)
    temp.close()
cred.close()