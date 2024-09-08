# Untitled - By: HQ - 周五 7月 25 2019
#############################################################
#	修改时间：2019.7.25
#	文件功能：功能选择函数
#	输    出：
#
#	备    注：此框架现有7个，可根据实际情况更改
##############################################################

import sensor, image, time, network, usocket, sys, pyb
from pyb import UART
from pyb import LED

# LED灯定义
green_led  = LED(1)
blue_led   = LED(2)

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


i = 0

PIN0 = pyb.Pin(pyb.Pin.board.P0, pyb.Pin.IN)
PIN1 = pyb.Pin(pyb.Pin.board.P1, pyb.Pin.IN)
PIN2 = pyb.Pin(pyb.Pin.board.P2, pyb.Pin.IN)

uart = UART(3, 115200)
clock = time.clock()
##########################################################
CountDown = 40  #延时40*100ms
while True:
    clock.tick()

    CountDown -= 1
    pyb.delay(100)
    print("CountDown = %d"%CountDown)
    if CountDown == 0:
        break

    i+=1
    if i % 10 == 0:
        green_led.toggle()
        pass
#########################################################

Port0 = False
Port1 = False
Port2 = False
Port = 0
########################################################
while(True):

    if PIN0.value():
        Port0 = True
    if PIN1.value():
        Port1 = True
    if PIN2.value():
        Port2 = True


    if Port0 and Port1 and Port2:
        Port = 7
        print("77777777777777777")
        break
    if Port0 and Port1 and (not Port2):
        Port = 6
        print("66666666666666666")
        break
    if Port0 and (not Port1) and Port2:
        Port = 5
        print("55555555555555555")
        break
    if Port0 and (not Port1) and (not Port2):
        Port = 4
        print("44444444444444444")
        break
    if (not Port0) and Port1 and Port2:
        Port = 3
        print("33333333333333333")
        break
    if (not Port0) and Port1 and (not Port2):
        Port = 2
        print("22222222222222222")
        break
    if (not Port0) and (not Port1) and Port2:
        Port = 1
        print("11111111111111111")
        break
    if (not Port0) and (not Port1) and (not Port2):
        print("00000000000000000")

    i += 1
    if i % 10 == 0:
        blue_led.toggle()
    pass
########################################################
#                  第一个功能函数
#                       摄像
########################################################

if Port == 1:
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)
    sensor.skip_frames(30)
    pass


record_time = 10000       # 10 seconds in milliseconds
cnt = 0
img_writer = image.ImageWriter("/Stream/stream.bin")
flag_stop = 0


while (Port == 1):
    clock.tick()

    cnt += 1
    if cnt == 1:
        start = pyb.millis()
        green_led.on()
        pass


    if pyb.elapsed_millis(start) < record_time:
        img = sensor.snapshot()
        img_writer.add_frame(img)
        print(clock.avg())
        flag_stop = 1
        pass

    else:
        if flag_stop == 1:
            img_writer.close()
            print("Done")
            flag_stop = 0
            pass

    #print(clock.avg())

    i += 1
    if i % 10 == 0:
        green_led.toggle()
        blue_led.toggle()
    pass
########################################################
#                  第二个功能函数
#
########################################################
if Port == 2:
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.QQVGA)
    sensor.skip_frames(30)
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    pass

while (Port == 2):


    i += 1
    if i % 10 == 0:
        green_led.toggle()
        blue_led.toggle()
    pass

########################################################
#                  第三个功能函数
#
########################################################

if Port == 3:
    pass


while (Port == 3):



    i += 1
    if i % 10 == 0:
        green_led.toggle()
        blue_led.toggle()
    pass

########################################################
#                  第四个功能函数                        #
########################################################
if Port == 4:
    pass

while (Port == 4):


    i += 1
    if i % 10 == 0:
        green_led.toggle()
        blue_led.toggle()
    pass

########################################################
#                  第五个功能函数                        #
########################################################
if Port == 5:
    pass

while (Port == 5):


    i += 1
    if i % 10 == 0:
        green_led.toggle()
        blue_led.toggle()
    pass

########################################################
#                  第六个功能函数                        #
########################################################
if Port == 6:
    pass

while (Port == 6):


    i += 1
    if i % 10 == 0:
        green_led.toggle()
        blue_led.toggle()
    pass

########################################################
#                  第七个功能函数                        #
########################################################
if Port == 7:
    pass

while (Port == 7):


    i += 1
    if i % 10 == 0:
        green_led.toggle()
        blue_led.toggle()
    pass

##########################################################


