import sensor, image, math

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(30)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

#条形码
def barcode_name(code):
    if(code.type() == image.EAN2):
        return "EAN2"
    if(code.type() == image.EAN5):
        return "EAN5"
    if(code.type() == image.EAN8):
        return "EAN8"
    if(code.type() == image.UPCE):
        return "UPCE"
    if(code.type() == image.ISBN10):
        return "ISBN10"
    if(code.type() == image.UPCA):
        return "UPCA"
    if(code.type() == image.EAN13):
        return "EAN13"
    if(code.type() == image.ISBN13):
        return "ISBN13"
    if(code.type() == image.I25):
        return "I25"
    if(code.type() == image.DATABAR):
        return "DATABAR"
    if(code.type() == image.DATABAR_EXP):
        return "DATABAR_EXP"
    if(code.type() == image.CODABAR):
        return "CODABAR"
    if(code.type() == image.CODE39):
        return "CODE39"
    if(code.type() == image.PDF417):
        return "PDF417"
    if(code.type() == image.CODE93):
        return "CODE93"
    if(code.type() == image.CODE128):
        return "CODE128"
def bar_code():
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.VGA)
    sensor.set_windowing((640, 160))#数字缩放窗口

    codes = img.find_barcodes()
    for code in codes:
        img.draw_rectangle(code.rect())
        print_args = (barcode_name(code), code.payload(), (180 * code.rotation()) / math.pi, code.quality())
        print("Barcode %s, Payload \"%s\", rotation %f (degrees), quality %d" % print_args)


#二维码
def QR_code():
    for code in img.find_qrcodes():
        img.draw_rectangle(code.rect())
        print(code)

    #判别二维码内容要做处理
    #b = code[4].replace('\ufeff','')#\ufeff为字节顺序标记，出现在文本文件头部要删掉

#datamatrix码
def datamatrix():
    sensor.set_framesize(sensor.QVGA)

    matrices = img.find_datamatrices()
    for matrix in matrices:
        img.draw_rectangle(matrix.rect(), color = (255, 0, 0))
        print_args = (matrix.rows(), matrix.columns(), matrix.payload(), (180 * matrix.rotation()) / math.pi)
        print("Matrix [%d:%d], Payload \"%s\", rotation %f (degrees)" % print_args)

#AprilTag码___只能识别160.120大小
def AprilTag():
    sensor.set_windowing((160,120))
    for tag in img.find_apriltags( families=image.TAG36H11): # defaults to TAG36H11 without "families".
            img.draw_rectangle(tag.rect(), color = (255, 0, 0))
            img.draw_cross(tag.cx(), tag.cy(), color = (0, 255, 0))
            degress = 180 * tag.rotation() / math.pi#AprilTag旋转的角度
            print(tag.id(),degress)

#3D定位
def degrees(radians):
    return (180 * radians) / math.pi

def positioning():
    f_x = (2.8 / 3.984) * 160 # 默认值 更改分辨率要相应更改乘数
    f_y = (2.8 / 2.952) * 120 # 默认值
    c_x = 160 * 0.5 # 默认值(image.w * 0.5)
    c_y = 120 * 0.5 # 默认值(image.h * 0.5)

    for tag in img.find_apriltags(fx=f_x, fy=f_y, cx=c_x, cy=c_y): # 默认为TAG36H11
            img.draw_rectangle(tag.rect(), color = (255, 0, 0))
            img.draw_cross(tag.cx(), tag.cy(), color = (0, 255, 0))
            print_args = (tag.x_translation(), tag.y_translation(), tag.z_translation(), \
                degrees(tag.x_rotation()), degrees(tag.y_rotation()), degrees(tag.z_rotation()))
            # 位置的单位是未知的，旋转的单位是角度，Tx, Ty, Tz为空间的3个位置量，Rx,Ry,Rz为三个旋转量。
            print("Tx: %f, Ty %f, Tz %f, Rx %f, Ry %f, Rz %f" % print_args)

while(True):
    img = sensor.snapshot().lens_corr(1.8)
    #二维码
    QR_code()
    print("haha")
    #条形码
    #bar_code()
    #datamatrix码
    #datamatrix()
    #AprilTag码
    #AprilTag()
    #3D定位
    #positioning()
