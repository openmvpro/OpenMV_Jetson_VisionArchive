#############################################################
#	修改时间：2019.7.24
#	文件功能：寻二维码
#	输    出：FormType		类型
#							可以返回当前坐标，也可以返回下一个坐标
#			  Loaction0		像素点x
#			  Location1		像素点y
#
#	备    注：使用前要先知道payload里面数据位在哪里
##############################################################

import sensor, image, time
from pyb import UART
from pyb import LED

# LED灯定义
green_led  = LED(1)
blue_led   = LED(2)
red_led    = LED(3)  #此灯无用

ROI = (10, 0, 140, 120)
black_threshold = [(0, 64)]


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

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
#sensor.set_windowing((160,120))
sensor.skip_frames(30) # 修改sensor配置之后， 跳过30帧
sensor.set_auto_gain(False) # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False) # must be turned off for color tracking
uart = UART(3, 115200)
clock = time.clock()


i = 0

while(True):
    clock.tick()
    img = sensor.snapshot()
    img.lens_corr(1.0) # strength of 1.8 is good for the 2.8mm lens.

    for code in img.find_qrcodes():
        img.draw_rectangle(code.rect(), color = (255, 255, 255))
        print(code)

        px = code.x() + int(code.w()/2)
        py = code.y() + int(code.h()/2)

        msg = code.payload()

        print("msg: %s" %msg)

        #next_x = int(msg[1])*10 + int(msg[2])
        #next_y = int(msg[5])*100 + int(msg[6])*10 + int(msg[7])
        #print("next_x: %d ,next_y: %d" %(next_x, next_y))
        #uart.write(UART_Send(80, next_x, next_y))

    i+=1
    if i % 10 == 0:
        green_led.on()
        blue_led.on()
    if i % 20 == 0:
        green_led.off()
        blue_led.off()
    pass

