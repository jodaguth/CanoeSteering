import network # type: ignore
import espnow # type: ignore
import ujson
from machine import Timer # type: ignore
import utime  # type: ignore

class Console ():

    def __init__(self):
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.e = espnow.ESPNow()
        self.e.active(True)
        self.e.add_peer(b'\xff\xff\xff\xff\xff\xff')
        self.Throttle_Mac = None
        self.Throttle_Status = False
        self.Steering_Mac = None
        self.Steering_Status = False

    def SendThrottle(self,x):
        if self.Throttle_Mac == None:
            if self.Pair('Throttle') == True:
                self.send('Throttle',x)
        else:
            self.send('Throttle',x)

    def SendSteering(self,x):
        if self.Steering_Mac == None:
            if self.Pair('Steering') == True:
                self.send('Steering',x)
        else:
            self.send('Steering',x)

    def send(self,device,data):
        if device == 'Throttle':
            self.e.send(self.Throttle_Mac,ujson.dumps(('Throttle',data)))
            mac,msg = self.e.recv(1)
            if msg != None:
                if self.Throttle_Mac == mac:
                    self.Throttle_Status = True
            else:
                self.Throttle_Status = False

        if device == 'Steering':
            self.e.send(self.Steering_Mac,ujson.dumps(('Steering',data)))
            mac1,msg1 = self.e.recv(1)
            if msg1 != None:
                if self.Steering_Mac == mac1:
                    self.Steering_Status = True
            else:
                self.Steering_Status = False
                
    def Pair(self,x):
        self.e.send(b'\xff\xff\xff\xff\xff\xff',ujson.dumps(('Pair',x)))
        mac,jsonmsg = self.e.recv(1)
        if msg != None:
            msg = ujson.loads(jsonmsg)
            if msg[1] == x:
                self.e.add_peer(mac)
                return True
        else:
            return False
    

class Peripheral():
    def __init__(self,Device_Type):
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.e = espnow.ESPNow()
        self.e.active(True)
        self.Console_Mac = None
        self.Console_Status = False
        self.Device = Device_Type
        self.Time = utime.time() + 2

    def Recieve(self):
        mac,msg = self.e.recv(1)
        if msg != None:
            data = ujson.loads(msg)
            if data[0] == 'Pair':
                if self.Console_Mac != mac:
                    self.e.add_peer(mac)
                    self.Console_Mac = mac
                    self.e.send(mac,ujson.dumps(('Paired',self.Device)))
                else:
                    self.e.send(mac,ujson.dumps(('Paired',self.Device)))

            elif data[0] == self.Device:
                if self.Console_Mac != mac:
                    self.e.add_peer(mac)
                    self.Console_Mac = mac
                    self.e.send(mac,ujson.dumps(('Recieved',self.Device)))
                    return data[1]
                else:
                    self.e.send(mac,ujson.dumps(('Recieved',self.Device)))
                    self.Time = utime.time()
                    return data[1]
        dif = utime.time() - self.Time
        if dif > 2:
            self.Console_Status = False
        else:
            self.Console_Status = True
            


