from yahoo_fin import stock_info as si
from tqdm import tqdm
from datetime import date
from datetime import timedelta
import os

def GetDailyDataFromTicker(ticker, pbar):
    todayDate = date.today()
    lookBack = timedelta(days=5000)
    data =  si.get_data(ticker, start_date=todayDate-lookBack, end_date=todayDate, 
                        interval='1d', index_as_date=False)
    pbar.update(1)
    return data

def GetDailyData(tickers):
    pbar = tqdm(total=len(tickers))

    if not os.path.exists('static/sp500'):
        os.makedirs('static/sp500')

    for i in range(len(tickers)):
        success = False
        
        while not success:
            try:
                data =  GetDailyDataFromTicker(tickers[i], pbar)
                success = True
            except:
                print("Server did not respond correctly to request of ticker " + tickers[i])
                print("Trying again")

        f = open('static/sp500/' + tickers[i] + ".csv", "w+")
        if not data.empty:
            f.write(data.drop(columns=['ticker']).to_csv(index=False))
        else:
            f.write("Failed")
        f.close()

    pbar.close()

if __name__ == "__main__":
    testTickers = ["AAPL", "AMC", "PLTR", "NOK", "GME", "TSLA", "SPY", "INTC", "AMD", "BRK-B", 
                   "NVDA", "MSFT", "AMZN"]
    print("Downloading tickers...")
    GetDailyData(testTickers)
    print("Done!")
