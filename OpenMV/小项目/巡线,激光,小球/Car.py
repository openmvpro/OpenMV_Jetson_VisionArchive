#初次使用追小球要算比例系数K=直径像素*实际距离(cm)

from pyb import Pin, Timer, LED, UART
import sensor, image, time, math, json, struct
from GeometryFeature import GeometryFeature


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_vflip(True)               #图像水平翻转
sensor.set_hmirror(True)             #图像垂直翻转

clock = time.clock()

#串口初始化，波特率115200
#8位数据位，无校验位，1位停止位
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

#发送数据函数定义
#格式为2个字符1个整型2个字符
#0xAA,0xAE作为两个帧头给stm32内数据解析函数当作开始数据解析的标识符
#这里加上0x0D和0x0A是为了作为两个帧尾供stm32串口中断服务函数检测，作为结束数据接收的标识符
def send_data_packet(X,Y,Z):
    temp = struct.pack("<bbiiibb",
                         0xAA,
                         0xAE,
                         int(X),
                         int(Y),
                         int(Z),
                         0x0D,
                         0x0A)
    uart.write(temp)

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

#测距
def Proportional_ranging(K,blobs):
    Lm = (blobs[2]+blobs[3])/2
    #初测常数K返回的直径像素Lm
    print('直径像素(Lm)：',Lm)
    #比例常数K
    #实测整个被测物距离*直径像素
    length = K/Lm
    return length

#多颜色组合追踪---------------------------------------------------------------------------------------
def Color_combination():
    thresholds = [(0, 100, 26, 127, -128, 127), # 粉色           色块位: 1
                    (0, 100, -1, 29, 7, 127)] # 绿色              2      若有第四组色块位为:8

    for blob in img.find_blobs(thresholds, pixels_threshold=100, area_threshold=100, merge=True):
        '''if blob.code() == 1:
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_string(blob.x() + 2, blob.y() + 2, "粉")
        if blob.code() == 2:
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_string(blob.x() + 2, blob.y() + 2, "绿")'''
        if blob.code() == 3:
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_string(blob.x() + 2, blob.y() + 2, "粉/绿")
            return blob
        print(blob.cod6e())

#巡线 0x01------------------------------------------------------------------------------------------
IMG_WIDTH  = 64
IMG_HEIGHT = 64
#--------------直线与直角检测部分 START -------------------

BLOB_MAX_WIDTH = 25 # 色块的最大宽度  25
BLOB_MIN_WIDTH = 8 # 色块的最小宽度  8
BLOB_MAX_HEIGHT = 25 # 色块的最大高度
BLOB_MIN_HEIGHT = 7 # 色块的最小高度

# 取样窗口
ROIS = {
    'down': (0, 55, 64, 8), # 横向取样-下方 1
    'middle': (0, 28, 64, 8), # 横向取样-中间 2
    'up': (0, 0, 64, 8), # 横向取样-上方 3
    'left': (0, 0, 8, 64), # 纵向取样-左侧 4
    'right': (56, 0, 8, 64) # 纵向取样-右侧 5
}


# 是否开启debug模式
# 如果是False就不print, 不进行可视化绘制，可以提高帧率
is_debug = True

def find_blobs_in_rois(img):
    '''
    在ROIS中寻找色块，获取ROI中色块的中心区域与是否有色块的信息
    '''
    global ROIS
    global is_debug

    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROIS.keys():
        roi_blobs_result[roi_direct] = {
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }
    for roi_direct, roi in ROIS.items():
        blobs=img.find_blobs(LINE_COLOR_THRESHOLD, roi=roi, merge=True, pixels_area=10)
        if len(blobs) == 0:
            continue

        largest_blob = max(blobs, key=lambda b: b.pixels())
        x,y,width,height = largest_blob[:4]

        if not(width >= BLOB_MIN_WIDTH and width <= BLOB_MAX_WIDTH and height >= BLOB_MIN_HEIGHT and height <= BLOB_MAX_HEIGHT):
            # 根据色块的宽度进行过滤
            continue

        roi_blobs_result[roi_direct]['cx'] = largest_blob.cx()
        roi_blobs_result[roi_direct]['cy'] = largest_blob.cy()
        roi_blobs_result[roi_direct]['blob_flag'] = True

        if is_debug:
            img.draw_rectangle((x,y,width, height), color=(255))

    return roi_blobs_result

def visualize_result(canvas, cx_mean, cx, cy, is_turn_left, is_turn_right, is_t, is_cross, reslut):
    '''
    可视化结果
    '''
    if not(is_turn_left or is_turn_right or is_t or is_cross):
        mid_x = int(canvas.width()/2)
        mid_y = int(canvas.height()/2)
        # 绘制x的均值点
        canvas.draw_circle(int(cx_mean), mid_y, 5, color=(255))
        # 绘制屏幕中心点
        canvas.draw_circle(mid_x, mid_y, 8, color=(0))
        canvas.draw_line((mid_x, mid_y, int(cx_mean), mid_y), color=(255))



    if is_t or is_cross:
        # 十字形或者T形
        canvas.draw_cross(int(cx), int(cy), size=10, color=(255))
        canvas.draw_circle(int(cx), int(cy), 5, color=(255))

    if is_t:
        turn_type = 'T' # T字形状
        #默认左转
        angle = reslut['left']['cx'] - canvas.width()/2
        time.sleep(200)
    elif is_cross:
        turn_type = 'C' # 十字形
        #默认右转
        angle = reslut['left']['cx'] - canvas.width()/2
        time.sleep(200)
    elif is_turn_left:
        turn_type = 'L' # 左转
        angle = reslut['left']['cx'] - canvas.width()/2
        time.sleep(200)
    elif is_turn_right:
        turn_type = 'R' # 右转
        angle = reslut['right']['cx'] - canvas.width()/2
        time.sleep(200)
    else:
        #走直线角度
        turn_type = 'N' # 啥转角也不是
        angle = reslut['middle']['cx'] - canvas.width()/2



    print(angle)

    #发送角度
    send_data_packet(0x01, angle, 0)

    canvas.draw_string(0, 0, turn_type, color=(0))

#--------------直线与直角检测部分 END -------------------
#巡线主功能
def Line_patrol():
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.B64X64)                  # 分辨率为B64X64

    lines = img.find_lines(threshold=1000, theta_margin = 50, rho_margin = 50)
    # 寻找相交的点 要求满足角度阈值
    intersect_pt = GeometryFeature.find_interserct_lines(lines, angle_threshold=(45,90),
    window_size=(IMG_WIDTH, IMG_HEIGHT))

    if intersect_pt is None:
        # 直线与直线之间的夹角不满足阈值范围
        intersect_x = 0
        intersect_y = 0
    else:
        intersect_x, intersect_y = intersect_pt

    reslut = find_blobs_in_rois(img)

    # 判断是否需要左转与右转
    is_turn_left = False
    is_turn_right = False


    if (not reslut['up']['blob_flag'] ) and reslut['down']['blob_flag']:
        if reslut['left']['blob_flag']:
            is_turn_left = True
        if reslut['right']['blob_flag']:
            is_turn_right = True


    # 判断是否为T形的轨道
    is_t = False
    # 判断是否十字形轨道
    is_cross = False

    cnt = 0
    for roi_direct in ['up', 'down', 'left', 'right']:
        if reslut[roi_direct]['blob_flag']:
            cnt += 1
    is_t = cnt == 3
    is_cross = cnt == 4

    # cx_mean 用于确定视角中的轨道中心
    # 用于表示左右偏移量
    cx_mean = 0
    for roi_direct in ['up', 'down', 'middle']:
       if reslut[roi_direct]['blob_flag']:
           cx_mean += reslut[roi_direct]['cx']
       else:
           cx_mean += IMG_WIDTH / 2
    cx_mean /= 3

    # cx, cy 只有在T形区域检测出来的时候才有用，
    # 用于确定轨道中圆形的大致区域， 用于定点， 是计算圆心的一种近似方法

    cx = 0
    cy = 0

    if is_cross or is_t:
        # 只在出现十字形或者T字形才计算圆心坐标
        cnt = 0
        for roi_direct in ['up', 'down']:
            if reslut[roi_direct]['blob_flag']:
                cnt += 1
                cx += reslut[roi_direct]['cx']
        if cnt == 0:
            cx = last_cx
        else:
            cx /= cnt

        cnt = 0
        for roi_direct in ['left', 'right']:
            if reslut[roi_direct]['blob_flag']:
                cnt += 1
                cy += reslut[roi_direct]['cy']
        if cnt == 0:
            cy = last_cy
        else:
            cy /= cnt


    last_cx = cx
    last_cy = cy

    if is_debug:
        visualize_result(img, cx_mean, cx, cy, is_turn_left, is_turn_right, is_t, is_cross, reslut)


#追激光 0x02-----------------------------------------------------------------------------------------
def color_blob(threshold):
    #更改曝光值
    sensor.set_auto_exposure(False, 501)

    blobs = img.find_blobs([threshold])

    if blobs:
        blob=find_max(blobs)
        print('激光像素：',blob.pixels())
        if blob.pixels() <300:
            img.draw_rectangle(blob[0:4])
            cx = blob[5]
            cy = blob[6]
            img.draw_cross(blob[5], blob[6])
            #激光坐标
            deflection_angle = cx - img.width()/2
            #使用测距前调K值
            length=Proportional_ranging(640,blob)
            send_data_packet(0x02, deflection_angle, length)
            print("转弯角度:{0:+f} 光学距离:{1:+f}" .format(deflection_angle, length))

    else:
       send_data_packet(0x02, '0x02', '0x02')


#追小球 0x03-----------------------------------------------------------------------------------------
def Chasing_ball():
    blobs = Color_combination()
    #blobs的返回值为：
    #[{"x":104, "y":46, "w":48, "h":37, "pixels":1365, "cx":127, "cy":65, "rotation":3.033448, "code":1, "count":1, "perimeter":204, "roundness":0.675996}]
    #                                    像素数量        中心x坐标            色块的旋转弧度
    if blobs:
        img.draw_rectangle(blobs[0:4]) # rect 找到的色块画矩形
        img.draw_cross(blobs[5], blobs[6]) # cx, cy 找到的色块中心画十字

        x_error = blobs[5]-img.width()/2
        length=Proportional_ranging(1125,blobs)
        send_data_packet(0x03,x_error,length)
        print("转弯角度:{0:+f} 光学距离:{1:+f}" .format(x_error, length))

    else:
       print('无目标')
       send_data_packet(0x03, '0x03', '0x03')

last_cx = 0
last_cy = 0

#直线灰度图颜色阈值
LINE_COLOR_THRESHOLD = [(0, 88)]

#激光阈值
laser_threshold = (0, 100, 62, 29, 7, 127)
#(47, 100, -128, 127, -128, 127)

#小球阈值
ball_threshold   = (0, 100, -128, 127, -128, -17)

while(True):
    #启动提示灯
    #LED(2).on()

    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    #巡线
    Line_patrol()
    #追激光
    #color_blob(laser_threshold)
    #追小球
    # Chasing_ball()
