
__author__ = 'Faizan Ahmed'
__email__ = 'faizan.ahmed18@stjohns.edu'
__date__  = '2022/04/05'


import requests
import pandas as pd
from bs4 import BeautifulSoup
from itertools import cycle
from datetime import date 
import numpy as np
from tqdm import tqdm   
import random
import time
import collections
import warnings

warnings.filterwarnings('ignore')

today_date = date.today().strftime("%m/%d/%y").replace('/', '.')

allStockData = {}
tickers = []
dataframes = []
sector_data = collections.defaultdict(lambda : collections.defaultdict(dict))
data_to_add = collections.defaultdict(list)


grading_metrics = {'Valuation' : ['Fwd P/E', 'PEG', 'P/S', 'P/B', 'P/FCF'],
                  'Profitability' : ['Profit M', 'Oper M', 'Gross M', 'ROE', 'ROA'],
                  'Growth' : ['EPS this Y', 'EPS next Y', 'EPS next 5Y', 'Sales Q/Q', 'EPS Q/Q'],
                  'Performance' : ['Perf Month', 'Perf Quart', 'Perf Half', 'Perf Year', 'Perf YTD', 'Volatility M']}


URL = 'https://finviz.com/screener.ashx?v=152&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,26,27,28,29,31,32,33,34,35,36,37,38,39,40,41,43,44,45,46,47,51,52,53,54,57,58,59,65,68,69'


def getProxies(inURL):

    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    terms = soup.find_all('tr')
    IPs = []

    for x in range(len(terms)):  
        
        term = str(terms[x])        
        
        if '<tr><td>' in str(terms[x]):
            pos1 = term.find('d>') + 2
            pos2 = term.find('</td>')

            pos3 = term.find('</td><td>') + 9
            pos4 = term.find('</td><td>US<')
            
            IP = term[pos1:pos2]
            port = term[pos3:pos4]
            
            if '.' in IP and len(port) < 6:
                IPs.append(IP + ":" + port)

    return IPs 


proxyURL = "https://www.us-proxy.org/"
pxs = getProxies(proxyURL)
proxyPool = cycle(pxs)

userAgentList = []
useragents = open("useragents.txt", "r")

for line in useragents:
    userAgentList.append(line.replace('\n', ''))
    
useragents.close()


def getNumStocks(url):

    agent = random.choice(userAgentList)
    headers = {'User-Agent': agent}

    page = requests.get(url, headers=headers, proxies = {"http": next(proxyPool)})
    soup = BeautifulSoup(page.content, 'html.parser')

    tableRows = soup.find_all('a', class_ = 'screener-link')
    
    raw_num = str(tableRows[0])
    num_stocks = raw_num[raw_num.find('">') + 2 : raw_num.find('</a>')]
    
    return float(num_stocks)


def get_company_data(url, debug=False):
    
    global allStockData
    
    pageCounter = 1
    num_stocks = getNumStocks(f"{URL}&r=10000") if debug == False else 200
    
    print('\nTotal Stocks:', num_stocks)
    print('\nScraping data...\n')

    with tqdm(total = num_stocks) as pbar:
        
        while pageCounter < num_stocks:
            agent = random.choice(userAgentList)
            headers = {'User-Agent': agent}

            page = requests.get(f"{url}&r={pageCounter}", headers=headers, proxies = {"http": next(proxyPool)})
            
            try:
                tables = pd.read_html(page.text)
            except:
                soup = BeautifulSoup(page.text, 'html.parser')
                print('PARSE ERRORR', soup)
            
            try:    
                table = tables[-2]  
                
                if pageCounter != 1:
                    table = table[1:]
                
                #print(tables[-2])
                dataframes.append(table)
            
            except:
                # print('TABLE ERROR', tables)
                # print(f"{url}&r={pageCounter}")
                # print()
                pass
                
            pageCounter += 20

            time.sleep(np.random.uniform(0.5, 1))
            
            pbar.update(20)

    allStockData = pd.concat(dataframes)
    allStockData.columns = list(allStockData.iloc[0])
    allStockData = allStockData[1:]
    

    
def remove_outliers(S, std):    
    s1 = S[~((S-S.mean()).abs() > std * S.std())]
    return s1[~((s1-s1.mean()).abs() > std * s1.std())]


def get_sector_data():
    
    global sector_data
    global allStockData
    
    sectors = allStockData['Sector'].unique()
    metrics = allStockData.columns[7: -3]

    for sector in sectors:
        
        rows = allStockData.loc[allStockData['Sector'] == sector]
        
        for metric in metrics:
            
            rows[metric] = rows[metric].str.rstrip('%')
            rows[metric] = pd.to_numeric(rows[metric], errors='coerce')
            data = remove_outliers(rows[metric], 2)
            
            sector_data[sector][metric]['Median'] = data.median(skipna=True)
            sector_data[sector][metric]['10Pct'] = data.quantile(0.1)
            sector_data[sector][metric]['90Pct'] = data.quantile(0.9)
            sector_data[sector][metric]['Std'] = np.std(data, axis=0) / 5    
    
    

def get_metric_val(ticker, metric_name):
    try:
        return float(str(allStockData.loc[allStockData['Ticker'] == ticker][metric_name].values[0]).rstrip("%"))
    except:
        return 0


def convert_to_letter_grade(val):

    grade_scores = {'A+' : 4.3, 'A' : 4.0, 'A-' : 3.7, 'B+' : 3.3, 'B' : 3.0, 'B-' : 2.7, 
                    'C+' : 2.3, 'C' : 2.0, 'C-' : 1.7, 'D+' : 1.3, 'D' : 1.0, 'D-' : 0.7, 'F' : 0.0}
    
    for grade in grade_scores:
        if val >= grade_scores[grade]:
            return grade
    

def get_metric_grade(sector, metric_name, metric_val):
    
    global sector_data
    
    lessThan = metric_name in ['Fwd P/E', 'PEG', 'P/S', 'P/B', 'P/FCF', 'Volatility M']
    
    grade_basis = '10Pct' if lessThan else '90Pct'
    
    start, change = sector_data[sector][metric_name][grade_basis], sector_data[sector][metric_name]['Std']
    
    grade_map = {'A+': 0, 'A': change, 'A-' : change * 2, 'B+' : change * 3, 'B' : change * 4, 
                 'B-' : change * 5, 'C+' : change * 6, 'C' : change * 7, 'C-' : change * 8, 
                 'D+' : change * 9, 'D' : change * 10, 'D-' : change * 11, 'F' : change * 12}
    
    
    for grade, val in grade_map.items():
        comparison = start + val if lessThan else start - val
       
        if lessThan and metric_val < comparison:
            return grade
        
        if lessThan == False and metric_val > comparison:
            return grade
            
    return 'C'


def get_category_grades(ticker, sector):
    
    global grading_metrics
    
    grade_scores = {'A+' : 4.3, 'A' : 4.0, 'A-' : 3.7, 'B+' : 3.3, 'B' : 3.0, 'B-' : 2.7, 
                    'C+' : 2.3, 'C' : 2.0, 'C-' : 1.7, 'D+' : 1.3, 'D' : 1.0, 'D-' : 0.7, 'F' : 0.0}
    
    category_grades = {}
    
    for category in grading_metrics:
        
        metric_grades = []
        
        for metric_name in grading_metrics[category]:
            
            metric_grades.append(get_metric_grade(sector, metric_name, get_metric_val(ticker, metric_name)))
            
        category_grades[category] = metric_grades
        
    for category in category_grades:
        
        score = 0
        
        for grade in category_grades[category]:
            score += grade_scores[grade]
        
        category_grades[category].append(round(score / len(category_grades[category]), 2))
        
    return category_grades
    
    
def get_stock_rating(category_grades):
    
    score = 0
    
    for category in category_grades:
        score += category_grades[category][-1]
        
    return round(score * 6.2, 2)   
    
    
def get_stock_rating_data(debug=False):
    
    global data_to_add
    global allStockData
    
    counter = 0
    print('\nCalculating Stock Ratings...\n')

    with tqdm(total = allStockData.shape[0]) as pbar:
        
        for row in allStockData.iterrows():
            
            ticker, sector = row[1]['Ticker'], row[1]['Sector']
            
            category_grades = get_category_grades(ticker, sector)
            stock_rating = get_stock_rating(category_grades)
            
            data_to_add['Overall Rating'].append(stock_rating)
            data_to_add['Valuation Grade'].append(convert_to_letter_grade(category_grades['Valuation'][-1]))
            data_to_add['Profitability Grade'].append(convert_to_letter_grade(category_grades['Profitability'][-1]))
            data_to_add['Growth Grade'].append(convert_to_letter_grade(category_grades['Growth'][-1]))
            data_to_add['Performance Grade'].append(convert_to_letter_grade(category_grades['Performance'][-1]))
            
            # print(row[1]['Ticker'])
            # print(category_grades)
            # print(stock_rating)
            # print()   
            
            counter += 1 
            pbar.update(1)
            
            if debug == True and counter == 10:
                break
    
    
def export_to_csv(filename):
    
    global allStockData
    
    allStockData['Overall Rating'] = data_to_add['Overall Rating']
    allStockData['Valuation Grade'] = data_to_add['Valuation Grade']
    allStockData['Profitability Grade'] = data_to_add['Profitability Grade']
    allStockData['Growth Grade'] = data_to_add['Growth Grade']
    allStockData['Performance Grade'] = data_to_add['Performance Grade']    
    allStockData['Percent Diff'] = (pd.to_numeric(allStockData['Target Price'], errors='coerce') - pd.to_numeric(allStockData['Price'], errors='coerce')) / pd.to_numeric(allStockData['Price'], errors='coerce') * 100

    ordered_columns = 'Ticker, Company, Market Cap, Overall Rating, Sector, Industry, Country, Valuation Grade, Profitability Grade, Growth Grade, Performance Grade, Fwd P/E, PEG, P/S, P/B, P/C, P/FCF, Dividend, Payout Ratio, EPS this Y, EPS next Y, EPS past 5Y, EPS next 5Y, Sales past 5Y, EPS Q/Q, Sales Q/Q, Insider Own, Insider Trans, Inst Own, Inst Trans, Short Ratio, ROA, ROE, ROI, Curr R, Quick R, LTDebt/Eq, Debt/Eq, Gross M, Oper M, Profit M, Perf Month, Perf Quart, Perf Half, Perf Year, Perf YTD, Volatility M, SMA20, SMA50, SMA200, 52W High, 52W Low, RSI, Earnings, Price, Target Price, Percent Diff'

    stock_csv_data = allStockData
    stock_csv_data = allStockData[ordered_columns.replace(', ', ',').split(',')]
    stock_csv_data.to_csv(filename, index=False)
    
    print('\nSaved as', f"StockRatings-{today_date}.csv")
    
      
       
get_company_data(URL, debug=False)

get_sector_data()

get_stock_rating_data()

export_to_csv(f"StockRatings-{today_date}.csv")
