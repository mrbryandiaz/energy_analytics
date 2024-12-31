from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, MO
from pandas.tseries.offsets import DateOffset
import pandas as pd
from datetime import datetime
from typing import Union

class NERCHolidayCalendar(AbstractHolidayCalendar):
    """
    A custom holiday calendar for NERC holidays.

    This calendar defines the following NERC holidays:
    - New Year's Day (January 1 or nearest weekday if on a weekend)
    - Memorial Day (last Monday of May)
    - Independence Day (July 4 or nearest weekday if on a weekend)
    - Labor Day (first Monday of September)
    - Thanksgiving (4th Thursday of November)
    - Christmas Day (December 25 or nearest weekday if on a weekend)
    """
    rules = [
        Holiday("New Year's Day", month=1, day=1, observance=nearest_workday),
        Holiday("Memorial Day", month=5, day=31, offset=DateOffset(weekday=MO(-1))),
        Holiday("Independence Day", month=7, day=4, observance=nearest_workday),
        Holiday("Labor Day", month=9, day=1, offset=DateOffset(weekday=MO(1))),
        Holiday("Thanksgiving", month=11, day=1, offset=DateOffset(weekday=3) + DateOffset(weeks=3)),
        Holiday("Christmas Day", month=12, day=25, observance=nearest_workday),
    ]

def is_nerc_holiday(date: datetime) -> bool:
    """
    Determines if a given date is a NERC holiday.

    Args:
        date (datetime): The date to check.

    Returns:
        bool: True if the date is a NERC holiday, False otherwise.
    """
    nerc_calendar = NERCHolidayCalendar()
    holidays = nerc_calendar.holidays(start=date.replace(year=date.year-1), end=date.replace(year=date.year+1))
    return date in holidays

def is_5x16_peak(date: datetime, return_text: bool = False) -> Union[bool, str]:
    """
    Determines if a given datetime falls within the 5x16 peak period.

    The 5x16 peak period is defined as:
    - Non-holiday weekdays
    - Hours from 8:00 AM to 11:59 PM

    Args:
        date (datetime): The datetime to check.
        return_text (bool): If True, returns "Peak" or "Off-Peak". 
                            If False, returns True (Peak) or False (Off-Peak).

    Returns:
        Union[bool, str]: "Peak" or "Off-Peak" if return_text is True.
                          True if in peak period, False otherwise when return_text is False.
    """
    if is_nerc_holiday(date) or date.weekday() >= 5 or not (8 <= date.hour <= 23):
        return "Off-Peak" if return_text else False
    return "Peak" if return_text else True

def apply_peak_offpeak(df: pd.DataFrame, datetime_column: str, return_text: bool = False) -> pd.DataFrame:
    """
    Applies the 5x16 peak/off-peak classification to a pandas DataFrame.

    This function evaluates each datetime in the specified column to determine
    if it falls within the peak or off-peak period, using the `is_5x16_peak` function.

    Args:
        df (pd.DataFrame): The input DataFrame containing datetime information.
        datetime_column (str): The name of the column containing datetime values.
        return_text (bool): If True, results in "Peak" or "Off-Peak".
                            If False, results in True/False for peak/off-peak.

    Returns:
        pd.DataFrame: The updated DataFrame with an additional "Peak_OffPeak" column.
    """
    df["Peak_OffPeak"] = df[datetime_column].apply(lambda x: is_5x16_peak(x, return_text=return_text))
    return df
