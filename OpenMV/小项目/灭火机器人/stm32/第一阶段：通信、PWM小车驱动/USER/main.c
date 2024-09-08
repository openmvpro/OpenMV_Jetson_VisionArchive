#include "sys.h"
#include "delay.h"
#include "my_usart.h"
#include "led.h"
#include "key.h"
#include "string.h"
#include "oled.h"
#include "openmv.h"
#include "pwm.h"
#include "timer.h"
#include "car.h"

/**************串口通信IO口连接***************/
//PA9(TXD)--------P5(RXD)
//PA10(RXD)-------P4(TXD)
//OpenMv与STM32需要共地
/*********************************************/


int main(void)
{
  HAL_Init();                    	//初始化HAL库    
  Stm32_Clock_Init(336,8,2,7);  	//设置时钟,168Mhz
	delay_init(168);               	//初始化延时函数
	my_usart_init(115200);
	LED_Init();											//初始化LED	
  KEY_Init();                     //初始化按键
	OLED_Init();
	CAR_Init();
	TIM3_Init(5000-1,8400-1);       //定时器3初始化，周期为500ms
	TIM4_PWM_Init(1000-1,84-1);    	//84M/84=1M的计数频率，自动重装载为500，那么PWM频率为1M/500=2kHZ
	
  while(1)
  {
		LED0 = 0;
	}
		
		
}


