import CanoeControl
import ESPNOW




esp = ESPNOW.Peripheral('Throttle')
Motor = CanoeControl.MotorThrottleModule(0,1,3)
print('Run')
c_state = False
while True:
    data = esp.Recieve()
    print(data)
    if data != None:
        Motor.process(data)
    
    if esp.Console_Status != c_state:
        c_state = esp.Console_Status
        print(c_state) 

