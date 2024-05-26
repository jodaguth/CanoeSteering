from machine import Pin,PWM,Timer
import utime
import micropython

def map_range(x, in_min, in_max, out_min, out_max,F=True):
    if F:
        xx = float(x)
        in_minn = float(in_min)
        in_maxx = float(in_max)
        out_minn = float(out_min)
        out_maxx = float(out_max)
        return round((xx - in_minn) * (out_maxx - out_minn) / (in_maxx - in_minn) + out_minn,2)
    else:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class SteeringModule ():
    def __init__(self,A,B,zero_pin,Min,Max):
        self.PinA = Pin(A, Pin.IN)
        self.PinB = Pin(B, Pin.IN)
        self.PinA.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.count_up)
        self.PinB.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.count_down)
        self.count = 0
        self.pastcount = 0
        self.Min = Min
        self.Max = Max
        self.data = [0.0,0]
        self.zeropin = Pin(zero_pin, Pin.IN)
    def count_up(self,r):
        if self.zeropin.value():
            if self.count < self.Max:
                self.count += 1
    def count_down(self,r):
        if self.zeropin.value():
            if self.count > self.Min:
                self.count -= 1        
    def current_count(self):
        return self.count
    def set_count(self,a = 0):
        self.count = a
    def process(self):
        if self.zeropin.value() == False:
            self.count = 0
            self.data[1] = 1
        else:
            self.data[1] = 0 

        if self.count != self.pastcount:
            self.pastcount = self.count
            self.data[0] = map_range(self.count,self.Min,self.Max,-90.0,90.0)
            return True
        else:
            return False
        
    def return_data(self):
        return self.data
class ThrottleModule ():
    def __init__(self,A,B,Min,Max,Throttle_Dead_Zone=100):
        self.PinA = Pin(A, Pin.IN)
        self.PinB = Pin(B, Pin.IN)
        self.PinA.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.count_up)
        self.PinB.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.count_down)
        self.count = 0
        self.pastcount = 0
        self.Min = Min
        self.Max = Max
        self.data = [0.0,0]
        self.mac = None
        self.deadzone = Throttle_Dead_Zone / 2
    def count_up(self,r):
        if self.count < self.Max:
            self.count += 1
    def count_down(self,r):
        if self.count > self.Min:
            self.count -= 1        
    def current_count(self):
        return self.count
    def set_count(self,a = 0):
        self.count = a
    def process(self):
        if self.count != self.pastcount:
            self.pastcount = self.count
            if abs(self.count) < self.deadzone:
                self.data[0] = 0.0
                self.data[1] = 0
            else:
                if self.count > 0:
                    self.data[0] = map_range(self.count,self.deadzone,self.Max,0.0,100.0)
                    self.data[1] = 1
                if self.count < 0:
                    self.data[0] = map_range(abs(self.count),self.deadzone,self.Max,0.0,100.0)
                    self.data[1] = 2
            return True
        else:
            return False
    
    def return_data(self):
        return self.data
        
class MotorThrottleModule ():
    def __init__(self,EN,PWMMFW,PWMMBW) -> None:
        self.PWMTFW = Pin(PWMMFW)
        self.PWMTBW = Pin(PWMMBW)
        self.PWMFW = PWM(self.PWMTFW)
        self.PWMBW = PWM(self.PWMTBW)
        self.EN_Pin = Pin(EN,Pin.OUT)
        self.EN_Pin.value(0)

        self.PWMFW.freq(15000)
        self.PWMFW.duty(0)
        self.PWMBW.freq(15000)
        self.PWMBW.duty(0)

    def process (self,data):
        if data[1] == 0:
            self.PWMBW.duty(0)
            self.PWMFW.duty(0)
            self.EN_Pin.value(0)
        elif data[1] == 1:
            duty = round(map_range(data[0],0,100,0,1023,F=False))
            self.PWMBW.duty(0)
            self.EN_Pin.value(1)
            self.PWMFW.duty(duty)
        elif data[1] == 2:
            duty = round(map_range(data[0],0,100,0,1023,F=False))
            self.PWMFW.duty(0)
            self.EN_Pin.value(1)
            self.PWMBW.duty(duty)

class StepperSteeringModule:
    def __init__(self,en_pin,step_pin,dir_pin,steps_per_second=6400,step_rotation=200,microstep = 1):
        self.en = Pin(en_pin,Pin.OUT,Pin.PULL_DOWN,value=1)
        self.step = Pin(step_pin,Pin.OUT,Pin.PULL_DOWN,value=0)
        self.dir = Pin(dir_pin,Pin.OUT,Pin.PULL_DOWN,value=0)
        self.timer = Timer(0)
        self.timer_running = False
        self.sps = steps_per_second
        self.steps_rotation = step_rotation
        self.microsteps = microstep
        self.pos = 0
        self.steps = 0
        self.target = 0
        self.rotations = 0
        self.micro_step_rotation = self.steps_rotation * self.microsteps
        self.engaged = False
        self.device_revolutions = 24

    def set_microsteps(self,m):
        self.microsteps = m
        self.micro_step_rotation = self.steps_rotation * self.microsteps

    def set_steps_rotation(self,s):
        self.steps_rotation = s
        self.micro_step_rotation = self.steps_rotation * self.microsteps
        
    def get_pos(self):
        self.pos = ((self.steps * 360) / self.micro_step_rotation) / 24
        return self.pos
    
    def set_device_rotations(self,rt):
        self.device_revolutions = rt

    def engage(self,en):
        if en == True:
            self.en.value(0)
            self.engaged = True
        else:
            self.en.value(1)
            self.engaged = False

    def track_target(self):
        if self.timer_running != True:
            self.timer.init(freq=self.sps,callback=self.run)
            self.timer_running = True
        else:
            self.timer.deinit()
            utime.sleep(0.000001)
            self.timer.init(freq=self.sps,callback=self.run)
            self.timer_running = True

    def target_pos(self,t):
        self.target = round((t * self.micro_step_rotation/360) * self.device_revolutions)
    
    def makeAstep(self,r):
        if self.engaged:
            self.dir.value(r)
            self.step.value(1)
            utime.sleep(0.000001)
            self.step.value(0)
            utime.sleep(0.000001)
            if r:
                self.steps -= 1 
            else:
                self.steps += 1
    def set_zero(self):
        self.target = 0
        self.pos = 0

    def run(self,r):
        if self.steps != self.target:
            self.engage(True)
            if self.target > self.steps:
                self.makeAstep(0)
            if self.target < self.steps:
                self.makeAstep(1)
        else:
            self.engage(False)
            
    def stop(self):
        self.timer.deinit()
        self.engage(False)
        self.timer_running(False)