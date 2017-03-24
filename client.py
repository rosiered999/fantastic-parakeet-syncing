import socket
import sys
import os
import hashlib
import re
import time
import subprocess
import threading

HOST = 'localhost'
PORT = int(sys.argv[1])

def serverdTCP(cmd_str):
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    souket.send(cmd_str[0]+" "+cmd_str[1]+" "+cmd_str[2])
    with open('received_file', 'wb') as f:
        print 'file opened'
        x = ['a']
        while not x[-1] == 'thanks':
            print('receiving data...')
            data = souket.recv(1024)
        #    print 'data', data
            # write data to a file
            x = data.split('$$$EOF$$$')
            if not x[0][0:4]=='hash' and not data=='thanks':
                f.write(x[0])
            else:
                print x[0]
        f.close()
    #print x
    #print data
    print('Successfully get the file')
    #if(x[-1]=='thanks_final'):
    #    souket.close()

def serverdUDP(cmd_str):
    print 'UDP yayayayayayayaya'
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    souket.send(cmd_str[0]+" "+cmd_str[1]+" "+cmd_str[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = 'localhost'
    port = 60001
    addr = (host,port)
    s.connect((host, port))
    s.sendto("Hello server!",addr)

    with open('received_file', 'wb') as f:
        print 'file opened'
        x = ['0']
        while not x[-1]=='':
            print('receiving data...')
            data,addr = s.recvfrom(1024)
            #print 'data', data
            x = data.split('$$$EOF$$$')
            #print 'x ',x
            # write data to a file
            f.write(x[0])

    f.close()
    print('Successfully get the file')
    s.sendto("thanks",addr)
    data,addr = s.recvfrom(1024)
    #print data
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    print('connection closed')


def servercheckall(cmd_str):
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    string = ""
    string = cmd_str[1]
    souket.send(string)
    hsh = souket.recv(1024)
    print hsh,
    souket.close()
    return

def servershortlist(cmd_str):
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    string = ""
    string = cmd_str[1] + " " + cmd_str[2]+ " " + cmd_str[3]+ " "+cmd_str[4]+ " " + cmd_str[5]
    souket.send(string)
    fil = souket.recv(1024)
    print fil

    souket.close()
    return

def serverlonglist(cmd_str):
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    souket.send(cmd_str[1])
    fil = souket.recv(1024)
    fileList = fil.split(' ')
    for f in fileList[:-1]:
        print f,
    print '\n'
    souket.close()
    return

def serververify(cmd_str):
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    string = ""
    string = cmd_str[1] + " " + cmd_str[2]
    souket.send(string)
    hsh = souket.recv(1024)
    print hsh,
    souket.close()
    return

def serverregex(cmd_str):
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    string = ""
    string = cmd_str[1] + " " + cmd_str[2]
    souket.send(string)
    reg = souket.recv(1024)
    print reg,
    souket.close()
    return

def longlist(cmd_str):
        serverlonglist(cmd_str)

def shortlist(cmd_str):
        servershortlist(cmd_str)

def regex(cmd_str):
        serverregex(cmd_str)

def verify(cmd_str):
        serververify(cmd_str)

def checkall(cmd_str):
        servercheckall(cmd_str)

def dTCP(cmd_str):
        serverdTCP(cmd_str)

def dUDP(cmd_str):
        serverdUDP(cmd_str)

def quit():
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    souket.send(cmd)
    souket.close()
    return

def sync():
    #print '\nsync'
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    first = ['ls', '-a', '-l']
    second = ['awk', 'NR > 3 {print $9 " " $1 " " $5 " " $6 " " $7 " " $8}']
#        third = ['awk', '{print substr($1,1,1)}']
    p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
    output = p2.communicate()[0]
    souket.send('sync ' + output)
    while True:
        d = souket.recv(1024)
        x = d.split('$$$EOF$$$')
        print 'x',x
        for y in x:
            print 'y', y
            if y.startswith('filename'):
                filename = y[8:]
                print 'filename',filename
                f = open(filename, 'wb+')
            elif y.startswith('fileperm'):
                print 'fileperm ',y
                perm1 = y[9:12]
                som = 0
                for i in perm1:
                    if i=='-':
                        party = 0o0
                    elif i=='r':
                        party=0o4
                    elif i=='w':
                        party=0o2
                    elif i=='x':
                        party=0o1
                    som = som + 8*party
        #        print som/8
                perm2 = y[12:15]
                som1 = 0
                for i in perm2:
                    if i=='-':
                        party = 0o0
                    elif i=='r':
                        party=0o4
                    elif i=='w':
                        party=0o2
                    elif i=='x':
                        party=0o1
                    som1 = som1 + 8*party
         #       print som1/8
                perm3 = y[15:18]
                som2 = 0
                for i in perm3:
                    if i=='-':
                        party = 0o0
                    elif i=='r':
                        party=0o4
                    elif i=='w':
                        party=0o2
                    elif i=='x':
                        party=0o1
                    som2 = som2 + 8*party
          #      print som2/8
           #     print som/8,som1/8,som2/8
                mode = som*8+som1+som2/8
            #    print mode
             #   print 'changing the perms'
                os.chmod(filename, mode)
            elif y == '$#ENDENDEND#$':
              #  print('Successfully get the file')
                souket.close()
                return
            elif y == 'end':
                f.close()
                os.chmod(filename, mode)
            elif not y=='':
                f.write(y)
    #print x
    #print data
    #threading.Timer(5.0, sync).start()

def sync_with_hash():
    #print '\nsync'
    souket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    souket.connect((HOST,PORT))
    first = ['find', '.', '!' ,'-type', 'd', '-print0'] 
    second = ['xargs', '-0', 'md5sum']
    p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
    output = p2.communicate()[0]
    souket.send('synchash ' + output)
    print output
    flag = 0
    while True:
        d = souket.recv(1024)
        x = d.split('$$$EOF$$$')
        print 'x',x
        for y in x:
            print 'y', y
            if y.startswith('filename'):
                filename = y[8:]
                print 'filename',filename
                flag = 0
                if not filename=='':
                    flag = 1
                    f = open(filename, 'wb+')
            elif y == '$#ENDENDEND#$':
              #  print('Successfully get the file')
                souket.close()
                return
            elif y == 'end':
                f.close()
                os.chmod(filename, mode)
            elif not y=='' and not flag==1:
                print 'writing to file',y
                f.write(y)
    #print x
    #print data
    #threading.Timer(5.0, sync).start()

def index(cmd_str):
    if(cmd_str[1]=='longlist'):
        longlist(cmd_str)
    elif(cmd_str[1]=='shortlist'):
        shortlist(cmd_str)
    elif(cmd_str[1]=='regex'):
        regex(cmd_str)

def hsh(cmd_str):
    if(cmd_str[1]=='verify'):
        verify(cmd_str)
    elif(cmd_str[1]=='checkall'):
        checkall(cmd_str)

def dwnload(cmd_str):
    if(cmd_str[1]=='TCP'):
        dTCP(cmd_str)
    elif(cmd_str[1]=='UDP'):
        dUDP(cmd_str)

history = []
starttime = time.time()
while(1):
    #print 'sync'
    sys.stdout.write('client$ ')
    #print starttime
    #print time.time()
    cmd = sys.stdin.readline().strip()
    history.append(cmd)
    if(cmd == 'quit'):
        quit()
        break
    if(cmd == 'sync'):
        sync()
    elif(cmd=='synchash'):
        sync_with_hash()
    elif(cmd == 'info'):
        print '\n'
        print 'index longlist for longlist of server files'
        print 'index shortlist time1 time2 for shortlist of server files'
        print 'index regex filename for list using regex'
        print 'hash verify filename'
        print 'hash checkall'
        print 'info'
    else:
        cmd_str = cmd.split(' ')
        if(cmd_str[0] == 'index'):
            index(cmd_str)
        elif(cmd_str[0] == 'hash'):
            hsh(cmd_str)
        elif(cmd_str[0] == 'download'):
            dwnload(cmd_str)
        elif(cmd_str[0]=='upload'):
            upload(cmd_str)
        elif(cmd_str[0] == 'history'):
            for i in history:
                print i