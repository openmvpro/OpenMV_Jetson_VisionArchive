# Blob Detection Example
#
# This example shows off how to use the find_blobs function to find color
# blobs in the image. This example in particular looks for dark green objects.

import sensor, image, time
import car
from pid import PID

# You may need to tweak the above settings for tracking green things...
# Select an area in the Framebuffer to copy the color settings.

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off. 要关闭白平衡，否则影响颜色追踪效果
clock = time.clock() # Tracks FPS.

# For color tracking to work really well you should ideally be in a very, very,
# very, controlled enviroment where the lighting is constant...
green_threshold   = (76, 96, -110, -30, 8, 66)
size_threshold = 2000 #像素点面积阈值
x_pid = PID(p=0.5, i=1, imax=100)#方向PID 控制方向 改变p参数调整拐弯角度 p大越大
h_pid = PID(p=0.05, i=0.1, imax=50)#距离PID 控制速度 改变p参数调整速度 p大越大

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    blobs = img.find_blobs([green_threshold])
    #blobs的返回值为：
    #[{"x":104, "y":46, "w":48, "h":37, "pixels":1365, "cx":127, "cy":65, "rotation":3.033448, "code":1, "count":1, "perimeter":204, "roundness":0.675996}]
    #                                    像素数量        中心x坐标            色块的旋转弧度
    if blobs:
        max_blob = find_max(blobs)
        x_error = max_blob[5]-img.width()/2
        h_error = max_blob[2]*max_blob[3]-size_threshold
        print("x error: ", x_error)
        '''
        for b in blobs:
            # Draw a rect around the blob.
            img.draw_rectangle(b[0:4]) # rect
            img.draw_cross(b[5], b[6]) # cx, cy
        '''
        img.draw_rectangle(max_blob[0:4]) # rect 找到的色块画矩形
        img.draw_cross(max_blob[5], max_blob[6]) # cx, cy 找到的色块中心画十字
        x_output=x_pid.get_pid(x_error,1)
        h_output=h_pid.get_pid(h_error,1)
        print("h_output",h_output)
        car.run(-h_output-x_output,-h_output+x_output)
    else:
        car.run(18,-18)
