# Untitled - By: HQ - 周五 7月 26 2019

import sensor, image, time, pyb
from pyb import UART
from pyb import LED
from pyb import Timer

# LED灯定义
green_led  = LED(1)
blue_led   = LED(2)



import micropython
micropython.alloc_emergency_exception_buf(100)


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

Echo = pyb.Pin(pyb.Pin.board.P0, pyb.Pin.IN)
Trig = pyb.Pin(pyb.Pin.board.P1, pyb.Pin.OUT_PP)

Distance = 0
Counter = 0
Flag = 0

def UL_Start():
    Trig.value(0)
    pyb.udelay(2)
    Trig.value(1)
    pyb.udelay(12)
    Trig.value(0)
    pass

def Calc_Distance():
    global Counter
    Distance = Counter*0.017
    print(Distance)
    pass

def Distance_Process():
    global Flag
    if Flag == 0:
        UL_Start()
        return False
    if Flag == 2:
        Calc_Distance()
        return True


tim = Timer(4)
tim.init(freq=1000000)


def Callback():
    global Counter, Flag

    if Echo.value():
       tim.init(freq=1000000)
       Flag = 1
    else:
        tim.deinit()
        Counter = tim.counter()
        tim.counter(0)
        Flag = 2


uart = UART(3, 115200)
clock = time.clock() # Tracks FPS.


extint = pyb.ExtInt(Echo, pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_DOWN, Callback())


while(True):
    clock.tick()
    ok = 0
    extint.enable()

    ok = Distance_Process()
    if ok:
        uart.write(UART_Send(80, int(Distance), 0))
        Flag = 0
        Counter = 0
        Distance = 0
        extint.disable()

    print(clock.fps())
