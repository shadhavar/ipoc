#!/usr/bin/python
import datetime
import zmq
import string



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


while True:
    msg = socket.recv()
    message = string.split(msg, '|', 1)
    if str(message[0]).strip() == "security":
        time, hostname, message = getDetails(message[1])
        message = message[message.index(' ')+1:]
        process, pid, message = getProcessInfo(message)
        print time
        print hostname
        print message
        print process
        print pid
    elif str(message[0]).strip() == "messages":
        time, hostname, message = getDetails(message[1])
        message = message[message.index(' ')+1:]
        process, pid, message = getProcessInfo(message)
        print time
        print hostname
        print message
        print process
        print pid
    socket.send(msg)