## Faizan Ahmed
## faizan.ahmed18@stjohns.edu
## 1/12/2021


# ## This program calculates the average values for metrics that relate to a stock's valuation, profitability, growth, and price performance, separated by sector.  


import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
from itertools import cycle
from csv import reader
import seaborn as sns
import numpy as np
import statistics
import ast
import sys
import time
import os
import csv



if os.path.isdir('SectorData') == False:
    
    # Creating the Sector Data Folder
    sectorDataDir = "SectorData"
    parentDir = os.getcwd()
    sectorDataPath = os.path.join(parentDir, sectorDataDir) 
    os.mkdir(sectorDataPath) 


if os.path.isdir('SymbolData') == False:

    # Creating the Symbol Data Folder
    symbolDataDir = "SymbolData"
    symbolDataPath = os.path.join(parentDir, symbolDataDir) 
    os.mkdir(symbolDataPath) 



path = 'SectorData\\'
symbolsPath = 'SymbolData\\'


sectors = ['basicmaterials', 'communicationservices', 
           'consumercyclical', 'consumerdefensive', 'energy',
          'financial', 'healthcare', 'industrials', 'realestate',
          'technology', 'utilities']

rawURL = 'https://finviz.com/screener.ashx?v=152&c=0,1,2,3,4,5,6,8,9,10,11,13,17,18,20,22,23,32,33,34,35,36,37,38,39,40,41,43,44,45,46,47,51&f=sec_'


agent = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}


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
                #print(IP + ":" + port)

    return IPs 


def clean(stng):
    
    output = ''

    for letter in stng:
        if letter not in "[]()'": 
            output += letter
        
    return output


proxyURL = "https://www.us-proxy.org/"
pxs = getProxies(proxyURL)
proxyPool = cycle(pxs)


# Scrape data from website and save to csv files


header = 'Index, Symbol, Company Name, Sector, Industry, Country, Market Cap, Forward PE, PEG, Price/Sales, Price/Book, Price/FCF, EPS This Y, EPS Next Y, EPS Next 5Y, EPS Q/Q, Sales Q/Q, ROA, ROE, ROI, Current Ratio, Quick Ratio, LT Debt/Equity, Debt/Equity, Gross Margin, Operating Margin, Net Margin, Perf Month, Perf Quarter, Perf Half Y, Perf Year, Perf YTD, Volatility (Month)' + '\n'
allData = []

for i in range(len(sectors)):
    
    pageCounter = 1
    stocksAdded = 20
    stockData = []
    
    print('\nGathering data from ' + sectors[i] + ' sector...')

    while stocksAdded == 20:

        stocksAdded = 0

        URL = rawURL + sectors[i] + '&r=' + str(pageCounter)

        #print(URL, pageCounter)

        page = requests.get(URL, headers=agent, proxies = {"http": next(proxyPool)})
        soup = BeautifulSoup(page.content, 'html.parser')

        tableLightStocks = soup.find_all('tr', {'class': 'table-light-row-cp'})
        tableDarkStocks = soup.find_all('tr', {'class': 'table-dark-row-cp'})

        tableStocks = list(tableLightStocks) + list(tableDarkStocks)

        for result in tableStocks:

            result = str(result)
            rawString = result
            data = ''

            while '<' in rawString:

                rawString = rawString[rawString.find('<') + 3 : ]
                stng = rawString[rawString.find('>') + 1 : rawString.find('<')]

                if len(stng) > 0:
                    data += stng.replace('&amp;', '&').replace(',', '') + ', '

            data = '[' + data[3 : -2] + ']'

            stockData.append([tuple(map(str, data.split(', '))) ])
            allData.append([tuple(map(str, data.split(', '))) ])
            stocksAdded += 1

        pageCounter += 20


    MyFile = open(path + 'SectorData - ' + sectors[i] + '.csv', 'w')
    MyFile.write(header)

    for row in stockData:
        MyFile.write(clean(str(row)))
        MyFile.write('\n')

    MyFile.close()
    print('Saved:', path + 'SectorData - ' + sectors[i] + '.csv')

                      
        


MyFile = open(path + 'SectorData - AllSectors.csv', 'w')
MyFile.write(header)

for row in allData:
    MyFile.write(clean(str(row)))
    MyFile.write('\n')

MyFile.close()
print('Saved:', path + 'SectorData - AllSectors.csv')


# ## This is a helper function for the `stockratings.py` file.
# 
# The method computes the average values for a specified metric for the provided sector after removing outliers
# 
# This method is used to evaluate the stock's rating, by comparing it to its overall sector.
# 
# ## The function has three outputs: 
#
# 1. **Smoothed Avg**: Represents the average value of the specified metric for the sector after removing outliers 
# 
# 
# 2. **Start**: This represents an optimal value for the specified metric for the sector. If a certain stock's metric has a value that is greater or lower than this number, it receives a grade of A+, as shown in the file `SP&500StockRatings.csv`. In the case that a lower value for the metric is considered "better", return the 10th percentile and if not, return the 90th percentile
# 
# 
# 3. **Stdev**: Represents the standard deviation of the values of all the metrics for the sector. This number is used to provide each stock with a letter grade, it is what separates an A+ and an A.
 

def getAverage(sector, metric, lessThan):
    
    with open(path + 'SectorData - ' + sector + '.csv', 'r') as rdr:
        
        csv = reader(rdr)
        sectorData = list(csv)
        
    avg = 0
    columnToSearch = 0 
    validCells = 0
    metrics = []
    
    for column in range(len(sectorData[0])):
        
        if sectorData[0][column][1: ].casefold() == metric.casefold():
            columnToSearch = column

            
    for row in range(1, len(sectorData)):
        
        cell = sectorData[row][columnToSearch].replace('%', '').replace(' ', '')
        
        if cell != '-':
            
            avg += float(cell)
            metrics.append(float(cell))
            validCells += 1
    
    elements = np.array(metrics)
    mean = np.mean(elements, axis=0)
    sd = np.std(elements, axis=0)

    for i in range(2):
        smoothedList = [x for x in metrics if (x > mean - 2 * sd)]
        smoothedList = [x for x in smoothedList if (x < mean + 2 * sd)]

        mean = np.mean(smoothedList, axis=0)
        sd = np.std(smoothedList, axis=0)

    metricAvg = avg / validCells 
    stdev = np.std(smoothedList, axis = 0) / 3
    
    
    start = np.percentile(smoothedList, 90)
    smoothedAvg =  np.percentile(smoothedList, 50)
    
    if lessThan == True:
        start = np.percentile(smoothedList, 10)
    
    #sns.distplot(smoothedList);
    
    #print(sector + ' raw ' + metric + ' Avg:', metricAvg, stdev)
    #print('\nMetrics Available:', [metric[1 : ] for metric in sectorData[0][7 : ]])
    
    return smoothedAvg, start, stdev
    

sectorData = []

#smoothAvg, start, change = getAverage('technology', 'net margin', False)
#print('\nAvg', smoothAvg, 'Start', str(start)[0:6], 'Change', str(change)[0:6])



header = [sector for sector in sectors]
header = ' ,' + (" ".join(header)).replace(' ', ', ') + '\n'


# ## Save all metric averages in a csv file


avgData = []
metrics = ['Forward PE', 'PEG', 'Price/Sales', 'Price/Book', 'Price/FCF', 'EPS This Y', 'EPS Next Y', 'EPS Next 5Y', 'EPS Q/Q', 'Sales Q/Q', 'ROA', 'ROE', 'ROI', 'Current Ratio', 'Quick Ratio', 'LT Debt/Equity', 'Debt/Equity', 'Gross Margin', 'Operating Margin', 'Net Margin', 'Perf Month', 'Perf Quarter', 'Perf Half Y', 'Perf Year', 'Perf YTD', 'Volatility (Month)']
lessThanMetrics = ['Forward PE', 'PEG', 'Price/Sales', 'Price/Book', 'Price/FCF', 'LT Debt/Equity', 'Debt/Equity', 'Volatility (Month)']


for metric in metrics:
    
    stng = ''
    
    for sector in sectors:
        
        lessThan = False
        if metric in lessThanMetrics: lessThan = True
        
        smoothAvg, start, change = getAverage(sector, metric, lessThan)
        
        if sector == 'basicmaterials': stng += str(metric) + ', ' + str(smoothAvg) + ', '
        else: stng += str(smoothAvg) + ', '
    
    
    stng = stng[:-2]
    avgData.append([stng])
        


MyFile = open(path + 'AverageSectorMetrics.csv', 'w')
MyFile.write(header)

for row in avgData:
    MyFile.write(clean(str(row)))
    MyFile.write('\n')

MyFile.close()
print('Saved to: ' + path + 'AverageSectorMetrics.csv')



symbolSets = ['S&P500', 'MidCap', 'SmallCapOver300', 'SmallCapUnder2B']

for i, symbolSet in enumerate(symbolSets):
    
    print('\nGetting ' + symbolSet + ' Symbols...')
    
    if i == 0: 
        rawURL = 'https://finviz.com/screener.ashx?v=111&f=idx_sp500'
    elif i == 1:
        rawURL = 'https://finviz.com/screener.ashx?v=111&f=cap_midover'
    elif i == 2:
        rawURL = 'https://finviz.com/screener.ashx?v=111&f=cap_smallover'
    else:
        rawURL = 'https://finviz.com/screener.ashx?v=111&f=cap_smallunder'
        
    symbols = []
    pageCounter = 1
    stocksAdded = 20
    
    while stocksAdded == 20:

        stocksAdded = 0
        
        URL = rawURL + '&r=' + str(pageCounter)
        page = requests.get(URL, headers=agent, proxies = {"http": next(proxyPool)})
        soup = BeautifulSoup(page.content, 'html.parser')

        tableLightStocks = soup.find_all('tr', {'class': 'table-light-row-cp'})
        tableDarkStocks = soup.find_all('tr', {'class': 'table-dark-row-cp'})

        tableStocks = list(tableLightStocks) + list(tableDarkStocks)

        for result in tableStocks:

            result = str(result)
            rawSymbol = result[result.find('"quote.ashx?t=') + 5 : result.find('"quote.ashx?t=') + 25]
            symbol = rawSymbol[rawSymbol.find('=') + 1 : rawSymbol.find('&')]

            symbols.append(symbol)
            stocksAdded += 1
        
            
        pageCounter += 20


    MyFile = open(symbolsPath + symbolSet + 'Symbols.csv', 'w')

    for row in symbols:
        MyFile.write(clean(str(row)))
        MyFile.write('\n')

    MyFile.close()
    print('Saved as ' + symbolsPath + symbolSet + 'Symbols.csv')