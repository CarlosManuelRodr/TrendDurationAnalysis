from yahoo_fin import stock_info as si
from tqdm import tqdm
from datetime import date
from datetime import timedelta
import os

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
           "T","TDG","TDY","TEL","TER","TFC","TFX","TGT","TIF","TJX","TMO","TMUS","TPR","TROW",
           "TRV","TSCO","TSN","TT","TTWO","TWTR","TXN","TXT","TYL","VAR","VFC","VIAC","VLO","VMC",
           "VNO","VRSK","VRSN","VRTX","VTR","VTRS","VZ","WAB","WAT","WBA","WDC","WEC","WELL",
           "WFC","WHR","WLTW","WMB","WM","WMT","WRB","WST","WU","WY","WYNN","XEL","XLNX",
           "XOM","XRAY","XRX","XYL","YUM","ZBH","ZBRA","ZION","ZTS"]

print("Downloading tickers...")

pbar = tqdm(total=len(tickers))

def get_daily_data_from_ticker(ticker):
    pbar.update(1)
    todayDate = date.today()
    lookBack = timedelta(days=5000)
    return si.get_data(ticker, start_date=todayDate-lookBack, end_date=todayDate, 
                       interval='1d', index_as_date=False)


if not os.path.exists('SP500'):
    os.makedirs('SP500')

for i in range(len(tickers)):
    try:
        data =  get_daily_data_from_ticker(tickers[i])
    except:
        print("Server did not respond correctly to request of ticker " + tickers[i])
        continue

    f = open('SP500/' + tickers[i] + ".csv", "w+")
    if not data.empty:
        f.write(data.drop(columns=['ticker']).to_csv(index=False))
    else:
        f.write("Failed")
    f.close()
    
print("Done!")
