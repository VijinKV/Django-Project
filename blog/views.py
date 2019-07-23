from django.shortcuts import render
from django.http import HttpResponse
from blog.models import Stocks
from django.shortcuts import redirect
import requests as rqst
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
import time

# Create your views here.
API_key = '2Z86GUWAX98UV2IH'

def getStockPrice(symbol,stockID):

    URL = 'https://www.alphavantage.co/query?'

    PARAMS = {#PARAMS for only Intraday on 1min chart
        'function' : 'BATCH_STOCK_QUOTES',
        'apikey' : API_key,   
        'symbols' : symbol
    }


    res = rqst.get(URL,PARAMS)
    data = res.json()

    #Returns false if the symbol doesnt exits
    if( list(data)[0] == "Error Message"):
        return False
    if(list(data)[0] == "Note"):#Overusage of API request, return true (5 request per minutes allowed by Alpha Vantage)
        print('#####################################################################################################################')
        print(data)#for debugging in cmd/console
        return True
    
    
    stockIter = list(data['Stock Quotes'])
    AllStockDetail = []

    for stockData,ID in zip(stockIter,stockID):
        stockDetails = {}

        #dict values to be filled in home page
        stockDetails['id'] = ID
        stockDetails['symbol'] = stockData['1. symbol']
        stockDetails['price'] = stockData['2. price']
        stockDetails['timeStamp'] = stockData['4. timestamp']

        AllStockDetail.append(stockDetails)

    return AllStockDetail

def getStockDetails(timeseries,symbol,stockID):

    URL = 'https://www.alphavantage.co/query?'

    if timeseries == 'TIME_SERIES_INTRADAY':
        PARAMS = {#PARAMS for only Intraday on 1min chart
            'function' : timeseries,
            'symbol' : symbol,
            'interval' : '1min',
            'apikey' : API_key     
        }
    else:
        PARAMS = {#PARAMS other timeseries
            'function' : timeseries,
            'symbol' : symbol,
            'apikey' : API_key        
        }

    #requesting stock json data
    res = rqst.get(URL,PARAMS)
    data = res.json()
    #Returns false if the symbol doesnt exits
    if( list(data)[0] == "Error Message"):
        return False
    if(list(data)[0] == "Note"):#Overusage of API request, return true (5 request per minutes allowed by Alpha Vantage)
        print('#########################################################')
        print(data)#for debugging in cmd/console
        return True
        

    timeSeriesName = list(data)[1]#Key value for accessing json data
    latestTime = list(data[timeSeriesName])[0]#Date keyvalue for latest date/time

    stockDetails = {}

    #dict values to be filled in home page
    stockDetails['symbol'] = data['Meta Data']['2. Symbol']
    stockDetails['id'] = stockID
    stockDetails['timeseries'] = timeSeriesName

    openCloseData = []

    openCloseArray = list(data[timeSeriesName])
    for openClose in openCloseArray:
        openCloseDict = {}
        openCloseDict['open'] = data[timeSeriesName][openClose]['1. open']
        openCloseDict['high'] = data[timeSeriesName][openClose]['2. high']
        openCloseDict['low'] = data[timeSeriesName][openClose]['3. low']
        openCloseDict['close'] = data[timeSeriesName][openClose]['4. close']
        openCloseDict['volume'] = data[timeSeriesName][openClose]['5. volume']
        openCloseDict['date'] =     openClose
        openCloseData.append(openCloseDict)
    
    stockDetails['openClose']=openCloseData
    return stockDetails

@login_required
def deleteStock(request):
    if request.method == "POST":
        request.POST['id']
        Stocks.objects.filter(id=request.POST['id']).delete()
        return redirect('/')

@login_required
def addStock(request):
    if request.method == "POST":
        passedTimeSeries = 'TIME_SERIES_INTRADAY'
        passedSymbol = request.POST['symbol']
        passedSymbol = passedSymbol.upper()
        isValidSymbol = getStockDetails(passedTimeSeries,passedSymbol,"")

        #Apla vanatge allow 5 request per minunte.. Hence waiting for a minute
        while isValidSymbol==True:
            time.sleep(15)
            isValidSymbol = getStockDetails(passedTimeSeries,passedSymbol,"")
        if isValidSymbol:
            try :
                addStock = Stocks(symbol = passedSymbol, user = request.user)
                addStock.save()
                return redirect('/')

            except IntegrityError as e: 
                messages.error(request,'Already Exist!')
        else :
            messages.error(request,'Invalid Symbol')
            return redirect('/stock_add_menu')
    return redirect('/')

def validResStocks(stockSymbol,stockID):
    #getStockDetail func will return a dictionary value with open, high, low, close and volume etc. 
    #if the function is over used the function will return true
    isOverRequested = getStockPrice(stockSymbol,stockID)

    #Apla vanatge allow 5 request per minunte.. Hence waiting for a minute
    while isOverRequested == True:
        time.sleep(15)
        isOverRequested = getStockPrice(stockSymbol,stockID)

    return isOverRequested

def validResDetail(timeseries,stockSymbol,stockID):
    #getStockDetail func will return a dictionary value with open, high, low, close and volume etc. 
    #if the function is over used the function will return true
    isOverRequested = getStockDetails(timeseries,stockSymbol,stockID)
    
    #Apla vanatge allow 5 request per minunte.. Hence waiting for a minute
    while isOverRequested == True:
        time.sleep(15)
        isOverRequested = getStockDetails(timeseries,stockSymbol,stockID)
    
    return isOverRequested

@login_required
def stockDetailPage(request):
    template = 'blog/stockDetail.html'

    stockID = request.POST['id']
    stockSymbol = request.POST['symbol']
    timeseries = request.POST['timeseries']
    
    stockDetails = validResDetail(timeseries,stockSymbol,stockID)

    return render(request, template, stockDetails)

@login_required
def wishListPage(request):

    template = 'blog/wishlist.html'
    allStocks = request.user.stocks_set.all()

    stockSymbol = ''
    stockID = []

    for stock in allStocks :        
        stockSymbol += stock.symbol + ',' 
        stockID.append(stock.id)

    
    stockDetails = validResStocks(stockSymbol,stockID)

    wishlistDict = {
        'wishlists' : stockDetails
    }
    
    return render(request, template, wishlistDict)

def aboutPage(request):
    template = 'blog/about.html'
    return render(request, template, {'title' : 'About us'})

@login_required
def addStockPage(request):
    template = 'blog/addStock.html'
    return render(request, template, {'title' : 'Add Stock Symbol'})