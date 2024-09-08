import sensor, image, time, sys, json
from pyb import Servo, LED
from pid import PID

pan_servo=Servo(1)
tilt_servo=Servo(2)

#pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID
tilt_pid = PID(p=0.12, i=0, imax=90)#在线调试使用这个PID

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # must be this
sensor.set_framesize(sensor.QVGA) # must be this
sensor.skip_frames(time = 10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_hmirror(True)#水平方向翻转
sensor.set_vflip(True)#垂直方向翻转

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

#在下面输入要追踪靶心的阈值
green=(0, 100, -128, 127, -128, -24)
red=(80, 100, -2, 127, -128, 127)

m=-90#水平方向初始位
n=-90#垂直方向初始位
t=0
a=0
while(True):
    img = sensor.snapshot().lens_corr(1) # Take a picture and return the image.

    blobs_green = img.find_blobs([green])
    blobs_red = img.find_blobs([red])
    '''
    img.draw_rectangle(blobs_green[0:4],color=(255,0,0))
    img.draw_cross(blobs_green.cx(), blobs_green.cy(),color=(255,0,0)) # cx, cy

    img.draw_rectangle(blobs_red[0:4],color=(255,0,0)) # cx, cy
    img.draw_cross(blobs_red.cx(), blobs_red.cy(),color=(255,0,0)) # cx, cy

    '''

    if a==1:

        max_blob_green = find_max(blobs_green)
        max_blob_red = find_max(blobs_red)

        pan_error = max_blob_green.cx()-max_blob_red.cx()
        tilt_error = max_blob_green.cy()-max_blob_red.cx()

        img.draw_rectangle(max_blob_green[0:4],color=(255,0,0))
        img.draw_cross(max_blob_green.cx(), max_blob_green.cy(),color=(255,0,0)) # cx, cy

        img.draw_rectangle(max_blob_red[0:4],color=(255,0,0)) # cx, cy
        img.draw_cross(max_blob_red.cx(), max_blob_red.cy(),color=(255,0,0)) # cx, cy


        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)

        #print("pan_output",pan_output)

        pan_servo.angle(pan_servo.angle()-pan_output)
        tilt_servo.angle(tilt_servo.angle()+tilt_output)

    else:
        if t == 0:
            m = m + 2
            if m == 90:
                t = 1
        else:
            m = m - 2
            if m == -90:
                t = 0

        if n == 90:
            n = -90
        else:
            n = n + 2

        LED(1).off()
        LED(2).off()
        LED(3).off()


        #云台自转8字形寻找标靶
        pan_servo.angle(m)
        tilt_servo.angle(n)
