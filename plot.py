#!/usr/bin/env python3
# coding=utf-8
import os
import shutil
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import MultipleLocator

GLO_RATIO = 0.5
DF_TABLE = []


def handleDataXY(lineData, ratio):
    xyData = lineData.split('	')
    return [round(float(xyData[0]) * ratio, 6), float(xyData[1]) / 1000]


def handleDataX(lineData):
    xyData = lineData.split('	')
    return float(xyData[1]) / 1000


def data_file_path(__folder_name, __file_name='__no_file'):
    if __file_name == '__no_file':
        return __folder_name + os.sep
    else:
        return __folder_name + os.sep + os.sep + __file_name


def result_file_path(__folder_name, __file_name='__no_file'):
    if __file_name == '__no_file':
        return __folder_name + os.sep + 'result'
    else:
        return __folder_name + os.sep + 'result' + os.sep + __file_name


def fileHandler(path):
    with open(path, 'rt') as data:
        activeFlag = 0  # 0代表未初始化，1代表已找到索引点 2代表已结束
        index = 0
        for line in data:
            if (activeFlag == 1 and line == '\n'):
                activeFlag = 2
            if activeFlag == 1:
                if len(DF_TABLE) > index:
                    DF_TABLE[index].append(handleDataX(line))
                else:
                    DF_TABLE.append(handleDataXY(line, GLO_RATIO))
                index += 1
            if (line.startswith('R.Time (min)	Intensity')) and (activeFlag == 0):
                activeFlag = 1


def paintRaw(df):
    ax = df.plot(x="V/mL", kind="line")
    ax.legend(loc="upper left")
    ax.set_ylabel("intensity")
    ax.xaxis.set_major_locator(MultipleLocator(2))
    plt.xlim(0, 24)  # 横轴左右边界
    plt.savefig(result_file_path(folder_name, 'raw_plt.png'),
                dpi=300, bbox_inches='tight')


def paintNorm(df):
    df_norm = (df - df.min()) * 100 / (df.max() - df.min())
    df_norm["V/mL"] = df["V/mL"]
    ax = df_norm.plot(x="V/mL", kind="line")
    ax.legend(loc="upper left")
    ax.set_ylabel("Percentage(%)")
    ax.xaxis.set_major_locator(MultipleLocator(2))
    plt.xlim(0, 24)  # 横轴左右边界
    plt.savefig(result_file_path(folder_name, 'norm_plt.png'),
                dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    folder_name = input("Please input folder name: ")
    folder_path = result_file_path(folder_name)

    if len(sys.argv) > 1:
        GLO_RATIO = float(sys.argv[1])
    else:
        GLO_RATIO = 0.5

    if not os.path.exists(folder_name):
        print('Folder "' + folder_name + '" not found.')
    else:
        if os.path.exists(result_file_path(folder_name)):
            continue_process = input(
                'Result folder already exists, input Y to overwrite: ')
            if continue_process == 'Y':
                shutil.rmtree(folder_path)
            else:
                print("Exiting...")
        else:
            pass

        os.mkdir(result_file_path(folder_name))
        all_files = os.listdir(folder_name)
        input_files = []
        for i in all_files:
            if i[-4:] == '.txt':
                i_no_ext = i[0:-4]
                shutil.copyfile(data_file_path(folder_name, i),
                                data_file_path(folder_name, i_no_ext))
                input_files.append(i_no_ext)
        for legends in input_files:
            print(legends)
        for file_name in input_files:
            dataPath = os.path.abspath(folder_name + os.sep + file_name)
            fileHandler(dataPath)

    input_files.insert(0, 'V/mL')

    df = pd.DataFrame(DF_TABLE, columns=input_files)
    df.to_csv(result_file_path(folder_name, 'output_data.csv'),
              sep=',', index=False, header=True)

    paintRaw(df)
    paintNorm(df)

    input_files.remove('V/mL')

    for j in input_files:
        os.remove(data_file_path(folder_name, j))

    exit()
