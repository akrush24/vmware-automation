import time
import socket



ip = '192.168.222.70'

time_start = int(time.time())

def time_out(time_start):
    time_curent = int(time.time()) - time_start
    if time_curent > 10:
        return True
    else:
        return False





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
        if check_ssh_port(ip = ip) == True:
            return True
            break
        else:
            continue



checktime()




