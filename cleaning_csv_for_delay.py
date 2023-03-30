import pandas as pd
import numpy as np
from delays import *

def build_dict_airport_delays(df: pd.DataFrame, column: int, filename: str) -> None:
    # finding time delayed for a specific airport
    df_airport = find_specified_df(column, df)
    airports = df_delays[delays_columns[column]].unique()

    airport_total_time_delayed_reason = np.zeros(len(df_airport), dtype=object)
    # creates a dictionary of the keys being the airport and the values being the total number of minutes delayed for each airport
    for count, value in enumerate(df_airport):
        airport_total_time_delayed_reason[count] = value[delays_columns[7]].sum()
    df_delayed_times_airports_total = dict(zip(airports, airport_total_time_delayed_reason))

    # create a dictionary of the keys being the airport and the values being a dictionary of the total number of minutes delayed for each reason
    airport_total_time_delayed = np.zeros(len(df_airport), dtype=object)
    for count, value in enumerate(df_airport):
        airport_total_time_delayed[count] = find_time_delayed_reasons(value)
    df_times_airports = dict(zip(airports, airport_total_time_delayed))
    df_delayed_times_airports_total = sort_dict(df_delayed_times_airports_total)

def export_dict_to_csv(df: dict, filename: str):
    dict_df = pd.DataFrame.from_dict(df, orient='index', columns=['Total Time Delayed'])
    dict_df.to_csv('{filename}.csv')   

def clean_up_delays_csv(filename_delays: str, filename_airports: str) -> pd.DataFrame:
    df_delay = pd.read_csv(filename_delays)
    df_airport = pd.read_csv(filename_airports)
    merged_df = pd.merge(df_delay, df_airport, on='icao', how='inner')
    return merged_df

# df = clean_up_delays_csv('total_time_delayed_airports.csv', 'node_list.csv')

def new_log_scale(df: str) -> pd.DataFrame :
    # scales the values to a range of 0-100
    df['Time_delayed_scale'] = df['Total Time Delayed'].apply(lambda x: np.log10(x))
    return df

# df_scaled = new_log_scale(df)
# df_scaled.to_csv('total_time_delay_cleaned.csv')
