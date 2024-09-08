####################################################################################################
#2020/11/20 18:40
#灭火机器人
#版本V3.0
#要求：
#    1、等待接受单片机信号
#    2、接受高电平信号，舵机载上OpenMV和风扇从左到右正负90°检测是否有火焰，如果有发送信号1给单片机启动风扇4s，
#       火焰熄灭后发送信号2给单片机
#
#功能说明：  P0：高电平启动OpenMV
#          P4：TXD
#          P5：RXD
#          P7:舵机信号线
#
#标志位      1：检测到火焰，启动风扇
#           2：火熄灭，按原路线行驶
#1.3ms    -17    启动电机
#1ms      -45    停止电机
#####################################################################################################


import sensor, image, time, math, json,struct
from pyb import Pin, Timer, LED, UART, Servo
from pid import PID

#云台配置--------------------------------------------------------------------------------------------
pan_servo = Servo(1)
dianji_servo = Servo(2)
pan_pid   = PID(p=0.07, i=0, imax=90)#在线调试使用这个PID

#闪光灯定义-------------------------------------------------------------------------------------------
red_led	    = LED(1)
green_led    =  LED(2)
blue_led	    = LED(3)

#引脚'P0'‘P1‘高电平识别-------------------------------------------------------------------------------
pin0 = Pin('P0', Pin.IN, Pin.PULL_DOWN)#设置p_in为输入引脚，并开启下拉电阻

#初始化----------------------------------------------------------------------------------------------
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False) # turn this off.
#sensor.set_vflip(True)               #图像水平翻转
#sensor.set_hmirror(True)             #图像垂直翻转

#更改曝光值
sensor.set_auto_exposure(False, 1200)

clock = time.clock()

#串口配置及协议----------------------------------------------------------------------------------------
#串口初始化，波特率115200
#8位数据位，无校验位，1位停止位
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

#发送数据函数定义
#格式为2个字符1个整型2个字符
#0xAA,0xAE作为两个帧头给stm32内数据解析函数当作开始数据解析的标识符
#这里加上0x0D和0x0A是为了作为两个帧尾供stm32串口中断服务函数检测，作为结束数据接收的标识符
def send_data_packet(X):
    temp = struct.pack("<bbibb",
                         0xAA,
                         0xAE,
                         int(X),
                         0x0D,
                         0x0A)

    Temp=bytearray(temp)
    #print(Temp)
    uart.write(Temp)

#找最大值--------------------------------------------------------------------------------------------
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

#初始定义的变量----------------------------------------------------------------------------------------
#火焰阈值
laser_threshold = (21, 100, -128, 18, -128, 127)#(8, 100, -128, 127, -128, 127)#(90, 100, -2, 127, -128, 127)#(19, 100, -128, 29, -128, 127)
#云台初始值
m=90#水平方向初始位
#找到火焰标志变量
flag =0
#找到火焰计算次数
num =0
num1=0

dianji_servo.angle(-45)
time.sleep(3000)


while(True):
    clock.tick()

    #启动提示灯
    green_led. on()

    img = sensor.snapshot().lens_corr(1.8)
    print('P0',pin0.value())

    if pin0.value() and flag==0:

        #白灯接收到高电平
        green_led.on()
        red_led.on()
        blue_led.on()
        print('m=',m)
        print('接收到灭火信号啦')

        blob = img.find_blobs([laser_threshold])
        if blob and m>-90:
            blobs=find_max(blob)

            img.draw_rectangle(blobs[0:4])

            pan_error = blobs.cx()-img.width()/2
            pan_output=pan_pid.get_pid(pan_error,1)/2
            pan_servo.angle(pan_servo.angle()-pan_output)

            #计数100次
            num+=1
            print('num',num)
            if num>20:
                flag=1
                #send_data_packet('1')
                dianji_servo.angle(-17)
                time.sleep(3000)
                print('首次找到火焰了')
            else:
                flag=0

            print('flag=',flag)

        else:
            num=0
            print('num=',num)
            m=round(m - 1,1)
            if m<-90:
                send_data_packet('1')
                dianji_servo.angle(-45)
                print('时间到了，没有找到火焰')
            else:
                print('没有找到火焰')
                pan_servo.angle(m)

    elif pin0.value() and flag==1:
        #白灯接收到高电平
        green_led.on()
        red_led.on()
        blue_led.on()

        print('接收到灭火信号啦也找到火焰啦')

        blob = img.find_blobs([laser_threshold])
        if blob and m>-90:
            blobs=find_max(blob)

            img.draw_rectangle(blobs[0:4])

            pan_error = blobs.cx()-img.width()/2
            pan_output=pan_pid.get_pid(pan_error,1)/2
            pan_servo.angle(pan_servo.angle()-pan_output)

            #计数100次
            num1+=1
            print('num1',num1)
            if num1>20:
                #send_data_packet('1')
                dianji_servo.angle(-17)
                time.sleep(3000)
                print('第二次找到火焰了')
        else:
            num1=0
            send_data_packet('1')
            dianji_servo.angle(-45)
            print('灭火了，大功告成')

    else:
        green_led.off()
        red_led.off()
        blue_led.off()

        print('没有接收到信号')

        flag =0
        num  =0
        num1 =0

        m=90
        pan_servo.angle(m)
