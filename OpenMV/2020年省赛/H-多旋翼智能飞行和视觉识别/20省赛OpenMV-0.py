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
sensor.set_framesize(sensor.QVGA)
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
#白色阈值
thresholds = [(193, 255)]

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

    #'P1'电平
    #print(pin1.value())

    if pin1.value():
        #高电平提示灯
        green_led.on()
        red_led.on()
        blue_led.on()

        #将数据保存到SD卡
        w = open('data_2.json','a+')

        #高电平开启识别Apriltags
        sensor.set_framesize(sensor.QQVGA)
        uart.write(UART_Send(2,0,0))
        img = sensor.snapshot().lens_corr(1.8)

        for blob in img.find_blobs(thresholds, pixels_threshold=2000, area_threshold=2000,merge=True):
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())

            #提前识别好哪个家族的Apriltags
            for tag in img.find_apriltags(families=image.TAG16H5):
                img.draw_rectangle(tag.rect(), color = (255, 0, 0))
                img.draw_cross(tag.cx(), tag.cy(), color = (0, 255, 0))
                X = tag.cx()
                Y = tag.cy()
                print('Apriltags_X',X,'Apriltags_Y',Y)
                uart.write(UART_Send(100,X,Y))

                w.write(str(tag))
                w.write('\n')
                print('apriltags内容：',tag)

            w.close()
    else:
        #画十
        img.draw_cross(160,120, color=(0,255,255), size=10, thickness=5)

        #低电平提示灯
        green_led.off()
        red_led.off()
        blue_led.off()

        uart.write(UART_Send(1,0,0))

        #将数据保存到SD卡
        f = open('data_1.json','a+')

        for blob in img.find_blobs(thresholds, pixels_threshold=2000, area_threshold=2000,merge=True):
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())

            #识别二维码
            for code in img.find_qrcodes():
                f.write(str(code[4]))
                f.write('\n')
                print('openmv内容：',code[4])

                CX=int(code[0]+code[2]/2)
                CY=int(code[1]+code[3]/2)

                arrive_x=abs(160-CX)
                arrive_y=abs(120-CY)

                img.draw_rectangle(code.rect())
                img.draw_cross(CX, CY,thickness=5)

                if code[4]=='0':
                    uart.write(UART_Send(80,CX,CY))
                    print('OK0')
                    if arrive_x<5 and arrive_y<5 :
                        uart.write(UART_Send(70,CX,CY))

                if code[4]=='1':
                    uart.write(UART_Send(81,CX,CY))
                    print('OK1')
                    if arrive_x<5 and arrive_y<5 :
                        uart.write(UART_Send(71,CX,CY))


                if code[4]=='2':
                    uart.write(UART_Send(82,CX,CY))
                    print('OK2')
                    if arrive_x<5 and arrive_y<5 :
                        uart.write(UART_Send(72,CX,CY))

                if code[4]=='3':
                    uart.write(UART_Send(83,CX,CY))
                    print('OK3')
                    if arrive_x<5 and arrive_y<5 :
                        uart.write(UART_Send(73,CX,CY))

                if code[4]=='4':
                    uart.write(UART_Send(84,CX,CY))
                    print('OK4')
                    if arrive_x<5 and arrive_y<5 :
                        uart.write(UART_Send(74,CX,CY))

            f.close()
            print('fps',clock.fps())
