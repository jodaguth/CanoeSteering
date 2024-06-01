import CanoeControl
import Esp32Now




esp = Esp32Now.Peripheral('Throttle')
esp.Connect()
Motor = CanoeControl.MotorThrottleModule(0,1,3)
print('Run')
while True:
    data = esp.listen()
    if data != None:
        Motor.process(data)

