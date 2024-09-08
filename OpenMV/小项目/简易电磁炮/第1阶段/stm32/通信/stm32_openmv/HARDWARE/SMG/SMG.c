#include "SMG.h"
#include "delay.h"

/*                           ����������ֿ�                			
     0    1    2    3    4    5    6    7    8    9    A    B    C    D    E    F
    0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f,0x77,0x7c,0x39,0x5e,0x79,0x71,
		
   black   -    H    J    K    L    N    o   P    U     t    G    Q    r   M    y
    0x00 ,0x40,0x76,0x1e,0x70,0x38,0x37,0x5c,0x73,0x3e,0x78,0x3d,0x67,0x50,0x37,0x6e,
		
      0.   1.   2.   3.   4.   5.   6.   7.   8.   9.  -1	
    0xbf,0x86,0xdb,0xcf,0xe6,0xed,0xfd,0x87,0xff,0xef,0x46
*/

u8 Wei_Code[]={0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80};       																					//���λ�����λ											
u8 Duan_Code[]={0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f,0x77,0x7c,0x39,0x5e,0x79,0x71,0x00};  //0~F��ȫ��
u8 Disp_Code[]={1,2,3,4,5,6,7,8};
u8 Code[]={2,0,1,6,3,5,4,6};


void SMG_Init(void)
{
	GPIO_InitTypeDef GPIO_Initure;
	
	__HAL_RCC_GPIOF_CLK_ENABLE();                      				//ʹ��GPIOFʱ��
	
	GPIO_Initure.Pin=GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;     //PF13��14��15
	GPIO_Initure.Mode=GPIO_MODE_OUTPUT_PP;                    //�������
	GPIO_Initure.Pull=GPIO_PULLUP;														//����
	GPIO_Initure.Speed=GPIO_SPEED_HIGH;												//����
	HAL_GPIO_Init(GPIOF,&GPIO_Initure);
	
}

void date_in(u8 temp)	
{
	u8 i;
	for(i=0;i<8;i++)
	 {
		  SCK=0;
		  if((temp&0x80) == 0x80)						
		  {
			  SI =1; 																			//�����������
		  }
		  else
		  {
			  SI = 0;
		  } 
		  temp<<=1;
			SCK=1; 																				//��λ����ʱ�ӣ�����������
	    delay_us(3);
		  SCK=0;
		}
}

void date_out(void)
{	
	 RCK=0; 																					//�������ʱ��
	 delay_us(10);	
	 RCK=1;
	 delay_us(10);	
	 RCK=0;
	
}



//ʵ�־�̬��ʾ
void SMG_Disp(u8 *Disp_Code)
{
	u8 j;
	for(j=0;j<8;j++)		
	{
		date_in(~Wei_Code[j]);
		date_in(Duan_Code[Disp_Code[j]]);
		date_out();
	}				
}

//��ÿ��λ��ֿ�Ϊ������λ���в���
void DIV_number(u8 counter)
{
	u8 i;
	for(i=8;i>0;i--)
	{
		Disp_Code[i-1]=counter%10;
		counter=counter/10;
		/*if(i-1<7)
		{
			if(Disp_Code[i-1]==0)
			{
				Disp_Code[i-1]=16;
			}
			else
			{
				Disp_Code[i-1]=Disp_Code[i-1];
			}
		}*/
	}
}


void SMG(u8 *Disp_Code)
{
	u8 j;
	for(j=0;j<8;j++)		
	{
		date_in(~Wei_Code[j]);
		delay_ms(50);
		date_in(Duan_Code[Disp_Code[j]]);
		delay_ms(50);
		date_out();
	}				
}


