import ESPControl
import CanoeControl

esp = ESPControl.espconnect('Console')

while True:
    if esp.Peripherals['Steering']['Connected'] == False:
        esp.connect('Steering')
    else:
        print('Steering Connected')
    if esp.Peripherals['Throttle']['Connected'] == False:
        esp.connect('Throttle')
    else:
        print('Throttle Connected')
    if esp.Peripherals['Steering']['Connected'] == True:
        if esp.Peripherals['Throttle']['Connected'] == True:
            break

Steering = CanoeControl.SteeringModule(0,1,6,-1800,1800)
Throttle = CanoeControl.ThrottleModule(3,4,-600,600)

while True:
    if Steering.process():
        esp.send('Steering',Steering.return_data())
    if Throttle.process():
        esp.send('Throttle',Throttle.return_data())
    