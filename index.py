#!/bin/env python3
# coding=utf-8
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

GLO_RATIO = 0.5
DF_TABLE = []
fileNameArr = []


def handleDataXY(lineData, ratio):
    xyData = lineData.split('	')
    return [round(float(xyData[0]) * ratio, 6), float(xyData[1]) / 1000]


def handleDataX(lineData):
    xyData = lineData.split('	')
    return float(xyData[1]) / 1000


def resultPath(name):
    if (not os.path.exists('result')):
        os.mkdir('result')
    return os.path.abspath('result' + os.sep + name)


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
    ax.legend(loc="upper right")
    ax.set_ylabel("intensity")
    ax.xaxis.set_major_locator(MultipleLocator(2))
    plt.xlim(0, 24)  # 横轴左右边界
    plt.savefig(resultPath("raw_plt.png"), dpi=300, bbox_inches='tight')


def paintNorm(df):
    df_norm = (df - df.min()) * 100 / (df.max() - df.min())
    df_norm["V/mL"] = df["V/mL"]
    ax = df_norm.plot(x="V/mL", kind="line")
    ax.legend(loc="upper right")
    ax.set_ylabel("percentage(%)")
    ax.xaxis.set_major_locator(MultipleLocator(2))
    plt.xlim(0, 24)  # 横轴左右边界
    plt.savefig(resultPath("norm_plt.png"), dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        GLO_RATIO = float(sys.argv[1])
    else:
        GLO_RATIO = 0.5

    if not os.path.exists('plain_data'):
        print('未找到放数据的文件夹: plain_data')
    else:
        fileNameArr = os.listdir('plain_data')
        fileNameArr.remove('.gitkeep')  # 去掉额外文件
        print(fileNameArr)  # 用于图例
        for fileName in fileNameArr:
            dataPath = os.path.abspath('plain_data' + os.sep + fileName)
            fileHandler(dataPath)

    fileNameArr.insert(0, 'V/mL')

    df = pd.DataFrame(DF_TABLE, columns=fileNameArr)
    df.to_csv(resultPath('pd.xlsx'), sep='\t', index=False, header=True)

    paintRaw(df)
    paintNorm(df)
