import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
    return trendDurations.count(j)/len(trendDurations)

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
    testResult = "Geométrico" if pValue >= 0.05 else "No geométrico"
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
    dates = GetDates("static/sp500/" + ticker + ".csv")
    closePrices = GetPrices("static/sp500/" + ticker + ".csv")
    datedPrices = np.transpose([dates,closePrices]).tolist()
    TestModelLatest(closePrices).to_csv("static/modelresults/" + ticker + "_Report.csv", index=False)
    PlotTestModelInTimeResults(TestModelInTime(datedPrices, 100, 1), ticker, "static/modelresults/" + ticker + "_Plot.png")

def PBarGenerateReport(ticker, pbar):
    pbar.update(1)
    GenerateReport(ticker)

def GenerateAllReports(tickers):
    if not os.path.exists('static/modelresults'):
        os.makedirs('static/modelresults')

    pbar = tqdm(total=len(tickers))
    for t in tickers:
        try:
            PBarGenerateReport(t, pbar)
        except:
            print("Error generating report of ticker " + t)
            continue
    pbar.close()

if __name__ == "__main__":
    testTickers = ["AAPL", "AMC", "PLTR", "NOK", "GME", "TSLA", "SPY", "INTC", "AMD", "BRK-B", 
                   "NVDA", "MSFT", "AMZN"]
    print("Starting to generate reports...")
    GenerateAllReports(testTickers)
    print("Done!")
