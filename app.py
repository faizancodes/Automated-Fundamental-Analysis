import matplotlib
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc


st.set_page_config(page_title="Stock Analysis", page_icon="📈", layout="centered")
st.header('Stock Market Analysis')

# Load the csv file in a dataframe
df = pd.read_csv('AllStockRatings12.18.21.csv')

st.dataframe(df)

st.subheader('Compare stats for each Sector')

remove_vals = ['Ticker', 'Sector', 'Company Name', 'Market Cap', 'Industry', 'Country', 'Earnings Date', 'Valuation Grade', 'Profitability Grade', 'Growth Grade', 'Performance Grade']
selectable_values = df.columns.tolist()
selectable_values = [ elem for elem in selectable_values if elem not in remove_vals ]


values = st.selectbox(
     'Select Values',
     (selectable_values))


st.markdown(f"Sector vs {values}")

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

fig = plt.figure(figsize=(25, 15))
matplotlib.rcParams['axes.grid'] = True
matplotlib.rcParams['savefig.transparent'] = True

sector1_data = np.array(sector1_df[metric])
d1 = np.abs(sector1_data - np.median(sector1_data))
mdev1 = np.median(d1)
s1 = d1 / mdev1 if mdev1 else 0.

sector2_data = np.array(sector2_df[metric])
d2 = np.abs(sector2_data - np.median(sector2_data))
mdev2 = np.median(d2)
s2 = d2 / mdev2 if mdev2 else 0.

sector1_data = sector1_data[s1 < 3.5]  
sector2_data = sector2_data[s2 < 3.5]  

custom_style = {'axes.labelcolor': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white'}

sns.set_style({'axes.grid' : False})
sns.set_style(rc=custom_style)

sns.distplot(sector1_data, bins=10)
sns.distplot(sector2_data, bins=10)
plt.legend([sector1, sector2])

st.pyplot(fig)



