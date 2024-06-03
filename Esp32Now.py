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
            self.Ptime = utime.ticks_ms()
            file = open("Values.json","r")
            x = file.read()
            xt = ujson.loads(x)
            self.Connect_Data = xt
            for x in self.Connect_Data:
                read = self.Connect_Data[x]['Mac']
                if read != None:
                     self.e.add_peer(read)
            file.close()
            

        def pair(self):
            while True:
                self.e.send(b'\xff\xff\xff\xff\xff\xff',ujson.dumps(('BroadCast',self.device)))
                mac,msg = self.e.recv(1000)
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
            else:
                self.e.add_peer(self.Connect_Data['Console']['Mac'])
            self.Ptime = utime.ticks_ms()                  

        def listen(self):
            mac,msg = self.e.recv(1)
            if msg != None:
                self.data = ujson.loads(msg)
                self.Ptime = utime.ticks_ms()
                self.console_status = True
                self.e.send(mac,ujson.dumps(('Recieved',self.device)))
                return self.data
            else:
                if utime.ticks_diff(self.Ptime, utime.ticks_ms()) > 1000:
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
        utime.sleep(.1)
        xt = ujson.loads(x)
        utime.sleep(.1)
        self.Connect_Data = xt
        for x in self.Connect_Data:
            read = self.Connect_Data[x]['Mac']
            if read != None:
                self.e.add_peer(read)
        file.close()
    
    def listen(self,y = None):
        mac,msg = self.e.recv(1)
        if msg != None:
            rmsg = ujson.loads(msg)
            if rmsg[0] == 'BroadCast':
                self.Connect_Data[rmsg[1]]['Mac'] = mac
                try:
                    self.e.add_peer(mac)
                except:
                    pass
                self.e.send(mac,ujson.dumps(('Paired','Console')))
                self.Connect_Data[rmsg[1]]['Status'] = True
                file = open("Values.json","w")
                file.write(ujson.dumps(self.Connect_Data))
                file.close()
            elif rmsg[0] == 'Recieved':
                self.Connect_Data[rmsg[1]]['Status'] = True
        else:
            if y != None:
                self.Connect_Data[y]['Status'] = False
    def send(self):
        for x in self.Connect_Data:
            if x != 'Console':
                self.listen()
                if self.Connect_Data[x]['Mac'] != None:
                    if self.Connect_Data[x]['Data'] != None:
                        self.e.send(self.Connect_Data[x]['Mac'],ujson.dumps(self.Connect_Data[x]['Data']))       
                        self.listen(y = x)
    def HeartBeat(self,r):
        self.send()
        utime.sleep(.2)

    def Start_Coms(self):
        tim = Timer(0)
        tim.init(mode=Timer.PERIODIC, freq=10, callback=self.HeartBeat)

    def update_data(self,device,data):
        self.Connect_Data[device]['Data'] = data
