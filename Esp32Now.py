import network
import espnow
import ujson
from machine import Timer
import utime 


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
                if x['Mac'] != None:
                     self.e.add_peer(x['Mac'])
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
            if x['Mac'] != None:
                self.e.add_peer(x['Mac'])
        file.close()