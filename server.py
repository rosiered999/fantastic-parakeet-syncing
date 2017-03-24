'''    filetype = p3.communicate()[0]
    print 'filetype', filetype
    prefix = ""
    if(filetype=='-'):
        prefix = 'file'
    elif(filetype == 'd'):
        prefix = 'dir'
    elif(filetype == 'c'):
        prefix = 'char spl file'
    elif(filetype == 'b'):
        prefix = 'block spl file'
    elif(filetype == 'l'):
        prefix = 'symlink'
    elif(filetype == 'p'):
        prefix = 'named pipe'
    elif(filetype == 's'):
        prefix = 'socket'''
import commands
import socket
import sys
import os
import subprocess
import hashlib
import re
import time

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
HOST = 'localhost'
PORT = int(sys.argv[1])

try:
    sou = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Server created'
except socket.error, msg:
    print 'Failed, error code ' + str(msg[0]) + 'message'
    sys.exit()

try:
    sou.bind((HOST,PORT))
except socket.error, msg:
    print 'Failed, error code ' + str(msg[0]) + 'message'
    sys.exit()

print 'Socket bind done'

sou.listen(1)
print 'Server listening'

while(1):
    conn,addr = sou.accept()
    split_cmd = []
#    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    cmd = conn.recv(1024)
    print 'client  - %s' %(cmd)
    split_cmd = cmd.split(' ')
    #print 'split_cmd', split_cmd
    if(split_cmd[0]=='quit'):
        break
    elif(split_cmd[0]=='sync'):
        sync_cmd = cmd[5:]
        #print sync_cmd
        first = ['ls', '-a', '-l']
        second = ['awk', 'NR > 3 {print $9 " " $1 " " $5 " " $6 " " $7 " " $8}']
    #        third = ['awk', '{print substr($1,1,1)}']
        p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        #print output
        split_sync_cmd = sync_cmd.split('\n')
        split_output = output.split('\n')
        print 'split_sync_cmd ', split_sync_cmd
        print 'split_output ', split_output
        
        not_synced = []

        for item in split_output:
            d1 = item.split(' ')
            for nextitem in split_sync_cmd:
                d2 = nextitem.split(' ')
                if d1[0] not in d2 and not d1[0]=='':
                    not_synced.append(item)
                    print 'appending ', item
        
        for item1 in split_output:
            d1 = item1.split(' ')
            print item1
            for item2 in split_sync_cmd:
                print item2
                print type(item2)
                d2 = item2.split(' ')
                if item2.startswith(d1[0]) and not d1[0]=='' and not d2[0]=='': #and months.index(d1[3])>months.index(d2[3]) or int(d1[4])>int(d2[4]) or d1[5]>d2[5]:
                    not_synced.append(item1)
                    print 'appending ', item1

        print 'split_output', split_output
        print 'split_sync_cmd', split_sync_cmd

        not_synced = list(set(not_synced))

        print 'not_synced', not_synced

        for f in not_synced:
            pre = f.split(' ')
         #   print pre[0]
          #  print 'send pre[0]'
            filename = pre[0]
            fileperm = pre[1]
            conn.send('filename'+filename+'$$$EOF$$$')
            conn.send('fileperm'+fileperm+'$$$EOF$$$')
            f = open(filename, 'rb')
            l = f.read(1024)
           # print l
            while(l):
                conn.send(l)
            #    print('sent ', repr(l))
                l = f.read(1024)
            conn.send('$$$EOF$$$')
            f.close()
            #print 'done sending'
            conn.send('end$$$EOF$$$')
        conn.send('$#ENDENDEND#$')

    elif(len(split_cmd) > 1 and split_cmd[0]=='download' and split_cmd[1]=='TCP'):
        print 'receiving data from client'
        filename = split_cmd[2]
        print 'filename', filename
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(filename, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        H = hasher.hexdigest()
        print H
        first = ['ls', filename, '-a', '-l']
        second = ['awk', '{print $5 " " $6 " " $7 " " $8 " " $9}']
        p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        hsh = H + " "+ output
        conn.send("hash" + " " + hsh)
        conn.send('$$$EOF$$$')

        f = open(filename, 'rb')
        l = f.read(1024)
        print l
        while(l):
            conn.send(l)
            print('sent ', repr(l))
            l = f.read(1024)
        conn.send('$$$EOF$$$')
        f.close()
        print 'done sending'
        conn.send('thanks')

    #    conn.send('thanks_final')
    elif(len(split_cmd) > 1 and split_cmd[0]=='download' and split_cmd[1]=='UDP'):
        port = 60001
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = 'localhost'

        s.bind((host, port))

        filename = 'testdata'
        print 'Server listening....'
        data = '0'
        while not data=='thanks':
            data,addr = s.recvfrom(1024)
            print data
            print('Server received', repr(data))

            f = open(filename,'rb')
            l = f.read(1024)
            print l
            while (l):
               s.sendto(l,addr)
               print('Sent ',repr(l))
               l = f.read(1024)
            s.sendto('$$$EOF$$$', addr)
        f.close()

        print('Done sending')
        s.sendto('Thank you for connecting',addr)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        continue
    elif(split_cmd[0] =='shortlist'):
    #    print 'split_cmd', split_cmd
        time1 = split_cmd[1] + split_cmd[2]
        time2 = split_cmd[3] + split_cmd[4]
    #    print 'time1 ', time1, 'time2', time2
        command = ["find", ".","-newermt", time1, "!", time2]
        proc = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
        output = proc.communicate()[0]

        result = output.split('\n')
        first1 = ['ls']
        first2 = ['-a', '-l']
        first = first1 + result + first2
#        print 'first', first
        second = ['awk', 'NR > 1 {print substr($1,1,1) " " $9 " " $5 " " $6 " " $7 " " $8}']
        p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
    #    print output
        conn.send(output)
    elif(split_cmd[0] == 'regex'):
        reg = split_cmd[1]
        cwd = os.getcwd()
        dirs = os.listdir(cwd)
        regexed_dir = []
        for d in dirs:
            if re.search(reg, d):
                regexed_dir.append(d)

        first1 = ['ls']
        first2 = ['-a', '-l']
        first = first1 + regexed_dir + first2
#        print 'first', first
        second = ['awk', '{print substr($1,1,1) " " $9 " " $5 " " $6 " " $7 " " $8}']
        p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        print output
        conn.send(output)
    elif(split_cmd[0]=='longlist'):
        first = ['ls', '-a', '-l']
        second = ['awk', 'NR > 1 {print substr($1,1,1) " " $9 " " $5 " " $6 " " $7 " " $8}']
#        third = ['awk', '{print substr($1,1,1)}']
        p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        conn.send(output)
    elif(split_cmd[0]=='verify'):
        filename = split_cmd[1]
        print 'filename', filename
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(filename, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        H = hasher.hexdigest()
        print H
        first = ['ls', filename, '-a', '-l']
        second = ['awk', '{print $6 " " $7 " " $8}']
        p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        hsh = H + " "+ output
        conn.send(hsh)
    elif(split_cmd[0]=='checkall'):
        cwd = os.getcwd()
        dirs = (fil for fil in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, fil)))
        print dirs
        H = []
        hash_send = ""
        for filename in dirs:
            BLOCKSIZE = 65536
            hasher = hashlib.md5()
            with open(filename, 'rb') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
            H.append(hasher.hexdigest())
            first = ['ls', filename, '-a', '-l']
            second = ['awk', '{print $9 " " $6 " " $7 " " $8}']
            p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
            p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
            output = p2.communicate()[0]
            hsh = H[-1] + " "+ output
            print hsh
            hash_send = " " + hash_send +" "+ hsh
        conn.send(hash_send)
    elif(split_cmd[0]=='synchash'):
        sync_cmd = cmd[8:]
        print sync_cmd
        first = ['find', '.', '!' ,'-type', 'd', '-print0'] 
        second = ['xargs', '-0', 'md5sum']
        p1 = subprocess.Popen(first, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(second, stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        print output

        output1 = output.split('\n')
        sync_cmd1 = sync_cmd.split('\n')

        #lis = output1.sort() + sync_cmd1.sort()
        #lis = set(lis)
        not_synced = output1

        for f in not_synced:
            pre = f.split(' ')
            print pre
         #   print pre[0]
          #  print 'send pre[0]'
            filename = pre[1]
            filehash = pre[0]
            conn.send('filename'+filename+'$$$EOF$$$')
            conn.send('filehash'+filehash+'$$$EOF$$$')
            f = open(filename, 'rb')
            l = f.read(1024)
           # print l
            while(l):
                conn.send(l)
            #    print('sent ', repr(l))
                l = f.read(1024)
            conn.send('$$$EOF$$$')
            f.close()
            #print 'done sending'
            conn.send('end$$$EOF$$$')
        conn.send('$#ENDENDEND#$')



sou.close()
print 'Server closed'
