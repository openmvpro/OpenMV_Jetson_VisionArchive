import sensor, image, time, network, usocket, sys, json
from pyb import UART

#串口配置--------------------------------------------------------------------------------------------
#串口初始化，波特率115200
#8位数据位，无校验位，1位停止位
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

#---------------------------------------------------------------------------------------------------

#wifi配置--------------------------------------------------------------------------------------------
SSID ='OPENMV_AP'    # Network SSID
KEY  ='1234567890'    # Network key (must be 10 chars)
HOST = ''           # Use first available interface
PORT = 8080         # Arbitrary non-privileged port

# 在AP模式下启动wlan模块。
wlan = network.WINC(mode=network.WINC.MODE_AP)
wlan.start_ap(SSID, key=KEY, security=wlan.WEP, channel=2)
#---------------------------------------------------------------------------------------------------
sensor.reset()
sensor.set_contrast(1)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()                    # Tracks FPS.

#串口-----------------------------------------------------------------------------------------------
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
    uart.write(temp)

#WIFI-----------------------------------------------------------------------------------------------
def start_streaming(s):
    print ('Waiting for connections..')
    client, addr = s.accept()
    # 将客户端套接字超时设置为2秒
    client.settimeout(2.0)
    print ('Connected to ' + addr[0] + ':' + str(addr[1]))

    # 从客户端读取请求
    data = client.recv(1024)
    # 应该在这里解析客户端请求

    # 发送多部分head
    client.send("HTTP/1.1 200 OK\r\n" \
                "Server: OpenMV\r\n" \
                "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n" \
                "Cache-Control: no-cache\r\n" \
                "Pragma: no-cache\r\n\r\n")

    # FPS clock
    clock = time.clock()

    # 开始流媒体图像
    #注：禁用IDE预览以增加流式FPS。
    while (True):
        clock.tick()
        #功能区
        img=sensor.snapshot().lens_corr(1.8)
        print(clock.fps())
        cframe = img.compressed(quality=35)
        header = "\r\n--openmv\r\n" \
                 "Content-Type: img/jpeg\r\n"\
                 "Content-Length:"+str(cframe.size())+"\r\n\r\n"
        client.send(header)
        client.send(cframe)



while(True):
    #串口
    send_data_packet('hello')

    #WIFI
    '''
    # 创建服务器套接字
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    try:
        # Bind and listen
        s.bind([HOST, PORT])
        s.listen(5)

        # 设置服务器套接字超时
        # 注意：由于WINC FW bug，如果客户端断开连接，服务器套接字必须
        # 关闭并重新打开。在这里使用超时关闭并重新创建套接字。
        s.settimeout(3)
        start_streaming(s)
    except OSError as e:
        s.close()
        print("socket error: ", e)
        #sys.print_exception(e)
    '''
