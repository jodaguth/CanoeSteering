import ESPNOW
import CanoeControl
import utime # type: ignore
esp = ESPNOW.Console()

Steering = CanoeControl.SteeringModule(0,1,6,-1800,1800)
Throttle = CanoeControl.ThrottleModule(3,4,-600,600)
s_state = False
t_state = False
print('Run')
Old_Time = utime.ticks_ms()
while True:
    if utime.ticks_diff(utime.ticks_ms(),Old_Time) > 25:
        Steering.process()
        esp.SendSteering(Steering.return_data())
        Throttle.process()
        esp.SendThrottle(Throttle.return_data())
        Old_Time = utime.ticks_ms()
    
    if s_state != esp.Steering_Status:
        s_state = esp.Steering_Status
        print('Steering: {0}'.format(s_state))
    if t_state != esp.Throttle_Status:
        t_state = esp.Throttle_Status
        print('Throttle: {0}'.format(t_state))