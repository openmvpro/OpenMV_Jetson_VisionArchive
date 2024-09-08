#左转，完成左转，右转，完成右转，四种T，十字型
import sensor
import image
import time
import math
import pyb , json
from pyb import Pin, Timer, UART,LED
from GeometryFeature import GeometryFeature

# 是否开启debug模式
# 如果是False就不print, 不进行可视化绘制，可以提高帧率
is_debug = True
#--------------感光芯片配置  START -------------------

DISTORTION_FACTOR = 1.5 # 设定畸变系数
IMG_WIDTH  = 64
IMG_HEIGHT = 64
def init_sensor():
    '''
    初始化感光芯片
    '''
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.B64X64)                  # 分辨率为B64X64
    sensor.skip_frames(time=2000)
    sensor.set_auto_gain(False)                         # 颜色追踪关闭自动增益
    sensor.set_auto_whitebal(False)                     # 颜色追踪关闭白平衡

init_sensor()
#--------------感光芯片配置  END -------------------

is_need_send_data = False # 是否需要发送数据的信号标志

#--------------串口发送 start -------------------
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
flag = 0
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

uart = UART(3, 115200)
#--------------串口发送 end ---------------------------


#--------------直线与直角检测部分 START -------------------

INTERSERCT_ANGLE_THRESHOLD = (45,90)

# 直线灰度图颜色阈值
LINE_COLOR_THRESHOLD = [(20, 137)]
# 如果直线是白色的，阈值修改为：
# LINE_COLOR_THRESHOLD = [(128, 255)]

# 取样窗口
ROIS = {
    'down':  (5, 55, 54, 10), # 横向取样-下方 1
    'middle':(5, 28, 54, 10), # 横向取样-中间 2
    'up':    (5, 0 , 54, 8), # 横向取样-上方 3
    'left':  (0, 0, 8 , 40), # 纵向取样-左侧 4
    'right': (56, 0, 8, 40) # 纵向取样-右侧 5
}


BLOB_MAX_WIDTH = 20 # 色块的最大宽度
BLOB_MIN_WIDTH = 7  # 色块的最小宽度
BLOB_MAX_HEIGHT = 20 # 色块的最大高度
BLOB_MIN_HEIGHT = 8 # 色块的最小高度


def find_blobs_in_rois(img):
    '''
    在ROIS中寻找色块，获取ROI中色块的中心区域与是否有色块的信息
    '''
    global ROIS
    global is_debug

    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROIS.keys():    #keys() 函数以列表返回一个字典所有的键
        roi_blobs_result[roi_direct] = {     #字典嵌套字典，roi_blobs_result嵌套了roi_direct
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }

    for roi_direct, roi in ROIS.items():  #遍历字典ROIS，items()以列表返回可遍历的(键, 值) 元组数组。
        blobs=img.find_blobs(LINE_COLOR_THRESHOLD, roi=roi, merge=True, pixels_area=10)
        if len(blobs) == 0:
            continue

        largest_blob = max(blobs, key=lambda b: b.pixels())
        x,y,width,height = largest_blob[:4]

        if not(width >= BLOB_MIN_WIDTH and width <= BLOB_MAX_WIDTH and height >= BLOB_MIN_HEIGHT and height <= BLOB_MAX_HEIGHT):
            # 根据色块的宽度进行过滤
            continue#continue 语句用来告诉Python跳过当前循环的剩余语句，然后继续进行下一轮循环。

        roi_blobs_result[roi_direct]['cx'] = largest_blob.cx()
        roi_blobs_result[roi_direct]['cy'] = largest_blob.cy()
        roi_blobs_result[roi_direct]['blob_flag'] = True

        if is_debug:
            img.draw_rectangle((x,y,width, height), color=(255))

    return roi_blobs_result

def visualize_result(canvas, cx_mean, cx, cy, is_straight, is_turn, is_alr_turn, is_t, is_cross):
    '''
    可视化结果
    '''
    turn_type = 'N' # 啥转角也不是
    num_t = 0 #计数是第几号T
    for t in is_t:
        if t==True:
            num_t +=1
    if (num_t==1):
        turn_type = 'T'
        # 十字形或者T形
        canvas.draw_cross(int(cx), int(cy), size=10, color=(255))
        canvas.draw_circle(int(cx), int(cy), 5, color=(255))
    if  is_cross:
        canvas.draw_cross(int(cx), int(cy), size=10, color=(255))
        canvas.draw_circle(int(cx), int(cy), 5, color=(255))
    if is_straight:
        turn_type = 'S' #直线
    elif is_cross:
        turn_type = 'C' # 十字形
    elif is_turn[0]:
        turn_type = 'L' # 左转
    elif is_turn[1]:
        turn_type = 'R' # 右转
    elif is_alr_turn[0]:
        turn_type = 'LA' # 完成左转
    elif is_alr_turn[1]:
        turn_type = 'RA' # 完成右转

    canvas.draw_string(0, 0, turn_type, color=(0))

#--------------直线与直角检测部分 END -------------------

#---------------------MAIN-----------------------
last_cx = 0
last_cy = 0

while True:

    # 拍摄图片
    img = sensor.snapshot().lens_corr(1.5)    # 去除图像畸变
    reslut = find_blobs_in_rois(img)
    #判断是否是直线
    is_straight = False

    # 判断是否需要左转与右转
    is_turn_left = False
    is_turn_right = False
    is_turn = [is_turn_left,is_turn_right]
    # 判断是否完成左转或者完成右转
    is_alr_turn_left = False
    is_alr_turn_right = False
    is_alr_turn = [is_alr_turn_left,is_alr_turn_right]
    # 判断是否为T形的轨道
    is_1t = False
    is_2t = False
    is_3t = False
    is_4t = False
    is_t = [is_1t,is_2t,is_3t,is_4t]

    # cx_mean 用于确定视角中的轨道中心
    # 用于表示左右偏移量
    cx_mean = 0
    for roi_direct in ['up', 'down', 'middle']:
        if reslut[roi_direct]['blob_flag']:
            cx_mean += reslut[roi_direct]['cx']
        else:
            cx_mean += IMG_WIDTH / 2
    cx_mean /= 3
    cx_mean = int(cx_mean)
    '''
    # cy_mean 用于确定视角中的轨道中心
    # 用于表示左右偏移量
    cy_mean = 0
    for roi_direct in ['right', 'left', 'middle']:
        if reslut[roi_direct]['blob_flag']:
            cy_mean += reslut[roi_direct]['cx']
        else:
            cy_mean += IMG_WIDTH / 2
    cy_mean /= 3
    cy_mean = int(cy_mean)
    '''
    #print('reslut',reslut)


#------------------------得到两条线的交点坐标 start----------------------------------------
    lines = img.find_lines(threshold=1000, theta_margin = 50, rho_margin = 50)#
    # 寻找相交的点 要求满足角度阈值
    intersect_pt = GeometryFeature.find_interserct_lines(lines, angle_threshold=(45,110), window_size=(IMG_WIDTH, IMG_HEIGHT))
    if intersect_pt is None:
        # 直线与直线之间的夹角不满足阈值范围
        intersect_x = 0
        intersect_y = 0
    else:
        intersect_x, intersect_y = intersect_pt

#--------------------------得到两条线的交点坐标 end------------------------------------------

    #判断直线
    if (not reslut['left']['blob_flag'] ) and (not reslut['right']['blob_flag']):
        if reslut['up']['blob_flag'] and ( reslut['down']['blob_flag']):
            is_straight = True


    #判断左转还是右转
    if (not reslut['up']['blob_flag'] ) and (reslut['down']['blob_flag']):
        if reslut['left']['blob_flag'] and (not reslut['right']['blob_flag']):
            is_turn[0] = True
        if reslut['right']['blob_flag'] and (not reslut['left']['blob_flag']):
            is_turn[1] = True
    #判断完成右转还是完成左转
    if (not reslut['down']['blob_flag'] ) and reslut['up']['blob_flag']:
        if reslut['left']['blob_flag'] and (not reslut['right']['blob_flag']):
            is_alr_turn[0] = True
            print(31)
        if reslut['right']['blob_flag'] and (not reslut['left']['blob_flag']):
            is_alr_turn[1] = True
            print(33)

    # 判断是否十字形轨道
    is_cross = False
    #判断是1号T还是2号T
    if (reslut['left']['blob_flag'] ) and reslut['right']['blob_flag']:
        if reslut['up']['blob_flag'] and (not reslut['down']['blob_flag'] ):
            is_t[0] = True
        if reslut['down']['blob_flag'] and (not reslut['up']['blob_flag']):
            is_t[1] = True
    #判断是3号T还是4号T
    if (reslut['up']['blob_flag'] ) and reslut['down']['blob_flag']:
        if reslut['right']['blob_flag'] and (not reslut['left']['blob_flag']):
            is_t[2] = True
        if reslut['left']['blob_flag']and (not reslut['right']['blob_flag']):
            is_t[3] = True

#-----------------------走直线并且发送坐标------------------------------------------
    if (is_straight==True):
        print([cx_mean,reslut['up']['cy']])
        uart.write(UART_Send(39,int(cx_mean),int(reslut['up']['cy'])))
#-----------------------左转并且发送坐标----------------000---------------------------------
    if is_turn[0]:
        #img.draw_rectangle((22, 22,20, 20))
        if not((22<intersect_x<42) and (22<intersect_y<42)):
            print(intersect_x,intersect_y)
            uart.write(UART_Send(30,int(intersect_x),int(intersect_y)))
        else:
            uart.write(UART_Send(90,0,0))

#-----------------------完成左转并且发送坐标----------------------------------------
    if (is_alr_turn[0]==True):
        print(intersect_x,intersect_y)
        uart.write(UART_Send(31,int(intersect_x),int(intersect_y)))

#-----------------------右转并且发送坐标----------------------------------------
    if (is_turn[1]==True):
        #img.draw_rectangle((22, 22,20, 20))
        if not(((22<intersect_x<42) and (22<intersect_y<42))):
            print(intersect_x,intersect_y)
            uart.write(UART_Send(32,int(intersect_x),int(intersect_y)))
        else:
            uart.write(UART_Send(90,0,0))

#-----------------------完成右转并且发送坐标----------------------------------------
    if (is_alr_turn[1]==True):
        print(intersect_x,intersect_y)
        uart.write(UART_Send(33,int(intersect_x),int(intersect_y)))

#-----------------------1号T并且发送坐标----------------------------------------
    if (is_t[0]==True):
        img.draw_rectangle((22, 22,20, 20))
        if not(((22<intersect_x<42) and (22<intersect_y<42))):
            print(34,intersect_x,intersect_y)
            uart.write(UART_Send(34,int(intersect_x),int(intersect_y)))
        else:
            uart.write(UART_Send(90,0,0))
            print(0,0)


#-----------------------2号T并且发送坐标----------------------------------------
    if (is_t[1]==True):
        img.draw_rectangle((17, 17,30, 30))
        if not(((17<intersect_x<47) and (17<intersect_y<47))):
            print(35,intersect_x,intersect_y)
            uart.write(UART_Send(35,int(intersect_x),int(intersect_y)))
        else:
            print(0,0)
            uart.write(UART_Send(90,0,0))

#-----------------------3号T并且发送坐标----------------------------------------
    if (is_t[2]==True):
        img.draw_rectangle((22, 22,20, 20))
        if not(((22<intersect_x<42) and (22<intersect_y<42))):
            print(36,intersect_x,intersect_y)
            uart.write(UART_Send(36,int(intersect_x),int(intersect_y)))
        else:
            print(0,0)
            uart.write(UART_Send(90,0,0))

#-----------------------4号T并且发送坐标----------------------------------------
    if (is_t[3]==True):
        img.draw_rectangle((22, 22,20, 20))
        if not(((22<intersect_x<42) and (22<intersect_y<42))):
            print(37,intersect_x,intersect_y)
            uart.write(UART_Send(37,int(intersect_x),int(intersect_y)))
        else:
            uart.write(UART_Send(90,0,0))
#-----------------------什么都没识别到----------------------------------------
    if not(is_straight or is_turn[0] or is_turn[1] or is_alr_turn[0] or is_alr_turn[1] or is_t[0] or is_t[1] or is_t[2] or is_t[3]):
        print('none')
        uart.write(UART_Send(90,0,0))

    cnt = 0
    for roi_direct in ['up', 'down', 'left', 'right']:
        if reslut[roi_direct]['blob_flag']:
            cnt += 1
    if cnt==4:
        is_cross = True
        print(38)


    # cx, cy 只有在T形区域检测出来的时候才有用，
    # 用于确定轨道中圆形的大致区域， 用于定点， 是计算圆心的一种近似方法

    cx = 0
    cy = 0

    if is_cross or is_t[0] or is_t[1] or is_t[2] or is_t[3] :
        # 只在出现十字形或者T字型才计算圆心坐标
        cnt = 0
        for roi_direct in ['up', 'down']:#根据上，下两块的x坐标取个平均值
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
        visualize_result(img, cx_mean, cx, cy,is_straight, is_turn, is_alr_turn, is_t, is_cross)
