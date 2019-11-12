import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import sys
import tweepy
import time
import os

symbols = []
stockCounter = 0
c = 0

def fixString(stng):
    
    output = ''
    output2 = ''
    
    if '&amp;' in stng:
        output += stng[0 : stng.find('&') + 1]
        output += stng[stng.find(';') + 1 : ]
    else:
        output = stng
    
    for letter in output:
        if letter != ',':
            output2 += letter

    return output2
    

def getSymbols(inURL):
    
    global symbols
    global stockCounter
    global c
    global stocksToAnalyze
    global searchThrough

    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    symbs = soup.find_all('a', {'class' : 'screener-link-primary'})

    for x in range(len(symbs)):
        if '&amp;b=1' in str(symbs[x]):
            symbols.append(str(symbs[x])[str(symbs[x]).find('&amp;b=1') + 10 : str(symbs[x]).find('/a') - 1])
            stockCounter = stockCounter + 1

        if stockCounter % 20 == 0:
            c = c + 20
            getSymbols(searchThrough + '&r=' + str(c))
        
        if stockCounter >= stocksToAnalyze:
            break


def convertNum(stng):
    s = ''

    if len(stng) > 20:
        return 0

    for x in range(len(stng)):
        if x != len(stng) - 1 and stng[x] == '-' and stng[x + 1] != '-':
            s += stng[x]
        
        elif stng[x] == '.':
            s += stng[x]

        elif x != len(stng) - 1 and stng[x] != ',' and stng[x] != "'" and stng[x] != '"' and (not stng[x].isalpha()) and stng[x] != ':' and stng[x].isdigit() and stng[x + 1] != '"':
            s += stng[x]

    if len(s) > 0 and len(s) < 10:
        try:
            return float(s)
        except:
            return 0

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
    

def getGrade(mtrc, val):

    start = 0
    change = 0
    lessThan = False
    grade = 'F'

    if mtrc == 'forwardPE':
        start = 10
        change = 5
        lessThan = True

        if val == 0:
            return 'D'

    if mtrc == 'peg':
        start = 1
        change = 0.15
        lessThan = True

        if val == 0:
            return 'D'
    
    if mtrc == 'priceSales':
        start = 4
        change = 1
        lessThan = True

        if val == 0:
            return 'D'

    if mtrc == 'priceBook':
        start = 3
        change = 1
        lessThan = True

        if val == 0:
            return 'D'

    if mtrc == 'priceFCF':
        start = 15
        change = 5
        lessThan = True

        if val == 0: 
            return 'D'

    if mtrc == 'profitMargin':
        start = 30
        change = 4

        if val == 0:
            return 'C'

    if mtrc == 'operMargin':
        start = 35
        change = 4

        if val == 0:
            return 'C'

    if mtrc == 'grossMargin':
        start = 40
        change = 4

        if val == 0:
            return 'B'

    if mtrc == 'roe':
        start = 30
        change = 5

        if val == 0:
            return 'D'

    if mtrc == 'roa':
        start = 15
        change = 3.5

        if val == 0:
            return 'D'

    if mtrc == 'epsThisY':
        start = 30
        change = 4

        if val == 0:
            return 'F'

    if mtrc == 'epsNextY':
        start = 30
        change = 4

        if val == 0:
            return 'F'

    if mtrc == 'epsNext5Y':
        start = 20
        change = 3.5

        if val == 0:
            return 'C'

    if mtrc == 'salesQQ':
        start = 25 
        change = 4

        if val == 0:
            return 'D'

    if mtrc == 'epsQQ':
        start = 25
        change = 3.5

        if val == 0:
            return 'D'

    if mtrc == 'perfMonth':
        start = 10
        change = 3

        if val == 0:
            return 'C'

    if mtrc == 'perfQuarter':
        start = 15
        change = 3

        if val == 0:
            return 'C'

    if mtrc == 'perfHalfY':
        start = 25
        change = 3.5

        if val == 0:
            return 'D'

    if mtrc == 'perfYear':
        start = 30
        change = 4

        if val == 0:
            return 'F'

    if mtrc == 'perfYTD':
        start = 25
        change = 3.5

        if val == 0:
            return 'F'

    if mtrc == 'volatility':
        start = 1.30
        change = 0.15
        lessThan = True

        if val > 2.1:
            return 'F-'


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


    return grade


def getCategoryGrade(arr):
    score = 0
    grade = "F"
    output = []

    for x in range(len(arr)):
        output.append(getGrade(arr[x][0], arr[x][1]))

    for grade in output:

        if grade == 'A+':
            score += 4.3
        if grade == 'A':
            score += 4
        if grade == 'A-':
            score += 3.7
        if grade == 'B+':
            score += 3.3
        if grade == 'B':
            score += 3
        if grade == 'B-':
            score += 2.7
        if grade == 'C+':
            score += 2.3
        if grade == 'C':
            score += 2 
        if grade == 'C-':
            score += 1.7
        if grade == 'D+':
            score += 1.3
        if grade == 'D':
            score += 1
        if grade == 'D-':
            score += 0.7
        if grade == 'F-':
            score -= 1.5

    #print(output)
    return score / len(arr)


def bubbleSort(subList): 
    
    l = len(subList) 

    for i in range(0, l): 
        
        for j in range(0, l-i-1): 
            
            if (subList[j][1] < subList[j + 1][1]): 
                tempo = subList[j] 
                subList[j]= subList[j + 1] 
                subList[j + 1] = tempo 

    return subList 


def getOverallRating(valGrade, profGrade, grGrade, pfGrade, vol):

    if vol > 2.1:
        return ((valGrade * 1.05) + profGrade + grGrade + pfGrade) * 6.25
    
    return ((valGrade * 1.20) + profGrade + grGrade + pfGrade) * 6.25 * 1.05 


def getRating(sym, val, prof, growth, perf):

    score = 0
    overallStats = []
    overallStats.append(getCategoryGrade(val))
    overallStats.append(getCategoryGrade(prof))
    overallStats.append(getCategoryGrade(growth))
    overallStats.append(getCategoryGrade(perf))

    '''
    print('Valuation:', getValuationGrade(val))
    print('Profitability:', getProfitabilityGrade(prof))
    print('Growth:', getGrowthGrade(growth))
    print('Performance:', getPerfGrade(perf))
    '''

    for grade in overallStats:
        
        if grade == 'A+':
            score += 4.3
        if grade == 'A':
            score += 4
        if grade == 'A-':
            score += 3.7
        if grade == 'B+':
            score += 3.3
        if grade == 'B':
            score += 3
        if grade == 'B-':
            score += 2.7
        if grade == 'C+':
            score += 2.3
        if grade == 'C':
            score += 2 
        if grade == 'C-':
            score += 1.7
        if grade == 'D+':
            score += 1.3
        if grade == 'D':
            score += 1
        if grade == 'D-':
            score += 0.7

    score = ((score * 25) / 4) + 6
    
    #print(score)
    #print()
    return score


overall = []
outputPrint = []

def getInfo(sym):

    global overall

    page = requests.get('https://finviz.com/quote.ashx?t=' + sym)
    soup2 = BeautifulSoup(page.text, 'html.parser')
    soup = str(BeautifulSoup(page.text, 'html.parser'))

    valuationStats = []
    profitabilityStats = []
    growthStats = []
    perfStats = []

    #print(soup)
    #print()
    #print()

    rawMarketCap = soup[soup.find('Market capitalization') : soup.find('Market capitalization') + 200]
    marketCap = rawMarketCap[rawMarketCap.find('<b>') + 3 : rawMarketCap.find('</b>')]

    rawCompanyName = soup[soup.find('id="ticker">') + 100 : soup.find('id="ticker">') + 500]
    companyName = rawCompanyName[rawCompanyName.find('<b>') + 3 : rawCompanyName.find('</b>')]

    rawSector = rawCompanyName[rawCompanyName.find('f=sec') : rawCompanyName.find('f=sec') + 50]
    sector = rawSector[rawSector.find('>') + 1 : rawSector.find('</a>')]

    rawIndustry = rawCompanyName[rawCompanyName.find('f=ind') : rawCompanyName.find('f=ind') + 100]
    industry = rawIndustry[rawIndustry.find('>') + 1 : rawIndustry.find('</a>')]

    ##Valuation

    rawforwardPE = soup[soup.find('Forward P/E') : soup.find('Forward P/E') + 150]
    forwardPE = convertNum(rawforwardPE[rawforwardPE.find('<b>') + 3 : rawforwardPE.find('</b>') + 1])

    if forwardPE == 0:
        forwardPE = convertNum(rawforwardPE[rawforwardPE.find(';') + 3 : rawforwardPE.find('</span>') + 1])

    rawPEG = soup[soup.find('PEG') : soup.find('PEG') + 150]
    peg = convertNum(rawPEG[rawPEG.find('<b>') + 3 : rawPEG.find('</b>') + 1])

    if peg == 0:
        peg = convertNum(rawPEG[rawPEG.find(';') + 3 : rawPEG.find('</span>') + 1])

    rawPriceSales = soup[soup.find('P/S') : soup.find('P/S') + 150]
    priceSales = convertNum(rawPriceSales[rawPriceSales.find('<b>') + 3 : rawPriceSales.find('</b>') + 1])

    if priceSales == 0:
        priceSales = convertNum(rawPriceSales[rawPriceSales.find(';') + 3 : rawPriceSales.find('</span>') + 1])

    rawPriceBook = soup[soup.find('P/B') : soup.find('P/B') + 150]
    priceBook = convertNum(rawPriceBook[rawPriceBook.find(';') + 3 : rawPriceBook.find('</span>') + 1])

    if priceBook == 0:
        priceBook = convertNum(rawPriceBook[rawPriceBook.find('<b>') + 3 : rawPriceBook.find('</b>') + 1])

    rawPriceFCF = soup[soup.find('P/FCF') : soup.find('P/FCF') + 150]
    priceFCF = convertNum(rawPriceFCF[rawPriceFCF.find('<b>') + 3 : rawPriceFCF.find('</b>') + 1])

    if priceFCF == 0:
        priceFCF = convertNum(rawPriceFCF[rawPriceFCF.find(';') + 3 : rawPriceFCF.find('</span>') + 1])

    print(sym)
    valuationStats.append(['forwardPE', forwardPE])
    valuationStats.append(['peg', peg])
    valuationStats.append(['priceSales', priceSales])
    valuationStats.append(['priceBook', priceBook])
    valuationStats.append(['priceFCF', priceFCF])
    valuationGrade = getCategoryGrade(valuationStats)
    
    print('Valuation Grade:', valuationGrade, convertToLetterGrade(valuationGrade))


    ##Profitability

    rawProfitMargin = soup[soup.find('Profit Margin') : soup.find('Profit Margin') + 250]
    profitMargin = convertNum(rawProfitMargin[rawProfitMargin.find(';') + 3 : rawProfitMargin.find('</span>') + 1])
   
    if profitMargin == 0:
        profitMargin = convertNum(rawProfitMargin[rawProfitMargin.find('<b>') + 3 : rawProfitMargin.find('</b>') + 1])

    rawOperMargin = soup[soup.find('Operating Margin') : soup.find('Operating Margin') + 250]
    operMargin = convertNum(rawOperMargin[rawOperMargin.find(';') + 3 : rawOperMargin.find('</span>') + 1])
   
    if operMargin == 0:
        operMargin = convertNum(rawOperMargin[rawOperMargin.find('<b>') + 3 : rawOperMargin.find('</b>') + 1])

    rawGrossMargin = soup[soup.find('Gross Margin') : soup.find('Gross Margin') + 250]
    grossMargin = convertNum(rawGrossMargin[rawGrossMargin.find('<b>') + 3 : rawGrossMargin.find('</b>') + 1])

    if grossMargin == 0:
        grossMargin = convertNum(rawGrossMargin[rawGrossMargin.find(';') + 3 : rawGrossMargin.find('</span>') + 1])

    rawROE = soup[soup.find('ROE') : soup.find('ROE') + 250]
    roe = convertNum(rawROE[rawROE.find(';') + 3 : rawROE.find('</span>') + 1])

    if roe == 0:
        roe = convertNum(rawROE[rawROE.find('<b>') + 3 : rawROE.find('</b>') + 1])

    rawROA = soup[soup.find('ROA') : soup.find('ROA') + 250]
    roa = convertNum(rawROA[rawROA.find(';') + 3 : rawROA.find('</span>') + 1])
    
    if roa == 0:
        roa = convertNum(rawROA[rawROA.find('<b>') + 3 : rawROA.find('</b>') + 1])
    
    profitabilityStats.append(['profitMargin', profitMargin])
    profitabilityStats.append(['operMargin', operMargin])
    profitabilityStats.append(['grossMargin', grossMargin])
    profitabilityStats.append(['roe', roe])
    profitabilityStats.append(['roa', roa])
    
    profitabilityGrade = getCategoryGrade(profitabilityStats)
    print('Profitability Grade:', profitabilityGrade, convertToLetterGrade(profitabilityGrade))


    ##Growth

    rawEPSThisY = soup[soup.find('EPS this Y') : soup.find('EPS this Y') + 250]
    epsThisY = convertNum(rawEPSThisY[rawEPSThisY.find(';') + 3 : rawEPSThisY.find('</span>') + 1])

    if epsThisY == 0:
        epsThisY = convertNum(rawEPSThisY[rawEPSThisY.find('<b>') + 3 : rawEPSThisY.find('</b>') + 1])

    rawEPSNextY = soup[soup.find('EPS growth next year') : soup.find('EPS growth next year') + 250]
    epsNextY = convertNum(rawEPSNextY[rawEPSNextY.find('<b>') + 3 : rawEPSNextY.find('</b>') + 1])

    if epsNextY == 0:
        epsNextY = convertNum(rawEPSNextY[rawEPSNextY.find(';') + 3 : rawEPSNextY.find('</span>') + 1])

    rawEPSNext5Y = soup[soup.find('EPS next 5Y') : soup.find('EPS next 5Y') + 250]
    epsNext5Y = convertNum(rawEPSNext5Y[rawEPSNext5Y.find('<b>') + 3 : rawEPSNext5Y.find('</b>') + 1])

    if epsNext5Y == 0:
        epsNext5Y = convertNum(rawEPSNext5Y[rawEPSNext5Y.find(';') + 3 : rawEPSNext5Y.find('</span>') + 1])

    rawSalesQQ = soup[soup.find('Sales Q/Q') : soup.find('Sales Q/Q') + 250]
    salesQQ = convertNum(rawSalesQQ[rawSalesQQ.find(';') + 3 : rawSalesQQ.find('</span>') + 1])

    if salesQQ == 0:
        salesQQ = convertNum(rawSalesQQ[rawSalesQQ.find('<b>') + 3 : rawSalesQQ.find('</b>') + 1])

    rawEPSQQ = soup[soup.find('EPS Q/Q') : soup.find('EPS Q/Q') + 250]
    epsQQ = convertNum(rawEPSQQ[rawEPSQQ.find(';') + 3 : rawEPSQQ.find('</span>') + 1])

    if epsQQ == 0:
        epsQQ = convertNum(rawEPSQQ[rawEPSQQ.find('<b>') + 3 : rawEPSQQ.find('</b>') + 1])

    growthStats.append(['epsThisY', epsThisY])
    growthStats.append(['epsNextY', epsNextY])
    growthStats.append(['epsNext5Y', epsNext5Y])
    growthStats.append(['salesQQ', salesQQ])
    growthStats.append(['epsQQ', epsQQ])
    
    growthGrade = getCategoryGrade(growthStats)
    print('Growth Grade:', growthGrade, convertToLetterGrade(growthGrade))


    ##Performance

    rawPerfMonth = soup[soup.find('Perf Month') : soup.find('Perf Month') + 250]
    perfMonth = convertNum(rawPerfMonth[rawPerfMonth.find(';') + 3 : rawPerfMonth.find('</span>') + 1])

    if perfMonth == 0:
        perfMonth = convertNum(rawPerfMonth[rawPerfMonth.find('<b>') + 3 : rawPerfMonth.find('</b>') + 1])

    rawPerfQuarter = soup[soup.find('Perf Quarter') : soup.find('Perf Quarter') + 250]
    perfQuarter = convertNum(rawPerfQuarter[rawPerfQuarter.find(';') + 3 : rawPerfQuarter.find('</span>') + 1])

    if perfQuarter == 0:
        perfQuarter = convertNum(rawPerfQuarter[rawPerfQuarter.find('<b>') + 3 : rawPerfQuarter.find('</b>') + 1])

    rawPerfHalfY = soup[soup.find('Perf Half Y') : soup.find('Perf Half Y') + 250]
    perfHalfY = convertNum(rawPerfHalfY[rawPerfHalfY.find(';') + 3 : rawPerfHalfY.find('</span>') + 1])

    if perfHalfY == 0:
        perfHalfY = convertNum(rawPerfHalfY[rawPerfHalfY.find('<b>') + 3 : rawPerfHalfY.find('</b>') + 1])

    rawPerfYear = soup[soup.find('Perf Year') : soup.find('Perf Year') + 250]
    perfYear = convertNum(rawPerfYear[rawPerfYear.find(';') + 3 : rawPerfYear.find('</span>') + 1])

    if perfYear == 0:
        perfYear = convertNum(rawPerfYear[rawPerfYear.find('<b>') + 3 : rawPerfYear.find('</b>') + 1])

    rawPerfYTD = soup[soup.find('Perf YTD') : soup.find('Perf YTD') + 250]
    perfYTD = convertNum(rawPerfYTD[rawPerfYTD.find(';') + 3 : rawPerfYTD.find('</span>') + 1])

    if perfYTD == 0:
        perfYTD = convertNum(rawPerfYTD[rawPerfYTD.find('<b>') + 3 : rawPerfYTD.find('</b>') + 1])

    rawVolatility = soup[soup.find('Volatility') : soup.find('Volatility') + 250]
    rawVol = rawVolatility[rawVolatility.find('<small>') + 7 : rawVolatility.find('</small>') + 1]
    volatility = convertNum(rawVol[rawVol.find(' ') + 1 : len(rawVol)])

    if volatility == 0:
        volatility = convertNum(rawVolatility[rawVolatility.find('<b>') + 3 : rawVolatility.find('</b>') + 1])
    
    perfStats.append(['perfMonth', perfMonth])
    perfStats.append(['perfQuarter', perfQuarter])
    perfStats.append(['perfHalfY', perfHalfY])
    perfStats.append(['perfYear', perfYear])
    perfStats.append(['perfYTD', perfYTD])
    perfStats.append(['volatility', volatility])
    
    perfGrade = getCategoryGrade(perfStats)
    print('Performance Grade:', perfGrade, convertToLetterGrade(perfGrade))
    #print(getGrade('volatility', volatility), volatility)
    
    #overallRating = ((valuationGrade * 1.10) + profitabilityGrade + growthGrade + perfGrade) * 6.25 * 1.10 
    overallRating = getOverallRating(valuationGrade, profitabilityGrade, growthGrade, perfGrade, volatility)

    print('Overall Rating:', overallRating)
    print()
    
    if overallRating >= 100:
        overallRating = 99

    overall.append([sym, round(overallRating), fixString(companyName), marketCap, fixString(sector), fixString(industry), convertToLetterGrade(getCategoryGrade(valuationStats)), convertToLetterGrade(getCategoryGrade(profitabilityStats)), convertToLetterGrade(getCategoryGrade(growthStats)), convertToLetterGrade(getCategoryGrade(perfStats))])

    '''
    print('\nforwardPE', forwardPE)
    print('\npeg', peg)
    print('\npriceSales', priceSales)
    print('\npriceBook', priceBook)
    print('\npriceFCF', priceFCF)
    print('\nprofitMargin', profitMargin)
    print('\noperMargin', operMargin)
    print('\ngrossMargin', grossMargin)
    print('\nroe', roe)
    print('\nroa', roa)
    print('\nepsThisY', epsThisY)
    print('\nepsNextY', epsNextY)
    print('\nepsNext5Y', epsNext5Y)
    print('\nsalesQ/Q', salesQQ)
    print('\nepsQ/Q', epsQQ)
    print('\nperfMonth', perfMonth)
    print('\nperfQuarter', perfQuarter)
    print('\nperfHalfY', perfHalfY)
    print('\nperfYear', perfYear)
    print('\nperfYTD', perfYTD)
    '''

    '''
    print(sym)
    print('fPE    ', getGrade('forwardPE', forwardPE), forwardPE)
    print('peg    ', getGrade('peg', peg), peg)
    print('pS     ', getGrade('priceSales', priceSales), priceSales)
    print('pb     ', getGrade('priceBook', priceBook), priceBook)
    print('FCF    ', getGrade('priceFCF', priceFCF), priceFCF)
    print('pfM    ', getGrade('profitMargin', profitMargin), profitMargin)
    print('opM    ', getGrade('operMargin', operMargin), operMargin)
    print('grM    ', getGrade('grossMargin', grossMargin), grossMargin)
    print('roe    ', getGrade('roe', roe), roe)
    print('roa    ', getGrade('roa', roa), roa)
    print('eTY    ', getGrade('epsThisY', epsThisY), epsThisY)
    print('eNY    ', getGrade('epsNextY', epsNextY), epsNextY)
    print('eN5    ', getGrade('epsNext5Y', epsNext5Y), epsNext5Y)
    print('sQQ    ', getGrade('salesQQ', salesQQ), salesQQ)
    print('eQQ    ', getGrade('epsQQ', epsQQ), epsQQ)
    print('pMo    ', getGrade('perfMonth', perfMonth), perfMonth)
    print('pQr    ', getGrade('perfQuarter', perfQuarter), perfQuarter)
    print('pHY    ', getGrade('perfHalfY', perfHalfY), perfHalfY)
    print('pYr    ', getGrade('perfYear', perfYear), perfYear)
    print('pYD    ', getGrade('perfYTD', perfYTD), perfYTD)
    print()
    '''



sAndP = 'https://finviz.com/screener.ashx?v=111&f=idx_sp500'
midCap = 'https://finviz.com/screener.ashx?v=111&f=cap_mid'

basicMaterials = 'https://finviz.com/screener.ashx?v=111&f=sec_basicmaterials'
conglomerates = 'https://finviz.com/screener.ashx?v=111&f=sec_conglomerates'
comsumerGoods = 'https://finviz.com/screener.ashx?v=111&f=sec_consumergoods'
financials = 'https://finviz.com/screener.ashx?v=111&f=sec_financial'
healthcare = 'https://finviz.com/screener.ashx?v=111&f=sec_healthcare'
industrialGoods = 'https://finviz.com/screener.ashx?v=111&f=sec_industrialgoods'
services = 'https://finviz.com/screener.ashx?v=111&f=sec_services'
tech = 'https://finviz.com/screener.ashx?v=111&f=sec_technology'
utilities = 'https://finviz.com/screener.ashx?v=111&f=sec_utilities'

searchThrough = sAndP
stocksToAnalyze = 600


getSymbols(searchThrough)


for stock in symbols:
    getInfo(stock)

bubbleSort(overall)
bubbleSort(outputPrint)

print('****************************Stocks:')
print('\n\n')

for x in range(len(overall)):
    print(overall[x][0], overall[x][1])
    print('Valuation Grade:', overall[x][6])
    print('Profitability Grade:', overall[x][7])
    print('Growth Grade:', overall[x][8])
    print('Performance Grade:', overall[x][9])
    print()
    

