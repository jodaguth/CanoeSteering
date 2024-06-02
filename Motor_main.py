import CanoeControl
import Esp32Now




esp = Esp32Now.Peripheral('Throttle')
esp.Connect()
Motor = CanoeControl.MotorThrottleModule(0,1,3)
print('Run')
c_state = False
while True:
    data = esp.listen()
    if data != None:
        Motor.process(data)
    
    if esp.console_status != c_state:
        c_state = esp.console_status
        print(c_state) 

