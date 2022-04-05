import pandas as pd
import numpy as np
import scipy.stats as stats
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rc

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
    df[metric] = df[metric].astype(str).str.replace('%', '')
    df[metric] = pd.to_numeric(df[metric], downcast="float")
    return df


def get_stock_info(df, ticker):
    
    df_row = df[df['Ticker'] == 'AAPL']
    sector = df_row['Sector'].values[0]
    
    
def plot_dist(df, ticker, sector, _filter, metric, metric_val, fig_size = (20,10), show_ticker=True, show_subheader=True):
    '''
    sector = True: Query by the stock's sector
    sector = False: Query by the stock's industry
    _filter: The sector or industry of the stock entered
    metric: The metric that the user selected
    '''
    
    metric_val = float(str(metric_val).replace('%', ''))
    
    stock_sector_df = df[df['Sector'] == _filter] if sector==True else df[df['Industry'] == _filter]

    stock_sector_df = convert_col_to_float(stock_sector_df, metric)
    stock_sector_data = remove_outliers(stock_sector_df, metric, 3.5 if sector==True else 10)

    fig = plt.figure(figsize=fig_size)
    matplotlib.rcParams['axes.grid'] = True
    matplotlib.rcParams['savefig.transparent'] = True

    custom_style = {'axes.labelcolor': 'white',
                    'xtick.color': 'white',
                    'ytick.color': 'white'}

    sns.set_style({'axes.grid' : False})
    sns.set_style(rc=custom_style)

    ax = sns.distplot(stock_sector_data, bins=10)
    
    display_metric = metric if metric != 'Operating Margin' else 'Op. Margin'
    if display_metric == 'Volatility (Month)': display_metric = 'Volatility' 
    
    subheader = f"{ticker if show_ticker == True else ''} {display_metric}: {str(metric_val)[ : str(metric_val).find('.') + 2]}"

    md = f"Distribution of {metric} values in the {_filter} {'Sector' if sector==True else 'Industry'}" if show_subheader == True else ''

    x_vals = [p.get_x() for p in ax.patches]
    x_vals = np.array(x_vals)
    diff = np.average(np.diff(x_vals))
    bin_to_color = float(metric_val)

    for p in ax.patches:
        if int(p.get_x()) in range(int(bin_to_color - diff), int(bin_to_color + diff)):
            p.set_color('crimson')

    return fig, subheader, md