import pandas
from flask import Flask, escape, request, render_template

app = Flask(__name__)

tickers = ["AAL","AAP","AAPL","ABBV","ABC","ABMD","ABT","ACN","A","ADBE","ADI","ADM",
           "ADP","ADSK","AEE","AEP","AES","AFL","AIG","AIV","AIZ","AJG","AKAM","ALB",
           "ALGN","ALK","ALL","ALLE","ALXN","AMAT","AMC","AMD","AME","AMGN","AMP","AMT","AMZN",
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
           "FRT","FTI","FTNT","FTV","GD","GE","GILD","GIS","GL","GLW","GM","GME","GOOG","GOOGL",
           "GPC","GPN","GPS","GRMN","GS","GWW","HAL","HAS","HBAN","HBI","HCA","HD","HES",
           "HFC","HIG","HII","HLT","HOLX","HON","HPE","HPQ","HRL","HSIC","HST","HSY","HUM",
           "HWM","IBM","ICE","IDXX","IEX","IFF","ILMN","INCY","INFO","INTC","INTU","IP","IPG",
           "IPGP","IQV","IR","ITW","IVZ","JBHT","JCI","J","JKHY","JNJ","JNPR","JPM","K","KEY",
           "KEYS","KHC","KIM","KLAC","KMB","KMI","KMX","KO","KR","KSU","LB","L","LDOS","LEG",
           "LEN","LH","LHX","LIN","LKQ","LLY","LMT","LNC","LNT","LOW","LRCX","LUMN","LUV",
           "LVS","LW","LYB","LYV","MAA","MA","MAR","MAS","MCD","MCHP","MCK","MCO","MDLZ",
           "MDT","MET","MGM","MHK","MKC","MKTX","MLM","MMC","MMM","MNST","MO","MOS","MPC",
           "MRK","MRO","MSCI","MS","MSFT","MSI","MTB","MTD","MU","MXIM","NCLH","NDAQ","NEE",
           "NEM","NFLX","NI","NOK","NOV","NOW","NRG","NSC","NTAP","NTRS","NUE","NVDA","NVR","NWL",
           "NWSA","NWS","O","ODFL","OKE","OMC","ORCL","ORLY","OTIS","OXY","PAYC","PAYX","PBCT",
           "PCAR","PEAK","PEG","PEP","PG","PGR","PH","PHM","PKG","PKI","PLD","PLTR","PM","PNC","PNR",
           "PNW","POOL","PPG","PPL","PRGO","PRU","PSA","PSX","PVH","PWR","PXD","PYPL","QCOM",
           "QRVO","RCL","RE","REG","REGN","RF","RHI","RJF","RL","RMD","ROK","ROL","ROP","ROST",
           "RSG","RTX","SBAC","SBUX","SCHW","SEE","SHW","SIVB","SJM","SLB","SLG","SNA","SNPS",
           "SO","SPG","SPGI","SPY","SRE","STE","STT","STX","STZ","SWK","SWKS","SYF","SYK","SYY","TAP",
           "T","TDG","TDY","TEL","TER","TFC","TFX","TGT", "TJX","TMO","TMUS","TPR","TROW",
           "TRV","TSCO","TSLA","TSN","TT","TTWO","TWTR","TXN","TXT","TYL","VAR","VFC","VIAC","VLO","VMC",
           "VNO","VRSK","VRSN","VRTX","VTR","VTRS","VZ","WAB","WAT","WBA","WDC","WEC","WELL",
           "WFC","WHR","WLTW","WMB","WM","WMT","WRB","WST","WU","WY","WYNN","XEL","XLNX",
           "XOM","XRAY","XRX","XYL","YUM","ZBH","ZBRA","ZION","ZTS"]

tickers.sort()

# Auxiliary
def get_ticker_plot_path(ticker):
    return "static/modelresults/" + ticker + "_Plot.png"

def get_ticker_last_date(ticker):
    tickerPath = "static/sp500/" + ticker + ".csv"
    dataFrame = pandas.read_csv(tickerPath)
    return dataFrame["date"].tolist()[-1]

def build_line(dataFrame, i):
    return {
        "days": dataFrame["Cantidad de días"][i],
        "pvalue": dataFrame["P-Valor"][i],
        "interpretation": dataFrame["Interpretación"][i]
    }

def get_ticker_table(ticker):
    tablePath = "static/modelresults/" + ticker + "_Report.csv"
    dataFrame = pandas.read_csv(tablePath)
    return [build_line(dataFrame, i) for i in range(len(dataFrame))]

# Web page
@app.route('/')
def home_page():
    return render_template('index.html', tickers = tickers)

@app.route("/analysis" , methods=['GET', 'POST'])
def calculate():
    select = request.form.get('stock_select')
    ticker = str(select)
    plotPath = get_ticker_plot_path(ticker)
    latestDate = get_ticker_last_date(ticker)
    tickerTable = get_ticker_table(ticker)

    return render_template('analysis.html', 
                            plotPath = plotPath, 
                            latestDate = latestDate, 
                            tickerTable = tickerTable
                        )