import csv
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--traffic_data_dir', type=str, help='Location of actuated signal data')
parser.add_argument('--output_dir', type=str, help='Where the daily traffic data will be stored')

args = parser.parse_args()

traffic_data_dir = args.traffic_data_dir
output_dir = args.output_dir

if not traffic_data_dir:
    traffic_data_dir = os.path.join(os.path.dirname(os.getcwd()), 'data/traffic/singal_data/')
if not output_dir:
    output_dir = os.path.join(os.path.dirname(os.getcwd()), 'data/traffic/hourly/')


# file_name = 'sorted_ControllerLogs_Signal_1039_2022_6.csv'
# file_name = 'sorted_ControllerLogs_Signal_1039_2022_7.csv'
# file_name = 'sorted_ControllerLogs_Signal_1039_2022_12.csv'
# file_name = 'sorted_ControllerLogs_Signal_1039_2023_1.csv'

format = "%m/%d/%Y %H:%M:%S.%f"

days_span = 31
grain_span = 60*60

id2month = {}

def get_idx(grain_span, time, start_time):
    return int((time - start_time).total_seconds()/grain_span)


time_steps = int(60 * 60 * 24 * days_span / grain_span)
x_axis = np.arange(0, time_steps)


total = len(os.listdir(traffic_data_dir))

c = 1
for filename in os.listdir(traffic_data_dir):
# for filename in sorted(os.listdir(dir)):
    print(str(c) + "/" + str(total))
    print(filename + " is starting...")

    df = pd.read_csv(os.path.join(traffic_data_dir, filename), index_col=False)
    df.drop(df.columns[0], axis=1, inplace=True)
    df.columns = ["time", "detector", "phrase", "parameter"]

    start_time = datetime.strptime(df['time'][0], format)

    activate81 = np.zeros(time_steps)
    activate82 = np.zeros(time_steps)

    for i, row in df.iterrows():

        time = datetime.strptime(row['time'], format)

        # time = row['time']
        # idx = int((time - start_time).total_seconds())
        idx = get_idx(grain_span, time, start_time)
        if idx >= time_steps:
            break

        if int(row['phrase']) == 81:
            activate81[idx] += 1
        elif int(row['phrase']) == 82:
            activate82[idx] += 1

        # date = datetime.date(int(item['year']), int(item['month']), int(item['day']))
        # day = date.timetuple().tm_yday
        # id2volumn[id][day] += amt

    # segs = filename.split('_')
    #
    # plot_name = segs[-3] + '_' + segs[-2] + '_' + segs[-1]
    #
    # if int(segs[-3]) not in id2month:
    #     id2month[int(segs[-3])] = {}
    #
    # id2month[int(segs[-3])][int(segs[-1][:-4])] = activate81

    print(filename + " is finished!")
    c += 1

    # id = int(segs[-3])
    # if len(id2month[id].keys()) == 4:
    #     if 6 in id2month[id] and 7 in id2month[id]:
    out_file = filename[:-4] + '_hourly.csv'
    summer = activate81
    DF_summer = pd.DataFrame(summer)
    DF_summer.to_csv(os.path.join(output_dir, out_file), index=False, header=False)

