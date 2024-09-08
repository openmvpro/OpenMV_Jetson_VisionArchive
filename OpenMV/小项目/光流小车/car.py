from pyb import Pin, Timer
inverse_left=False  #将其更改为True以反转左轮
inverse_right=False #将其更改为True以反转右轮

#控制第一个电机
ain1 =  Pin('P0', Pin.OUT_PP)#命名为ain1的P0设置为推挽输出 上拉电阻
ain2 =  Pin('P1', Pin.OUT_PP)

#控制第二个电机
bin1 =  Pin('P2', Pin.OUT_PP)
bin2 =  Pin('P3', Pin.OUT_PP)

#引脚初始化低电平
ain1.low()
ain2.low()
bin1.low()
bin2.low()

#PWM脉宽调制
pwma = Pin('P4')
pwmb = Pin('P5')
tim = Timer(2, freq=1000)#设置定时器4频率为1KHz
ch1 = tim.channel(3, Timer.PWM, pin=pwma)#设置通道1对应P7
ch2 = tim.channel(4, Timer.PWM, pin=pwmb)
ch1.pulse_width_percent(0)#脉冲宽度占空比设置为0
ch2.pulse_width_percent(0)

def run(left_speed, right_speed):
    if inverse_left==True:
        left_speed=(-left_speed)
    if inverse_right==True:
        right_speed=(-right_speed)

    if left_speed < 0:#反转
        ain1.low()
        ain2.high()
    else:
        ain1.high()
        ain2.low()
    ch1.pulse_width_percent(abs(left_speed))#速度的绝对值越大脉冲占空比越大，转速越大

    if right_speed < 0:
        bin1.low()
        bin2.high()
    else:
        bin1.high()
        bin2.low()
    ch2.pulse_width_percent(abs(right_speed))
