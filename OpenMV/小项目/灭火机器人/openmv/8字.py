import sensor, image, time
from pyb import Servo
from pid import PID

#云台配置--------------------------------------------------------------------------------------------
pan_servo=Servo(1)
tilt_servo=Servo(2)

#pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.35, i=0, imax=90)#在线调试使用这个PID
tilt_pid = PID(p=0.35, i=0, imax=90)#在线调试使用这个PID


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()

tilt_servo.angle(-45)
time.sleep(3000)
tilt_servo.angle(-17)
time.sleep(3000)
m=-90#水平方向初始位
n=-90#垂直方向初始位
t=0
while(True):
    clock.tick()
    img = sensor.snapshot()
    if t == 0:
        m = m + 1
        if m == 90:
            t = 1
    else:
        m = m - 1
        if m == -90:
            t = 0

    if n == 90:
        n = -90
    else:
        n = n + 1
    tilt_servo.angle(-45)
    #云台自转8字形寻找标靶
    #pan_servo.angle(m)



#1.3ms    -17    启动电机
#1ms      -45    停止电机
