#!/usr/bin/python3

import socket
import wx
import time
import threading
import re  
from wx.lib.pubsub import pub

milli_time = lambda: int(round(time.time() * 1000))
timeout = 1000

class RotorCom(threading.Thread):

    def __init__(self, host, port):
        self.cmdBuffer=[]
        self.Values={}
        self._stop_event = threading.Event()
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.socket.connect((host, port))
        except socket.error as e:
            print("Can't connect: ",e)
        finally:
            threading.Thread.__init__(self)
            self.start()

    def run(self):
        self.TestValues()
        # Run Worker Thread
        doUpdate = 0
        try:
            while (not self.stopped()):
                if (doUpdate==0):
                    self.socket.sendall(b"showStatus\r\n")
                    time.sleep(0.2)
                    #t_start = milli_time()
                    #t_end = t_start + timeout
                    line = ""
                    #while(milli_time()<t_end):
                    #while True:
                    data = self.socket.recv(4096)
                    for i in range(len(data)):
                        if (chr(data[i]) == '\n' or chr(data[i]) == '\r'):
                            if(line.startswith(r"[0KRotor")): 
                                self.ProcessStatusLine(line)
                            line=""
                        elif(data[i]!=27):
                            line+=chr(data[i])
                    doUpdate=2
                while (len(self.cmdBuffer) > 0):
                    print("Send: "+self.cmdBuffer[0])
                    self.socket.sendall( (self.cmdBuffer[0]+"\r\n").encode() )
                    del(self.cmdBuffer[0])
                time.sleep(0.1)
                doUpdate-=1
        except socket.error as e:
            print("Socket error: ",e)
        

    def TestValues(self):
        time.sleep(2)
        newValues = {}
        newValues["UpperPosition"] = 175.0
        newValues["LowerPosition"] = 85.0
        newValues["UpperSetpoint"] = 175.0
        newValues["LowerSetpoint"] = 85.0
        newValues["UpperSteps"] = 0
        newValues["LowerSteps"] = 0
        newValues["UpperReferenced"] = 1
        newValues["LowerReferenced"] = 1
        newValues["UpperActive"] = 0
        newValues["LowerActive"] = 0
        newValues["UpperCurrent"] = 0
        newValues["LowerCurrent"] = 0
        self.Values = newValues
        wx.CallAfter(pub.sendMessage,"update",msg = "") 


    def ProcessStatusLine(self,line):
        #print(line)
        if(not line.startswith("[0KRotor DOWN/UP:")): return
        sl = line.split('\t')
        if (len(sl) != 8): return
        x = re.search(r"Position: ([0-9\.]*)/([0-9\.]*) Degree", sl[1])
        newValues = {}
        newValues["UpperPosition"] = float(x.group(2))
        newValues["LowerPosition"] = float(x.group(1))

        x = re.search(r"TargetPosition: ([0-9\.nan]*)/([0-9\.nan]*) Degree", sl[7])
        newValues["UpperSetpoint"] = float(x.group(2))
        newValues["LowerSetpoint"] = float(x.group(1))

        x = re.search(r"Counter: ([0-9\-]*)/([0-9\-]*) Steps", sl[2])
        newValues["UpperSteps"] = int(x.group(2))
        newValues["LowerSteps"] = int(x.group(1))

        x = re.search(r"Referenced: ([0-9]*)/([0-9]*)", sl[3])
        newValues["UpperReferenced"] = int(x.group(2))
        newValues["LowerReferenced"] = int(x.group(1))

        x = re.search(r"MotorActive: ([0-9]*)/([0-9]*)", sl[4])
        newValues["UpperActive"] = int(x.group(2))
        newValues["LowerActive"] = int(x.group(1))

        x = re.search(r"MotorCurrent: ([0-9]*)/([0-9]*) mA", sl[5])
        newValues["UpperCurrent"] = int(x.group(2))
        newValues["LowerCurrent"] = int(x.group(1))
        print(newValues)
        if (newValues != self.Values):
            self.Values = newValues
            wx.CallAfter(pub.sendMessage,"update",msg = "") 
        
    def SendCommand(self, cmd):
        self.cmdBuffer.append(cmd)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

