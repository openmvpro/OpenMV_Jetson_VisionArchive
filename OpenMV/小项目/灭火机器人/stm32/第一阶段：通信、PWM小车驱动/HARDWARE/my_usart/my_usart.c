#include "my_usart.h"
#include "sys.h"
#include "string.h"
#include "openmv.h"
#include "led.h"

int fputc(int ch, FILE *f)
{ 	
	while( (USART1->SR&0X40) == 0);//ѭ������,ֱ���������   
	USART1->DR = (u8) ch;      
	return ch;
}

u8 recv1_data_ok=0;                //���յ���ȷ�����ݰ�
u8 data_number = 0;
u8 rec_start = 0;
u8 star_buffer=0;
u8 control_data[MAX_DATA_LENS]={0xAA,0x55,0x07,0x50,0x00,0x00,0x00,0x00,0x00,0x056};


UART_HandleTypeDef UART1_Handler;  //UART���
u8 USART_RX_BUF[USART_REC_LEN];     //���ջ���,���USART_REC_LEN���ֽ�.
//����״̬
//bit15��	������ɱ�־
//bit14��	���յ�0x0d
//bit13~0��	���յ�����Ч�ֽ���Ŀ
u16 USART_RX_STA = 0;       //����״̬���

u8 aRxBuffer[RXBUFFERSIZE];       //HAL��ʹ�õĴ��ڽ��ջ���

void my_usart_init(u32 bound)
{
  //UART ��ʼ������
	UART1_Handler.Instance = USART1;					            //USART1
	UART1_Handler.Init.BaudRate = bound;				          //������
	UART1_Handler.Init.WordLength = UART_WORDLENGTH_8B;   //�ֳ�Ϊ8λ���ݸ�ʽ
	UART1_Handler.Init.StopBits = UART_STOPBITS_1;	      //һ��ֹͣλ
	UART1_Handler.Init.Parity = UART_PARITY_NONE;		      //����żУ��λ
	UART1_Handler.Init.HwFlowCtl = UART_HWCONTROL_NONE;   //��Ӳ������
	UART1_Handler.Init.Mode = UART_MODE_TX_RX;		        //�շ�ģʽ
	HAL_UART_Init(&UART1_Handler);					              //HAL_UART_Init()��ʹ��UART1
	
	//HAL_UART_Receive_IT(&UART1_Handler, (u8 *)aRxBuffer, RXBUFFERSIZE);
	__HAL_UART_ENABLE_IT(&UART1_Handler,UART_IT_RXNE);     //���������ж�
}

//UART�ײ��ʼ����ʱ��ʹ�ܣ��������ã��ж�����
//�˺����ᱻHAL_UART_Init()����
//huart:���ھ��
//PA9:TXD(����)   PA10:RXD�����գ�
void HAL_UART_MspInit(UART_HandleTypeDef *huart)
{
   //GPIO�˿�����
	GPIO_InitTypeDef GPIO_Initure;
	//PA9--------TXD
	//PA10-------RXD
	if(huart->Instance == USART1)                   //����Ǵ���1�����д���1 MSP��ʼ��
	{
		__HAL_RCC_GPIOA_CLK_ENABLE();			            //ʹ��GPIOAʱ��
		__HAL_RCC_USART1_CLK_ENABLE();			          //ʹ��USART1ʱ��
	
		GPIO_Initure.Pin = GPIO_PIN_9;			          //PA9
		GPIO_Initure.Mode = GPIO_MODE_AF_PP;		      //�����������
		GPIO_Initure.Pull = GPIO_PULLUP;			        //����
		GPIO_Initure.Speed = GPIO_SPEED_FAST;		      //����
		GPIO_Initure.Alternate = GPIO_AF7_USART1;	    //����ΪUSART1
		HAL_GPIO_Init(GPIOA,&GPIO_Initure);	   	      //��ʼ��PA9

		GPIO_Initure.Pin = GPIO_PIN_10;			          //PA10
		HAL_GPIO_Init(GPIOA,&GPIO_Initure);	   	      //��ʼ��PA10
		
		HAL_NVIC_EnableIRQ(USART1_IRQn);				      //ʹ��USART1�ж�ͨ��
		HAL_NVIC_SetPriority(USART1_IRQn,3,3);			  //��ռ���ȼ�3�������ȼ�3
	}
}

/*void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	if(huart->Instance == USART1)																//����Ǵ���1
	{
		if( (USART_RX_STA & 0x8000) == 0 )													  //����δ���
		{  
			if(USART_RX_STA & 0x4000)														   	  //���յ���0x0d
			{
				if(aRxBuffer[0] != 0x0a)
					USART_RX_STA = 0;													          //���մ���,���¿�ʼ
				else
					USART_RX_STA |= 0x8000;													    //��������� 
			}
			else 																					          //��û�յ�0X0D
			{	
				if(aRxBuffer[0] == 0x0d)
					USART_RX_STA |= 0x4000;
				else
				{
					USART_RX_BUF[USART_RX_STA&0X3FFF] = aRxBuffer[0] ;
					USART_RX_STA++;
					if(USART_RX_STA > (USART_REC_LEN-1))
						USART_RX_STA = 0;														//�������ݴ���,���¿�ʼ����	  
				}		 
			}
		}
	}
}

//����1�жϷ������
void USART1_IRQHandler(void)                	
{ 
	u32 timeout = 0;
	HAL_UART_IRQHandler(&UART1_Handler);	//����HAL���жϴ����ú���
	timeout = 0;
  while (HAL_UART_GetState(&UART1_Handler) != HAL_UART_STATE_READY)//�ȴ�����
	{
	 timeout++;////��ʱ����
   if(timeout > HAL_MAX_DELAY) 
		 break;		
	}  
	timeout = 0;
	while(HAL_UART_Receive_IT(&UART1_Handler, (u8 *)aRxBuffer, RXBUFFERSIZE) != HAL_OK)//һ�δ������֮�����¿����жϲ�����RxXferCountΪ1
	{
	 timeout++; //��ʱ����
	 if(timeout > HAL_MAX_DELAY) 
		 break;	
	}
} */

u8 len;	
u16 t;

//����1�жϷ������
void USART1_IRQHandler(void)                	
{ 
	u8 Res;
	if( (__HAL_UART_GET_FLAG(&UART1_Handler,UART_FLAG_RXNE) != RESET) )  //�����ж�(���յ������ݱ�����0x0d 0x0a��β)
	{
    HAL_UART_Receive(&UART1_Handler,&Res,1,1000); 
		if( (USART_RX_STA & 0x8000) == 0 )//����δ���
		{
			if( USART_RX_STA & 0x4000)//���յ���0x0d
			{
				if(Res != 0x0a)
					USART_RX_STA = 0;//���մ���,���¿�ʼ
				else USART_RX_STA |= 0x8000;	//��������� 
			}
			else //��û�յ�0X0D
			{	
				if(Res == 0x0d)
					USART_RX_STA |= 0x4000;
				else
				{
					USART_RX_BUF[USART_RX_STA & 0X3FFF] = Res ;
					USART_RX_STA++;
					if( USART_RX_STA > (USART_REC_LEN-1) )
						USART_RX_STA = 0;//�������ݴ���,���¿�ʼ����	  
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
			printf("����״̬:%d\r\n",X);
			printf("�Ƕ�:%d\r\n",Y);
			printf("����:%d\r\n",Z);
		}
		HAL_UART_IRQHandler(&UART1_Handler);	
	} 
}

//void USART1_IRQHandler(void)         //Ѳ��
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



    
//׷С��
//void USART1_IRQHandler(void)                	//����1�жϷ������
//{
//	u8 i=0,j=0;
//	if(__HAL_UART_GET_FLAG(&UART1_Handler, USART_IT_RXNE) != RESET)  //�����ж�(���յ������ݱ�����0x0d 0x0a��β)
//	{
//		control_data[data_number] = USART1->DR;
//		data_number++; 
//		if(data_number < (MAX_DATA_LENS+4) )                     //�������ݳ���δ������ͷ�Ͱ���3���ֽ�,+4
//		{
//			if(control_data[0] == 0xaa)//���ݰ���ͷ�ֽ�
//			{
//				if(data_number > 3)
//				{
//					if(control_data[1] == 0x55)
//					{	
//						if(data_number >= (control_data[2]+3))  //���������ݰ����������ֽ�Ϊ���ݳ��ȣ����ݳ��Ȳ�������ͷ��У���֣�
//						{
//							for(i = 0;i <= (data_number-2);i++)  //���յ����ݰ������һ���ֽ�ΪУ���֣�У�鷽�����������ݽ����ۼӣ�������У���֣�
//							{
//								j += control_data[i];
//							}
//							if(j == control_data[data_number-1])     //�ж�У���Ƿ�ɹ�
//							{
//								j = 0;
//								recv1_data_ok = 1;                 //���յ���ȷ�������ݰ���־λ��
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
//		if(rebuf[0] != 0xb3)//֡ͷ
//			i = 0;
//	  if( (i == 2) && (rebuf[1] != 0xb3) )//�ж�֡ͷ
//			i = 0;
//		if(i >= 7)//����һ֡�������
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






