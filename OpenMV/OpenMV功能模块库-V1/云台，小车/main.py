import sensor, image, time
#import car
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

#云台------------------------------------------------------------------------------------------------
#云台8字寻找
def yuntai_eight():
    m=-90#水平方向初始位
    n=-90#垂直方向初始位
    t=0
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

    #云台自转8字形寻找标靶
    print("m=",m)
    print("n=",n)
    pan_servo.angle(m)
    tilt_servo.angle(n)

#云台追踪
def yuntai_track():
    #阈值自行填写
    blobs = img.find_blobs([green_threshold])
    if blobs:
        max_blob = find_max(blobs)
        pan_error = max_blob.cx()-img.width()/2
        tilt_error = max_blob.cy()-img.height()/2

        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)

        pan_servo.angle(pan_servo.angle()+pan_output)
        tilt_servo.angle(tilt_servo.angle()-tilt_output)

#小车------------------------------------------------------------------------------------------------
def car(blobs):
    #阈值自行填写
    blobs = img.find_blobs([green_threshold])
    if blobs:
        max_blob = find_max(blobs)
        x_error = max_blob[5]-img.width()/2
        h_error = max_blob[2]*max_blob[3]-size_threshold

        x_output=x_pid.get_pid(x_error,1)
        h_output=h_pid.get_pid(h_error,1)
        print("h_output",h_output)

while(True):
    clock.tick()
    img = sensor.snapshot()
    #云台--------------------------------------------------------------------------------------------
    #云台8字
    yuntai_eight()
    #云台追踪
    #yuntai_track()
    #小车--------------------------------------------------------------------------------------------
    #car()
