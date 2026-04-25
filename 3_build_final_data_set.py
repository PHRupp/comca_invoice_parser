
import logging
import os
import traceback as tb

from os.path import join

import numpy as np
import pandas as pd

from parser.utils import fix_phone_number

pd.options.mode.chained_assignment = None  # default is 'warn'

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
    # Priority: In -> Paid -> Pickup
    data_final['Customer'] = data_final['CustomerNameIn'].fillna(data_final['CustomerNamePaid']).fillna(data_final['CustomerNamePickup'])
    drop_cols = ['CustomerNameIn', 'CustomerNamePaid', 'CustomerNamePickup']
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up final date/time and mirror the clean cloud export column names
    data_final['Placed'] = pd.to_datetime(data_final['DateIn'] + " " + data_final['TimeIn'])
    #data_final['Cleaned'] = pd.to_datetime(data_final['DateReady'] + " " + data_final['TimeReady'])
    data_final['Cleaned'] = pd.NaT
    data_final['Ready By'] = pd.NaT
    data_final['Collected'] = pd.to_datetime(data_final['DatePickup'] + " " + data_final['TimePickup'])
    data_final['Payment Date'] = pd.to_datetime(data_final['DatePaid'] + " " + data_final['TimePaid'])
    drop_cols = ['DateIn', 'TimeIn', 'DatePickup', 'TimePickup', 'DatePaid', 'TimePaid']
    data_final.drop(columns=drop_cols, inplace=True)

    # Check the dates if they are reasonable, fix those that aren't
    data_final.loc[data_final['Collected'].dt.year < 2020, 'Collected'] = pd.NaT

    # if the Placed date is missing, then fill it with Collected then Paid
    data_final['Placed'] = data_final['Placed'].fillna(data_final['Collected']).fillna(data_final['Payment Date'])

    # clean up phone numbers, will completely exclude as this was fixed in another file
    drop_cols = ['PhoneNumberIn', 'PhoneNumberPaid', 'PhoneNumberPickup']
    data_final['Phone'] = [fix_phone_number(row) for row in data_final[drop_cols].values.tolist()]
    data_final['Phone'] = data_final['Phone'].str.replace(r'\D', '', regex=True)
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up amount, paid is priority, followed by pickup, ready, and in
    # Priority: Paid -> Pickup -> In
    data_final['Total'] = data_final['AmountPaid'].fillna(data_final['AmountPickup']).fillna(data_final['AmountIn'])
    drop_cols = ['AmountPaid', 'AmountPickup', 'AmountIn']
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up quantity, paid is priority, followed by pickup, ready, and in
    # Priority: Paid -> Pickup -> In. Fallback to 0 to ensure integer casting.
    data_final['Pieces'] = data_final['QtyPaid'].fillna(data_final['QtyPickup']).fillna(data_final['QtyIn']).fillna(0).astype(int)
    drop_cols = ['QtyPaid', 'QtyPickup', 'QtyIn']
    data_final.drop(columns=drop_cols, inplace=True)

    # clean up payment type, paid is priority, followed by pickup, ready, and in
    # Priority: Paid -> Pickup
    data_final['Payment Type'] = data_final['FoPPaid'].fillna(data_final['FoPPickup'])
    drop_cols = ['FoPPaid', 'FoPPickup']
    data_final.drop(columns=drop_cols, inplace=True)

    # Map payment types to categories. Regex for 'CK' makes it robust to new check numbers.
    data_final['Payment Type'] = data_final['Payment Type'].replace({
        r'Discover|VISA|MC|AMX|Debit|Split|DEBIT|SPLIT': 'Card',
        r'CASH|CK\s?#.*': 'Cash'
    }, regex=True).fillna('')

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
    
    # Re-arrange the columns in the order to match clean cloud and column make inserts easy
    final_columns = [
        'Store ID', 'Store Name', 'Order ID', 'Placed', 'Staff Taking Order',
        'Ready By', 'Cleaned', 'Staff Marking Cleaned', 'Collected', 'Staff Completing',
        'Customer', 'Customer ID', 'Custom ID', 'Email', 'Phone', 'Address',
        'Promo Signup ID', 'Pieces', 'Summary', 'Notes', 'Pickup', 'Pickup Date',
        'Staff Pickup', 'Delivery', 'Bags In', 'Bags Out', 'Retail', 'Paid',
        'Payment Type', 'Card Payment Type', 'Payment Date', 'Staff Taking Payment',
        'Route #', 'Discount', 'Cash Discount', 'Product Rules Discount', 'Credit',
        'Pre Pay Amount', 'Total', 'Total after Credit Used', 'Tax', 'Tax 2', 'Tax 3',
        'Status', 'Locker Location ID', 'Locker Name', 'Section IDs', 'Rack', 'Total weight'
    ]

    # Add other columns to mirror Clean Cloud
    # Ensure all columns exist; initialize new/missing ones with empty strings
    data_final.loc[:, 'Store ID'] = 24942
    data_final.loc[:, 'Store Name'] = 'MLX Hunters Creek Cleaners'
    for col in final_columns:
        if col not in data_final.columns:
            data_final[col] = ""
    data_final = data_final[final_columns]
    data_final.sort_values(by='Placed', inplace=True)

    # Map the customer ID from other file into data set for matching phone numbers
    # Normalize map phone numbers to digits only to match data_final['Phone']
    map_file = join(data_dir, 'HC_CC_CustomerIDMap.xlsx')
    customer_map = pd.read_excel(map_file, sheet_name='customers')
    customer_map['Phone'] = customer_map['Phone'].astype(str).str.replace(r'\D', '', regex=True)
    customer_map = customer_map.drop_duplicates(subset='Phone')
    id_mapping = customer_map.set_index('Phone')['Customer ID']
    data_final['Customer ID'] = data_final['Phone'].map(id_mapping).fillna(data_final['Customer ID'])

    # Remove records where customer IDs that are null
    ind = data_final['Customer ID'].isna() | (data_final['Customer ID'] == "")
    data_final.drop(index=data_final.index[ind], inplace=True)

    # print data to file
    data_final.to_csv(out_file, index=False)
except Exception as e:
    logging.error(tb.format_exc())
