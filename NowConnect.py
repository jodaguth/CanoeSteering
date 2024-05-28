import network
import espnow
import ujson
from machine import Timer
import utime 

class EspNow ():
    def __init__(self,device_type):
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.e = espnow.ESPNow()
        self.e.active(True)
        self.e.add_peer(b'\xff\xff\xff\xff\xff\xff')
        self.device = device_type
        self.tally = 0
        self.Peripherals = {'Console':{'mac': None,'Connected': False},'Steering':{'mac': None, 'Connected': False, 'data': None},'Throttle':{'mac': None, 'Connected': False, 'data': None}}
        self.Ptime = 0


    def recieve(self):

        if self.tally >= 150:
            self.Ptime = utime.ticks_ms()
            self.Peripherals['Console']['Connected'] = True
        elif utime.ticks_diff(utime.ticks_ms(), self.Ptime) > 1000:
            self.Peripherals['Console']['Connected'] = False

        if self.device == 'Steering':
            mac,msg = self.e.recv()
            if msg != None:
                self.tally += 1
                data = ujson.loads(msg)
                if data[0] == 'Broadcast':
                    if data[1] == 'Steering':
                        self.e.add_peer(mac)
                        self.e.send(mac,ujson.dumps(('Broadcast','Steering')))
                        self.Peripherals['Console']['mac'] = mac
                        self.Peripherals['Console']['Connected'] = True
                        return None
                elif data[0] == 'Check':
                    if self.Peripherals['Console']['mac'] != None:
                        self.e.send(mac,ujson.dumps('Thanks'))
                        return None
                    else:
                        self.e.add_peer(mac)
                        self.Peripherals['Console']['mac'] = mac
                        self.e.send(mac1,ujson.dumps('Thanks'))
                        return None
                else:
                    return data
            else:
                return None
            

        if self.device == 'Throttle':
            mac1,msg1 = self.e.recv()
            if msg1 != None:
                self.tally += 1
                data = ujson.loads(msg1)
                if data[0] == 'Broadcast':
                    if data[1] == 'Throttle':
                        self.e.add_peer(mac1)
                        self.e.send(mac1,ujson.dumps(('Broadcast','Throttle')))
                        self.Peripherals['Console']['mac'] = mac1
                        self.Peripherals['Console']['Connected'] = True
                        return None
                elif data[0] == 'Check':
                    if self.Peripherals['Console']['mac'] != None:
                        self.e.send(mac1,ujson.dumps('Thanks'))
                        return None
                    else:
                        self.e.add_peer(mac1)
                        self.Peripherals['Console']['mac'] = mac1
                        self.e.send(mac1,ujson.dumps('Thanks'))
                        return None
                else:
                    return data
            else:
                return None



    def heartbeat(self,r):
        if self.Peripherals['Steering']['mac'] == None:
            self.e.send(b'\xff\xff\xff\xff\xff\xff',ujson.dumps(('BroadCast','Steering')))
            mac,msg = self.e.recv()
            if msg != None:
                data = ujson.loads(msg)
                if data[0] == 'Broadcast':
                    if data[1] == 'Steering':
                        self.Peripherals['Steering']['mac'] = mac
                        self.Peripherals['Steering']['Connected'] = True
        else:
            if self.Peripherals['Steering']['data'] != None:
                self.e.send(self.Peripherals['Steering']['mac'],ujson.dumps(self.Peripherals['Steering']['data']))
                mac1,msg1 = self.e.recv()
                if msg1 != None:
                    self.Peripherals['Steering']['Connected'] = True
                else:
                    self.Peripherals['Steering']['Connected'] = False
            else:
                self.e.send(self.Peripherals['Steering']['mac'],ujson.dumps(('Check','Console')))
                macc,msgg = self.e.recv()
                if msgg != None:
                    self.Peripherals['Steering']['Connected'] = True
                else:
                    self.Peripherals['Steering']['Connected'] = False

        if self.Peripherals['Throttle']['mac'] == None:
            self.e.send(b'\xff\xff\xff\xff\xff\xff',ujson.dumps(('BroadCast','Throttle')))
            mac2,msg2 = self.e.recv()
            if msg2 != None:
                data = ujson.loads(msg2)
                if data[0] == 'Broadcast':
                    if data[1] == 'Throttle':
                        self.Peripherals['Throttle']['mac'] = mac
                        self.Peripherals['Throttle']['Connected'] = True
        else:
            if self.Peripherals['Throttle']['data'] != None:
                self.e.send(self.Peripherals['Throttle']['mac'],ujson.dumps(self.Peripherals['Throttle']['data']))
                mac3,msg3 = self.e.recv()
                if msg3 != None:
                    self.Peripherals['Throttle']['Connected'] = True
                else:
                    self.Peripherals['Throttle']['Connected'] = False
            else:
                self.e.send(self.Peripherals['Throttle']['mac'],ujson.dumps(('Check','Console')))
                macc1,msgg1 = self.e.recv()
                if msgg1 != None:
                    self.Peripherals['Throttle']['Connected'] = True
                else:
                    self.Peripherals['Throttle']['Connected'] = False
  
    def start_Console(self):
        tim = Timer(3)
        tim.init(mode=Timer.PERIODIC, freq=200, callback=self.heartbeat)
