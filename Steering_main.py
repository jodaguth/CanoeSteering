import ESPNOW
import CanoeControl

esp = ESPNOW.Peripheral('Steering')


stepper_motor = CanoeControl.StepperSteeringModule(0,1,3)
stepper_motor.set_microsteps(8)
stepper_motor.set_device_rotations(24)
stepper_motor.track_target()
stepper_target = 0
stepper_set = 0
print('Run')
c_state = False
while True:

####### recieve data ###########################################################
    data = esp.Recieve()
    if data != None:
        #print(data)
        stepper_target = data[0]
        stepper_set = data[1]
################################################################################

####### Set Zero ###############################################################
    if stepper_set == 1:
        stepper_motor.set_zero()
################################################################################

######### Set Target ###########################################################
    #stepper_targeting = map_range(stepper_target,-600,600,-90,90)
    stepper_targeting = stepper_target
    stepper_motor.target_pos(stepper_targeting)
################################################################################
    if esp.Console_Status != c_state:
        c_state = esp.Console_Status
        #print(c_state)