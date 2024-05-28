import ESPControl
import CanoeControl
import utime
esp = ESPControl.espconnect('Console')
print('Steering Disconnected')
print('Throttle Disconnected')
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
ptime = utime.ticks_ms()
while True:
    ctime = utime.ticks_ms()
    dtime = utime.ticks_diff(ctime, ptime)
    if Steering.process():
        if dtime >= 100:
            esp.send('Steering',Steering.return_data())
            ptime = utime.ticks_ms()
    if Throttle.process():
        esp.send('Throttle',Throttle.return_data())
    if dtime >= 500:
        ptime = utime.ticks_ms()