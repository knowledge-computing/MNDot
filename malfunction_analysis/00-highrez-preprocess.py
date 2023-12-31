import pyspark
import argparse
import json
from pyspark.sql import SQLContext
# import itertools
import os
import sys
import time
# import easydict
# import pandas as pd
import datetime as dt
from datetime import timedelta

# os.environ['PYSPARK_PYTHON'] = sys.executable
# os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable


def main():

    # filePath = "/home/yuankun/Desktop/MnDOT/python_proj_haoji/MNDot/signal_data_JanAug2023/"  # 文件夹路径
    fileList = os.listdir(args.filePath)
    # print(fileList)
    kkk = 0

    intersection_id_dict = {'1735536': 51.0, '2397012': 1039.0}

    def timestring(string):
        string = string.split(' ')
        date = string[0].split('/')
        new_datetime = date[2] + '-' + date[0] + \
            '-' + date[1] + ' ' + string[1] + '00'
        return new_datetime

    def timestamp(string):
        string = string.split(' ')
        string0 = string[0].split('-')
        string1 = string[1].split('.')
        string2 = string1[0].split(':')
        return dt.datetime(year=int(string0[0]), month=int(string0[1]), day=int(string0[2]), hour=int(string2[0]), minute=int(string2[1]), second=int(string2[2]), microsecond=int(string1[1] + '000'))

    for file in fileList:
        if kkk == 0:
            # print(kkk)

            kkk += 1
            f = open(os.path.join(args.filePath, file)).name
            # f = f.read()
            # print(file)
            # print(f.name)

            filename_list = file.split('_')
            # print(filename_list)
            data = sqlContext.read.format('com.databricks.spark.csv') \
                .options(header='true', inferschema='true') \
                .load(f) \
                .rdd \
                .map(list) \
                .map(lambda x: [x[0], filename_list[1], x[2], x[3]])
            # print(data.count())

        else:
            # print(kkk)

            f = open(os.path.join(args.filePath, file)).name
            # f = f.read()
            # print(file)  # 文件名
            # # print(f)
            filename_list = file.split('_')
            # # print(filename_list)

            data1 = sqlContext.read.format('com.databricks.spark.csv') \
                .options(header='true', inferschema='true') \
                .load(f).rdd.map(list) \
                .map(lambda x: [x[0], filename_list[1], x[2], x[3]])

            data = data.union(data1)

            data1.unpersist()

        # while True:
        #     line = f.readline()
        #     if not line:
        #         break
        #     line = line.strip('\n')
        #     print(line)  # txt文件内容
        # print('-------------------------')

    data = data.map(lambda x: [timestring(
        x[0]), intersection_id_dict[x[1]], float(x[2]), float(x[3])]) \
        .filter(lambda x: x[1] == args.targetIntersection) \
        .map(lambda x: [timestamp(x[0]), x[0], str(x[1]), str(x[2]), str(x[3])]) \
        .sortBy(lambda x: x[0]) \
        .map(lambda x: [x[1], x[2], x[3], x[4]]) \
        .map(lambda x: ','.join(x) + "\n")

    # print(data.take(5))
    # print(data.count())
    # data1 = sqlContext.read.format('com.databricks.spark.csv').options(
    #     header='true', inferschema='true').load(args.input_file2).rdd.map(list)

    # data = sqlContext.read.format('com.databricks.spark.csv').options(
    #     header='true', inferschema='true').load(args.input_file1).rdd.map(list).union(data1)

    # data1.unpersist()

    # data = data.map(lambda x: [timestamp(x[0]), x[1], x[2], x[3]]) \
    #     .filter(lambda x: x[0] >= timestamp(args.startdt)) \
    #     .filter(lambda x: x[0] <= timestamp(args.enddt)) \
    #     .sortBy(lambda x: x[0]).groupBy(lambda x: x[3]) \
    #     .map(lambda x: (x[0], list(x[1]), list(x[1])[1:] + [[timestamp(args.enddt)] + list(x[1])[-1][1:]])) \
    #     .map(lambda x: (list(zip(x[1], x[2])))) \
    #     .map(lambda x: [list(i) for i in x]) \
    #     .flatMap(lambda x: x) \
    #     .map(lambda x: ((x[0][1], x[0][3], x[0][2], x[0][0].isoweekday(), x[0][0].date(), x[0][0].hour), [(x[1][0] - x[0][0]) / timedelta(microseconds=1), 1])) \
    #     .reduceByKey(lambda x, y: [x[0] + y[0], x[1] + y[1]]) \
    #     .map(lambda x: {"intersection": x[0][0], "parameter": x[0][1], "phase": x[0][2], "weekday": x[0][3], "date": x[0][4].__str__(), "hour": x[0][5], "cumu_sec": x[1][0]/100000, "count": x[1][1], "avg_sec": x[1][0] / (x[1][1] * 100000)})

    # print(data.take(10))

    output = data.collect()
    # f = open(args.output_file, 'w')
    # for i in output:
    #     json.dump(i, f)
    #     f.write('\n')

    with open(args.output_filePath + 'sorted_ControllerLogs_Signal_' + file[:-4] + '.csv', 'w') as f:
        f.write("time,detector,phase,parameter\n")
        for j in output:
            f.write(j)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='A1T1')
    parser.add_argument('--targetIntersection', type=float,
                        default=1039.0, help='the target intersection id')
    parser.add_argument('--filePath', type=str,
                        default=os.path.join(os.path.dirname(os.getcwd()), 'data/signal_data/'), help='path of multiple files')
    parser.add_argument('--output_filePath', type=str,
                        default=os.path.join(os.path.dirname(os.getcwd()), 'data/signal_data_sorted/'), help='the output file path')

    args = parser.parse_args()

    if __name__ == '__main__':
        sc_conf = pyspark.SparkConf() \
            .setAppName('task1') \
            .setMaster('local[*]') \
            .set('spark.driver.memory', '8g') \
            .set('spark.executor.memory', '4g')

        sc = pyspark.SparkContext(conf=sc_conf)
        sc.setLogLevel("OFF")
        sqlContext = SQLContext(sc)

        main()
