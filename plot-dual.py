#!/usr/bin/env python3
# coding=utf-8
import os
import shutil
import sys

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib import rcParams
import pandas as pd

GLO_RATIO = 0.5


def data_file_path(folder_name, file_name='_no_file'):
    return folder_name + os.sep + os.sep + file_name


def result_file_path(folder_name, file_name='_no_file'):
    if file_name == '_no_file':
        return folder_name + os.sep + 'result'
    else:
        return folder_name + os.sep + 'result' + os.sep + file_name


def remove_file_path(file_list):
    for file_names in file_list:
        os.remove(data_file_path(folder_name, file_names))


def file_handler(path):
    with open(path, 'rt') as data:
        _index = 0

        _active_flag = 0
        # 0 - Unintialized, 1 - GFP data ready (488/512), 2 - GFP data end, 3 - mCherry data ready (587/610), 4 - mCherry data end, 5 - A280 data ready, 6 - A280 data end.

        for line in data:
            if (line.startswith('Ex. Wavelength(nm)	488')):
                _active_flag = 1
                _index = 0

            elif (line.startswith('Ex. Wavelength(nm)	587')):
                _active_flag = 3
                _index = 0

            elif (line.startswith('Ex. Wavelength(nm)	280')):
                _active_flag = 5
                _index = 0

            if (_active_flag == 1 and line == '\n'):
                _active_flag = 2
            elif (_active_flag == 3 and line == '\n'):
                _active_flag = 4
            elif (_active_flag == 5 and line == '\n'):
                _active_flag = 6

            if _active_flag == 1 and (_index < 10):
                _index += 1
            elif _active_flag == 1 and (_index == 10):
                if handle_data(line, GLO_RATIO)[0] > 2:
                    gfp_table.append(handle_data(line, GLO_RATIO))

            if _active_flag == 3 and (_index < 10):
                _index += 1
            elif _active_flag == 3 and (_index == 10):
                if handle_data(line, GLO_RATIO)[0] > 2:
                    mcherry_table.append(handle_data(line, GLO_RATIO))

            if _active_flag == 5 and (_index < 10):
                _index += 1
            elif _active_flag == 5 and (_index == 10):
                if handle_data(line, GLO_RATIO)[0] > 2:
                    a280_table.append(handle_data(line, GLO_RATIO))


def handle_data(line_data, ratio):
    _xy_data = line_data.split('	')
    return [round(float(_xy_data[0]) * ratio, 6), float(_xy_data[1]) / 1000]


def norm(raw_list: list):
    _list_max = max(raw_list)
    _list_min = min(raw_list)

    _norm_list = [100 * (x - _list_min)/(_list_max - _list_min)
                  for x in raw_list]

    return _norm_list


def paint(save_path, gfp, mcherry, a280, legend, normalize=0):
    _major_loc = MultipleLocator(5)
    _minor_loc = MultipleLocator(1)

    plt.figure()

    plt.xlabel('V/mL')
    plt.xlim(2, 24)

    if normalize == 0:
        plt.ylabel('Absorbance')
    else:
        plt.ylabel('Percentage(%)')

    if gfp != []:
        _gfp_x = [_gfp[0] for _gfp in gfp]

        if normalize == 0:
            _gfp_y = [_gfp[1] for _gfp in gfp]
        else:
            _gfp_y = norm([_gfp[1] for _gfp in gfp])
        plt.plot(_gfp_x, _gfp_y, label=legend +
                 ' (GFP)', color='#14D005')

    if mcherry != []:
        _mcherry_x = [_mcherry[0] for _mcherry in mcherry]

        if normalize == 0:
            _mcherry_y = [_mcherry[1] for _mcherry in mcherry]
        else:
            _mcherry_y = norm([_mcherry[1] for _mcherry in mcherry])
        plt.plot(_mcherry_x, _mcherry_y, label=legend +
                 ' (mCherry)', color='#DF5118')

    if a280 != []:
        _a280_x = [_a280[0] for _a280 in a280]

        if normalize == 0:
            _a280_y = [_a280[1] for _a280 in a280]
        else:
            _a280_y = norm([_a280[1] for _a280 in a280])
        plt.plot(_a280_x, _a280_y, label=legend +
                 ' (A280)', color='#4287F5')

    else:
        pass

    ax = plt.gca()
    ax.xaxis.set_major_locator(_major_loc)
    ax.xaxis.set_minor_locator(_minor_loc)

    # ax.legend(loc='center', bbox_to_anchor=(0,1), ncol=3, fancybox=True, shadow=True)
    ax.legend(loc='center', bbox_to_anchor=(0.5, 1.05), ncol=2)

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


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
            elif continue_process == 'y':
                shutil.rmtree(folder_path)
            else:
                print("Exiting...")
                exit()
        else:
            pass

    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['Arial']

    os.mkdir(result_file_path(folder_name))
    all_files = os.listdir(folder_name)

    input_files = []
    for i in all_files:
        if i[-4:] == '.txt':
            i_no_ext = i[0:-4]
            shutil.copyfile(data_file_path(folder_name, i),
                            data_file_path(folder_name, i_no_ext))
            input_files.append(i_no_ext)

    for file_name in input_files:
        print(file_name)
        gfp_table = []
        mcherry_table = []
        a280_table = []
        norm_mcherry_table = []

        data_path = os.path.abspath(folder_name + os.sep + file_name)
        file_handler(data_path)

        if gfp_table != []:
            gfp_df = pd.DataFrame(gfp_table)
            gfp_df.to_csv(result_file_path(folder_name, file_name +
                                           '-gfp_data.csv'), sep=',', index=False, header=True)
        if mcherry_table != []:
            mcherry_df = pd.DataFrame(mcherry_table)
            mcherry_df.to_csv(result_file_path(folder_name, file_name +
                                               '-mcherry_data.csv'), sep=',', index=False, header=True)
        if a280_table != []:
            a280_df = pd.DataFrame(a280_table)
            a280_df.to_csv(result_file_path(folder_name, file_name +
                                            '-a280_data.csv'), sep=',', index=False, header=True)

        paint(result_file_path(folder_name, file_name +
                               '_raw.png'), gfp_table, mcherry_table, a280_table, file_name, 0)
        paint(result_file_path(folder_name, file_name +
                               '_normalized.png'), gfp_table, mcherry_table, a280_table, file_name, 1)

    remove_file_path(input_files)

    exit()
