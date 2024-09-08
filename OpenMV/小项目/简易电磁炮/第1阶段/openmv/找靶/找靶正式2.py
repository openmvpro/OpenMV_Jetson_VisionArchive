#在下面输入要追踪靶心的阈值
b=(0, 100, -128, -14, 33, -128)


import sensor, image, time, sys, json
from pyb import UART, Servo, LED
from pid import PID

pan_servo=Servo(1)
tilt_servo=Servo(2)

#pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID
tilt_pid = PID(p=0.09, i=0, imax=90)#在线调试使用这个PID

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # must be this
sensor.set_framesize(sensor.QVGA) # must be this
sensor.skip_frames(time = 10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_auto_gain(False) # must be turned off for color tracking
clock = time.clock() # Tracks FPS.

uart = UART(3,115200)

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

m=-180#水平方向初始位
n=-180#垂直方向初始位
t=0

while(True):
    LED(1).on()

    clock.tick() # Track elapsed milliseconds between snapshots().帧率
    img = sensor.snapshot().lens_corr(1.8) # Take a picture and return the image.

    blobs = img.find_blobs([b])

    if blobs:
        LED(1).on()
        LED(2).on()
        LED(3).on()

        #发送开启激光指令
        uart.write("begin\r\n")

        max_blob = find_max(blobs)

        pan_error = max_blob.cx()-img.width()/2
        tilt_error = max_blob.cy()-img.height()/2

        img.draw_circle(int(max_blob.cx()), int(max_blob.cy()),int(max_blob.cyf()-max_blob.y()) , color = (255, 0, 0))
        img.draw_cross(max_blob.cx(), max_blob.cy(),color=(255,0,0)) # cx, cy

        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)

        #print("pan_output",pan_output)

        pan_servo.angle(pan_servo.angle()+pan_output)
        tilt_servo.angle(tilt_servo.angle()-tilt_output)

    else:
        if t == 0:
            m = m + 1
            if m == 180:
                t = 1
        else:
            m = m - 1
            if m == -180:
                t = 0

        if n == 180:
            n = -180
        else:
            n = n + 1

        LED(1).off()
        LED(2).off()
        LED(3).off()

        #发送关闭激光指令
        uart.write("close\r\n")

        #云台自转8字形寻找标靶
        pan_servo.angle(m)
        tilt_servo.angle(n)
