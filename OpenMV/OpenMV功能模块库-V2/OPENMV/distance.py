
import time, math, sensor, image

from pyb import UART
from pyb import LED
from pyb import Timer
from pyb import Pin
from machine import I2C
from vl53l1x import VL53L1X


# LED灯定义
red_led     = LED(1)
green_led   = LED(2)
blue_led    = LED(3)


def ExceptionVar(var):
    data = []
    data.append(0)
    data.append(0)

    if var == -1:
        data[0] = 0
        data[1] = 0
    else:
        data[0] = var & 0xFF
        data[1] = var >> 8
    return data

Frame_Cnt = 0
fCnt_tmp = [0,0]
def UART_Send(FormType, Loaction0, Location1):
    global Frame_Cnt
    global fCnt_tmp
    Frame_Head = [170,170]
    Frame_End = [85,85]
    fFormType_tmp = [FormType]
    Frame_Cnt += 1

    if Frame_Cnt > 65534 :
        FrameCnt = 0

    fHead = bytes(Frame_Head)

    fCnt_tmp[0] = Frame_Cnt & 0xFF
    fCnt_tmp[1] = Frame_Cnt >> 8
    fCnt = bytes(fCnt_tmp)

    fFormType = bytes(fFormType_tmp)
    fLoaction0 = bytes(ExceptionVar(Loaction0))
    fLoaction1 = bytes(ExceptionVar(Location1))
    fEnd = bytes(Frame_End)
    FrameBuffe = fHead + fCnt + fFormType + fLoaction0 + fLoaction1 + fEnd
    return FrameBuffe


sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((160,120))
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False) # must be turned off for color tracking

#关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡。
uart = UART(3, 115200)
clock = time.clock() # Tracks FPS.

pin1 = Pin('P1', Pin.IN, Pin.PULL_DOWN)#设置p_in为输入引脚，并开启上拉电阻

Port1 = False
while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    #外部低电平开启任务
    if pin1.value():
        Port1 = True
        pass

    if Port1:
        G_Flag = 1
        green_led.off()
        red_led.off()
        blue_led.off()
        break


    green_led.on()
    red_led.on()
    blue_led.on()



#2 p4,p5
#4 p7,p8
i2c = I2C(4)
distance = VL53L1X(i2c)



old_dist = 0

def distance_function():
    global old_dist

    distance_num = distance.read()
    distance_num /= 10

    if abs(old_dist - distance_num) < 5:
        print("range: %d cm "%distance_num)
        uart.write(UART_Send(66,int(distance_num),0))

    else:
        print("range:00000000000000000")
        uart.write(UART_Send(66,0,0))

    old_dist = distance_num
    pass


i = 0
while True:
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    distance_function()

    print("%f" %(clock.fps()))
    #time.sleep(50)

    i += 1
    if i%5 == 0:
        green_led.on()
    if i%10 == 0:
        green_led.off()
