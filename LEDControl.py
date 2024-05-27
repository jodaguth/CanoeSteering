import utime
from machine import Pin,PWM,Timer

class LEDBLINK():
    def __init__(self,LED_PIN = 8, frequ = 8):
        self.LED = Pin(LED_PIN)
        self.LEDPWM = PWM(self.LED)
        self.LEDPWM.freq(15000)
        self.LEDPWM.duty(0)
        self.frequency = (1000 / frequ) / 10 
        self.pasttime = -10
        self.difference = 0
        self.duty = 0
        self.dir = 0

    def freq(self,f):
        self.frequency = (1000 / f) / 10

    def process(self):
        if self.pasttime == -10:
            self.pastime = utime.ticks_ms()
        else:
            self.difference = utime.ticks_ms() - self.pasttime
            if self.difference >= 10:
                if self.dir == 0:
                    if self.duty < 1023.00:
                        self.duty += 1023 / self.frequency
                        if self.duty > 1023:
                            self.duty = 1023
                    else:
                        self.dir = 1
                if self.dir == 1:
                    if self.duty > 0:
                        self.duty -= 1023 / self.frequency
                        if self.duty < 0:
                            self.duty = 0
                    else:
                        self.dir = 0

        self.LEDPWM.duty(self.duty)

            
        

utime.mktime()