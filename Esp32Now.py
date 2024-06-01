import network # type: ignore
import espnow # type: ignore
import ujson
from machine import Timer # type: ignore
import utime  # type: ignore


class Peripheral():
        def __init__(self,device_type):
            self.sta = network.WLAN(network.STA_IF)
            self.sta.active(True)
            self.e = espnow.ESPNow()
            self.e.active(True)
            self.e.add_peer(b'\xff\xff\xff\xff\xff\xff')
            self.device = device_type
            self.data = None
            self.console_status = False
            self.Ptime = utime.tick_ms()
            file = open("Values.json","r")
            x = file.read()
            self.Connect_Data = ujson.loads(x)
            for x in self.Connect_Data:
                if self.Connect_Data[x]['Mac'] != None:
                     self.e.add_peer(self.Connect_Data[x]['Mac'])
            file.close()
            

        def pair(self):
            while True:
                self.e.send(b'\xff\xff\xff\xff\xff\xff',ujson.dumps(('BroadCast',self.device)))
                mac,msg = self.e.recv()
                if msg != None:
                    self.e.add_peer(mac)
                    self.console_status = True
                    self.Connect_Data['Console']['Mac'] = mac
                    self.console_saved = True
                    file = open("Values.json","w")
                    file.write(ujson.dumps(self.Connect_Data))
                    file.close()
                    break

        def Connect(self):
            if self.Connect_Data['Console']['Mac'] == None:
                self.pair()
            self.Ptime = utime.ticks_ms()                  

        def listen(self):
            mac,msg = self.e.recv()
            if msg != None:
                self.data = ujson.loads(msg)
                self.Ptime = utime.ticks_ms()
                self.console_status = True
                self.e.send(mac,ujson.dumps((self.device,'Recieved')))
                return self.data
            else:
                if utime.ticks_diff(utime.ticks_ms, self.Ptime) > 1000:
                    self.console_status = False
                return None
            
class Host():

    def __init__(self):
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.e = espnow.ESPNow()
        self.e.active(True)
        self.e.add_peer(b'\xff\xff\xff\xff\xff\xff')
        file = open("Values.json","r")
        x = file.read()
        self.Connect_Data = ujson.loads(x)
        for x in self.Connect_Data:
            if self.Connect_Data[x]['Mac'] != None:
                self.e.add_peer(self.Connect_Data[x]['Mac'])
        file.close()
    
    def listen(self):
        mac,msg = self.e.recv()
        if msg != None:
            rmsg = ujson.dumps(msg)
            if rmsg[0] == 'Broadcast':
                self.Connect_Data[rmsg[1]]['Mac'] = mac
                self.Connect_Data[rmsg[1]]['Status'] = True

    def send(self):
        for x in self.Connect_Data:
            if x != 'Console':
                if self.Connect_Data[x]['Data'] != None:
                    self.e.send(self.Connect_Data[x]['Mac'],self.Connect_Data[x]['Data'])
                    mac,msg = self.e.recv()
                    if msg != None:
                        data = ujson.dumps(msg)
                        if data == 'Recieved':
                            self.Connect_Data[x]['Status'] = True
                    else:
                        self.Connect_Data[x]['Status'] = False       

    def HeartBeat(self):
        self.listen()
        self.send()

    def Start_Coms(self):
        tim = Timer(3)
        tim.init(mode=Timer.PERIODIC, freq=200, callback=self.heartbeat)