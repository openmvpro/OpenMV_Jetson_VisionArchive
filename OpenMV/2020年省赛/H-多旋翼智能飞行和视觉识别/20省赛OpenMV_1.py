####################################################################################################
#2020/10/09 23:45pm
#版本1.0
#实现功能：
#1、找二维码并发送位置信息
#2、根据'P1'高低电平进行AprilTag标记跟踪
####################################################################################################

#模块导入--------------------------------------------------------------------------------------------
import sensor, image, time, sys, json
from pyb import UART
from pyb import Pin
from pyb import LED

#引脚'P1'高电平识别Apriltags--------------------------------------------------------------------------
pin1 = Pin('P1', Pin.IN, Pin.PULL_DOWN)#设置p_in为输入引脚，并开启上拉电阻

#串口配置--------------------------------------------------------------------------------------------
uart = UART(3, 115200)

#闪光灯定义-------------------------------------------------------------------------------------------
red_led	 = LED(1)
green_led   = LED(2)
blue_led	= LED(3)

#感光元件定义-----------------------------------------------------------------------------------------
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(20)
sensor.set_auto_whitebal(True)
sensor.set_auto_gain(True)
#关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡。
clock = time.clock() # Tracks FPS.

#传输协议--------------------------------------------------------------------------------------------
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

#初始化定义-------------------------------------------------------------------------------------------
#拍照计数
i=0
#照片顺序
a=1

while(True):
    clock.tick()
    #img.draw_rectangle((120,90,80,60))
    #功能区-----------------------------------------------------------------
    #分辨率     标志位
    #QVGA      1
    #QQVGA     2
    #QQQVGA    3
    #B64X64    4
    #无用       90

    #高电平开启识别Apriltags
    uart.write(UART_Send(2,0,0))

    img = sensor.snapshot().lens_corr(1.8)

    #将数据保存到SD卡
    w = open('data_2.json','a+')

    for tag in img.find_apriltags(families=image.TAG16H5):
        img.draw_rectangle(tag.rect())
        img.draw_cross(tag.cx(), tag.cy())

        X = tag.cx()
        Y = tag.cy()

        print('Apriltags_X',X,'Apriltags_Y',Y)
        w.write(str(tag.id()))
        w.write('\n')
        uart.write(UART_Send(100,X,Y))

    if pin1.value():
        print('a',a)
        print('i',i)
        green_led. on()
        red_led. on()
        blue_led. on()
        if a==1 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                img.save("0.0.jpg")
                i+=1


            elif i==1:
                img.save("0.1.jpg")
                i+=1


            elif i==2:
                img.save("0.2.jpg")
                i+=1


            elif i==3:
                img.save("0.3.jpg")
                i+=1


            elif i==4:
                img.save("0.4.jpg")
                i+=1
                a=2


        elif a==2 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                img.save("1.0.jpg")
                i+=1

            elif i==1:
                img.save("1.1.jpg")
                i+=1

            elif i==2:
                img.save("1.2.jpg")
                i+=1

            elif i==3:
                img.save("1.3.jpg")
                i+=1

            elif i==4:
                img.save("1.4.jpg")
                i+=1
                a=3


        elif a==3 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                img.save("2.0.jpg")
                i+=1


            elif i==1:
                img.save("2.1.jpg")
                i+=1


            elif i==2:
                img.save("2.2.jpg")
                i+=1


            elif i==3:
                img.save("2.3.jpg")
                i+=1


            elif i==4:
                img.save("2.4.jpg")
                i+=1
                a=4


        elif a==4 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                img.save("3.0.jpg")
                i+=1


            elif i==1:
                img.save("3.1.jpg")
                i+=1


            elif i==2:
                img.save("3.2.jpg")
                i+=1


            elif i==3:
                img.save("3.3.jpg")
                i+=1


            elif i==4:
                img.save("3.4.jpg")
                i+=1
                a=5


        elif a==5 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                img.save("4.0.jpg")
                i+=1


            elif i==1:
                img.save("4.1.jpg")
                i+=1


            elif i==2:
                img.save("4.2.jpg")
                i+=1


            elif i==3:
                img.save("4.3.jpg")
                i+=1


            elif i==4:
                img.save("4.4.jpg")
                i+=1
                a=6
    else:
        i = 0
        green_led.off()
        red_led.off()
        blue_led.off()
    w.close()
