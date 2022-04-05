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

user_input_file = st.file_uploader("Upload the StockRatings CSV file", type=["csv"])

if user_input_file is not None:
     
     # Load the csv file in a dataframe
     df = pd.read_csv(user_input_file)

     st.dataframe(df)

     st.subheader('Compare stats for each Sector')

     remove_vals = ['Ticker', 'Sector', 'Company', 'Market Cap', 'Industry', 'Country', 'Earnings Date', 'Valuation Grade', 'Profitability Grade', 'Growth Grade', 'Performance Grade']
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
     col1.metric("Company", row['Company'].values[0])
     col2.metric("Market Cap", row['Market Cap'].values[0])
     col3.metric("Overall Rating", str(rating)[0 : str(rating).find('.')])

     col4, col5, col6 = st.columns(3)
     col4.metric("Price", row['Price'].values[0])
     col5.metric("Sector", row['Sector'].values[0])
     col6.metric("Industry", row['Industry'].values[0])

     stock_metric = st.selectbox(
          'Pick a metric to analyze',
          (selectable_values))

     filter_by = st.radio(
          "Analyze by",
          ('Sector', 'Industry'))


     fig, subheader, md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=stock_metric, metric_val=row[stock_metric].values[0])

     st.subheader(subheader)
     st.markdown(md)
     st.pyplot(fig)

     # Valuation Section 

     st.text('')
     st.subheader(f"Valuation Grade: {row['Valuation Grade'].values[0]}")

     val_col1, val_col2, val_col3 = st.columns(3)
     val_cols = [val_col1, val_col2, val_col3]

     val_col4, val_col5, val_col6 = st.columns(3)
     val_cols2 = [val_col4, val_col5, val_col6]

     for i, _metric in enumerate(['Fwd P/E', 'P/S', 'P/FCF']):
          val_fig, val_subheader, val_md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=_metric, metric_val=row[_metric].values[0], fig_size=(35, 25), show_ticker=False, show_subheader=False)
          val_cols[i].subheader(val_subheader)
          val_cols[i].pyplot(val_fig)


     for i, _metric in enumerate(['PEG', 'P/C', 'P/B']):
          val_fig, val_subheader, val_md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=_metric, metric_val=row[_metric].values[0], fig_size=(35, 25), show_ticker=False, show_subheader=False)
          val_cols2[i].subheader(val_subheader)
          val_cols2[i].pyplot(val_fig)


     # Profitability Section

     st.text('')
     st.subheader(f"Profitability Grade: {row['Profitability Grade'].values[0]}")

     prof_col1, prof_col2, prof_col3 = st.columns(3)
     prof_cols = [prof_col1, prof_col2, prof_col3]

     prof_col4, prof_col5, prof_col6 = st.columns(3)
     prof_cols2 = [prof_col4, prof_col5, prof_col6]

     for i, _metric in enumerate(['Profit M', 'Oper M', 'Gross M']):
          prof_fig, prof_subheader, prof_md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=_metric, metric_val=row[_metric].values[0], fig_size=(35, 25), show_ticker=False, show_subheader=False)
          prof_cols[i].subheader(prof_subheader)
          prof_cols[i].pyplot(prof_fig)


     for i, _metric in enumerate(['ROE', 'ROA', 'ROI']):
          prof_fig, prof_subheader, prof_md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=_metric, metric_val=row[_metric].values[0], fig_size=(35, 25), show_ticker=False, show_subheader=False)
          prof_cols2[i].subheader(prof_subheader)
          prof_cols2[i].pyplot(prof_fig)


     # Growth Section 

     st.text('')
     st.subheader(f"Growth Grade: {row['Growth Grade'].values[0]}")

     gr_col1, gr_col2, gr_col3 = st.columns(3)
     gr_cols = [gr_col1, gr_col2, gr_col3]

     gr_col4, gr_col5, gr_col6 = st.columns(3)
     gr_cols2 = [gr_col4, gr_col5, gr_col6]

     for i, _metric in enumerate(['EPS this Y', 'EPS next Y', 'EPS next 5Y']):
          gr_fig, gr_subheader, gr_md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=_metric, metric_val=row[_metric].values[0], fig_size=(35, 25), show_ticker=False, show_subheader=False)
          gr_cols[i].subheader(gr_subheader)
          gr_cols[i].pyplot(gr_fig)


     for i, _metric in enumerate(['EPS past 5Y', 'Sales Q/Q', 'EPS Q/Q']):
          gr_fig, gr_subheader, gr_md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=_metric, metric_val=row[_metric].values[0], fig_size=(35, 25), show_ticker=False, show_subheader=False)

          gr_cols2[i].subheader(gr_subheader)
          gr_cols2[i].pyplot(gr_fig)


     # Performance Section 

     st.text('')
     st.subheader(f"Performance Grade: {row['Performance Grade'].values[0]}")

     perf_col1, perf_col2, perf_col3 = st.columns(3)
     perf_cols = [perf_col1, perf_col2, perf_col3]

     perf_col4, perf_col5, perf_col6 = st.columns(3)
     perf_cols2 = [perf_col4, perf_col5, perf_col6]

     for i, _metric in enumerate(['Perf Month', 'Perf Quart', 'Perf Half']):
          perf_fig, perf_subheader, perf_md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=_metric, metric_val=row[_metric].values[0], fig_size=(35, 25), show_ticker=False, show_subheader=False)
          perf_cols[i].subheader(perf_subheader)
          perf_cols[i].pyplot(perf_fig)


     for i, _metric in enumerate(['Perf Year', 'Perf YTD', 'Volatility M']):
          perf_fig, perf_subheader, perf_md = ut.plot_dist(df, ticker, sector=(filter_by=='Sector'), _filter=row[filter_by].values[0], metric=_metric, metric_val=row[_metric].values[0], fig_size=(35, 25), show_ticker=False, show_subheader=False)
          perf_cols2[i].subheader(perf_subheader)
          perf_cols2[i].pyplot(perf_fig)