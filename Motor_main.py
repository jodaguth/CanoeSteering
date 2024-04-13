import CanoeControl
import ESPControl

esp = ESPControl.espconnect('Throttle')

Motor = CanoeControl.MotorThrottleModule(0,1,3)

while True:
    data = esp.recieve()
    if data != None:
        Motor.process(data)

