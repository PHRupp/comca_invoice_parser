
import logging
import os
import traceback as tb

from os.path import join

import numpy as np
import pandas as pd

in_file_name = 'HC_%s_final.csv'
out_file_name = 'HC_final.csv'

data_dir = 'G:/My Drive/LBA/MLX Admin/HC/Analysis/6mo Data Sets'
log_file = './logs/build_final_results.log'

in_data_file = join(data_dir, in_file_name % 'in')
paid_data_file = join(data_dir, in_file_name % 'paid')
pickup_data_file = join(data_dir, in_file_name % 'pickup')
out_file = join(data_dir, out_file_name)

# Remove the log file
if os.path.exists(log_file):
    os.remove(log_file)

logging.basicConfig(filename=log_file, level=logging.INFO)

try:
    # read the files
    data_in = pd.read_csv(in_data_file)
    data_paid = pd.read_csv(paid_data_file)
    data_pickup = pd.read_csv(pickup_data_file)

    # merge the data
    data_final = pd.merge(data_in, data_paid, on='Invoice', how='outer', suffixes=('In', 'Paid'))
    data_final = pd.merge(data_final, data_pickup, on='Invoice', how='outer', suffixes=('', 'Pickup'))

    # Fill in the Customer name from whatever is populated
    data_final.loc[:,'Customer'] = data_final['CustomerNameIn']
    is_na = data_final['Customer'].isna().to_list()
    data_final.loc[is_na, 'Customer'] = data_final.loc[is_na, 'CustomerNamePaid']
    is_na = data_final['Customer'].isna().to_list()
    data_final.loc[is_na, 'Customer'] = data_final.loc[is_na, 'CustomerNamePickup']
    drop_cols = ['CustomerNameIn', 'CustomerNamePaid', 'CustomerNamePickup']
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up final date/time and mirror the clean cloud export column names
    data_final['Placed'] = pd.to_datetime(data_final['DateIn'] + " " + data_final['TimeIn'])
    #data_final['Cleaned'] = pd.to_datetime(data_final['DateReady'] + " " + data_final['TimeReady'])
    data_final['Cleaned'] = pd.NaT
    data_final['Ready By'] = pd.NaT
    data_final['Collected'] = pd.to_datetime(data_final['DatePickup'] + " " + data_final['TimePickup'])
    data_final['Paid Date'] = pd.to_datetime(data_final['DatePaid'] + " " + data_final['TimePaid'])
    drop_cols = ['DateIn', 'TimeIn', 'DatePickup', 'TimePickup', 'DatePaid', 'TimePaid']
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up phone numbers, will completely exclude as this was fixed in another file
    data_final.loc[:, "Phone"] = np.nan
    drop_cols = ['PhoneNumberIn', 'PhoneNumberPaid', 'PhoneNumberPickup']
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up amount, paid is priority, followed by pickup, ready, and in
    data_final.loc[:,'Total'] = data_final['AmountPaid']
    is_na = data_final['Total'].isna().to_list()
    data_final.loc[is_na, 'Total'] = data_final.loc[is_na, 'AmountPickup']
    is_na = data_final['Total'].isna().to_list()
    data_final.loc[is_na, 'Total'] = data_final.loc[is_na, 'AmountIn']
    drop_cols = ['AmountPaid', 'AmountPickup', 'AmountIn']
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up quantity, paid is priority, followed by pickup, ready, and in
    data_final.loc[:,'Pieces'] = data_final['QtyPaid']
    is_na = data_final['Pieces'].isna().to_list()
    data_final.loc[is_na, 'Pieces'] = data_final.loc[is_na, 'QtyPickup']
    is_na = data_final['Pieces'].isna().to_list()
    data_final.loc[is_na, 'Pieces'] = data_final.loc[is_na, 'QtyIn']
    drop_cols = ['QtyPaid', 'QtyPickup', 'QtyIn']
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up payment type, paid is priority, followed by pickup, ready, and in
    data_final.loc[:,'PaymentType'] = data_final['FoPPaid']
    is_na = data_final['PaymentType'].isna().to_list()
    data_final.loc[is_na, 'PaymentType'] = data_final.loc[is_na, 'FoPPickup']
    drop_cols = ['FoPPaid', 'FoPPickup']
    data_final.drop(columns=drop_cols, inplace=True)
    data_final.loc[:, 'PaymentType'].replace({
        'Discover': 'Card',
        'VISA': 'Card',
        'MC': 'Card',
        'CASH': 'Cash',
        'AMX': 'Card',
        'Debit': 'Card',
        'Split': 'Card',
        'CK #1364': 'Cash',
        'CK #721': 'Cash',
    }, inplace=True)

    # drop and/or rename columns to match clean cloud
    drop_cols = ['TransactionTypeIn', 'TransactionTypePaid', 'TransactionTypePickup']
    data_final.drop(columns=drop_cols, inplace=True)
    data_final.rename(columns={
        'Invoice': 'Order ID',
    }, inplace=True)
    data_final.drop(
        index=data_final.index[data_final['Order ID'].isnull()],
        inplace=True,
    )

    print(data_final.dtypes)
    print(data_final)

    # print data to file
    data_final.to_csv(out_file, index=False)
except Exception as e:
    logging.error(tb.format_exc())
