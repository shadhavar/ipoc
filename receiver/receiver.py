#!/usr/bin/python
import datetime
import zmq
import string
import re

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:5000")

def getTimestamp(offset, dirtyString):
    months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    timeString = dirtyString[int(offset)+2:int(offset)+16+2]
    hmsString = timeString[timeString.index(':')-2:]
    time = datetime.datetime(datetime.datetime.now().year,  int(months[timeString[0:3]]), int(timeString[4:6]), int(hmsString[0:2]), int(hmsString[3:5]), int(hmsString[6:8]))
    return (offset+16, time)

def getHostname(dirtyString):
    offset = int(dirtyString.index('|'))
    return (offset, dirtyString[0:offset].strip())

def getProcessInfo(line):
    totLenght = line.index(':')
    info = line[:totLenght]
    if info.find('[') == -1:
        processName = info
        pid = -1
    else:
        lenght = info.index('[')
        processName = info[:lenght]
        pid = info[lenght+1:-1]
    message = line[totLenght+2:]
    return (processName, pid, message)

def getDetails(dirtyString):
    offset, hostname = getHostname(str(dirtyString))
    offset, time = getTimestamp(offset, dirtyString)
    return time, hostname, dirtyString[offset+2:].strip()

def extractSecurity(message):
    warning = -1
    process = -1
    login = -1
    uid = -1
    euid = -1
    tty = -1
    ruser = -1
    rhost = -1
    rport = -1
    user = -1

    openSession = re.compile("pam_unix\((.*)\): session opened for user (.*) by (.*)\(uid=([0-9]+)\)").match(message)
    closeSession = re.compile("pam_unix\((.*)\): session closed for user (.*)").match(message)
    loginFail = re.compile("pam_unix\((.*)\): authentication failure; logname=(.*) uid=([0-9]+) euid=([0-9]+) tty=(.*) ruser=(.*) rhost=(.*)  user=(.*)").match(message)
    passFail = re.compile("password check failed for user \((.*)\)").match(message)
    remotePassFail = re.compile("Failed password for (.*) from (.*) port ([0-9]+) (.*)").match(message)
    if (openSession):
        warning = 0
        info = openSession.groups()
        process = info[0]
        login = info[1]
        uid = info[2]
    elif closeSession:
        warning = 0
        info = closeSession.groups()
        process = info[0]
        login = info[1]
    elif loginFail:
        warning = 1
        info = loginFail.groups()
        process = info[0]
        login = info[1]
        uid = info[2]
        euid = info[3]
        tty = info[4]
        ruser = info[5]
        rhost = info[6]
        user = info[7]
    elif passFail:
        warning = 1
        info = passFail.groups()
        login = info[0]
    elif remotePassFail:
        warning = 1
        info = remotePassFail.groups()
        login = info[0]
        rhost = info[1]
        rport = info[2]
        process = info[3]

    return (warning, process, login, uid, euid, tty, ruser, rhost, rport, user)

def switch(msg):
    message = string.split(msg, '|', 1)
    if str(message[0]).strip() == "security":
        time, hostname, message = getDetails(message[1])
        message = message[message.index(' ')+1:]
        process, pid, message = getProcessInfo(message)
        warning, process, login, uid, euid, tty, ruser, rhost, rport, user = extractSecurity(message)
        print warning
        print process
        print login
        print uid
        print euid
        print tty
        print ruser
        print rhost
        print rport
        print user

    elif str(message[0]).strip() == "messages":
        time, hostname, message = getDetails(message[1])
        message = message[message.index(' ')+1:]
        process, pid, message = getProcessInfo(message)

while True:
    msg = socket.recv()
    switch(msg)
    socket.send(msg)