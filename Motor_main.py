import CanoeControl
import ESPControl
import LEDControl

Led = LEDControl.LEDBLINK()

esp = ESPControl.espconnect('Throttle')

Motor = CanoeControl.MotorThrottleModule(0,1,3)

while True:
    Led.process()
    data = esp.recieve()
    if esp.Peripherals['Console']['Connected'] == True:
        Led.freq(2)
    if data != None:
        Motor.process(data)

