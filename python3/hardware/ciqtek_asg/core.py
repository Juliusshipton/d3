# -*- coding: utf-8 -*-

import os
from ctypes import *
import platform
import time


ERROR_CALLBACKTYPE = CFUNCTYPE(None, c_int, c_int, c_char_p)
COUNT_CALLBACKTYPE = CFUNCTYPE(None, c_int, c_int, c_int, POINTER(c_uint32))


ErrorCode =\
    {
        0:"成功",
        1:"设备未连接",
        2:"设备断开连接",
        3:"握手超时",
        4:"握手数据错误",
        5:"关闭等待超时",
        6:"",
        7:"无设备",

        65537:"错误信息回调函数为空",
        65538:"count数据回调函数为空",
        65539:"ASG通道设置参数错误",
        65540:"COUNT使能参数错误",
        65541:"工作模式参数错误",
        65542:"工作模式参数错误",
        65543: "asg和count段信息不相同",

        131073:"ASG脉宽必须是1ns的正整数倍",
        131074:"ASG脉宽必须是2ns的正整数倍",
        131076:"ASG脉宽必须是4ns的正整数倍",
        131077:"ASG段数错误",
        131078:"最大脉宽1.6s",
        131079:"最大总时长8260s",
        131080:"SG循环必须大于0",

        196609:"COUNT脉宽是5的整数倍",
        196610:"COUNT高电平最小10ns",
        196611:"COUNT低电平最小20ns",
        196612:"COUNT最小以25ns低电平结束",
        196613:"COUNT读取线程已存在",
        196614:"COUNT最大脉宽5497558138880",
        196615:"COUNT循环必须大于0",
        196616:"COUNT采集停止超时",

    };

class ASG8x00(object):
    _instance = None

    m_CountCount = 0
    py_callback = {}

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        wd = os.path.abspath(os.path.dirname(__file__))
        arch = platform.architecture()[0]

        dll_path = ""

        if arch == '64bit':
            dll_path = os.path.join(wd, 'ASG8X00_x64.dll')#ASG8X00_x64d.dll
            print(" USE ASG8400_x64.dll ")
        else:
            dll_path = os.path.join(wd, 'ASG8X00_Win32.dll')
            print(" USE ASG8400_Win32.dll ")

        if os.path.isfile(dll_path):
            self.__dll = CDLL(dll_path)
        else:
            raise Exception("can not found dll")

        #dev
        self.__dll.ASG8x00_Connect.restype = c_int
        self.__dll.ASG8x00_Disconnect.restype = c_int
        self.__dll.ASG8x00_DeviceMonitor.restype = c_int

        #pub
        self.__dll.ASG8x00_StartPlay.argtypes = [c_int]
        self.__dll.ASG8x00_StartPlay.restype = c_int
        self.__dll.ASG8x00_StopPlay.restype = c_int
        self.__dll.ASG8x00_SetErrorCallback.restype = c_int
        self.__dll.ASG8x00_SetCountCallback.restype = c_int
        self.__dll.ASG8x00_AsgSetHightLevel.argtypes = [c_int]
        self.__dll.ASG8x00_AsgSetHightLevel.restype = c_int

        self.__dll.ASG8x00_AsgSetChannelEnable.argtypes = [c_int]
        self.__dll.ASG8x00_AsgSetChannelEnable.restype = c_int

        #asg
        #self.__dll.ASG8x00_AsgDownload.argtypes = [POINTER(POINTER(c_longlong)), POINTER(POINTER(c_longlong)),POINTER(c_int)]
        self.__dll.ASG8x00_AsgDownload.restype = c_int

        #count
        #self.__dll.ASG8x00_CounterDownload.argtypes = [POINTER(POINTER(c_longlong)), POINTER(POINTER(c_longlong)),POINTER(c_ushort),c_ushort]
        self.__dll.ASG8x00_CounterDownload.restype = c_int


    # dev
    def connect(self):
        return self.__dll.ASG8x00_Connect()

    def disconnect(self):
        return self.__dll.ASG8x00_Disconnect()

    def monitor_status(self):
        return self.__dll.ASG8x00_DeviceMonitor()

    # pub
    def start(self,count = 0):
        if count > 0xfffffffe:
            exit("循环次数太多")  
        return self.__dll.ASG8x00_StartPlay(count)

    def stop(self):
        return self.__dll.ASG8x00_StopPlay()


    def error_callback(self, func):
        if type(func) == ERROR_CALLBACKTYPE:
            return self.__dll.ASG8x00_SetErrorCallback(func)
        else:
            return False

    def count_callback(self, func):
        if type(func) == COUNT_CALLBACKTYPE:
            return self.__dll.ASG8x00_SetCountCallback(func)
        else:
            return False


    def AsgSetHightLevel(self,iLevel):
        return self.__dll.ASG8x00_AsgSetHightLevel(c_int(iLevel))

    def ASG8x00_AsgSetChannelEnable(self,iEnable):
        return self.__dll.ASG8x00_AsgSetChannelEnable(c_int(iEnable))


    '''
    高8bit表示IN1的模式
    7	    0：时钟模式     1: Counter模式，bit[6:0]无效
    6	    0: 内部时钟，bit[5:0]无效   1： 外部时钟
    5-0     1：外部时钟10M  02为外部时钟100M

    低8bit表示IN2的模式
    7	    0：触发模式   1:  Counter模式，bit[6:0]无效
    6-0     00: 正常工作模式，输出只受播放停止命令控制   01：trigger模式，播放后收到trigger信号才输出
    '''
    def SetClockAndWorkMode(self,IN1,IN2):
        return self.__dll.ASG8x00_SetClockAndWorkMode(c_int(IN1),c_int(IN2))

    '''
    asg序列
    asg_data = [(segment1),(segment2),...,(segmentn)]     asg_Data由segment列表组成
    segment = (loop,[(row1),(row2),...,(rown)])           segment由循环和行列表组成
    row = (time,[ch1,ch2,ch3,ch4,ch5,ch6，ch7，ch8])       row由电平持续时间和各通道在这一行的电平组成
    '''
    def AsgDownload(self, data):
        seg_num = len(data)
        loop = []

        pulses = []
        for i in range(8):
            pulses.append([])

        length = []
        for i in range(seg_num):
            length.append([0] * 8)

        seg_idx = -1
        for l, seg_data in data:
            seg_idx += 1
#            print('Segment {}, loop {}'.format(seg_idx, l))

            loop.append(l)

            level_arr = []
            time_arr = []
            for tm, lvl in seg_data:
                time_arr.append(tm)
                level_arr.append(lvl)

#            print("time arr:", time_arr)
#            print("level arr:", level_arr)
            for ch in range(8):
                pre_lvl = 1
                st = 0
                for i in range(len(time_arr)):
                    if (level_arr[i][ch] != 1) and (level_arr[i][ch] != 0):
                        exit(" 电平错误");
                    if level_arr[i][ch] != pre_lvl:
                        length[seg_idx][ch] += 1
                        pulses[ch].append(st)
                        pre_lvl = level_arr[i][ch]
                        st = 0
                    st += time_arr[i]
                length[seg_idx][ch] += 1
                pulses[ch].append(st)

                if length[seg_idx][ch] % 2 == 1:
                    length[seg_idx][ch] += 1
                    pulses[ch].append(0)

#        print(pulses)
#        print(length)
#        print(loop)
#        print(seg_num)

        # 数据正确，类型转换
        c_pulses = []
        for i in range(8):
            c_pulses.append((c_longlong * len(pulses[i]))(*pulses[i]))
        c_pulses = (POINTER(c_longlong) * len(c_pulses))(*c_pulses)
        # print(type(c_pulses))

        ttype = c_longlong * 8
        length = (ttype * seg_num)(*(tuple(i) for i in length))
        loop = (c_ushort * len(loop))(*loop)
        seg_num = c_ushort(seg_num)

        # CRS_ASGPulseDownload(double **pulses, int length[][8], unsigned short* loop, unsigned short segmentNum);
        # pulses[i][2*j], pulses[i][2*j+1], 第i个通道的一对高低电平
        # length[i][j] 表示第i段Segment第j个通道pluses高+低电平的个数, 是2的倍数
        return self.__dll.ASG8x00_AsgDownload(c_pulses, length, loop, seg_num)

    '''
    count序列
    count_data = [(segment1),(segment2),...,(segmentn)]   count_data由segment列表组成
    segment = (loop,[(row1),(row2),...,(rown)])           segment由循环和行列表组成
    ow = (time,[ch1,ch2])                                row由电平持续时间和各通道在这一行的电平组成
    '''

    def Asg_prepare(self, data):
        seg_num = len(data)
        loop = []

        pulses = []
        for i in range(8):
            pulses.append([])

        length = []
        for i in range(seg_num):
            length.append([0] * 8)

        seg_idx = -1
        for l, seg_data in data:
            seg_idx += 1
#            print('Segment {}, loop {}'.format(seg_idx, l))

            loop.append(l)

            level_arr = []
            time_arr = []
            for tm, lvl in seg_data:
                time_arr.append(tm)
                level_arr.append(lvl)

#            print("time arr:", time_arr)
#            print("level arr:", level_arr)
            for ch in range(8):
                pre_lvl = 1
                st = 0
                for i in range(len(time_arr)):
                    if (level_arr[i][ch] != 1) and (level_arr[i][ch] != 0):
                        exit(" 电平错误");
                    if level_arr[i][ch] != pre_lvl:
                        length[seg_idx][ch] += 1
                        pulses[ch].append(st)
                        pre_lvl = level_arr[i][ch]
                        st = 0
                    st += time_arr[i]
                length[seg_idx][ch] += 1
                pulses[ch].append(st)

                if length[seg_idx][ch] % 2 == 1:
                    length[seg_idx][ch] += 1
                    pulses[ch].append(0)

#        print(pulses)
#        print(length)
#        print(loop)
#        print(seg_num)


        return pulses, length, loop, seg_num

    def AsgDownload_prepared(self, c_pulses, length, loop0, seg_num):

        # CRS_ASGPulseDownload(double **pulses, int length[][8], unsigned short* loop, unsigned short segmentNum);
        # pulses[i][2*j], pulses[i][2*j+1], 第i个通道的一对高低电平
        # length[i][j] 表示第i段Segment第j个通道pluses高+低电平的个数, 是2的倍数
        # 数据正确，类型转换
        cc_pulses = []
        for i in range(8):
            cc_pulses.append((c_longlong * len(c_pulses[i]))(*c_pulses[i]))
        cc_pulses = (POINTER(c_longlong) * len(cc_pulses))(*cc_pulses)
        # print(type(c_pulses))

        ttype = c_longlong * 8
        length = (ttype * seg_num)(*(tuple(i) for i in length))
        loop00 = (c_ushort * len(loop0))(*loop0)
        seg_num = c_ushort(seg_num)
        return self.__dll.ASG8x00_AsgDownload(cc_pulses, length, loop00, seg_num)

    def CounterDownload(self, data):
        seg_num = len(data)
        loop = []

        pulses = []
        for i in range(2):
            pulses.append([])

        length = []
        for i in range(seg_num):
            length.append([0] * 2)

        seg_idx = -1
        for l, seg_data in data:
            seg_idx += 1
#            print('Segment {}, loop {}'.format(seg_idx, l))
            # print(d)
            loop.append(l)

            level_arr = []
            time_arr = []
            for tm, lvl in seg_data:
                time_arr.append(tm)
                level_arr.append(lvl)

#            print("time arr:", time_arr)
#            print("level arr:", level_arr)
            for ch in range(2):
                pre_lvl = 1
                st = 0
                for i in range(len(time_arr)):
                    if (level_arr[i][ch] != 1) and (level_arr[i][ch] != 0):
                        exit(" 电平错误");
                    if level_arr[i][ch] != pre_lvl:
                        length[seg_idx][ch] += 1
                        pulses[ch].append(st)
                        pre_lvl = level_arr[i][ch]
                        st = 0
                    st += time_arr[i]
                length[seg_idx][ch] += 1
                pulses[ch].append(st)

                if length[seg_idx][ch] % 2 == 1:
                    length[seg_idx][ch] += 1
                    pulses[ch].append(0)

#        print(pulses)
#        print(length)
#        print(loop)
#        print(seg_num)

        t_length = []
        t_length.append([])
        t_length.append([])
        for i in range(len(length)):
            t_length[0].append(length[i][0])
            t_length[1].append(length[i][1])
        #print("t_length",t_length)
        # 数据正确，类型转换
        c_pulses = []
        c_length = []
        for i in range(2):
            c_pulses.append((c_longlong * len(pulses[i]))(*pulses[i]))
            c_length.append((c_longlong * len(t_length[i]))(*t_length[i]))

        c_pulses = (POINTER(c_longlong) * len(c_pulses))(*c_pulses)
        c_length = (POINTER(c_longlong) * len(c_length))(*c_length)
#        print(type(c_pulses))
#        print(type(c_length))

        #ttype = c_longlong * 2
        #length = (ttype * seg_num)(*(tuple(i) for i in length))
        loop = (c_ushort * len(loop))(*loop)
        seg_num = c_ushort(seg_num)

        return self.__dll.ASG8x00_CounterDownload(c_pulses, c_length, loop, seg_num)

