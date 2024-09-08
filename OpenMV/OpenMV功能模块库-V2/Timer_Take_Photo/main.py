#############################################################
#	修改时间：2019.7.24
#	文件功能：定时拍照
#	输    出：空
#
#	备    注：需要注意路径
##############################################################

import sensor, image, time
from pyb import UART
from pyb import LED
from pyb import Timer
# LED灯定义
green_led  = LED(1)
blue_led   = LED(2)


import micropython
micropython.alloc_emergency_exception_buf(100)


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


Count_num = 0
Old_Count_num = 0
def Taking_Photo(tim):
    global Count_num
    Count_num += 1
    pass


sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA) # max: 320*240
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False) # must be turned off for color tracking

#关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡。
uart = UART(3, 115200)
clock = time.clock() # Tracks FPS.
tim = Timer(4)
tim.init(freq=1)        #每秒一次
tim.callback(Taking_Photo)


i = 0
cnt = 0
while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    #5s一次
    if  Count_num % 5 == 0 and (Count_num != Old_Count_num):
        cnt += 1
        img.save("/Pic/Flag%d.jpg" %(cnt))
        print("cnt = %d" % cnt)

    Old_Count_num = Count_num

    i+=1
    if i % 5 == 0:
            blue_led.on()
    if i % 10 == 0:
            blue_led.off()
