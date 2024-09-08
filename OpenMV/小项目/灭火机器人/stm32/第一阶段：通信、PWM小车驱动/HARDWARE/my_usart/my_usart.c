#include "my_usart.h"
#include "sys.h"
#include "string.h"
#include "openmv.h"
#include "led.h"

int fputc(int ch, FILE *f)
{ 	
	while( (USART1->SR&0X40) == 0);//循环发送,直到发送完毕   
	USART1->DR = (u8) ch;      
	return ch;
}

u8 recv1_data_ok=0;                //接收到正确的数据包
u8 data_number = 0;
u8 rec_start = 0;
u8 star_buffer=0;
u8 control_data[MAX_DATA_LENS]={0xAA,0x55,0x07,0x50,0x00,0x00,0x00,0x00,0x00,0x056};


UART_HandleTypeDef UART1_Handler;  //UART句柄
u8 USART_RX_BUF[USART_REC_LEN];     //接收缓冲,最大USART_REC_LEN个字节.
//接收状态
//bit15，	接收完成标志
//bit14，	接收到0x0d
//bit13~0，	接收到的有效字节数目
u16 USART_RX_STA = 0;       //接收状态标记

u8 aRxBuffer[RXBUFFERSIZE];       //HAL库使用的串口接收缓冲

void my_usart_init(u32 bound)
{
  //UART 初始化设置
	UART1_Handler.Instance = USART1;					            //USART1
	UART1_Handler.Init.BaudRate = bound;				          //波特率
	UART1_Handler.Init.WordLength = UART_WORDLENGTH_8B;   //字长为8位数据格式
	UART1_Handler.Init.StopBits = UART_STOPBITS_1;	      //一个停止位
	UART1_Handler.Init.Parity = UART_PARITY_NONE;		      //无奇偶校验位
	UART1_Handler.Init.HwFlowCtl = UART_HWCONTROL_NONE;   //无硬件流控
	UART1_Handler.Init.Mode = UART_MODE_TX_RX;		        //收发模式
	HAL_UART_Init(&UART1_Handler);					              //HAL_UART_Init()会使能UART1
	
	//HAL_UART_Receive_IT(&UART1_Handler, (u8 *)aRxBuffer, RXBUFFERSIZE);
	__HAL_UART_ENABLE_IT(&UART1_Handler,UART_IT_RXNE);     //开启接受中断
}

//UART底层初始化，时钟使能，引脚配置，中断配置
//此函数会被HAL_UART_Init()调用
//huart:串口句柄
//PA9:TXD(发送)   PA10:RXD（接收）
void HAL_UART_MspInit(UART_HandleTypeDef *huart)
{
   //GPIO端口设置
	GPIO_InitTypeDef GPIO_Initure;
	//PA9--------TXD
	//PA10-------RXD
	if(huart->Instance == USART1)                   //如果是串口1，进行串口1 MSP初始化
	{
		__HAL_RCC_GPIOA_CLK_ENABLE();			            //使能GPIOA时钟
		__HAL_RCC_USART1_CLK_ENABLE();			          //使能USART1时钟
	
		GPIO_Initure.Pin = GPIO_PIN_9;			          //PA9
		GPIO_Initure.Mode = GPIO_MODE_AF_PP;		      //复用推挽输出
		GPIO_Initure.Pull = GPIO_PULLUP;			        //上拉
		GPIO_Initure.Speed = GPIO_SPEED_FAST;		      //高速
		GPIO_Initure.Alternate = GPIO_AF7_USART1;	    //复用为USART1
		HAL_GPIO_Init(GPIOA,&GPIO_Initure);	   	      //初始化PA9

		GPIO_Initure.Pin = GPIO_PIN_10;			          //PA10
		HAL_GPIO_Init(GPIOA,&GPIO_Initure);	   	      //初始化PA10
		
		HAL_NVIC_EnableIRQ(USART1_IRQn);				      //使能USART1中断通道
		HAL_NVIC_SetPriority(USART1_IRQn,3,3);			  //抢占优先级3，子优先级3
	}
}

/*void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	if(huart->Instance == USART1)																//如果是串口1
	{
		if( (USART_RX_STA & 0x8000) == 0 )													  //接收未完成
		{  
			if(USART_RX_STA & 0x4000)														   	  //接收到了0x0d
			{
				if(aRxBuffer[0] != 0x0a)
					USART_RX_STA = 0;													          //接收错误,重新开始
				else
					USART_RX_STA |= 0x8000;													    //接收完成了 
			}
			else 																					          //还没收到0X0D
			{	
				if(aRxBuffer[0] == 0x0d)
					USART_RX_STA |= 0x4000;
				else
				{
					USART_RX_BUF[USART_RX_STA&0X3FFF] = aRxBuffer[0] ;
					USART_RX_STA++;
					if(USART_RX_STA > (USART_REC_LEN-1))
						USART_RX_STA = 0;														//接收数据错误,重新开始接收	  
				}		 
			}
		}
	}
}

//串口1中断服务程序
void USART1_IRQHandler(void)                	
{ 
	u32 timeout = 0;
	HAL_UART_IRQHandler(&UART1_Handler);	//调用HAL库中断处理公用函数
	timeout = 0;
  while (HAL_UART_GetState(&UART1_Handler) != HAL_UART_STATE_READY)//等待就绪
	{
	 timeout++;////超时处理
   if(timeout > HAL_MAX_DELAY) 
		 break;		
	}  
	timeout = 0;
	while(HAL_UART_Receive_IT(&UART1_Handler, (u8 *)aRxBuffer, RXBUFFERSIZE) != HAL_OK)//一次处理完成之后，重新开启中断并设置RxXferCount为1
	{
	 timeout++; //超时处理
	 if(timeout > HAL_MAX_DELAY) 
		 break;	
	}
} */

u8 len;	
u16 t;

//串口1中断服务程序
void USART1_IRQHandler(void)                	
{ 
	u8 Res;
	if( (__HAL_UART_GET_FLAG(&UART1_Handler,UART_FLAG_RXNE) != RESET) )  //接收中断(接收到的数据必须是0x0d 0x0a结尾)
	{
    HAL_UART_Receive(&UART1_Handler,&Res,1,1000); 
		if( (USART_RX_STA & 0x8000) == 0 )//接收未完成
		{
			if( USART_RX_STA & 0x4000)//接收到了0x0d
			{
				if(Res != 0x0a)
					USART_RX_STA = 0;//接收错误,重新开始
				else USART_RX_STA |= 0x8000;	//接收完成了 
			}
			else //还没收到0X0D
			{	
				if(Res == 0x0d)
					USART_RX_STA |= 0x4000;
				else
				{
					USART_RX_BUF[USART_RX_STA & 0X3FFF] = Res ;
					USART_RX_STA++;
					if( USART_RX_STA > (USART_REC_LEN-1) )
						USART_RX_STA = 0;//接收数据错误,重新开始接收	  
				}		 
			}
		}
		if( USART_RX_STA & 0x8000 )
		{
			len = USART_RX_STA & 0x3FFF;
			for(t = 0;t < len;t++)
			{
				Receive_Prepare(USART_RX_BUF[t]);
				while( (USART1->SR&0X40) == 0);
			}
			USART_RX_STA = 0;
			printf("风扇状态:%d\r\n",X);
			printf("角度:%d\r\n",Y);
			printf("距离:%d\r\n",Z);
		}
		HAL_UART_IRQHandler(&UART1_Handler);	
	} 
}

//void USART1_IRQHandler(void)         //巡线
//{
//	u8 temp;    
//	if(__HAL_UART_GET_FLAG(&UART1_Handler, USART_IT_RXNE) != RESET )
//	{ 
//		__HAL_UART_CLEAR_FLAG(&UART1_Handler,USART_IT_RXNE);
//		temp = USART1->DR;
//		Receive_Prepare(temp); 
//		HAL_UART_Transmit(&UART1_Handler,(u8 *)temp,sizeof(temp)/sizeof(uint8_t),0xffff);
//	}
//}



    
//追小球
//void USART1_IRQHandler(void)                	//串口1中断服务程序
//{
//	u8 i=0,j=0;
//	if(__HAL_UART_GET_FLAG(&UART1_Handler, USART_IT_RXNE) != RESET)  //接收中断(接收到的数据必须是0x0d 0x0a结尾)
//	{
//		control_data[data_number] = USART1->DR;
//		data_number++; 
//		if(data_number < (MAX_DATA_LENS+4) )                     //定义数据长度未包括包头和包长3个字节,+4
//		{
//			if(control_data[0] == 0xaa)//数据包包头字节
//			{
//				if(data_number > 3)
//				{
//					if(control_data[1] == 0x55)
//					{	
//						if(data_number >= (control_data[2]+3))  //接收完数据包（第三个字节为数据长度，数据长度不包含开头和校验字）
//						{
//							for(i = 0;i <= (data_number-2);i++)  //接收到数据包的最后一个字节为校验字；校验方法对整包数据进行累加（不包含校验字）
//							{
//								j += control_data[i];
//							}
//							if(j == control_data[data_number-1])     //判断校验是否成功
//							{
//								j = 0;
//								recv1_data_ok = 1;                 //接收到正确完整数据包标志位置
//							}
//							else
//							{
//								recv1_data_ok = 0;
//							}
//							j = 0;
//							data_number = 0;													
//						}
//					}
//					else
//					{
//						recv1_data_ok = 0;
//						data_number = 0;
//					}
//				}
//			}
//			else
//			{ 
//				recv1_data_ok = 0;
//				data_number = 0;
//			}
//		}
//		else
//		{
//			recv1_data_ok = 0;
//			data_number = 0;
//		}
//			
//  } 

//} 
//u8 OpenMV_Rx_BUF[8];

//void USART1_IRQHandler(void)
//{
//	static uint8_t rebuf[8]={0},i=0;
//	if(__HAL_UART_GET_FLAG(&UART1_Handler,USART_IT_RXNE) != RESET)
//	{
//		rebuf[i++] = USART1->DR;	
//		if(rebuf[0] != 0xb3)//帧头
//			i = 0;
//	  if( (i == 2) && (rebuf[1] != 0xb3) )//判断帧头
//			i = 0;
//		if(i >= 7)//代表一帧数据完毕
//		{
//			//memcpy(OpenMV_Rx_BUF,rebuf,i);
//			for(i = 0;i <=7;i++)
//			{
//				OpenMV_Rx_BUF[i] = rebuf[i];
//			}
//			i = 0;
//		}
//		__HAL_UART_CLEAR_FLAG(&UART1_Handler,USART_FLAG_RXNE);
//	}	
//}






