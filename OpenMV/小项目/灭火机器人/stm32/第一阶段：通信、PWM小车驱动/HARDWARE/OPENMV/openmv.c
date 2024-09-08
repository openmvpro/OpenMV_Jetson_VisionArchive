#include "openmv.h"

/******openmv���ݽ���******/
/*********��Ҫԭ��*********/
/*openmvͨ�����Իع�õ�ƫ�ƽǶȺ�ƫ�Ƴߴ磬
	������0XAA��0XAE����֡ͷ�����Ը����Լ������޸ģ�
	0x0D,0x0A����֡β�������������ݵı�ʶ���������޸ģ�
	�����16�������ݣ����͸�stm32	*/
//�����ΪʲôҪ�Խ��յ������ݽ��л�ԭ


int X,Y,Z;    

/*************************************/
//��openmv���͵����ݽ��л�ԭ
//���յõ�ƫ�ƽǶȺ�ƫ�Ƴߴ�
/*************************************/
void Data_Processing(u8 *data_buf,u8 num)   
{
	int pan_state, car_angle,car_length;
	/*��ȡƫ�ƽǶ�ԭʼ����*/
  pan_state = (int)(*(data_buf+1)<<0) | (int)(*(data_buf+2)<<8) | (int)(*(data_buf+3)<<16) | (int)(*(data_buf+4)<<24) ; 
  X = pan_state;
	
	/*��ȡƫ�Ƴߴ�ԭʼ����*/
  car_angle = (int)(*(data_buf+5)<<0) | (int)(*(data_buf+6)<<8) | (int)(*(data_buf+7)<<16) | (int)(*(data_buf+8)<<24) ; 
  Y = car_angle; 

	car_length = (int)(*(data_buf+9)<<0) | (int)(*(data_buf+10)<<8) | (int)(*(data_buf+11)<<16) | (int)(*(data_buf+12)<<24) ; 
  Z = car_length; 
  
}


/*************************************/
//���ڶ�openmv���͹��������ݽ��н���
//ͨ��������֡ͷ���жϽ����ж����ݵ���Ч��
/*************************************/
void Receive_Prepare(u8 data)    
{
	/*��̬�ֲ����������ջ���*/
	static u8 RxBuffer[10];
	/*���ݳ��ȣ������±�*/
  static u8  _data_cnt = 0;
	/*����״̬*/
  static u8 state = 0;
  if(state == 0 && data == 0xAA)
  {
		state = 1;
  } 
  else if(state==1 && data == 0xAE)
	{
		state = 2;
    _data_cnt = 0; 
  }
  else if(state == 2)  
  {
    RxBuffer[++_data_cnt] = data;
    if(_data_cnt >= 12)
    { 
			state = 0;
      Data_Processing(RxBuffer,_data_cnt);
		}
   } 
   else
		state = 0;   
}
