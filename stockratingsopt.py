#!/usr/bin/env python

__author__ = 'Faizan Ahmed'
__email__ = 'faizan.ahmed18@stjohns.edu'
__date__  = '2021/10/04'

import json
import requests
from requests.exceptions import RequestException
from contextlib import closing
import pandas as pd
from bs4 import BeautifulSoup
from itertools import cycle
from datetime import date 
import numpy as np
from tqdm import tqdm   
import sys
import time
import os
import csv


symbols = []
stockCounter = 0

allStockData = {}
sectorData = {}

today = date.today()
todays_date = today.strftime("%m/%d/%y").replace('/', '.')

path = 'SectorData\\'
agent = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}


# With this repository, you can generate data from each stock in the S&P500, Mid Cap stocks, or Small Cap stocks. 

stockSetNum = ''
stockSet = ''

try:
    stockSetNum = float(input('Which set of stocks do you want to get the ratings for?\nEnter 1 for S&P500 stocks\nEnter 2 for Mid Cap stocks over $2B Market Cap \nEnter 3 for stocks over $300 Mln Market Cap\nEnter 4 for stocks under $2B Market Cap\n'))
except:
    print('\n**Enter 1, 2, 3, or 4 to represent the set of stocks you want to get the ratings for**')

if stockSetNum == 1:
    stockSet = 'S&P500'
elif stockSetNum == 2:
    stockSet = 'MidCap'
elif stockSetNum == 3:
    stockSet = 'SmallCapOver300'
elif stockSetNum == 4:
    stockSet = 'SmallCapUnder2B'


# This is where'S&P500Symbols.csv' and 'MidCap+2BSymbols.csv' are located  
symbolsFileName = f"SymbolData\\{stockSet}Symbols.csv"


if os.path.isdir('StockRatings') == False:

    # Creating the Symbol Data Folder
    stockRatingsDir = "StockRatings"
    parentDir = os.getcwd()
    stockRatingsPath = os.path.join(parentDir, stockRatingsDir) 
    os.mkdir(stockRatingsPath) 


# This is where the all the Excel files for the Stock Ratings are stored
saveToFileName = f"StockRatings\\{stockSet}StockRatings{todays_date}.csv"


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


def fixString(stng):
    
    output = ''
    output2 = ''
    
    if '&amp;' in stng:
        output += stng[0 : stng.find('&') + 1]
        output += stng[stng.find(';') + 1 : ]
    else:
        output = stng
    
    for letter in output:
        if letter != ',' and letter.isalpha():
            output2 += letter

    return output2


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

    percentile = np.percentile(smoothedList, 90) if lessThan == True else np.percentile(smoothedList, 10)
    return percentile, stdev


def convertNum(stng):

    output = ''

    for x in range(len(stng)):

        if stng[x].isdigit() or stng[x] == '.' or (x != len(stng) - 1 and stng[x] == '-' and stng[x + 1].isdigit()):
            output += stng[x]

    try:
        return float(output)
    except:
        return 0


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

    if mtrc in ['Forward PE', 'PEG', 'Price/Sales', 'Price/Book', 'Price/FCF', 'Volatility (Month)']:
        lessThan = True
    
    start, change = getSectorStats(sector, mtrc, lessThan)

    if isinstance(change, np.ndarray) == True:
        change = change[0]

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


def getStockData(sym, debug=False):

    global allStockData
    global sectorData

    page = requests.get('https://finviz.com/quote.ashx?t=' + sym, headers=agent, proxies = {"http": next(proxyPool)})
    soup2 = BeautifulSoup(page.text, 'html.parser')
    soup = str(BeautifulSoup(page.text, 'html.parser'))

    stockStats = {}
    stockStats['Symbol'] = sym
 
    rawMarketCap = soup[soup.find('Market capitalization') : soup.find('Market capitalization') + 200]
    stockStats['Market Cap'] = rawMarketCap[rawMarketCap.find('<b>') + 3 : rawMarketCap.find('</b>')]

    rawCompanyName = soup[soup.find('id="ticker">') + 100 : soup.find('id="ticker">') + 500]
    stockStats['Company Name'] = rawCompanyName[rawCompanyName.find('<b>') + 3 : rawCompanyName.find('</b>')]

    rawSector = rawCompanyName[rawCompanyName.find('f=sec') : rawCompanyName.find('f=sec') + 100]
    sector = fixString(rawSector[rawSector.find('>') + 1 : rawSector.find('</a>') + 1].replace(' ', ''))
    stockStats['Sector'] = sector

    rawIndustry = rawCompanyName[rawCompanyName.find('f=ind') : rawCompanyName.find('f=ind') + 100]
    industry = fixString(rawIndustry[rawIndustry.find('>') + 1 : rawIndustry.find('</a>')])
    stockStats['Industry'] = industry


    if not (len(industry) <= 1 or ' Fund' in industry):

        ## =========================================  Valuation  ================================================================

        rawforwardPE = soup[soup.find('Forward P/E') : soup.find('Forward P/E') + 150]
        stockStats['Forward PE'] = convertNum(rawforwardPE[rawforwardPE.find('<b>') + 3 : rawforwardPE.find('</b>') + 1])

        rawPEG = soup[soup.find('PEG') : soup.find('PEG') + 150]
        stockStats['PEG'] = convertNum(rawPEG[rawPEG.find('<b>') + 3 : rawPEG.find('</b>') + 1])

        rawPriceSales = soup[soup.find('P/S') : soup.find('P/S') + 150]
        stockStats['Price/Sales'] = convertNum(rawPriceSales[rawPriceSales.find('<b>') + 3 : rawPriceSales.find('</b>') + 1])

        rawPriceBook = soup[soup.find('P/B') : soup.find('P/B') + 150]
        stockStats['Price/Book'] = convertNum(rawPriceBook[rawPriceBook.find('<b>') + 3 : rawPriceBook.find('</b>') + 1])

        rawPriceFCF = soup[soup.find('P/FCF') : soup.find('P/FCF') + 150]
        stockStats['Price/FCF'] = convertNum(rawPriceFCF[rawPriceFCF.find('<b>') + 3 : rawPriceFCF.find('</b>') + 1])


        ## =========================================  Profitability  ==============================================================

        rawProfitMargin = soup[soup.find('Profit Margin') : soup.find('Profit Margin') + 250]
        stockStats['Profit Margin'] = convertNum(rawProfitMargin[rawProfitMargin.find('<b>') + 3 : rawProfitMargin.find('</b>') + 1])

        rawOperMargin = soup[soup.find('Operating Margin') : soup.find('Operating Margin') + 250]
        stockStats['Operating Margin'] = convertNum(rawOperMargin[rawOperMargin.find('<b>') + 3 : rawOperMargin.find('</b>') + 1])

        rawGrossMargin = soup[soup.find('Gross Margin') : soup.find('Gross Margin') + 250]
        stockStats['Gross Margin'] = convertNum(rawGrossMargin[rawGrossMargin.find('<b>') + 3 : rawGrossMargin.find('</b>') + 1])

        rawROE = soup[soup.find('ROE') : soup.find('ROE') + 250]
        stockStats['ROE'] = convertNum(rawROE[rawROE.find('<b>') + 3 : rawROE.find('</b>') + 1])

        rawROA = soup[soup.find('ROA') : soup.find('ROA') + 250]
        stockStats['ROA'] = convertNum(rawROA[rawROA.find('<b>') + 3 : rawROA.find('</b>') + 1])
        

        ## =========================================  Growth  ==============================================================


        rawEPSThisY = soup[soup.find('EPS this Y') : soup.find('EPS this Y') + 250]
        stockStats['EPS This Y'] = convertNum(rawEPSThisY[rawEPSThisY.find('<b>') + 3 : rawEPSThisY.find('</b>') + 1])

        rawEPSNextY = soup[soup.find('EPS growth next year') : soup.find('EPS growth next year') + 250]
        stockStats['EPS Next Y'] = convertNum(rawEPSNextY[rawEPSNextY.find('<b>') + 3 : rawEPSNextY.find('</b>') + 1])

        rawEPSNext5Y = soup[soup.find('EPS next 5Y') : soup.find('EPS next 5Y') + 250]
        stockStats['EPS Next 5Y'] = convertNum(rawEPSNext5Y[rawEPSNext5Y.find('<b>') + 3 : rawEPSNext5Y.find('</b>') + 1])

        rawSalesQQ = soup[soup.find('Sales Q/Q') : soup.find('Sales Q/Q') + 250]
        stockStats['Sales Q/Q'] = convertNum(rawSalesQQ[rawSalesQQ.find('<b>') + 3 : rawSalesQQ.find('</b>') + 1])

        rawEPSQQ = soup[soup.find('EPS Q/Q') : soup.find('EPS Q/Q') + 250]
        stockStats['EPS Q/Q'] = convertNum(rawEPSQQ[rawEPSQQ.find('<b>') + 3 : rawEPSQQ.find('</b>') + 1])


        ## =========================================  Price Performance  ====================================================

        rawPerfMonth = soup[soup.find('Perf Month') : soup.find('Perf Month') + 250]
        stockStats['Perf Month'] = convertNum(rawPerfMonth[rawPerfMonth.find('<b>') + 3 : rawPerfMonth.find('</b>') + 1])

        rawPerfQuarter = soup[soup.find('Perf Quarter') : soup.find('Perf Quarter') + 250]
        stockStats['Perf Quarter'] = convertNum(rawPerfQuarter[rawPerfQuarter.find('<b>') + 3 : rawPerfQuarter.find('</b>') + 1])

        rawPerfHalfY = soup[soup.find('Perf Half Y') : soup.find('Perf Half Y') + 250]
        stockStats['Perf Half Y'] = convertNum(rawPerfHalfY[rawPerfHalfY.find('<b>') + 3 : rawPerfHalfY.find('</b>') + 1])

        rawPerfYear = soup[soup.find('Perf Year') : soup.find('Perf Year') + 250]
        stockStats['Perf Year'] = convertNum(rawPerfYear[rawPerfYear.find('<b>') + 3 : rawPerfYear.find('</b>') + 1])

        rawPerfYTD = soup[soup.find('Perf YTD') : soup.find('Perf YTD') + 250]
        stockStats['Perf YTD'] = convertNum(rawPerfYTD[rawPerfYTD.find('<b>') + 3 : rawPerfYTD.find('</b>') + 1])

        rawVolatility = soup[soup.find('Volatility') : soup.find('Volatility') + 250]
        rawVol = rawVolatility[rawVolatility.find('<small>') + 7 : rawVolatility.find('</small>') + 1]
        stockStats['Volatility (Month)'] = convertNum(rawVol[rawVol.find(' ') + 1 : len(rawVol)])

        if stockStats['Volatility (Month)'] == 0:
            stockStats['Volatility (Month)'] = convertNum(rawVolatility[rawVolatility.find('<b>') + 3 : rawVolatility.find('</b>') + 1])
        
        volatility = stockStats['Volatility (Month)']

        ## =========================================  Additional Metrics  ====================================================
        
        rawDividend = soup[soup.find('Dividend %') : soup.find('Dividend %') + 250]
        stockStats['Dividend'] = convertNum(rawDividend[rawDividend.find('<b>') + 3 : rawDividend.find('</b>')])

        if stockStats['Dividend'] == 0:
            stockStats['Dividend'] = convertNum(rawDividend[rawDividend.find(';') + 3 : rawDividend.find('</span>') + 1])
        
        rawSMA20 = soup[soup.find('SMA20') : soup.find('SMA20') + 250]
        stockStats['SMA 20'] = convertNum(rawSMA20[rawSMA20.find('<b>') + 3 : rawSMA20.find('</b>') + 1])

        rawSMA50 = soup[soup.find('SMA50') : soup.find('SMA50') + 250]
        stockStats['SMA 50'] = convertNum(rawSMA50[rawSMA50.find('<b>') + 3 : rawSMA50.find('</b>') + 1])

        rawSMA200 = soup[soup.find('SMA200') : soup.find('SMA200') + 250]
        stockStats['SMA 200'] = convertNum(rawSMA200[rawSMA200.find('<b>') + 3 : rawSMA200.find('</b>') + 1])

        rawInstTrans = soup[soup.find('Inst Trans') : soup.find('Inst Trans') + 250]
        stockStats['Inst Trans'] = convertNum(rawInstTrans[rawInstTrans.find('%"><b>') + 3 : rawInstTrans.find('</b></td>')])

        if stockStats['Inst Trans'] == 0:
            stockStats['Inst Trans'] = convertNum(rawInstTrans[rawInstTrans.find(';') + 3 : rawInstTrans.find('</span>') + 1])

        rawInstOwn = soup[soup.find('Inst Own') : soup.find('Inst Own') + 250]
        stockStats['Inst Own'] = convertNum(rawInstOwn[rawInstOwn.find('%"><b>') + 3 : rawInstOwn.find('</b></td>')])

        if stockStats['Inst Own'] == 0:
            stockStats['Inst Own'] = convertNum(rawInstOwn[rawInstOwn.find(';') + 3 : rawInstOwn.find('</span>') + 1])

        rawInsiderOwn = soup[soup.find('Insider Own') : soup.find('Insider Own') + 250]
        stockStats['Insider Own'] = convertNum(rawInsiderOwn[rawInsiderOwn.find('%"><b>') + 3 : rawInsiderOwn.find('</b></td>')])

        if stockStats['Insider Own'] == 0:
            stockStats['Insider Own'] = convertNum(rawInsiderOwn[rawInsiderOwn.find(';') + 3 : rawInsiderOwn.find('</span>') + 1])

        rawInsiderTrans = soup[soup.find('Insider Trans') : soup.find('Insider Trans') + 250]
        stockStats['Insider Trans'] = convertNum(rawInsiderTrans[rawInsiderTrans.find('%"><b>') + 3 : rawInsiderTrans.find('</b></td>')])

        if stockStats['Insider Trans'] == 0:
            stockStats['Insider Trans'] = convertNum(rawInsiderTrans[rawInsiderTrans.find(';') + 3 : rawInsiderTrans.find('</span>') + 1])

        rawTargetPrice = soup[soup.find('Target Price') : soup.find('Target Price') + 250]
        stockStats['Target Price'] = convertNum(rawTargetPrice[rawTargetPrice.find('<b>') + 3 : rawTargetPrice.find('</b>') + 1])
        
        rawPrevClose = soup[soup.find('Prev Close') : soup.find('Prev Close') + 250]
        stockStats['Prev Close'] = convertNum(rawPrevClose[rawPrevClose.find('%"><b>') + 3 : rawPrevClose.find('</b></td>')])

        if stockStats['Prev Close'] == 0:
            stockStats['Prev Close'] = convertNum(rawPrevClose[rawPrevClose.find(';') + 3 : rawPrevClose.find('</span>') + 1])

        try:
            stockStats['Price Projection'] = (stockStats['Target Price'] - stockStats['Prev Close']) / stockStats['Prev Close'] * 100
        except:
            stockStats['Price Projection'] = 0
        
        rawRSI = soup[soup.find('RSI (14)') : soup.find('RSI (14)') + 250]
        stockStats['RSI'] = convertNum(rawRSI[rawRSI.find('<b>') + 3 : rawRSI.find('</b></td>')])
        
        rawShortFloat = soup[soup.find('Short Float') : soup.find('Short Float') + 250]
        stockStats['Short Float'] = convertNum(rawShortFloat[rawShortFloat.find('%"><b>') + 3 : rawShortFloat.find('</b></td>')])

        if stockStats['Short Float'] == 0:
            stockStats['Short Float'] = convertNum(rawShortFloat[rawShortFloat.find(';') + 3 : rawShortFloat.find('</span>') + 1])
        
        raw52WHigh = soup[soup.find('52W High') : soup.find('52W High') + 250]
        stockStats['52W High'] = convertNum(raw52WHigh[raw52WHigh.find('%"><b>') + 3 : raw52WHigh.find('</b></td>')])

        if stockStats['52W High'] == 0:
            stockStats['52W High'] = convertNum(raw52WHigh[raw52WHigh.find(';') + 3 : raw52WHigh.find('</span>') + 1])

        raw52WLow = soup[soup.find('52W Low') : soup.find('52W Low') + 250]
        stockStats['52W Low'] = convertNum(raw52WLow[raw52WLow.find('%"><b>') + 3 : raw52WLow.find('</b></td>')])

        if stockStats['52W Low'] == 0:
            stockStats['52W Low'] = convertNum(raw52WLow[raw52WLow.find(';') + 3 : raw52WLow.find('</span>') + 1])

        rawCurrRatio = soup[soup.find('Current Ratio') : soup.find('Current Ratio') + 250]
        stockStats['Current Ratio'] = convertNum(rawCurrRatio[rawCurrRatio.find('<b>') + 3 : rawCurrRatio.find('</b></td>')])

        rawEarningsDate = soup[soup.find('Earnings date&lt;br&gt') + 150: soup.find('Earnings date&lt;br&gt') + 300]
        stockStats['Earnings Date'] = rawEarningsDate[rawEarningsDate.find('<b>') + 3 : rawEarningsDate.find('</b></td>')]

        allStockData[sym] = stockStats

        ## =========================================  Sector Data  ====================================================

        if (len(sectorData)) == 0 or (sector not in sectorData):
            
            sectorData[sector] = {}

            for key, value in sectorData.items():
                for metric in list(stockStats.keys())[5:26]:
                    sectorData[sector][metric] = []
     
        for metric, value in list(stockStats.items())[5:26]:
            sectorData[sector][metric].append(value)
            
            
def getSymbolsCSV(fileName):
    
    global symbols
    print('\nLoading data from ' + fileName)

    with open(fileName) as csvfile:
    
        readCSV = csv.reader(csvfile, delimiter=',')
        
        for row in readCSV:
            
            symbol  = str(row[0]).replace('ï»¿', '')
            
            symbols.append(symbol)  

            
def getStockStats():

    global symbols
    
    for stock in tqdm(symbols):
    
        getStockData(stock, debug=True)
    
    for stock in tqdm(allStockData.keys()):
        
        allStockData[stock]['Valuation Grade'] = getCategoryGrade(allStockData[stock]['Sector'], {key : value for key, value in list(allStockData[stock].items())[5:10]})
        allStockData[stock]['Profitability Grade'] = getCategoryGrade(allStockData[stock]['Sector'], {key : value for key, value in list(allStockData[stock].items())[10:15]})
        allStockData[stock]['Growth Grade'] = getCategoryGrade(allStockData[stock]['Sector'], {key : value for key, value in list(allStockData[stock].items())[15:20]})
        allStockData[stock]['Performance Grade'] = getCategoryGrade(allStockData[stock]['Sector'], {key : value for key, value in list(allStockData[stock].items())[20:26]})
        
        allStockData[stock]['Overall Rating'] = getOverallRating(allStockData[stock]['Valuation Grade'], allStockData[stock]['Profitability Grade'], allStockData[stock]['Growth Grade'], allStockData[stock]['Performance Grade'], allStockData[stock]['Volatility (Month)'])
        
        allStockData[stock]['Valuation Grade'] = convertToLetterGrade(allStockData[stock]['Valuation Grade'])
        allStockData[stock]['Profitability Grade'] = convertToLetterGrade(allStockData[stock]['Profitability Grade'])
        allStockData[stock]['Growth Grade'] = convertToLetterGrade(allStockData[stock]['Growth Grade'])
        allStockData[stock]['Performance Grade'] = convertToLetterGrade(allStockData[stock]['Performance Grade'])

        if allStockData[stock]['Overall Rating'] >= 100:
            allStockData[stock]['Overall Rating'] = 99


def exportData(fileName):

    global allStockData

    header = 'Company Name,Market Cap,Overall Rating,Sector,Industry,Valuation Grade,Profitability Grade,Growth Grade,Performance Grade,Forward PE,PEG,Price/Sales,Price/Book,Price/FCF,Profit Margin,Operating Margin,Gross Margin,ROE,ROA,EPS This Y,EPS Next Y,EPS Next 5Y,Sales Q/Q,EPS Q/Q,Perf Month,Perf Quarter,Perf Half Y,Perf YTD,Perf Year,Volatility (Month),SMA 20,SMA 50,SMA 200,Dividend,Inst Trans,Inst Own,Insider Own,Insider Trans,Target Price,Prev Close,Price Projection,RSI,Short Float,52W High,52W Low,Current Ratio,Earnings Date'

    df = pd.DataFrame(allStockData)
    df = df.T.iloc[: , 1:]
    df.index.name = 'Symbol'
    df = df[header.split(',')]
    df.to_csv(fileName)

    print('\nSaved as ' + fileName)


getSymbolsCSV(symbolsFileName)

getStockStats()

exportData(saveToFileName)

