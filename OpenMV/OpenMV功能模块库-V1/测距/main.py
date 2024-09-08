#测距
#方案一：Apriltag3D定位返回值，参考目录Apriltag
#方案二：比例测距
#方案三：TOF光学测距
import sensor, image
#TOF
import time
from machine import I2C
from vl53l1x import VL53L1X

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(10)
sensor.set_auto_whitebal(False)

#方案二：比例测距
def Proportional_ranging():
    #比例常数
    K=5000#实测整个被测物距离*直径像素Lm
    #测量对象阈值
    threshold   = ( 56,   83,    5,   57,   63,   80)
    blobs = img.find_blobs([threshold])
    if len(blobs) == 1:
        b = blobs[0]
        img.draw_rectangle(b[0:4])
        img.draw_cross(b[5], b[6])
        Lm = (b[2]+b[3])/2
        #初测常数K返回的直径像素
        #print(Lm)
        length = K/Lm
        print(length)

#方案三：TOF光学测距
def TOF(old_dist):
    distance_num = distance.read()
    distance_num /= 10
    if abs(old_dist - distance_num) < 5:
        print("range: %d cm "%distance_num)
    else:
        print("range:00000000000000000")
    old_dist = distance_num
    return old_dist

old_dist = 0
i2c = I2C(2)
distance = VL53L1X(i2c)
while(True):
    img = sensor.snapshot()
    #方案二：比例测距
    #Proportional_ranging()
    #方案三：TOF光学测距
    old_dist=TOF(old_dist)
