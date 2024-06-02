import Esp32Now
import CanoeControl
esp = Esp32Now.Host()

Steering = CanoeControl.SteeringModule(0,1,6,-1800,1800)
Throttle = CanoeControl.ThrottleModule(3,4,-600,600)
esp.Start_Coms()
s_state = False
t_state = False
print('Run')
while True:
    if Steering.process():
        esp.update_data('Steering',Steering.return_data())

    if Throttle.process():
        esp.update_data('Throttle',Throttle.return_data())
    
    if s_state != esp.Connect_Data['Steering']['Status']:
        s_state = esp.Connect_Data['Steering']['Status']
        print(s_state)
    if t_state != esp.Connect_Data['Throttle']['Status']:
        t_state = esp.Connect_Data['Throttle']['Status']
        print(t_state)
