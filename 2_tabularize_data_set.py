
import logging
import os
import traceback as tb

from os.path import join

import pandas as pd

from parser.transaction_parser import parse_reduced_df

"""
WARNING: Processing XLSX files instead of the XLS provides more data. Not sure why, but it 
parses the XLS and has missing area codes or phone numbers, but it's fully populated in XLSX.

Also, Files must be in order of time from earliest top to more recent bottom. This is because
some of the files have overlapping transactions where order matters to combine them.
"""

in_file_name = 'HC_%s.csv'
out_file_name = 'HC_%s_final.csv'

data_dir = 'G:/My Drive/LBA/MLX Admin/HC/Analysis/6mo Data Sets'
log_file = './logs/tabularize_results.log'

# Remove the log file
if os.path.exists(log_file):
    os.remove(log_file)

logging.basicConfig(filename=log_file, level=logging.INFO)

for s in ['in', 'paid', 'pickup']: #, 'ready'

    in_file = join(data_dir, in_file_name % s)
    out_file = join(data_dir, out_file_name % s)

    try:
        data = pd.read_csv(in_file)
        data = parse_reduced_df(data, s)
        data.to_csv(out_file, index=False)
    except Exception as e:
        logging.error(tb.format_exc())
