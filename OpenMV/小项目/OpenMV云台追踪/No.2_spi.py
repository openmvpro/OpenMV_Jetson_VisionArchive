import sensor, image, time, sys, json
from pyb import Pin, SPI, UART
from pyb import Servo
from pid import PID

pan_servo=Servo(1)
tilt_servo=Servo(2)

#pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.35, i=0, imax=90)#在线调试使用这个PID
tilt_pid = PID(p=0.35, i=0, imax=90)#在线调试使用这个PID

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # must be this
sensor.set_framesize(sensor.QQQVGA) # must be this
sensor.skip_frames(time = 2000) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_auto_gain(False) # must be turned off for color tracking
clock = time.clock() # Tracks FPS.

uart = UART(3,115200)

cs  = Pin("P3", Pin.OUT_OD)
rst = Pin("P6", Pin.OUT_PP)
rs  = Pin("P9", Pin.OUT_PP)
# # OpenMV上的硬件SPI总线都是2
spi = SPI(2, SPI.MASTER, baudrate=int(1000000000/66), polarity=0, phase=0)

def maxs(a,b):#两数取大
    return (((a+b)+abs(a-b))//2)

def mins(a,b):#两数取小
    return(((a-b)+abs(-a-b))//2)

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

def find_circles(b):
    if b :
        for c in img.find_circles(threshold = 2500, x_margin = 10, y_margin = 10, r_margin = 10,
                r_min = 2, r_max = 100, r_step = 2):  #threshold检测像素点大小，step渐增半径数
            area = (c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r())#area为识别到的圆的区域，即圆的外接矩形框 x,y为圆中心坐标
            statistics = img.get_statistics(roi=area)#像素颜色统计
            #(0,100,0,120,0,120)是红色的阈值，所以当区域内的众数（也就是最多的颜色），范围在这个阈值内，就说明是红色的圆。
            #l_mode()，a_mode()，b_mode()是L通道，A通道，B通道的众数。
            if mins(b[0],b[1])<statistics.l_mode()<maxs(b[0],b[1]) and mins(b[2],b[3])<statistics.a_mode()<maxs(b[2],b[3]) and mins(b[4],b[5])<statistics.b_mode()<maxs(b[4],b[5]):#if the circle is red
                img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))#识别到的b色域的圆用红色的圆框出来
            a = {str(c[0]),str(c[1]),str(c[2])}
            a_str = json.dumps(a)
            output_str = json.dumps(statistics)
            uart.write(output_str+'\n')
            uart.write(a_str+'\n')

    else:
        for c in img.find_circles(threshold = 2500, x_margin = 10, y_margin = 10, r_margin = 10,
                r_min = 2, r_max = 100, r_step = 2):  #threshold检测像素点大小，step渐增半径数
            area = (c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r())

            #area为识别到的圆的区域，即圆的外接矩形框 x,y为中心坐标
            statistics = img.get_statistics(roi=area)#像素颜色统计
            #(0,100,0,120,0,120)是红色的阈值，所以当区域内的众数（也就是最多的颜色），范围在这个阈值内，就说明是红色的圆。
            #l_mode()，a_mode()，b_mode()是L通道，A通道，B通道的众数。
            if 64<statistics.l_mode()<100 and -128<statistics.a_mode()<1 and -128<statistics.b_mode()<127:#if the circle is red
                img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))#识别到的红色圆形用红色的圆框出来
            else:
                img.draw_rectangle(area, color = (255, 255, 255))
                #将非红色的圆用白色的矩形框出来
            a = {str(c[0]),str(c[1]),str(c[2])}
            a_str = json.dumps(a)
            output_str = json.dumps(statistics)
            uart.write(output_str+'\n')
            uart.write(a_str+'\n')

    write_command(0x2C) # Write image command...
    write_image(img)

def write_command_byte(c):
    cs.low()
    rs.low()
    spi.send(c)
    cs.high()

def write_data_byte(c):
    cs.low()
    rs.high()
    spi.send(c)
    cs.high()

def write_command(c, *data):
    write_command_byte(c)
    if data:
        for d in data: write_data_byte(d)

def write_image(img):
    cs.low()
    rs.high()
    spi.send(img)
    cs.high()

# 重启
rst.low()
time.sleep(100)
rst.high()
time.sleep(100)

write_command(0x11) # Sleep Exit
time.sleep(120)

# Memory Data Access Control
write_command(0x36, 0xC0)

# 设置 Pixel Format 接口
write_command(0x3A, 0x05)

# 开启显示
write_command(0x29)

b=()

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().帧率
    img = sensor.snapshot().lens_corr(1.8) # Take a picture and return the image.
    img.replace(vflip=1)#画面垂直翻转

    find_circles(b)

    if uart.any():
        a = uart.read().decode()
        c = a.replace("{","").replace("}","").replace("'","").replace("(","").replace(")","").split(",")#将接收的字符串分割（依传输数据格式待完善）
        rgb_tuple = list(map(int,c))#将字符串转为整型存为列表再转元组
        b = image.rgb_to_lab(rgb_tuple)

    if b :
        blobs = img.find_blobs([b])#找出所有b色域的色块
        if blobs:
            max_blob = find_max(blobs)#找出最大b色域的色块
            pan_error = max_blob.cx()-img.width()/2
            tilt_error = max_blob.cy()-img.height()/2

            img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy 最大b色域的色块中心画十字

            pan_output=pan_pid.get_pid(pan_error,1)/2
            tilt_output=tilt_pid.get_pid(tilt_error,1)

            pan_servo.angle(pan_servo.angle()+pan_output)
            tilt_servo.angle(tilt_servo.angle()-tilt_output)

    else:
        red_threshold  = (64, 100, 1, -128, -128, 127)
        blobs = img.find_blobs([red_threshold])
        if blobs:
            max_blob = find_max(blobs)
            pan_error = max_blob.cx()-img.width()/2
            tilt_error = max_blob.cy()-img.height()/2

            img.draw_rectangle(max_blob.rect()) # rect

            pan_output=pan_pid.get_pid(pan_error,1)/2
            tilt_output=tilt_pid.get_pid(tilt_error,1)

            pan_servo.angle(pan_servo.angle()+pan_output)
            tilt_servo.angle(tilt_servo.angle()-tilt_output)
