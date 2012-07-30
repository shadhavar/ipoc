#!/usr/bin/python
import time
import zmq
import os
import string
import json
import platform

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5000")

log = {}

def start():
    if os.path.exists('test'):
        try:
            f = open('test')
        except:
            print 'Error opening file'
        old = json.loads(f.readline())
        for entry in log:
            #are the files changed?
            if log[entry]['partition'] == old[entry]['partition'] and log[entry]['inode'] == old[entry]['inode']:
                #if updates already have happened since last check, update offset so everything will be loaded
                if log[entry]['offset'] != old[entry]['offset']:
                    log[entry]['offset'] = old[entry]['offset']
            else:
                    log[entry]['offset'] = 0


def whatlogs():
    if os.path.exists('logfiles'):
        logs = list()
        try:
            f = open('logfiles', 'r')
        except:
            print 'bar'
        for row in f.readlines():
            rowSplit = string.split(row, ' ', 2)
            logs.append(rowSplit)
        return logs

def findlogs(pointer, offset=-1):
    if offset != -1:
        pointer[1].seek(offset)
    for line in pointer[1].readlines():
        yield (line)
    else:
        time.sleep(0.1)
    log[pointer[0]]['offset'] = pointer[1].tell()


def watch():
    logs = whatlogs()
    pointers = logs
    i=0

    for logfile in logs:
        filename = logfile[1][:-1]
        pointers[i][1] = open(filename, 'r')
        st = os.stat(filename)
        i+=1
        log[logfile[0]] = {'inode': st.st_ino, 'partition': st.st_dev, 'offset': st.st_size}

    start()

    while True:
        for pointer in pointers:
            for line in findlogs(pointer, int(log[pointer[0]]['offset'])):
                yield (pointer[0], line)

try:
    host = platform.uname()[1]
    for a, b in watch():
        msg = "{0} | {1} | {2}".format(a, host, b[:-1])
        print "Send %s" % msg
        socket.send(msg)
        msg_in = socket.recv()
except KeyboardInterrupt:
    f = open('test', 'w')
    f.write(json.dumps(log))
    f.flush()
    f.close()
    print json.dumps(log)
