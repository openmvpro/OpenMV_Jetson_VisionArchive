
#追踪线的阈值
THRESHOLD = (0, 100, -128, -6, -124, 127) # Grayscale threshold for dark things...


import sensor, image, time
from pyb import LED
import car
from pid import PID

#y=ax+b
rho_pid = PID(p=0.4, i=0)#类似于b  控制线在视野中的位置偏移
theta_pid = PID(p=0.001, i=0)#类似于a  调整线在视野中与底部的角度

#开灯补光稳定光源
LED(1).on()
LED(2).on()
LED(3).on()

sensor.reset()
sensor.set_vflip(True)#图像水平翻转
sensor.set_hmirror(True)#图像垂直翻转
sensor.set_pixformat(sensor.RGB565)
#小分辨率确保线性回归get_regression运算速度的保证
sensor.set_framesize(sensor.QQQVGA) # 80x60 (4,800 pixels) - O(N^2) max = 2,3040,000.
#sensor.set_windowing([0,20,80,40])
sensor.skip_frames(time = 2000)     # WARNING: If you use QQVGA it may take seconds
clock = time.clock()                # to process a frame sometimes.

while(True):
    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD])#对获取的图片在设定的阈值内进行二值化分割
    #对图像所有阈值像素进行线性回归计算
    #若 robust 为True，则使用Theil-Sen线性回归算法，它计算图像中所有阈值像素的斜率的中位数。
    line = img.get_regression([THRESHOLD], robust = True)
    if (line):
        rho_err = abs(line.rho())-img.width()/2  #计算返回的line与图像中央的偏移距离像素

        #对直线的坐标进行角度变换，以正y轴方向为0°，正x轴方向为90°
        if line.theta()>90:
            theta_err = line.theta()-180
        else:
            theta_err = line.theta()

        img.draw_line(line.line(), color = 127)#把线性回归返回的值画出来

        #print(rho_err,line.magnitude(),rho_err)#line.magnitude()为霍夫变换后的直线的模

        if line.magnitude()>8:  #返回的模越大线性效果越好
            #if -40<b_err<40 and -30<t_err<30:
            rho_output = rho_pid.get_pid(rho_err,1)
            theta_output = theta_pid.get_pid(theta_err,1)
            output = rho_output+theta_output
            print('rho_err:',rho_err)
            print('rho_output:',rho_output)
            print('theta_err:',theta_err)
            print('theta_output:',theta_output)
            print('output:',output)
            car.run(50+output, 50-output)#以中央速度50位基准，可调整其速度
        else:
            car.run(0,0)
    else:
        car.run(50,-50)
        pass
    #print(clock.fps())
