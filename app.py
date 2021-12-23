import matplotlib
import pandas as pd
from seaborn.relational import lineplot
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc
import utils as ut


st.set_page_config(page_title="Stock Analysis", page_icon="📈", layout="centered")
st.header('Stock Market Analysis')

# Load the csv file in a dataframe
df = pd.read_csv('AllStockRatings12.23.21.csv')

st.dataframe(df)

st.subheader('Compare stats for each Sector')

remove_vals = ['Ticker', 'Sector', 'Company Name', 'Market Cap', 'Industry', 'Country', 'Earnings Date', 'Valuation Grade', 'Profitability Grade', 'Growth Grade', 'Performance Grade']
selectable_values = [ elem for elem in df.columns.tolist() if elem not in remove_vals ]

values = st.selectbox(
     'Select Values',
     (selectable_values))


df = df[df[values] != '-']

# make the values column numeric
df[values] = pd.to_numeric(df[values], downcast="float")

pivot_table = df.pivot_table(index='Sector', values=values, aggfunc=[np.median])
pivot_table.reset_index(inplace=True)
pivot_table.columns = ['Sector', f"Median {values}"]
pivot_table = pivot_table.sort_values(by= f"Median {values}", ascending=False)
pivot_table[f"Median {values}"] = pivot_table[f"Median {values}"].apply(lambda x: round(x, 1))

st.dataframe(pivot_table)

# Plot the dataframe
bar_plot = px.bar(pivot_table, x='Sector', y=f"Median {values}")
bar_plot.update_xaxes(showgrid=False, zeroline=False)
bar_plot.update_yaxes(showgrid=False, zeroline=False)
st.plotly_chart(bar_plot)


################################################
## Whisker Box Plot
################################################

grouped = df.loc[:,['Sector', values]] \
          .groupby(['Sector']) \
          .median() \
          .sort_values(by=values, ascending=False)


fig = plt.figure(figsize=(25, 15))
matplotlib.rcParams['axes.grid'] = True
matplotlib.rcParams['savefig.transparent'] = True

custom_style = {'axes.labelcolor': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white'}

sns.set_style({'axes.grid' : False})
sns.set_style(rc=custom_style)

sns.boxplot(x=df['Sector'], y=df[values], order=grouped.index, showfliers=False)
sns.set(font_scale = 2)
locs, labels = plt.xticks()
plt.setp(labels, rotation=-45)

st.pyplot(fig)


################################################
## Sector Distribution Plot
################################################

st.markdown("***")
st.subheader('Select two Sectors and compare a metric')

sector1 = st.selectbox(
     'Select a Sector',
     (set(df['Sector'])))

sector2 = st.selectbox(
     'Select a Sector to Compare',
     (set(df['Sector']) - {sector1}))


metric = st.selectbox(
     'Select a Metric',
     (selectable_values))


df = df[df[metric] != '-']
df[metric] = pd.to_numeric(df[metric], downcast="float")

sector1_df = df[df['Sector'] == sector1]
sector2_df = df[df['Sector'] == sector2]

sector1_data = ut.remove_outliers(sector1_df, metric, 3.5)
sector2_data = ut.remove_outliers(sector2_df, metric, 3.5)

fig = plt.figure(figsize=(25, 15))
matplotlib.rcParams['axes.grid'] = True
matplotlib.rcParams['savefig.transparent'] = True

custom_style = {'axes.labelcolor': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white'}

sns.set_style({'axes.grid' : False})
sns.set_style(rc=custom_style)

sns.distplot(sector1_data, bins=10)
sns.distplot(sector2_data, bins=10)
plt.legend([sector1, sector2])

st.pyplot(fig)


################################################
## Metric Scatter Plot
################################################

st.markdown("***")

st.subheader('Select two metrics to compare and find any correlations')

metric1 = st.selectbox(
     'Select x-axis metric',
     (selectable_values))

new_selectable_values = selectable_values.copy()
new_selectable_values.remove(metric1)

metric2 = st.selectbox(
     'Select y-axis metric',
     (new_selectable_values))


df = ut.convert_col_to_float(df, metric1)
df = ut.convert_col_to_float(df, metric2)

df = ut.remove_outliers_2(df, metric1)
df = ut.remove_outliers_2(df, metric2)


scatter_plot = px.scatter(df, x=metric1, y=metric2, color='Sector', trendline="ols", trendline_scope='overall', opacity=0.55)
scatter_plot.update_xaxes(showgrid=False, zeroline=False)
scatter_plot.update_yaxes(showgrid=False, zeroline=False)
st.plotly_chart(scatter_plot)

correlation_matrix = np.corrcoef(df[metric1], df[metric2])
correlation_xy = correlation_matrix[0,1]
r_squared = round(correlation_xy**2, 3)

st.subheader(f"R^2: {r_squared}")


################################################
## Stock Analysis
################################################

st.markdown("***")

ticker = st.text_input('Enter a Ticker Symbol', 'AAPL')

row = df[df['Ticker'] == ticker]

rating = round(row['Overall Rating'].values[0], 1)

col1, col2, col3 = st.columns(3)
col1.metric("Company Name", row['Company Name'].values[0])
col2.metric("Market Cap", row['Market Cap'].values[0])
col3.metric("Overall Rating", str(rating)[0 : str(rating).find('.')])

col4, col5, col6 = st.columns(3)
col4.metric("Current Price", row['Current Price'].values[0])
col5.metric("Sector", row['Sector'].values[0])
col6.metric("Industry", row['Industry'].values[0])

stock_metric = st.selectbox(
     'Pick a metric to analyze',
     (selectable_values))

# col7, col8, col9 = st.columns(3)

stock_sector_df = df[df['Sector'] == row['Sector'].values[0]]

stock_sector_df = ut.convert_col_to_float(stock_sector_df, stock_metric)
stock_sector_data = ut.remove_outliers(stock_sector_df, stock_metric, 3.5)

fig = plt.figure(figsize=(25, 15))
matplotlib.rcParams['axes.grid'] = True
matplotlib.rcParams['savefig.transparent'] = True

custom_style = {'axes.labelcolor': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white'}

sns.set_style({'axes.grid' : False})
sns.set_style(rc=custom_style)

ax = sns.distplot(stock_sector_data, bins=10)

st.subheader(f"{ticker} {stock_metric}: {str(row[stock_metric].values[0]).split('.')[0]}")

st.markdown(f"Distribution of {stock_metric} values in the {row['Sector'].values[0]} Sector")

x_vals = [p.get_x() for p in ax.patches]
x_vals = np.array(x_vals)
diff = np.average(np.diff(x_vals))
bin_to_color = float(row[stock_metric].values[0])

for p in ax.patches:
     if int(p.get_x()) in range(int(bin_to_color - diff), int(bin_to_color + diff)):
          p.set_color('crimson')

st.pyplot(fig)
