# AprilTags3D定位例程


import sensor, image, time, math


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA) # we run out of memory if the resolution is much bigger...
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()



# AprilTags库输出标签的姿势信息。 这是x / y / z平移和x / y / z旋转。
# x / y / z旋转以弧度表示，可以转换为度数。 至于翻译单位是无量纲的，
# 你必须应用一个转换函数。

# f_x是相机的x焦距。它应该等于以mm为单位的镜头焦距除以x传感器尺寸（以mm为单位）乘以图像中的像素数。
# 以下数值适用于配备2.8毫米镜头的OV7725相机。

# f_y是相机的y焦距。它应该等于以mm为单位的镜头焦距除以y传感器尺寸（以mm为单位）乘以图像中的像素数。
# 以下数值适用于配备2.8毫米镜头的OV7725相机。





f_x = (2.8 / 3.984) * 160 # find_apriltags 如果没有设置，则默认为这个
f_y = (2.8 / 2.952) * 120 # find_apriltags 如果没有设置，则默认为这个
c_x = 160 * 0.5 # find_apriltags 如果没有设置，则默认为这个 (the image.w * 0.5)
c_y = 120 * 0.5 # find_apriltags 如果没有设置，则默认为这个 (the image.h * 0.5)

def degrees(radians):
    return (180 * radians) / math.pi

while(True):
    clock.tick()
    img = sensor.snapshot()
    for tag in img.find_apriltags(families=image.TAG16H5, fx=f_x, fy=f_y, cx=c_x, cy=c_y): # 默认为 TAG36H11
        img.draw_rectangle(tag.rect(), color = (255, 0, 0))
        img.draw_cross(tag.cx(), tag.cy(), color = (0, 255, 0))

        print_args = (tag.x_translation(), tag.y_translation(), tag.z_translation(), \
            degrees(tag.x_rotation()), degrees(tag.y_rotation()), degrees(tag.z_rotation()))
        # 变换单位不详。旋转单位是度数。
        print("Tx: %f, Ty %f, Tz %f, Rx %f, Ry %f, Rz %f" % print_args)

    print(clock.fps())
