#!/usr/bin/env python3
# coding=utf-8
import os
import shutil
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import MultipleLocator

GLO_RATIO = 0.5
ch1_table = []
ch2_table = []

def data_file_path(folder_name, file_name = '_no_file'):
    return folder_name + os.sep + os.sep + file_name

def result_file_path(folder_name, file_name = '_no_file'):
    if file_name == '_no_file':
        return folder_name + os.sep + 'result'
    else: 
        return folder_name + os.sep + 'result' + os.sep + file_name

def remove_file_path(file_list):
    for file_names in file_list:
        os.remove(data_file_path(folder_name,file_names))

def file_handler(path):
    with open(path, 'rt') as data:
        _channel = 1
        _index = 0
        _active_flag = 0  # 0 - Unintialized, 1 - Ch1 data ready, 2 - Ch1 data end, 3 - Ch2 data ready, 4 - Ch2 data end.

        for line in data:
            if (line.startswith('[LC Chromatogram(Detector A-Ch1)]')):
                assert _channel == 1
                _active_flag = 1
                _index = 0

            elif (line.startswith('[LC Chromatogram(Detector A-Ch2)]')):
                _active_flag = 3
                _index = 0

            if (_active_flag == 1 and line == '\n'):
                _active_flag = 2
            elif (_active_flag == 3 and line == '\n'):
                _active_flag = 4

            if _active_flag == 1 and (_index < 10):
                _index += 1
            elif _active_flag == 1 and (_index == 10):
                ch1_table.append(handle_data(line, GLO_RATIO))

            if _active_flag == 3 and (_index < 10):
                _index += 1
            elif _active_flag == 3 and (_index == 10):
                ch2_table.append(handle_data(line, GLO_RATIO))

def handle_data(line_data, ratio):
    _xy_data = line_data.split('	')
    return [round(float(_xy_data[0]) * ratio, 6), float(_xy_data[1]) / 1000]

def norm(raw_list:list):
    _list_max = max(raw_list)
    _list_min = min(raw_list)

    _norm_list = [(x - _list_min)/(_list_max - _list_min) for x in raw_list]

    # for x in raw_list:
    #     _norm_list.append((x - _list_min)/(_list_max - _list_min))

    return _norm_list


def paint_raw(save_path,ch1,ch2,legend):

    plt.figure()
    _ch1_x = [_ch1[0] for _ch1 in ch1]
    _ch1_y = [_ch1[1] for _ch1 in ch1]

    _ch2_x = [_ch2[0] for _ch2 in ch2]
    _ch2_y = [_ch2[1] for _ch2 in ch2]

    plt.plot(_ch1_x,_ch1_y,label=legend + ' (Channel 1)')
    plt.plot(_ch2_x,_ch2_y,label=legend + ' (Channel 2)')

    plt.legend(loc='upper left')

    plt.ylabel('Intensity')
    plt.xlabel('V/mL')
    plt.xlim(0, 24)  # 横轴左右边界

    plt.savefig(save_path, dpi=300, bbox_inches='tight')

def paint_norm(save_path,ch1,ch2,legend):
    plt.figure()
    _ch1_x = [_ch1[0] for _ch1 in ch1]
    _ch1_y = norm([_ch1[1] for _ch1 in ch1])

    _ch2_x = [_ch2[0] for _ch2 in ch2]
    _ch2_y = norm([_ch2[1] for _ch2 in ch2])

    plt.plot(_ch1_x,_ch1_y,label=legend + ' (Channel 1)')
    plt.plot(_ch2_x,_ch2_y,label=legend + ' (Channel 2)')

    plt.legend(loc='upper left')

    plt.ylabel('Percentage (%)')
    plt.xlabel('V/mL')
    plt.xlim(0, 24)  # 横轴左右边界

    plt.savefig(save_path, dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    folder_name = input("Please input folder name (Dual channel): ")
    folder_path = result_file_path(folder_name)

    if len(sys.argv) > 1:
        GLO_RATIO = float(sys.argv[1])
    else:
        GLO_RATIO = 0.5

    if not os.path.exists(folder_name):
        print('ERROR: Folder \'' + folder_name + '\' not found, exiting...')
        exit()
    else:
        if os.path.exists(result_file_path(folder_name)):
            continue_process = input(
                'WARNING: Result folder already exists, input Y to overwrite: ')
            if continue_process == 'Y':
                shutil.rmtree(folder_path)
            else:
                print("Exiting...")
                exit()
        else:
            pass

        os.mkdir(result_file_path(folder_name))
        all_files = os.listdir(folder_name)

        file_number = 0
        input_files = []
        for i in all_files:
            if i[-4:] == '.txt':
                i_no_ext = i[0:-4]
                shutil.copyfile(data_file_path(folder_name, i), data_file_path(folder_name, i_no_ext))
                input_files.append(i_no_ext)
                file_number += 1

        for file_names in input_files:
            print(file_names)

        if file_number != 1:
            print("ERROR: Multiple file plotting not supported, exiting.")
            remove_file_path(input_files)
            exit()
        
        data_path = os.path.abspath(folder_name + os.sep + input_files[0])
        file_handler(data_path)

    ch1_df = pd.DataFrame(ch1_table)
    ch2_df = pd.DataFrame(ch2_table)
    ch1_df.to_csv(result_file_path(folder_name, 'channel1_output_data.csv'), sep='\t', index=False, header=True)
    ch2_df.to_csv(result_file_path(folder_name, 'channel2_output_data.csv'), sep='\t', index=False, header=True)

    paint_raw(result_file_path(folder_name,'raw_plt.png'),ch1_table,ch2_table,input_files[0])
    paint_norm(result_file_path(folder_name,'normalized_plt.png'),ch1_table,ch2_table,input_files[0])

    remove_file_path(input_files)

    exit()