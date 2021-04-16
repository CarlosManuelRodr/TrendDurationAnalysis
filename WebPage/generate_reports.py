import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import more_itertools as mit
import datetime
import os
from scipy import interpolate
from math import pow
from tqdm import tqdm

# Dataset getters
def GetPrices(tickerPath):
    data = pandas.read_csv(tickerPath)
    return np.array(data["close"])

def GetDates(tickerPath):
    data = pandas.read_csv(tickerPath)
    return np.array(data["date"])

# Statistic model
def TrendDuration(prices):
    returns = np.diff(prices)
    trendSigns = np.sign(returns).tolist()
    fixedTrendSigns = [x for x in trendSigns if x != 0.0]
    trendStartPoints = np.insert(np.where(np.diff(fixedTrendSigns))[0], 0, -1)
    trendDuration = np.diff(trendStartPoints)
    fixForGeometricModel = trendDuration - 1
    return fixForGeometricModel.tolist()

def ModelP(j):
    modelP = 0.5
    for i in range(j):
        modelP /= 2.0
    return modelP

def PEstimator(trendDurations, j):
    return trendDurations.count(j)/len(testData)

def Z(trendDurations, j):
    n = len(trendDurations)
    sjSum = 0.0
    tjSum = 0.0
    
    for i in range(j+1):
        sjSum += trendDurations.count(i)
        tjSum += n*ModelP(i)
    
        
    return sjSum - tjSum

def GeometricCramerVonMisesTest(trendDurations):
    testScore = 0.0
    n = len(trendDurations)
    m = max(trendDurations)
    for j in range(m+1):
        testScore += pow(Z(trendDurations, j), 2) * ModelP(j)
        
    return testScore / n

pValData = pandas.read_csv("testScoreToPValuePts.csv")
[testValue, pValue] = np.transpose(np.array(pValData)).tolist()
minTestValue = min(testValue)
maxTestValue = max(testValue)
pValueFunction = interpolate.interp1d(testValue, pValue)

def GeometricCramerVonMisesPValue(trendDurations):
    testStatistic = GeometricCramerVonMisesTest(trendDurations)
    if minTestValue <= testStatistic <= maxTestValue:
        return float(pValueFunction(testStatistic))
    else:
        return 0.0

# Time-series partition
def IsNotNone(dataPoint):
    return not dataPoint is None

def Partition(listToPartition, partSize, step):
    partitions = list(mit.windowed(listToPartition, n = partSize, step = step))
    partitions = [np.array(list(filter(IsNotNone, p))) for p in partitions]
    return partitions

# Analysis
def TestPartition(part):
    date = part[:,0][-1]
    prices = part[:,1].astype(float)
    pVal = GeometricCramerVonMisesPValue(TrendDuration(prices))
    return [date, pVal]

def TestModelInTime(datedPrices, partSize, step):
    partitions = Partition(datedPrices, partSize, step)
    testResults = [TestPartition(part) for part in partitions]
    return testResults

def TestModelLatestAtWindow(closePrices, window):
    lastChunk = closePrices[-window:-1]
    pValue = GeometricCramerVonMisesPValue(TrendDuration(lastChunk))
    testResult = "Eficiente" if pValue >= 0.05 else "No Eficiente"
    return [window, pValue, testResult]

def TestModelLatest(closePrices):
    latestTestResults = [TestModelLatestAtWindow(closePrices, w) for w in range(20, 110, 10)]
    return pandas.DataFrame(latestTestResults, columns=["Cantidad de días", "P-Valor", "Interpretación"])#.style.hide_index()

def PlotTestModelInTimeResults(testResults, stockName, saveOutputPath = None):
    [dates, pValues] = np.transpose(testResults)
    xPlotValues = [datetime.datetime.strptime(d,"%Y-%m-%d").date() for d in dates]
    yPlotValues = pValues.astype(float).tolist()
    
    ax = plt.gca()
    formatter = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.hlines([0.1, 0.05, 0.01], 
              xmin=mdates.date2num(xPlotValues[0]), 
              xmax=mdates.date2num(xPlotValues[-1]), 
              colors=['y','r','g'], 
              linestyle='--')


    yellow_patch = mlines.Line2D([], [], color='yellow', label='CL: 0.1', linestyle='--')
    red_patch = mlines.Line2D([], [], color='red', label='CL: 0.05', linestyle='--')
    green_patch = mlines.Line2D([], [], color='green', label='CL: 0.01', linestyle='--')
    plt.legend(handles=[yellow_patch, red_patch, green_patch])

    plt.rcParams['figure.figsize'] = [10, 5]
    plt.yscale("log")
    plt.title(stockName)
    plt.xlabel("Date")
    plt.ylabel("p-value")
    plt.plot(xPlotValues, yPlotValues)
    
    if saveOutputPath is not None:
        fig = plt.gcf()
        fig.set_size_inches(10, 5)
        fig.savefig(saveOutputPath, dpi=100)

    plt.clf()

# Generate report
def GenerateReport(ticker):
    dates = GetDates("static/sp500" + ticker + ".csv")
    closePrices = GetPrices("static/sp500" + ticker + ".csv")
    datedPrices = np.transpose([dates,closePrices]).tolist()
    TestModelLatest(closePrices).to_csv("static/modelresults" + ticker + "_Report.csv", index=False)
    PlotTestModelInTimeResults(TestModelInTime(datedPrices, 100, 1), ticker, "static/modelresults" + ticker + "_Plot.png")


tickers = ["AAL","AAP","AAPL","ABBV","ABC","ABMD","ABT","ACN","A","ADBE","ADI","ADM",
           "ADP","ADSK","AEE","AEP","AES","AFL","AIG","AIV","AIZ","AJG","AKAM","ALB",
           "ALGN","ALK","ALL","ALLE","ALXN","AMAT","AMD","AME","AMGN","AMP","AMT","AMZN",
           "ANET","ANSS","ANTM","AON","AOS","APA","APD","APH","APTV","ARE","ATO","ATVI",
           "AVB","AVGO","AVY","AWK","AXP","AZO","BAC","BA","BAX","BBY","BDX","BEN","BF-B",
           "BIIB","BIO","BK","BKNG","BKR","BLK","BLL","BMY","BR","BRK-B","BSX","BWA",
           "BXP","CAG","CAH","CAT","CB","CBOE","CBRE","CCI","CCL","C","CDNS","CDW","CE",
           "CERN","CF","CFG","CHD","CHRW","CHTR","CI","CINF","CL","CLX","CMA","CMCSA",
           "CME","CMG","CMI","CMS","CNC","CNP","COF","COG","COO","COP","COST","CPB","CPRT",
           "CRM","CSCO","CSX","CTAS","CTLT","CTSH","CTVA","CTXS","CVS","CVX","DAL","D",
           "DD","DE","DFS","DG","DGX","DHI","DHR","DISCA","DISCK","DIS","DISH","DLR","DLTR",
           "DOV","DOW","DPZ","DRE","DRI","DTE","DUK","DVA","DVN","DXC","DXCM","EA","EBAY",
           "ECL","ED","EFX","EIX","EL","EMN","EMR","EOG","EQIX","EQR","ES","ESS","ETN","ETR",
           "ETSY","EVRG","EW","EXC","EXPD","EXPE","EXR","FANG","FAST","FB","FBHS","F","FCX",
           "FDX","FE","FFIV","FIS","FISV","FITB","FLIR","FLS","FLT","FMC","FOXA","FRC",
           "FRT","FTI","FTNT","FTV","GD","GE","GILD","GIS","GL","GLW","GM","GOOG","GOOGL",
           "GPC","GPN","GPS","GRMN","GS","GWW","HAL","HAS","HBAN","HBI","HCA","HD","HES",
           "HFC","HIG","HII","HLT","HOLX","HON","HPE","HPQ","HRL","HSIC","HST","HSY","HUM",
           "HWM","IBM","ICE","IDXX","IEX","IFF","ILMN","INCY","INFO","INTC","INTU","IP","IPG",
           "IPGP","IQV","IR","ITW","IVZ","JBHT","JCI","J","JKHY","JNJ","JNPR","JPM","K","KEY",
           "KEYS","KHC","KIM","KLAC","KMB","KMI","KMX","KO","KR","KSU","LB","L","LDOS","LEG",
           "LEN","LH","LHX","LIN","LKQ","LLY","LMT","LNC","LNT","LOW","LRCX","LUMN","LUV",
           "LVS","LW","LYB","LYV","MAA","MA","MAR","MAS","MCD","MCHP","MCK","MCO","MDLZ",
           "MDT","MET","MGM","MHK","MKC","MKTX","MLM","MMC","MMM","MNST","MO","MOS","MPC",
           "MRK","MRO","MSCI","MS","MSFT","MSI","MTB","MTD","MU","MXIM","NCLH","NDAQ","NEE",
           "NEM","NFLX","NI","NOV","NOW","NRG","NSC","NTAP","NTRS","NUE","NVDA","NVR","NWL",
           "NWSA","NWS","O","ODFL","OKE","OMC","ORCL","ORLY","OTIS","OXY","PAYC","PAYX","PBCT",
           "PCAR","PEAK","PEG","PEP","PG","PGR","PH","PHM","PKG","PKI","PLD","PM","PNC","PNR",
           "PNW","POOL","PPG","PPL","PRGO","PRU","PSA","PSX","PVH","PWR","PXD","PYPL","QCOM",
           "QRVO","RCL","RE","REG","REGN","RF","RHI","RJF","RL","RMD","ROK","ROL","ROP","ROST",
           "RSG","RTX","SBAC","SBUX","SCHW","SEE","SHW","SIVB","SJM","SLB","SLG","SNA","SNPS",
           "SO","SPG","SPGI","SRE","STE","STT","STX","STZ","SWK","SWKS","SYF","SYK","SYY","TAP",
           "T","TDG","TDY","TEL","TER","TFC","TFX","TGT", "TJX","TMO","TMUS","TPR","TROW",
           "TRV","TSCO","TSN","TT","TTWO","TWTR","TXN","TXT","TYL","VAR","VFC","VIAC","VLO","VMC",
           "VNO","VRSK","VRSN","VRTX","VTR","VTRS","VZ","WAB","WAT","WBA","WDC","WEC","WELL",
           "WFC","WHR","WLTW","WMB","WM","WMT","WRB","WST","WU","WY","WYNN","XEL","XLNX",
           "XOM","XRAY","XRX","XYL","YUM","ZBH","ZBRA","ZION","ZTS"]

print("Starting to generate reports...")

pbar = tqdm(total=len(tickers))
def PBarGenerateReport(ticker):
    pbar.update(1)
    GenerateReport(ticker)

if not os.path.exists('static/modelresults'):
    os.makedirs('static/modelresults')

#GenerateReport('CMG')

for t in tickers:
    try:
        PBarGenerateReport(t)
    except:
        print("Error generating report of ticker " + t)
        continue
