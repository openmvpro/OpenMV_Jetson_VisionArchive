#include "sys.h"
#include "delay.h"
#include "my_usart.h"
#include "led.h"
#include "key.h"
#include "string.h"
#include "oled.h"
#include "string.h"

/**************串口通信IO口连接***************/
//PA9(TXD)--------P5(RXD)
//PA10(RXD)-------P4(TXD)
//OpenMv与STM32需要共地
/*********************************************/


int main(void)
{
	u8 len;	
	u16 t;
	char cmd[200];


  HAL_Init();                    	//初始化HAL库    
  Stm32_Clock_Init(336,8,2,7);  	//设置时钟,168Mhz
	delay_init(168);               	//初始化延时函数
	my_usart_init(115200);
	LED_Init();											//初始化LED	
  KEY_Init();                     //初始化按键
	OLED_Init();
	
  while(1)
  {
		if( USART_RX_STA & 0x8000 )
		{
			len = USART_RX_STA & 0x3FFF;
			for(t = 0;t < len;t++)
			{
				cmd[t] = USART_RX_BUF[t];
				//Receive_Prepare(USART_RX_BUF[t]);
				while( (USART1->SR&0X40) == 0);
			}
			USART_RX_STA = 0;
			//HAL_UART_Transmit(&UART1_Handler,(u8 *)USART_RX_BUF,len,0xffff);
		}
		//刚开启PF10亮红外灭
		if( !(strcmp(cmd,"begin")) )               //判断strcmp中两个字符是否相等
		{
			HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8,GPIO_PIN_SET); 	//PB8 置1  红外亮
		
      HAL_GPIO_WritePin(GPIOF,GPIO_PIN_10,GPIO_PIN_RESET);   	//PF10亮
	
			memset( cmd,0,strlen(cmd) );               //清除cmd[]
		}
		else if( !(strcmp(cmd,"close")) )
		{
			HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8,GPIO_PIN_RESET); 	//PB8 置0 红外灭
      HAL_GPIO_WritePin(GPIOF,GPIO_PIN_10,GPIO_PIN_SET);   	//PF10灭
			memset( cmd,0,strlen(cmd) );               //清除cmd[]
		}

	}
		
		
}



