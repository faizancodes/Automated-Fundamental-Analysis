#!/usr/bin/env python

__author__ = 'Faizan Ahmed'
__email__ = 'faizan.ahmed18@stjohns.edu'
__date__  = '2021/10/04'

import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from itertools import cycle
from datetime import date 
import numpy as np
from tqdm import tqdm   
import random
import sys
import time
import os
import re
import csv


symbols = []
stockCounter = 0

allStockData = {}
sectorData = {}

todaysDate = date.today().strftime("%m/%d/%y").replace('/', '.')

userAgentList = []
useragents = open("useragents.txt", "r")

for line in useragents:
    userAgentList.append(line.replace('\n', ''))


rawURL = 'https://finviz.com/screener.ashx?v=152&c=0,1,2,3,4,5,6,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,26,27,28,29,31,32,33,34,35,36,37,38,39,40,41,43,44,45,46,47,51,52,53,54,57,58,59,65,68,69'
metrics = 'No., Ticker, Company Name, Sector, Industry, Country, Market Cap, Forward P/E, PEG, Price / Sales, Price / Book, Price / Cash, Price / FCF, Dividend Yield, Payout Ratio, EPS This Y, EPS Next Y, EPS Past 5Y, EPS Next 5Y, Sales Past 5Y, EPS Q/Q, Sales Q/Q, Insider Own, Insider Trans, Inst Own, Inst Trans, Short Ratio, ROA, ROE, ROI, Current Ratio, Quick Ratio, LT Debt/Eq, Debt/Eq, Gross Margin, Operating Margin, Profit Margin, Perf Month, Perf Quarter, Perf Half Y, Perf Year, Perf YTD, Volatility (Month), SMA 20, SMA 50, SMA 200, 52W High, 52W Low, RSI, Current Price, Earnings Date, Target Price'
metricFields = metrics.replace(', ', ',').split(',')

gradingMetrics = {'Valuation' : ['Forward P/E', 'PEG', 'Price / Sales', 'Price / Book', 'Price / FCF'],
                  'Profitability' : ['Profit Margin', 'Operating Margin', 'Gross Margin', 'ROE', 'ROA'],
                  'Growth' : ['EPS This Y', 'EPS Next Y', 'EPS Next 5Y', 'Sales Q/Q', 'EPS Q/Q'],
                  'Performance' : ['Perf Month', 'Perf Quarter', 'Perf Half Y', 'Perf Year', 'Perf YTD', 'Volatility (Month)']}

path = 'SectorData\\'

# With this repository, you can generate data from each stock in the S&P500, Mid Cap stocks, or Small Cap stocks. 

stockSetNum = ''
stockSet = ''

try:
    stockSetNum = float(input('Which set of stocks do you want to get the ratings for?\nEnter 1 for S&P500 stocks\nEnter 2 for Mid Cap stocks over $2B Market Cap \nEnter 3 for stocks over $300 Mln Market Cap\nEnter 4 for stocks under $2B Market Cap\nEnter 5 for all stocks\n'))
except:
    print('\n**Enter 1, 2, 3, 4, or 5 to represent the set of stocks you want to get the ratings for**')

if stockSetNum == 1:
    stockSet = 'S&P500'
elif stockSetNum == 2:
    stockSet = 'MidCap'
elif stockSetNum == 3:
    stockSet = 'SmallCapOver300'
elif stockSetNum == 4:
    stockSet = 'SmallCapUnder2B'
elif stockSetNum == 5:
    stockSet = 'All'


# This is where'S&P500Symbols.csv' and 'MidCap+2BSymbols.csv' are located  
symbolsFileName = f"SymbolData\\{stockSet}Symbols.csv"


if os.path.isdir('StockRatings') == False:

    # Creating the Symbol Data Folder
    stockRatingsDir = "StockRatings"
    parentDir = os.getcwd()
    stockRatingsPath = os.path.join(parentDir, stockRatingsDir) 
    os.mkdir(stockRatingsPath) 


# This is where the all the Excel files for the Stock Ratings are stored
saveToFileName = f"StockRatings\\{stockSet}StockRatings{todaysDate}.csv"


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


def convertNum(num):
    try:
        return float(num)
    except:
        return '-'


def removeOutliers(data, std):
    
    data = np.array(data)
    d = np.abs(data - np.median(data))
    
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    
    return data[s < std]  


def getSectorStats(sector, metric, lessThan):

    global sectorData

    smoothedList = removeOutliers(sectorData[sector][metric], 2)
    stdev = np.std(smoothedList, axis = 0) / 3

    percentile = np.percentile(smoothedList, 90) if lessThan == False else np.percentile(smoothedList, 10)
    return percentile, stdev


def convertToLetterGrade(num):
    
    output = 'F'

    if num == 4.3:
        output = 'A+'
    elif num >= 4.0:
        output = 'A'
    elif num >= 3.7:
        output = 'A-'
    elif num >= 3.3:
        output = 'B+'
    elif num >= 3:
        output = 'B'
    elif num >= 2.7:
        output = 'B-'
    elif num >= 2.3:
        output = 'C+'
    elif num >= 2:
        output = 'C'
    elif num >= 1.7:
        output = 'C-'
    elif num >= 1.3:
        output = 'D+'
    elif num >= 1:
        output = 'D'
    elif num >= 0.7:
        output = 'D-'

    return output
    

def getGrade(mtrc, val, sector):

    start = change = 0
    lessThan = False
    grade = 'F'

    if mtrc in ['Forward P/E', 'PEG', 'Price / Sales', 'Price / Book', 'Price / FCF', 'Volatility (Month)']:
        lessThan = True
    
    start, change = getSectorStats(sector, mtrc, lessThan)

    if isinstance(change, np.ndarray) == True:
        change = change[0]

    if isinstance(val, str) == True:
        #print('*********', mtrc, val, sector)
        return 'C'


    if lessThan == True:

        if val < start:
            grade = 'A+'
        elif val < start + change:
            grade = 'A'
        elif val < start + (change * 2):
            grade = 'A-'
        elif val < start + (change * 3):
            grade = 'B+'
        elif val < start + (change * 4):
            grade = 'B'
        elif val < start + (change * 5):
            grade = 'B-'
        elif val < start + (change * 6):
            grade = 'C+'
        elif val < start + (change * 7):
            grade = 'C'
        elif val < start + (change * 8):
            grade = 'C-'
        elif val < start + (change * 9):
            grade = 'D+'
        elif val < start + (change * 10):
            grade = 'D'
        elif val < start + (change * 11):
            grade = 'D-'

    else:

        if val > start:
            grade = 'A+'
        elif val > start - change:
            grade = 'A'
        elif val > start - (change * 2):
            grade = 'A-'
        elif val > start - (change * 3):
            grade = 'B+'
        elif val > start - (change * 4):
            grade = 'B'
        elif val > start - (change * 5):
            grade = 'B-'
        elif val > start - (change * 6):
            grade = 'C+'
        elif val > start - (change * 7):
            grade = 'C'
        elif val > start - (change * 8):
            grade = 'C-'
        elif val > start - (change * 9):
            grade = 'D+'
        elif val > start - (change * 10):
            grade = 'D'
        elif val > start - (change * 11):
            grade = 'D-'

    #print(mtrc, val, start, change, sector, grade)

    return grade


def getCategoryGrade(sector, metric_dict):
    
    score = 0
    grade = "F"
    output = []

    for metric, value in metric_dict.items():
        output.append(getGrade(metric, value, sector))

    for grade in output:

        if grade == 'A+':
            score += 4.3
        elif grade == 'A':
            score += 4
        elif grade == 'A-':
            score += 3.7
        elif grade == 'B+':
            score += 3.3
        elif grade == 'B':
            score += 3
        elif grade == 'B-':
            score += 2.7
        elif grade == 'C+':
            score += 2.3
        elif grade == 'C':
            score += 2 
        elif grade == 'C-':
            score += 1.7
        elif grade == 'D+':
            score += 1.3
        elif grade == 'D':
            score += 1
        elif grade == 'D-':
            score += 0.7
        elif grade == 'F-':
            score -= 1.5

    return round(score / len(metric_dict), 2)


def getOverallRating(valGrade, profGrade, grGrade, pfGrade, vol):
    
    return (valGrade + profGrade + grGrade + pfGrade) * 6


def getNumStocks(url):

    agent = random.choice(userAgentList)
    headers = {'User-Agent': agent}

    page = requests.get(url, headers=headers, proxies = {"http": next(proxyPool)})
    soup = BeautifulSoup(page.content, 'html.parser')

    tableRows = soup.find_all('tr', class_ = re.compile('^table-.*'))
    tags = tableRows[0].find_all(href=True)
    return float(tags[0].text)


def getStockData(sector='all', debug=False):

    sectorAddon = '' if sector == 'all' else f"&f=sec_{sector}"
    pageCounter = 1
    stocksAdded = 20

    numStocks = getNumStocks(f"{rawURL}{sectorAddon}&r=10000") if debug == False else 1000

    print('\n\nGetting Stock Data...')

    with tqdm(total = numStocks) as pbar:
        
        while pageCounter < numStocks:
            
            agent = random.choice(userAgentList)
            headers = {'User-Agent': agent}

            page = requests.get(f"{rawURL}{sectorAddon}&r={pageCounter}", headers=headers, proxies = {"http": next(proxyPool)})
            soup = BeautifulSoup(page.content, 'html.parser')
            tableRows = soup.find_all('tr', class_ = re.compile('^table-.*'))
            stocksAdded = 0
            
            # For every stock in the table 
            for row in tableRows:
            
                tags = row.find_all(href=True)
                ticker = ''

                # All the metrics for the stock
                for i, metric in enumerate(tags):
                    
                    if i == 1:
                        ticker = metric.text
                        allStockData[ticker] = {}
                        stocksAdded += 1
                    
                    elif i > 1:
                        if i >= 7 and i < len(tags) - 2: allStockData[ticker][metricFields[i]] = convertNum(metric.text.strip('%'))
                        else: allStockData[ticker][metricFields[i]] = metric.text
                
                try:
                    allStockData[ticker]['Percent Diff'] = round((float(allStockData[ticker]['Target Price']) - float(allStockData[ticker]['Current Price'])) / float(allStockData[ticker]['Current Price']) * 100, 2)
                except:
                    allStockData[ticker]['Percent Diff'] = '-'
                        
                # Sector Data 
                if (len(sectorData)) == 0 or (allStockData[ticker]['Sector'] not in sectorData):
                    
                    sectorData[allStockData[ticker]['Sector']] = {}

                    for key, value in sectorData.items():
                        for metric in metricFields[7 : -2]:
                            sectorData[allStockData[ticker]['Sector']][metric] = []

                for metric, value in list(allStockData[ticker].items())[5 : -3]:
                    if value != '-': sectorData[allStockData[ticker]['Sector']][metric].append(value)

            pageCounter += 20
            pbar.update(20)


    if debug == True:
        #print(json.dumps(allStockData, indent=4))
        print('\n\n\n\n\n')
        #print(json.dumps(sectorData, indent=4))



def getSectorData():

    print('\n\nGetting Sector Data...')

    for stock in tqdm(allStockData.keys()):
        
        categoryStats = {}
     
        for category in gradingMetrics.keys():
            for metric in gradingMetrics[category]:
                
                if category not in categoryStats:
                    categoryStats[category] = {}
                
                categoryStats[category][metric] = allStockData[stock][metric]


        for category in gradingMetrics.keys():
            try:
                allStockData[stock][f"{category} Grade"] = getCategoryGrade(allStockData[stock]['Sector'], {key : value for key, value in categoryStats[category].items()})
                #print(stock, allStockData[stock][f"{category} Grade"])
            except: 
                allStockData[stock][f"{category} Grade"] = '-'
        
        allStockData[stock]['Overall Rating'] = getOverallRating(allStockData[stock]['Valuation Grade'], allStockData[stock]['Profitability Grade'], allStockData[stock]['Growth Grade'], allStockData[stock]['Performance Grade'], allStockData[stock]['Volatility (Month)'])
        
        for category in gradingMetrics.keys():
            allStockData[stock][f"{category} Grade"] = convertToLetterGrade(allStockData[stock][f"{category} Grade"])

        if allStockData[stock]['Overall Rating'] >= 100:
            allStockData[stock]['Overall Rating'] = 99


def exportStockData(fileName):

    columns = 'Company Name, Market Cap, Overall Rating, Sector, Industry, Country, Valuation Grade, Profitability Grade, Growth Grade, Performance Grade, Forward P/E, PEG, Price / Sales, Price / Book, Price / Cash, Price / FCF, Dividend Yield, Payout Ratio, EPS This Y, EPS Next Y, EPS Past 5Y, EPS Next 5Y, Sales Past 5Y, EPS Q/Q, Sales Q/Q, Insider Own, Insider Trans, Inst Own, Inst Trans, Short Ratio, ROA, ROE, ROI, Current Ratio, Quick Ratio, LT Debt/Eq, Debt/Eq, Gross Margin, Operating Margin, Profit Margin, Perf Month, Perf Quarter, Perf Half Y, Perf Year, Perf YTD, Volatility (Month), SMA 20, SMA 50, SMA 200, 52W High, 52W Low, RSI, Earnings Date, Current Price, Target Price, Percent Diff'

    df = pd.DataFrame(allStockData)
    df = df.T
    df.index.name = 'Ticker'
    df = df[columns.replace(', ', ',').split(',')]
    df.to_csv(fileName)

    print('\nSaved as ' + fileName)


def exportSectorData(fileName):
    
    formattedSectorData = {}
    
    for sector in sectorData.keys():
        for metric in sectorData[sector].keys():
            
            if sector not in formattedSectorData:
                formattedSectorData[sector] = {}
            
            smoothedList = removeOutliers(sectorData[sector][metric], 2)
            formattedSectorData[sector][metric] = [round(np.percentile(smoothedList, 90), 2), round(np.median(smoothedList), 2), round(np.percentile(smoothedList, 10), 2)]
        
    df = pd.DataFrame(formattedSectorData)
    
    df.to_csv("SectorDataRemovedOutliers1x.csv")

    print('\nSaved as ' + 'SectorDataRemovedOutliers1x')


getStockData(debug=False)

getSectorData()

exportStockData(saveToFileName)

exportSectorData(saveToFileName)