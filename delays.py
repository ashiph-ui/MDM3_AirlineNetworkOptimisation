"""
Author: Aaron Vinod
Date: 2023-03-17
Description: 
This script reads in the data from the file apt_dly_2022.csv, then finds the delays for a specific reason.

Useful information:
APT: Airport 
APT_ICAO: Airport ICAO code, netwwork manager
APT_NAME: Airport name
APT_CITY: Airport city
STATE_NAME: State name
FLT_ARR_1: How many flights arrived on time
"""
import numpy as np
import pandas as pd

# Read the data from the file
df_delays = pd.read_csv('apt_dly_2022.csv').fillna(0)

# Get the column names
delays_columns = df_delays.columns

def sort_dict(dictionary: dict) -> dict:
    """ Sorts a dictionary by value

    Args:
        dictionary (dict): The dictionary to be sorted
    
    Returns:
        dict: A dictionary sorted by value
    
    Example:
        >>> sort_dict({'a': 1, 'b': 2, 'c': 3})
        outputs:
        {'c': 3, 'b': 2, 'a': 1}
    """
    return dict(sorted(dictionary.items(), key= lambda x: x[1], reverse=True))

def find_specified_df(val: int, df: pd.DataFrame) -> np.ndarray:
    """ Filters the dataset by whichever column is passed in

    Args:
        val (int): The column number
        df (pd.DataFrame): The dataframe to be filtered
    
    Returns:
        np.ndarray: A array of filtered dataframes
    
    Example:
        >>> find_specified_df(4, df_delays)
        outputs: 
        ndarray of dataframes, each corresponding to all the rows 
        in the original dataset about a specific network manager
    """
    df_specific = df[delays_columns[val]].unique()
    df_specific_array = np.zeros(len(df_specific), dtype=object)
    for counter, values in enumerate(df_specific):
        # will find the rows that contain the value
        df_specific_array[counter] = (df==values).any(axis=1)
        # will create a new dataframe with the rows that contain the value
        df_specific_array[counter] = df[df_specific_array[counter]]
    return df_specific_array

def find_time_delayed_reasons(df: pd.DataFrame) -> dict:
    """ Finds the total time delayed for a specific column 
    
    Args:
        df (pd.DataFrame): The dataframe to be filtered
    
    Returns:
        dict: A dictionary of the total time delayed for a specific column
    
    Example:
        >>> find_total_time_delayed(df_delays)
        outputs:
        a dictionary of total time delayed for a specific reason pertaining to the whole dataset
    """
    delays_times: dict = {}
    columns = df.columns
    for count_delay, value_delay in enumerate(columns[8:-1]):
        delays_times[value_delay] = delays_times.get(value_delay, 0) + df[value_delay].sum()
    # delays_times = dict(sorted(delays_times.items(), key= lambda x: x[1], reverse=True))
    delays_times = sort_dict(delays_times)
    return delays_times

# def find_total_time_delayed(delays_times: dict) -> int:
#     for key, value in delays_times.items():
#         total_time_delayed_reason += value
#     return total_time_delayed_reason

# finding total_time delayed
total_time_delayed = df_delays[delays_columns[7]].sum()
# print(f'Total time delayed: {total_time_delayed}'

# finding total number of time delayed for a specific reason
delays_times = find_time_delayed_reasons(df_delays)

# finding time delayed for a specific place
df_country = find_specified_df(6, df_delays)
countries = df_delays[delays_columns[6]].unique()
country_total_time_delayed_reason = np.zeros(len(df_country), dtype=object)
# creates a dictionary of the keys being the country and the values being the total number of minutes delayed for each country 
for count, value in enumerate(df_country):
    country_total_time_delayed_reason[count] = value[delays_columns[7]].sum()
df_delayed_times_countries_total = dict(zip(countries, country_total_time_delayed_reason))
# creats a dictionary of the keys being the country and the values being a dictionary of the total number of minutes delayed for each reason
country_total_time_delayed = np.zeros(len(df_country), dtype=object)
for count, value in enumerate(df_country):
    country_total_time_delayed[count] = find_time_delayed_reasons(value)
df_times_countries = dict(zip(countries, country_total_time_delayed))
df_delayed_times_countries_total = sort_dict(df_delayed_times_countries_total)
