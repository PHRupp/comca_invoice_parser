
import re
from datetime import datetime
from os.path import join
from typing import List


# CONSTANTS
run_date_col = 'Unnamed: 1'
title_col1 = 'Unnamed: 6'
title_col2 = 'Unnamed: 7'
title_col3 = 'Unnamed: 8'
section_title = "Hunter's Creek"
section_invoice_in = 'Invoice In Report'
section_invoice_paid = 'Invoice Paid'
section_invoice = {
    'in': section_invoice_in,
    'ready': section_invoice_paid,
    'pickup': section_invoice_paid,
    'paid': section_invoice_paid,
}
section_end_run_date = 'Run Date'

INVOICE_PATTERN = '^A\d+$'
AREA_CODE_PATTERN = '^(\(\d{3}\))'
PARTIAL_PHONE_NUMBER_PATTERN = '(\d{3}-\d{4})'
PARTIAL_PHONE_NUMBER_PATTERN_ONLY = '^\d{3}-\d{4}$'
PHONE_NUMBER_PATTERN = re.compile('\(\d{3}\) \d{3}-\d{4}')
PHONE_NUMBER_PATTERN_ONLY = re.compile('^\(\d{3}\) (\d{3}-\d{4}$)')
TIME_FORMAT_12HR = "%I:%M %p" #"02:30 PM"


def is_partial_phone_number_format(phone_s: str, only: bool = True) -> bool:
    is_phone_number: bool = False
    phone_regex = PARTIAL_PHONE_NUMBER_PATTERN_ONLY if only else PARTIAL_PHONE_NUMBER_PATTERN
    try:
        match = re.search(phone_regex, phone_s)
        if match is not None:
            is_phone_number = True
    except Exception as e:
        #logging.warning(tb.format_exc())
        pass
    return is_phone_number


def get_partial_phone_number(phone_s: str, only: bool = True) -> str | None:
    phone_number: str = None
    phone_regex = PARTIAL_PHONE_NUMBER_PATTERN_ONLY if only else PARTIAL_PHONE_NUMBER_PATTERN
    try:
        match = re.search(phone_regex, phone_s)
        if match is not None:
            phone_number = match.group(1)
    except Exception as e:
        #logging.warning(tb.format_exc())
        pass
    return phone_number


def is_time_format(time_s: str) -> bool:
    is_time: bool = False
    try:
        d = datetime.strptime(time_s, TIME_FORMAT_12HR)
        is_time = True
    except Exception as e:
        #logging.warning(tb.format_exc())
        pass
    return is_time


def is_phone_missing_area_code(ph: str) -> bool:
    return '(000)' in ph


def is_valid_phone(ph: str) -> bool:
    if not type(ph) == str:
        ph = ''
    return (re.match(PHONE_NUMBER_PATTERN_ONLY, ph) is not None) and (not is_phone_missing_area_code(ph))


def fix_phone_number(phone_numbers: List[str]) -> str:
    phone = None
    phone_numbers = [p for p in phone_numbers if p is not None]
    phone_numbers = [p for p in phone_numbers if type(p) == str]

    # return valid phone
    for ph in phone_numbers:
        if is_valid_phone(ph):
            return ph

    # fix the phone numbers
    area_code = '(000)'
    phone_without_area_code = '000-0000'
    for ph in phone_numbers:

        # Get the area code
        area_code_match = re.match(AREA_CODE_PATTERN, ph)
        if (area_code_match is not None) and not is_phone_missing_area_code(ph):
            area_code = area_code_match.group(1)

        # get the final 7 digits
        phone_match = re.match(PHONE_NUMBER_PATTERN_ONLY, ph)
        if (phone_match is not None) and is_phone_missing_area_code(ph):
            phone_without_area_code = phone_match.group(1)

    # Combine the new phone and check to make sure it's valid
    new_phone = area_code + " " + phone_without_area_code
    if not is_phone_missing_area_code(new_phone) and not "000-0000" in new_phone:
        return new_phone

    return phone
