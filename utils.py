import pandas as pd
import numpy as np
import scipy.stats as stats

def remove_outliers(df, metric, std):
    
    data = np.array(df[metric])
    d = np.abs(data - np.median(data))
    
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    
    return data[s < std]  


def remove_outliers_2(df, metric):
   
    z_scores = stats.zscore(df[metric])
    abs_z_scores = np.abs(z_scores)
    
    filtered_entries = (abs_z_scores < 3)
    return df[filtered_entries]
        

def convert_col_to_float(df, metric):
    df = df[df[metric] != '-']
    df[metric] = pd.to_numeric(df[metric], downcast="float")
    return df


def get_stock_info(df, ticker):
    
    df_row = df[df['Ticker'] == 'AAPL']
    sector = df_row['Sector'].values[0]