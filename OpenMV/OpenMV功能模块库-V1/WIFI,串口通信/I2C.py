# Arduino 作为I2C主设备， OpenMV作为I2C从设备。
#
# 请把OpenMV和Arduino按照下面连线：
#
# OpenMV Cam Master I2C Data  (P5) - Arduino Uno Data  (A4)
# OpenMV Cam Master I2C Clock (P4) - Arduino Uno Clock (A5)
# OpenMV Cam Ground                - Arduino Ground

import pyb, ustruct
from pyb import Pin

P4 = Pin('P4', Pin.IN, Pin.PULL_UP)
P5 = Pin('P5', Pin.IN, Pin.PULL_UP)

text = "Hello World!\n"
data = ustruct.pack("<%ds" % len(text), text)
# 使用 "ustruct" 来生成需要发送的数据包
# "<" 把数据以小端序放进struct中
# "%ds" 把字符串放进数据流，比如："13s" 对应的 "Hello World!\n" (13 chars).
# 详见 https://docs.python.org/3/library/struct.html

# READ ME!!!
#
# 请理解，当您的OpenMV摄像头不是I2C主设备，所以不管是使用中断回调，
# 还是下方的轮循，都可能会错过响应发送数据给主机。当这种情况发生时，
# Arduino会获得NAK，并且不得不从OpenMV再次读数据。请注意，
# OpenMV和Arduino都不擅长解决I2C的错误。在OpenMV和Arduino中，
# 你可以通过释放I2C外设，再重新初始化外设，来恢复功能。

# OpenMV上的硬件I2C总线都是2
bus = pyb.I2C(2, pyb.I2C.SLAVE, addr=0x12)
bus.deinit() # 完全关闭设备
bus = pyb.I2C(2, pyb.I2C.SLAVE, addr=0x12)
print("Waiting for Arduino...")



# 请注意，为了正常同步工作，OpenMV Cam必须 在Arduino轮询数据之前运行此脚本。
# 否则，I2C字节帧会变得乱七八糟。所以，保持Arduino在reset状态，
# 直到OpenMV显示“Waiting for Arduino...”。


while(True):
    try:
        bus.send(ustruct.pack("<h", len(data)), timeout=10000) # 首先发送长度 (16-bits).
        try:
            bus.send(data, timeout=10000) # 然后发送数据
            print("Sent Data!") # 没有遇到错误时，会显示
        except OSError as err:
            pass # 不用担心遇到错误，会跳过
            # 请注意，有3个可能的错误。 超时错误（timeout error），
            # 通用错误（general purpose error）或繁忙错误
            #（busy error）。 “err.arg[0]”的错误代码分别
            # 为116,5,16。
    except OSError as err:
        pass # 不用担心遇到错误，会跳过
        # 请注意，有3个可能的错误。 超时错误（timeout error），
        # 通用错误（general purpose error）或繁忙错误
        #（busy error）。 “err.arg[0]”的错误代码分别
        # 为116,5,16。
