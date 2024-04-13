import network
import espnow
import ujson


class espconnect():
    def __init__(self,device_type):
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.e = espnow.ESPNow()
        self.e.active(True)
        self.e.add_peer(b'\xff\xff\xff\xff\xff\xff')
        self.device = device_type
        self.Peripherals = {'Console':{'mac': None,'Connected': False},'Steering':{'mac': None, 'Connected': False},'Throttle':{'mac': None, 'Connected': False}}
    
    def connect(self,device_type = None):
        if self.device == 'Steering':
            mac2,msg2 = self.e.recv()
            if msg2 != None:
                data2 = ujson.loads(msg2)
                if data2[0] == 'BroadCast':
                    if data2[1] == 'Steering':
                        self.Peripherals['Console']['mac'] = mac2
                        self.Peripherals['Console']['Connected'] = True
                        self.e.add_peer(mac2)
                        self.e.send(mac2,('Response','Steering'))

        if self.device == 'Throttle':
            mac3,msg3 = self.e.recv()
            if msg3 != None:
                data3 = ujson.loads(msg3)
                if data3[0] == 'BroadCast':
                    if data[1] == 'Throttle':
                        self.Peripherals['Console']['mac'] = mac3
                        self.Peripherals['Console']['Connected'] = True
                        self.e.add_peer(mac3)
                        self.e.send(mac2,('Response','Throttle'))

        if self.device == 'Console':
            if device_type == 'Steering':
                self.e.send(b'\xff\xff\xff\xff\xff\xff',ujson.dumps(('BroadCast','Steering')))
                mac,msg = self.e.recv(10)
                if msg != None:
                    data = ujson.loads(msg)
                    if data[0] == 'Response':
                        if data[1] == 'Steering':
                            self.Peripherals['Steering']['mac'] = mac
                            self.Peripherals['Steering']['Connected'] = True
                            self.e.add_peer(mac)

            if device_type == 'Throttle':
                self.e.send(b'\xff\xff\xff\xff\xff\xff',ujson.dumps(('BroadCast','Throttle')))
                mac1,msg1 = self.e.recv(10)
                if msg1 != None:
                    data1 = ujson.loads(msg1)
                    if data1[0] == 'Response':
                        if data1[1] == 'Throttle':
                            self.Peripherals['Throttle']['mac'] = mac1
                            self.Peripherals['Throttle']['Connected'] = True
                            self.e.add_peer(mac1)

    def send(self,device,datatosend):
        data2send = ujson.dumps(datatosend)
        if self.e.send(self.Peripherals[device]['mac'],data2send):
            self.Peripherals[device]['Connected'] = True
        else:
            self.Peripherals[device]['Connected'] = False


    def recieve(self):
        emac,emsg = self.e.recv(0)
        if emsg != None:
            data = ujson.loads(emsg)
            if data[0] == 'BroadCast':
                if data[1] == self.device:
                    self.Peripherals['Console']['mac'] = emac
                    self.Peripherals['Console']['Connected'] = True
                    try:
                        self.e.add_peer(emac)
                    except OSError as err:
                        if len(err.args) < 2:
                            raise err
                        elif err.args[1] == 'ESP_ERR_ESPNOW_EXIST':
                            pass
                    bmsg = ujson.dumps(('Response',self.device))
                    self.e.send(emac,bmsg)
                    return None
            if data[0] != 'BroadCast':
                return data
        else:
            return None

