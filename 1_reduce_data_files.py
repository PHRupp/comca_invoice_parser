
import logging
import os
import traceback as tb

from os.path import join
from typing import List

import pandas as pd

from parser.file_reduce import reduce_file

"""
WARNING: Processing XLSX files instead of the XLS provides more data. Not sure why, but it 
parses the XLS and has missing area codes or phone numbers, but it's fully populated in XLSX.

Also, Files must be in order of time from earliest top to more recent bottom. This is because
some of the files have overlapping transactions where order matters to combine them.
"""

dataset = 'pickup'  # in, ready, paid, pickup
data_dir = 'G:/My Drive/LBA/MLX Admin/HC/Analysis/6mo Data Sets'
log_file = './logs/reduced_results.log'
out_file_name = 'HC_%s.csv' % dataset

in_file_names = []

if dataset == 'in':
    in_file_names = [
        #'2015Q1234_in.xlsx',
        #'2016Q1234_in.xlsx',
        #'2017Q1234_in.xlsx',
        #'2018Q12_in.xlsx',
        #'2018Q34_in.xlsx',
        #'2019Q12_in.xlsx',
        #'2019Q34_in.xlsx',
        '2020Q12_in.xlsx',
        '2020Q34_in.xlsx',
        '2021Q12_in.xlsx',
        '2021Q34_in.xlsx',
        '2022Q12_in.xlsx',
        '2022Q34_in.xlsx',
        '2023Q12_in.xlsx',
        '2023Q34_in.xlsx',
        '2024Q12_in.xlsx',
        '2024Q34_in.xlsx',
        '2025Q12_in.xlsx',
        '2025Q34_in.xlsx',
    ]
elif dataset == 'ready':
    in_file_names = [
    ]
elif dataset == 'paid':
    in_file_names = [
        #'2015Q1234_paid.xlsx',
        #'2016Q1234_paid.xlsx',
        #'2017Q1234_paid.xlsx',
        #'2018Q1234_paid.xlsx',
        #'2019Q1234_paid.xlsx',
        '2020Q12_paid.xlsx',
        '2020Q34_paid.xlsx',
        '2021Q12_paid.xlsx',
        '2021Q34_paid.xlsx',
        '2022Q12_paid.xlsx',
        '2022Q34_paid.xlsx',
        '2023Q12_paid.xlsx',
        '2023Q34_paid.xlsx',
        '2024Q12_paid.xlsx',
        '2024Q34_paid.xlsx',
        '2025Q12_paid.xlsx',
        '2025Q34_paid.xlsx',
    ]
elif dataset == 'pickup':
    in_file_names = [
        #'2015Q1234_pickup.xlsx',
        #'2016Q1234_pickup.xlsx',
        #'2017Q1234_pickup.xlsx',
        #'2018Q12_pickup.xlsx',
        #'2018Q34_pickup.xlsx',
        #'2019Q12_pickup.xlsx',
        #'2019Q34_pickup.xlsx',
        '2020Q12_pickup.xlsx',
        '2020Q34_pickup.xlsx',
        '2021Q12_pickup.xlsx',
        '2021Q34_pickup.xlsx',
        '2022Q12_pickup.xlsx',
        '2022Q34_pickup.xlsx',
        '2023Q12_pickup.xlsx',
        '2023Q34_pickup.xlsx',
        '2024Q12_pickup.xlsx',
        '2024Q34_pickup.xlsx',
        '2025Q12_pickup.xlsx',
        '2025Q34_pickup.xlsx',
    ]

try:
    if os.path.exists(log_file):
        os.remove(log_file)
except Exception as e:
    print(tb.format_exc())

out_file = join(data_dir, out_file_name)

logging.basicConfig(filename=log_file, level=logging.INFO)

data_frames: List[pd.DataFrame] = []

for f in in_file_names:
    try:
        logging.info('FILE: %s' % f)
        in_file = join(data_dir, f)
        data_frames += reduce_file(in_file, dataset)
    except Exception as e:
        print('FILE ERROR!')
        logging.warning(tb.format_exc())

# put all the data together
pd.concat(data_frames, ignore_index=True).to_csv(out_file, index=False)
