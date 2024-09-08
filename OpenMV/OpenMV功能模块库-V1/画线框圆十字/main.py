import sensor, image, time

sensor.reset() # 初始化摄像头
sensor.set_pixformat(sensor.RGB565) # 格式为 RGB565.
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(10) # 跳过10帧，使新设置生效
while(True):
    img = sensor.snapshot()         # Take a picture and return the image.
    #画线
    img.draw_line((0, 0, 100, 100), color=(255,0,0), thickness=1)#位置，颜色，线粗
    #画框
    img.draw_rectangle((0, 0, 100, 100), color=(0,255,0), thickness=1, fill=False)#同上+填充
    #画圆
    img.draw_circle((50, 50, 50), color=(0,0,255), thickness=1, fill=False)#同上
    #画十
    img.draw_cross(50,50, color=(0,255,255), size=10, thickness=1)#同上+长度
    #写字
    img.draw_string(70,50, "hello", color=(255,255,0), scale=1.5, x_spacing=0, y_spacing=0,
    mono_space=False, char_hmirror=False, char_vflip=False, string_rotation=0, string_vflip=False)
    #位置，文字，颜色，缩放，字符间距，行间距，强制文本间距固定，水平翻转，字符垂直翻转，旋转，文本垂直翻转
